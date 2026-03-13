import requests
import json
import time


import os

class ExplanationGenerator:
    def __init__(self, domain_id: str, inference_engine=None, use_local=True, model_name="gemma:2b"):
        self.domain_id = domain_id
        self.ie = inference_engine
        self.use_local = use_local
        self.model_name = model_name
        
        # Ollama API endpoint
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_url = f"{self.base_url}/api/generate"
        
        from utils.rule_loader import RuleLoader
        self.rule_loader = RuleLoader(domain_id=domain_id)
        
        if self.use_local:
            print(f"Connecting to Ollama ({self.base_url}) with model: {self.model_name} for Domain: {domain_id}...")
            self._test_ollama_connection()

    def _test_ollama_connection(self):
        """Test Ollama connection with proper retry and timeout handling."""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # First, check if Ollama is running at all
                health_check = requests.get(self.base_url, timeout=2)
                
                # Then try a simple generation (this might take time on first load)
                print(f"  Attempt {attempt + 1}/{max_retries}: Testing model '{self.model_name}'...")
                
                test_response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.model_name,
                        "prompt": "test",
                        "stream": False
                    },
                    timeout=30  # Give it 30 seconds for first load
                )
                
                if test_response.status_code == 200:
                    print(f"✓ Successfully connected to Ollama with model: {self.model_name}")
                    return
                elif test_response.status_code == 404:
                    print(f"⚠ Model '{self.model_name}' not found. Attempting to auto-pull...")
                    try:
                        pull_response = requests.post(f"{self.base_url}/api/pull", json={"name": self.model_name}, stream=True, timeout=600)
                        if pull_response.status_code == 200:
                            print(f"✓ Successfully initiated pull for {self.model_name}. This may take a while.")
                            # Continue to retry loop to wait for it to be ready
                            time.sleep(10)
                            continue
                        else:
                            print(f"✗ Failed to auto-pull model: {pull_response.text}")
                    except Exception as e:
                        print(f"✗ Auto-pull failed: {e}")
                    
                    # If auto-pull fails or is not supported, just warn but allow startup
                    print(f"⚠ WARNING: Model '{self.model_name}' missing. LLM features will fail until installed.")
                    print(f"  Run: docker exec -it expert-agent-ollama ollama pull {self.model_name}")
                    return # Don't crash, allow backend to start for Admin UI
                else:
                    print(f"⚠ Ollama responded with status: {test_response.status_code}")
                    
            except Exception as e:
                print(f"⚠ WARNING: Ollama connection failed: {e}")
                print("  LLM features will be unavailable until Ollama is ready.")
                return 

    def generate_explanation(self, inference_result, risk_level="low"):
        """
        RAG: Combines retrieved sections into a final answer using local LLM.
        Enhanced with Enterprise JSON-schema enforcement for high-risk intents.
        """

        context_parts = []
        doc_results = inference_result.get("top_sections", [])
        for doc_item in doc_results:
            for sec in doc_item.get("sections", []) or []:
                content = sec.get("context")
                if content:
                    context_parts.append(content)

        context_text = "\n\n".join(context_parts) or "No relevant documentation found."

        # Enterprise Constraint: Structured output for High-Risk/Critical intents
        is_high_risk = risk_level in ["high", "critical"]
        
        # 1. Load Template from DB
        templates = self.rule_loader.load_templates()
        intent = inference_result.get("intent", "General")
        template_info = templates.get(intent) or templates.get("General")
        
        if template_info:
            template = template_info.get("template_body") # Use template_body from PromptTemplate
            # Simple placeholder replacement
            prompt = template.replace("{question}", inference_result.get('question'))
            prompt = prompt.replace("{context}", context_text)
        else:
            # Absolute fallback if no template in DB
            prompt = f"Answer this question based on context:\nQ: {inference_result.get('question')}\nContext: {context_text}"

        # 2. Call local LLM
        try:
            answer = self._call_ollama(prompt, format_json=is_high_risk)
            
            # 3. Post-process structured output
            if is_high_risk:
                answer = self._post_process_structured_json(answer)
        except Exception as e:
            answer = f"Error generating response: {str(e)}"

        # If Ollama returned nothing or an error marker, fall back to a simple RAG summary
        if not answer or answer.strip() == "No response generated" or answer.startswith("❌") or answer.startswith("Error"):
            if context_text and context_text != "No relevant documentation found.":
                snippet = context_text.strip()[:1000]
                answer = f"### Documentation Snippet\n\n{snippet}..."
            else:
                answer = "No documentation available to answer this question."

        return self._format_final_response(answer, inference_result)

    def _post_process_structured_json(self, raw_json: str) -> str:
        """Parse and format structured JSON output for the final UI."""
        try:
            data = json.loads(raw_json)
            formatted = f"### 🛡️ Secure Answer\n{data.get('answer', 'N/A')}\n\n"
            formatted += f"### 🛠️ Implementation\n{data.get('implementation', 'N/A')}\n\n"
            
            warnings = data.get('security_warnings', [])
            if warnings:
                formatted += "### ⚠️ Security Compliance\n"
                for w in warnings:
                    formatted += f"- {w}\n"
                    
            return formatted
        except:
            # Fallback if LLM failed to produce valid JSON despite prompt discipline
            return raw_json

    def _call_ollama(self, prompt, format_json=False):
        """Call Ollama API with optional JSON format enforcement."""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2 if format_json else 0.7, # Lower temperature for structural stability
                "top_p": 0.9,
                "num_predict": 1000 if format_json else 500
            }
        }
        
        if format_json:
            payload["format"] = "json" # Ollama structured output enforcement
        
        try:
            print("  Generating response with Ollama...")
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=120  # 2 minutes for generation
            )
            response.raise_for_status()
            result = response.json()
            
            # DEBUG: Print raw response start to see structure
            # (Debug print removed for cleanup)

            # Primary extraction for /api/chat
            answer = None
            if "message" in result and "content" in result["message"]:
                answer = result["message"]["content"]
            
            # Fallback extraction
            if not answer:
                # Robust extraction of text from various possible Ollama shapes
                def extract_text(obj):
                    if obj is None:
                        return None
                    if isinstance(obj, str):
                        return obj
                    if isinstance(obj, dict):
                        # dive into common wrapper keys
                        for wrap in ("result", "data", "outputs", "generated", "generation"):
                            if wrap in obj and obj[wrap]:
                                text = extract_text(obj[wrap])
                                if text:
                                    return text
                        # common keys used by LLM APIs
                        for key in ("response", "text", "result", "output", "reply", "answer", "content"):
                            if key in obj and obj[key]:
                                text = extract_text(obj[key])
                                if text:
                                    return text
                        # choices/messages pattern
                        if "choices" in obj and isinstance(obj["choices"], list) and obj["choices"]:
                            return extract_text(obj["choices"][0])
                        if "message" in obj:
                            return extract_text(obj["message"]) 
                    if isinstance(obj, list) and obj:
                        # try first element with text
                        for item in obj:
                            text = extract_text(item)
                            if text:
                                return text
                    return None
            
                answer = extract_text(result)

            if not answer:
                print(f"  ⚠ Failed to extract answer from: {json.dumps(result)[:200]}")
                answer = "No response generated"

            print(f"  ✓ Generated {len(answer)} characters")
            return answer
            
        except requests.exceptions.Timeout:
            return "⏱ Request timed out. The model is taking too long to respond. Try a smaller model like 'phi3' or increase timeout."
        except requests.exceptions.RequestException as e:
            return f"❌ Error calling Ollama: {str(e)}"
        except json.JSONDecodeError:
            return "❌ Error parsing Ollama response - received invalid JSON"

    def _stream_ollama(self, prompt: str):
        """Streaming version of _call_ollama for internal pipeline use."""
        from engines.ollama_client import OllamaClient
        client = OllamaClient(base_url=self.base_url, model=self.model_name)
        
        for chunk in client.stream_generate(prompt):
            yield chunk

    def stream_explanation(self, inference_result, risk_level="low", target_language="en"):
        """
        Streaming version of generate_explanation.
        Yields (type, data) tuples: ('status', msg), ('chunk', text), ('trace', data)
        """
        context_parts = []
        doc_results = inference_result.get("top_sections", [])
        for doc_item in doc_results:
            for sec in doc_item.get("sections", []) or []:
                content = sec.get("context")
                if content:
                    context_parts.append(content)

        context_text = "\n\n".join(context_parts) or "No relevant documentation found."
        is_high_risk = risk_level in ["high", "critical"]
        
        # 1. Load Template from DB
        templates = self.rule_loader.load_templates()
        intent = inference_result.get("intent", "General")
        template_info = templates.get(intent) or templates.get("General")
        
        if template_info:
            template = template_info.get("template")
            prompt = template.replace("{question}", inference_result.get('question'))
            prompt = prompt.replace("{context}", context_text)
            if target_language != "en":
                prompt += f"\nAnswer in {target_language} language."
        else:
            prompt = f"Answer in {target_language}:\nQ: {inference_result.get('question')}\nContext: {context_text}"

        # 2. Call local LLM (streaming)
        yield "status", "✍️ Generating expert response..."
        
        full_answer = ""
        collated_chunk = ""
        
        # We need an internal client for streaming if not already there
        from engines.ollama_client import OllamaClient
        client = OllamaClient(base_url=self.base_url, model=self.model_name)
        
        for chunk in client.stream_generate(prompt):
            full_answer += chunk
            yield "chunk", chunk

        # 3. Final trace info
        trace_info = {
            "sources": [d.get("name") for d in inference_result.get("selected_documents", []) if isinstance(d, dict)],
            "rules": [r.get("name") if isinstance(r, dict) else str(r) for r in inference_result.get("activated_rules", [])]
        }
        yield "trace", trace_info
        
        # Build the final formatted output for legacy support or internal use
        output = [
            "### 🤖 AI Expert Answer",
            full_answer,
            "\n---\n",
            "### 📚 Reasoning & Sources",
        ]
        
        # Add top source if available
        if inference_result.get('selected_documents'):
            top_doc = inference_result['selected_documents'][0]
            if isinstance(top_doc, dict):
                info = top_doc.get("info", {}) or {}
                top_doc_name = info.get("name") or top_doc.get("name") or "N/A"
                output.append(f"**Top Source:** {top_doc_name}")

                if top_doc.get("sections"):
                    section_names = [s.get("section", "Unknown") for s in top_doc["sections"][:3]]
                    output.append(f"**Top Sections:** {' | '.join(section_names)}")
            else:
                output.append(f"**Top Source:** {top_doc}")

        if inference_result.get('keywords'):
            keywords = inference_result.get('keywords', [])[:5]
            output.append(f"**Keywords:** {', '.join(keywords)}")

        rules = inference_result.get("activated_rules", [])
        if rules:
            descriptions = [
                r.get("description", str(r))
                for r in rules
                if isinstance(r, dict)
            ]
            if descriptions:
                output.append(f"**Expert Rules Triggered:** {', '.join(descriptions)}")

        yield "final_text", "\n\n".join(output)

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from api.auth import get_current_user_optional, User
from api.routers.utils import detect_language, translate_text

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    question: str
    model: str = "gemma:2b"
    mode: str = "hybrid"  # "internal", "external", or "hybrid"
    domain_id: Optional[str] = None
    tenant_id: Optional[str] = None

class IntentHypothesis(BaseModel):
    intent: str
    confidence: float
    evidence: List[str]

class NLPAnalysisResponse(BaseModel):
    intent_hypotheses: List[IntentHypothesis]
    entities: Dict[str, str]
    semantic_roles: Dict[str, str]
    keywords: List[str]
    question_type: str

class IntentArbitrationResponse(BaseModel):
    final_intent: str
    confidence: float
    reason: str
    rejected_intents: List[str]

class RetrievalPathResponse(BaseModel):
    tier1_symbolic: Dict[str, Any]
    tier2_semantic: Dict[str, Any]
    final_documents: List[str]

class AnswerPlanResponse(BaseModel):
    goal: str
    structure: str
    steps: List[str]
    excluded_topics: List[str]
    max_length: int

class DocumentReference(BaseModel):
    name: str
    score: float
    sections: List[str]

class ChatResponse(BaseModel):
    answer: str
    reasoning: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    confidence: float
    architecture_info: Optional[Dict[str, str]] = None
    detected_language: str
    explanation: Optional[Dict[str, Any]] = None # Logic for refusal
    source: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_hybrid(request: ChatRequest, req: Request, user: User = Depends(get_current_user_optional)):
    """Standard (Non-streaming) Hybrid API Endpoint"""
    from core.pipeline_manager import pipeline_manager
    
    # 1. Determine Domain & Tenant
    domain_id = request.domain_id or user.domain_id
    tenant_id = request.tenant_id or user.tenant_id
    
    if not domain_id:
        raise HTTPException(status_code=400, detail="domain_id is required either in request or user context")
        
    # 2. Get Pipeline
    pipeline = pipeline_manager.get_pipeline(domain_id=domain_id, tenant_id=tenant_id)
    original_query = request.question
    lang = detect_language(original_query)
    english_query = translate_text(original_query, lang, 'en')
    
    res = pipeline.process(question=english_query, user=user, target_language=lang)
    
    return ChatResponse(
        answer=res.answer,
        reasoning=res.reasoning,
        validation=res.validation,
        confidence=res.confidence,
        architecture_info={"layers": "8", "orchestrator": "HybridPipelineV2"},
        detected_language=lang,
        source="Full Pipeline"
    )

@router.post("/chat/stream")
async def chat_hybrid_stream(request: ChatRequest, req: Request, user: User = Depends(get_current_user_optional)):
    import json
    import asyncio
    import dataclasses
    from fastapi.responses import StreamingResponse
    
    # Custom encoder for handles dataclasses, numpy types, etc.
    class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            from enum import Enum
            if isinstance(obj, Enum):
                return obj.value
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            try:
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
            except ImportError:
                pass
            return super().default(obj)

    def safe_json_dumps(obj):
        return json.dumps(obj, cls=EnhancedJSONEncoder)

    from core.pipeline_manager import pipeline_manager
    import time
    
    # 1. Determine Domain & Tenant
    domain_id = request.domain_id or user.domain_id
    tenant_id = request.tenant_id or user.tenant_id
    
    if not domain_id:
        raise HTTPException(status_code=400, detail="domain_id is required either in request or user context")
        
    # 2. Get Pipeline
    pipeline = pipeline_manager.get_pipeline(domain_id=domain_id, tenant_id=tenant_id)
    dual_llm = req.app.state.dual_llm
    original_query = request.question
    mode = request.mode or "full"
    
    print(f"📡 New Hybrid Stream Request | Query: '{original_query[:50]}...' | Mode: {mode}")

    # 1. Detect Language & Translate
    try:
        lang = detect_language(original_query)
        english_query = translate_text(original_query, lang, 'en')
        print(f"  └─ Lang: {lang} | Translated: '{english_query[:30]}...'")
    except Exception as e:
        print(f"  └─ ⚠️ Pre-processing error: {e}")
        lang, english_query = 'en', original_query

    async def event_generator():
        # Initialize queue and loop here so they are available in all modes
        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()
        
        try:
            # Mode-based Logic
            if mode == "llm":
                # Security Check
                yield f"data: {safe_json_dumps({'type': 'status', 'message': '🔒 Security check...'})}\n\n"
                security_check = pipeline.security.check_query_security(english_query, user)
                if not security_check.allowed:
                    pipeline.audit.log_rejection(english_query, user, security_check.reason, "llm_bypass")
                    yield f"data: {safe_json_dumps({'type': 'error', 'message': f'Security Violation: {security_check.reason}'})}\n\n"
                    return

                yield f"data: {safe_json_dumps({'type': 'status', 'message': '🚀 Querying Pure AI (LLM)...'})}\n\n"
                
                client = dual_llm.client 
                prompt = f"Answer this question: {english_query}"
                
                start_time = time.time()

                def run_llm():
                    try:
                        for chunk in client.stream_generate(prompt):
                            if loop.is_running():
                                loop.call_soon_threadsafe(queue.put_nowait, chunk)
                    except Exception as e:
                        print(f"❌ LLM Stream Error: {e}")
                    finally:
                        if loop.is_running():
                            loop.call_soon_threadsafe(queue.put_nowait, None)

                asyncio.create_task(asyncio.to_thread(run_llm))
                
                full_content = ""
                while True:
                    chunk = await queue.get()
                    if chunk is None: break
                    full_content += chunk
                    yield f"data: {safe_json_dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # Log to audit
                pipeline.audit.log_query(
                    query=english_query,
                    user=user,
                    intent="General (LLM Bypass)",
                    decision={"action": "approved", "source": "Pure LLM"},
                    trace_id="llm_bypass",
                    security_check={"allowed": True, "risk_level": "medium"},
                    performance={"total_time_ms": (time.time() - start_time) * 1000}
                )

                yield f"data: {safe_json_dumps({'type': 'final', 'source': 'Pure LLM', 'confidence': 1.0, 'architecture_info': {'type': 'Direct LLM', 'mode': 'llm'}})}\n\n"

            elif mode == "external":
                # Security Check
                yield f"data: {safe_json_dumps({'type': 'status', 'message': '🔒 Security check...'})}\n\n"
                security_check = pipeline.security.check_query_security(english_query, user)
                if not security_check.allowed:
                    pipeline.audit.log_rejection(english_query, user, security_check.reason, "lod_bypass")
                    yield f"data: {safe_json_dumps({'type': 'error', 'message': f'Security Violation: {security_check.reason}'})}\n\n"
                    return

                yield f"data: {safe_json_dumps({'type': 'status', 'message': '🌐 Querying Linked Data (DBpedia)...'})}\n\n"
                from agents.hybrid_agent import HybridKnowledgeAgent
                agent = HybridKnowledgeAgent()
                
                start_time = time.time()
                response = await asyncio.to_thread(agent.ask, english_query, mode="external")
                
                yield f"data: {safe_json_dumps({'type': 'chunk', 'content': response['answer']})}\n\n"
                
                # Log to audit
                pipeline.audit.log_query(
                    query=english_query,
                    user=user,
                    intent="General (LOD Bypass)",
                    decision={"action": "approved", "source": response['source']},
                    trace_id="lod_bypass",
                    security_check={"allowed": True, "risk_level": "medium"},
                    performance={"total_time_ms": (time.time() - start_time) * 1000}
                )

                yield f"data: {safe_json_dumps({'type': 'final', 'source': response['source'], 'confidence': 1.0, 'architecture_info': {'type': 'LOD Agent', 'mode': 'external'}})}\n\n"

            else: # full / internal / auto
                def run_pipeline():
                    try:
                        for event in pipeline.stream_process(question=english_query, user=user, target_language=lang):
                            if loop.is_running():
                                loop.call_soon_threadsafe(queue.put_nowait, event)
                    except Exception as e:
                        print(f"❌ Pipeline Stream Error: {e}")
                    finally:
                        if loop.is_running():
                            loop.call_soon_threadsafe(queue.put_nowait, None)

                asyncio.create_task(asyncio.to_thread(run_pipeline))
                
                source = "Full Pipeline"
                while True:
                    event = await queue.get()
                    if event is None:
                        break
                    
                    if event.get("type") == "final":
                        # Ensure source is set if missing, but preserve pipeline's architecture_info
                        if not event.get("source"):
                            event["source"] = source
                        
                        reasoning = event.get("reasoning", {})
                        docs_count = len(reasoning.get("documents", []))
                        print(f"  └─ ✅ Final Event Sent | Sources: {docs_count} | Confidence: {event.get('confidence')}")
                    
                    yield f"data: {safe_json_dumps(event)}\n\n"

        except Exception as e:
            print(f"❌ Critical Stream Error: {e}")
            try:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            except:
                pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")

def build_agent_reasoning(query: str, response: Dict) -> Dict:
    intent = response.get("intent", "General")
    entity = response.get("entity")
    docs_list = response.get("documents", [])
    return {
        "nlp_analysis": {
            "intent_hypotheses": [{"intent": intent, "confidence": 1.0, "evidence": ["Keyword Match"]}],
            "question_type": "Factoid" if "what" in query.lower() else "Procedure",
            "keywords": [entity] if entity else [],
            "entities": {"subject": entity} if entity else {},
            "semantic_roles": {}
        },
        "intent_arbitration": {"final_intent": intent, "confidence": 1.0, "reason": "Direct Mapping", "rejected_intents": []},
        "retrieval_path": {
            "tier1_symbolic": {"topic_filter": "Mapped", "forbidden_docs": [], "eligible_count": len(docs_list)},
            "tier2_semantic": {"top_scores": [[d.get("name", "Unknown"), d.get("score", 0.0)] for d in docs_list]},
            "final_documents": [d.get("name", "Unknown") for d in docs_list]
        },
        "answer_plan": {"goal": f"Answer about {intent}", "structure": "Definition", "steps": ["Retrieve", "Translate"], "excluded_topics": [], "max_length": 1500},
        "documents": [{"name": d.get("name", "Unknown"), "score": d.get("score", 0.0), "sections": []} for d in docs_list]
    }

def build_dual_reasoning(mode: str, meta: Dict) -> Dict:
    return {
        "nlp_analysis": {
            "intent_hypotheses": [{"intent": meta.get("intent", "General"), "confidence": meta.get("confidence", 0.0), "evidence": []}],
            "question_type": "Data Retrieval" if mode == "expert" else "Generation",
            "keywords": [],
            "entities": meta.get("entities", {}),
            "semantic_roles": {}
        },
        "intent_arbitration": {"final_intent": meta.get("intent", "General"), "confidence": meta.get("confidence", 1.0), "reason": f"Routed to {mode.upper()}", "rejected_intents": []},
        "retrieval_path": {"tier1_symbolic": {"topic_filter": mode}, "tier2_semantic": {"top_scores": []}, "final_documents": []},
        "answer_plan": {"goal": "Dual-Mode Response", "structure": "Direct", "steps": ["Route", "Execute"], "excluded_topics": [], "max_length": 1000},
        "documents": []
    }

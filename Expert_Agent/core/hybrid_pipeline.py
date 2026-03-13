
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import time
import uuid

# Import all layers
from agents.expert_agent import ExpertAgent
from core.nlp_core import AdvancedNLPCore, NLPAnalysis
from core.intent_arbitration import IntentArbitrator
from core.answer_planner import AnswerPlanner, AnswerPlan
from data.knowledge_base import KnowledgeBase
from security.security_enforcer import SecurityEnforcer
from security.audit_logger import AuditLogger
from engines.retrieval_engine import AgentDrivenRetrieval
from engines.ollama_client import OllamaClient
from utils.explanation import ExplanationGenerator
from agents.validation_agent import ValidationAgent
from api.auth import User
from data.cache_manager import cache
from data.cache_governance import get_governance, nlp_cache_key

@dataclass
class HybridResponse:
    """Complete response from the hybrid system"""
    answer: str
    reasoning: Dict[str, Any]
    validation: Dict[str, Any]
    confidence: float
    detected_language: Optional[str] = None

class HybridPipeline:
    """
    Main Hybrid NLP-Expert Agent Pipeline.
    Orchestrates all 8 layers in the correct sequence.
    Now fully domain-agnostic and database-driven.
    """
    
    def __init__(self, domain_id: str, tenant_id: str = None, use_embeddings=True, use_local_llm=True, model_name="gemma:2b"):
        self.domain_id = domain_id
        self.tenant_id = tenant_id
        
        print(f"🚀 Initializing Hybrid Pipeline (Domain: {domain_id}, Tenant: {tenant_id})...")
        
        # Layer 1: Advanced NLP Core (Domain-aware)
        self.nlp_core = AdvancedNLPCore(domain_id=domain_id)
        
        # Security & Audit (Domain-aware)
        self.security = SecurityEnforcer(domain_id=domain_id)
        self.audit = AuditLogger(log_dir=f"audit_db/{domain_id}")
        
        # Layer 2: Expert Agent Core (Domain-aware)
        self.expert_agent = ExpertAgent(domain_id=domain_id)
        
        # Layer 3: Intent Arbitration
        self.arbitrator = IntentArbitrator(self.expert_agent)
        
        # Knowledge Base (Domain-aware)
        self.kb = KnowledgeBase(domain_id=domain_id, enable_auto_discovery=True)
        
        # Layer 4: Agent-Driven Retrieval (Domain-aware)
        embedder = None
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                embedder = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                print("⚠️  Embeddings not available")
        
        self.retrieval = AgentDrivenRetrieval(
            self.kb, 
            self.expert_agent, 
            embedder, 
            domain_id=domain_id,
            tenant_id=tenant_id
        )
        
        # Layer 5: Answer Planning
        self.planner = AnswerPlanner(self.expert_agent)
        
        # Layer 6: Controlled NLP Generation
        self.generator = ExplanationGenerator(
            domain_id=domain_id,
            inference_engine=None,
            use_local=use_local_llm,
            model_name=model_name
        )
        
        # Layer 7: Self-Validation
        self.validator = ValidationAgent(self.expert_agent)
        
        print(f"✅ Hybrid Pipeline Ready for Domain: {domain_id}")

    def process(self, question: str, user: User, max_retries: int = 1, target_language: Optional[str] = None) -> HybridResponse:
        start_time = time.time()
        trace_id = uuid.uuid4().hex
        
        # 🔒 Security Check
        security_check = self.security.check_query_security(question, user)
        if not security_check.allowed:
            self.audit.log_rejection(question, user, security_check.reason, trace_id, self.domain_id, self.tenant_id)
            return self._create_rejection_response(security_check.reason, trace_id)

        # 🟢 Cache Check (Governance-aware)
        user_id = user.id if user else "anonymous"
        user_role = user.role.value if hasattr(user, 'role') and hasattr(user.role, 'value') else "guest"
        cache_key = nlp_cache_key(question, user_id, user_role)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"🚀 Cache Hit: {cache_key}")
            # Log with cache_hit=True
            self.audit.log_query(
                question, user, cached_data.get("reasoning", {}).get("intent", "unknown"),
                cached_data, trace_id, self.domain_id, self.tenant_id,
                performance={"total_time_ms": 0, "cache_hit": True}
            )
            return HybridResponse(**cached_data)
            
        # 🧠 NLP Analysis
        nlp_analysis = self.nlp_core.analyze(question)
        
        # ⚖️ Intent Arbitration
        arbitration = self.arbitrator.arbitrate(nlp_analysis, user=user)
        
        # RBAC Check
        access_check = self.security.check_access(arbitration.final_intent, user)
        if not access_check.allowed:
            self.audit.log_rejection(question, user, access_check.reason, trace_id, self.domain_id, self.tenant_id)
            return self._create_rejection_response(access_check.reason, trace_id)

        # 🛡️ Rule Enforcement (Layer 2 Override)
        applicable_rules = self.expert_agent.get_applicable_rules(arbitration.final_intent, user, nlp_analysis)
        for rule in applicable_rules:
            action = rule.get_action()
            if action.get("message"):
                print(f"🛑 Rule {rule.id} triggered with deterministic message. Overriding pipeline.")
                # We stop here - deterministic rules are authoritative
                return HybridResponse(
                    answer=action["message"],
                    reasoning={
                        "logic": "production_rule_override",
                        "rule_id": rule.id,
                        "intent": arbitration.final_intent,
                        "description": rule.description
                    },
                    validation={"valid": True, "checks": {"rule_override": True}},
                    confidence=1.0
                )

        # 🔍 Retrieval
        retrieved_docs, retrieval_trace, grounding_report, kg_facts = self.retrieval.retrieve(
            arbitration.final_intent,
            nlp_analysis,
            max_docs=2,
            user=user
        )
        
        # 📋 Planning
        answer_plan = self.planner.create_plan(arbitration.final_intent, retrieved_docs, nlp_analysis)
        
        # ✍️ Generation
        inference_result = {
            "question": question,
            "top_sections": [{"sections": [{"context": doc.get("best_chunk") or doc.get("content")} for doc in retrieved_docs]}],
            "activated_rules": [asdict(r) if hasattr(r, "__dataclass_fields__") else r for r in self.expert_agent.get_applicable_rules(arbitration.final_intent, user, nlp_analysis)],
            "selected_documents": retrieved_docs,
            "keywords": nlp_analysis.keywords
        }
        
        # Build constrained prompt (Domain-agnostic)
        prompt = self._build_constrained_prompt(answer_plan, question, target_language)
        answer = self.generator._call_ollama(prompt)
        
        # ✅ Validation
        validation = self.validator.validate(answer, answer_plan, arbitration.final_intent)
        
        # 🔒 Strict Security Rejection (Layer 7 Enforcement)
        if not validation.checks.get("forbidden_topics", True):
            self.audit.log_rejection(question, user, "Security violation: Forbidden topic detected in answer.", trace_id, self.domain_id, self.tenant_id)
            return self._create_rejection_response("I am not authorized to reveal secret information as per policy.", trace_id)
        
        # 📊 Trace & Confidence
        reasoning = self._build_reasoning_trace(nlp_analysis, arbitration, retrieval_trace, answer_plan, retrieved_docs, grounding_report)
        confidence = self._calculate_confidence(arbitration, validation, retrieved_docs)
        
        # 📝 Audit to JSONL
        total_time = (time.time() - start_time) * 1000
        self.audit.log_query(
            query=question,
            user=user,
            intent=arbitration.final_intent,
            decision={"action": "approved" if validation.valid else "flagged", "final_intent": arbitration.final_intent},
            trace_id=trace_id,
            domain_id=self.domain_id,
            tenant_id=self.tenant_id,
            performance={"total_time_ms": total_time}
        )

        # 💾 Audit to PostgreSQL Transactional Tables
        try:
            from data.database import SessionLocal
            from api.models import (
                Query, ReasoningTrace, GeneratedAnswer, RuleExecutionHistory,
                AnswerPlan, ValidationReport, RetrievalEvent, ModelUsageMetric,
                AuditLog, SecurityEvent
            )
            
            db = SessionLocal()
            
            # Save Query
            new_query = Query(
                id=trace_id,
                user_id=user.id if hasattr(user, "id") else None,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                raw_question=question,
                detected_language=target_language or "en",
            )
            db.add(new_query)
            db.flush()
            
            # Save Trace
            new_trace = ReasoningTrace(
                id=trace_id,
                query_id=trace_id,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                nlp_output=reasoning.get("nlp_analysis"),
                intent_arbitration=reasoning.get("intent_arbitration"),
                rules_triggered={"applied": []},  # Extracted from expert engine
                retrieval_path=reasoning.get("retrieval_path"),
                answer_plan=reasoning.get("answer_plan"),
                validation={"score": reasoning.get("validation", {}).get("score", 0.0), "generation_model": "gemma:2b"}
            )
            db.add(new_trace)
            
            # Save Generated Answer
            new_answer = GeneratedAnswer(
                id=trace_id,
                query_id=trace_id,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                answer_text=answer,
                confidence=confidence,
                valid=validation.valid if hasattr(validation, 'valid') else True
            )
            db.add(new_answer)
            
            # Save Answer Plan
            plan_dict = reasoning.get("answer_plan", {})
            new_plan = AnswerPlan(
                id=uuid.uuid4().hex,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                goal=plan_dict.get("goal", "Answer query"),
                steps=plan_dict.get("steps", []),
                excluded_topics=plan_dict.get("excluded_topics", [])
            )
            db.add(new_plan)

            # Save ValidationReport
            db.add(ValidationReport(
                id=uuid.uuid4().hex,
                answer_id=trace_id,
                validation_score=reasoning.get("validation", {}).get("score", 0.0),
                issues=reasoning.get("validation", {}).get("issues", []),
                action_taken="approved" if validation.valid else "rejected"
            ))

            # Save Retrieval Events
            for idx, doc in enumerate(retrieved_docs):
                db.add(RetrievalEvent(
                    id=uuid.uuid4().hex,
                    query_id=trace_id,
                    domain_id=self.domain_id,
                    tenant_id=self.tenant_id,
                    relevance_score=doc.get("score", 0.9),
                    allowed=True
                ))

            # Save Model Usage Metric
            # prompt is not strictly defined here, we will mock it based on raw text size
            prompt_len = len(question) * 2
            db.add(ModelUsageMetric(
                query_id=trace_id,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                model_name="gemma:2b",
                prompt_tokens=prompt_len // 4,
                completion_tokens=len(answer) // 4,
                total_tokens=(prompt_len + len(answer)) // 4,
                inference_time_ms=int(total_time)
            ))

            # Save Audit Log
            db.add(AuditLog(
                id=uuid.uuid4().hex,
                user_id=user.id if hasattr(user, "id") else None,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                action="CHAT_QUERY",
                target="HybridPipeline",
                meta_info={"trace_id": trace_id, "intent": arbitration.final_intent}
            ))
            
            # Security Event (if flagged)
            if not security_check.allowed:
                db.add(SecurityEvent(
                    id=uuid.uuid4().hex,
                    event_type="PROMPT_INJECTION_OR_POLICY_VIOLATION",
                    user_id=user.id if hasattr(user, "id") else None,
                    domain_id=self.domain_id,
                    tenant_id=self.tenant_id,
                    severity="high",
                    details={"reason": getattr(security_check, "reason", "Security flagged")}
                ))
            
            db.commit()
            db.close()
            print(f"💾 Successfully saved DB logs for query {trace_id}")
        except Exception as db_e:
            print(f"❌ Failed to save to PostgreSQL logs: {db_e}")
            
        # 🟢 Prepare Final Response
        final_response = HybridResponse(
            answer=answer,
            reasoning=reasoning,
            validation=asdict(validation) if hasattr(validation, "__dataclass_fields__") else validation,
            confidence=confidence,
            detected_language=target_language or "en"
        )
        
        # 💾 Cache Result (Governance-aware)
        try:
            cache.set(cache_key, asdict(final_response), ttl=3600)
            print(f"💾 Cached response for {cache_key}")
        except Exception as cache_e:
            print(f"⚠️ Cache set failed: {cache_e}")
            
        return final_response

    def stream_process(self, question: str, user: User, target_language: Optional[str] = None):
        trace_id = uuid.uuid4().hex
        start_time = time.time()
        
        yield {"type": "status", "message": "🔒 Security check...", "layer": "security"}
        security_check = self.security.check_query_security(question, user)
        if not security_check.allowed:
            # Log and short-circuit on security violations
            self.audit.log_rejection(
                question,
                user,
                security_check.reason,
                trace_id,
                self.domain_id,
                self.tenant_id,
            )
            yield {"type": "error", "message": security_check.reason}
            return
        yield {
            "type": "layer_result",
            "layer": "security",
            "result": {
                "allowed": security_check.allowed,
                "reason": getattr(security_check, "reason", "Query permitted") or "Query permitted"
            }
        }

        # 🟢 Cache Check (Governance-aware)
        user_id = user.id if user else "anonymous"
        user_role = user.role.value if hasattr(user, 'role') and hasattr(user.role, 'value') else "guest"
        cache_key = nlp_cache_key(question, user_id, user_role)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"🚀 Cache Hit (Stream): {cache_key}")
            yield {"type": "status", "message": "🚀 Serving from cache..."}
            yield {"type": "chunk", "content": cached_data.get("answer", "")}
            
            # Log with cache_hit=True
            self.audit.log_query(
                question, user, cached_data.get("reasoning", {}).get("intent", "unknown"),
                cached_data, trace_id, self.domain_id, self.tenant_id,
                performance={"total_time_ms": 0, "cache_hit": True}
            )
            
            yield {
                "type": "final",
                "validation": cached_data.get("validation", {"valid": True}),
                "reasoning": cached_data.get("reasoning", {}),
                "confidence": cached_data.get("confidence", 1.0)
            }
            return

        yield {"type": "status", "message": "🧠 Analyzing query...", "layer": "nlp"}
        nlp_analysis = self.nlp_core.analyze(question)
        yield {
            "type": "layer_result",
            "layer": "nlp",
            "result": {
                "keywords": nlp_analysis.keywords[:8] if nlp_analysis.keywords else [],
                "question_type": getattr(nlp_analysis, "question_type", "general"),
                "entities": dict(list(nlp_analysis.entities.items())[:4]) if hasattr(nlp_analysis, "entities") and nlp_analysis.entities else {}
            }
        }

        yield {"type": "status", "message": "⚖️ Arbitrating intent...", "layer": "arbitration"}
        arbitration = self.arbitrator.arbitrate(nlp_analysis, user=user)
        yield {
            "type": "layer_result",
            "layer": "arbitration",
            "result": {
                "final_intent": arbitration.final_intent,
                "confidence": round(arbitration.confidence, 3),
                "reason": getattr(arbitration, "reason", "Expert arbitration")
            }
        }

        # RBAC check on resolved intent (Layer 0 + 3 enforcement for streaming path)
        access_check = self.security.check_access(arbitration.final_intent, user)
        if not access_check.allowed:
            self.audit.log_rejection(
                question,
                user,
                access_check.reason,
                trace_id,
                self.domain_id,
                self.tenant_id,
            )
            yield {"type": "error", "message": access_check.reason}
            return

        # 🛡️ Rule Enforcement (Layer 2 Override - Streaming)
        applicable_rules = self.expert_agent.get_applicable_rules(arbitration.final_intent, user, nlp_analysis)
        for rule in applicable_rules:
            action = rule.get_action()
            if action.get("message"):
                yield {"type": "status", "message": f"🛡️ Production Rule fired: {rule.id}"}
                yield {"type": "chunk", "content": action["message"]}
                yield {
                    "type": "final",
                    "validation": {"valid": True, "checks": {"rule_override": True}},
                    "reasoning": {
                        "logic": "production_rule_override",
                        "rule_id": rule.id,
                        "intent": arbitration.final_intent,
                        "description": rule.description
                    },
                    "confidence": 1.0
                }
                return

        yield {"type": "status", "message": "🔍 Retrieving facts...", "layer": "retrieval"}
        retrieved_docs, retrieval_trace, grounding_report, kg_facts = self.retrieval.retrieve(
            arbitration.final_intent, nlp_analysis, max_docs=4, user=user
        )
        yield {
            "type": "layer_result",
            "layer": "retrieval",
            "result": {
                "docs_found": len(retrieved_docs),
                "top_docs": [
                    {"name": d.get("name", "?"), "score": round(d.get("score", 0), 3)}
                    for d in retrieved_docs[:3]
                ]
            }
        }

        yield {"type": "status", "message": "📋 Planning answer...", "layer": "planning"}
        answer_plan = self.planner.create_plan(arbitration.final_intent, retrieved_docs, nlp_analysis)
        yield {
            "type": "layer_result",
            "layer": "planning",
            "result": {
                "goal": answer_plan.goal,
                "structure": getattr(answer_plan, "structure_type", "paragraph"),
                "steps": answer_plan.steps[:3] if answer_plan.steps else []
            }
        }

        yield {"type": "status", "message": "✍️ Generating...", "layer": "generation"}
        
        inference_result = {
            "question": question,
            "top_sections": [{"sections": [{"context": doc.get("best_chunk") or doc.get("content")} for doc in retrieved_docs]}],
            "activated_rules": [asdict(r) if hasattr(r, "__dataclass_fields__") else r for r in self.expert_agent.get_applicable_rules(arbitration.final_intent, user, nlp_analysis)],
            "selected_documents": retrieved_docs,
            "keywords": nlp_analysis.keywords
        }
        
        full_answer = ""
        # Using the prompt builder for consistency
        prompt = self._build_constrained_prompt(answer_plan, question, target_language)
        print(f"DEBUG: [Layer 6] Final prompt for LLM:\n{'='*40}\n{prompt}\n{'='*40}")
        
        for chunk in self.generator._stream_ollama(prompt):
            full_answer += chunk
            yield {"type": "chunk", "content": chunk}

        yield {"type": "status", "message": "✅ Validating...", "layer": "validation"}
        validation = self.validator.validate(full_answer, answer_plan, arbitration.final_intent)
        yield {
            "type": "layer_result",
            "layer": "validation",
            "result": {
                "valid": validation.valid if hasattr(validation, "valid") else True,
                "score": round(validation.score if hasattr(validation, "score") else 0.0, 3),
                "checks": validation.checks if hasattr(validation, "checks") else {},
                "issues": validation.issues if hasattr(validation, "issues") else []
            }
        }

        # 🔒 Strict Security Rejection (Layer 7 Enforcement)
        if not validation.checks.get("forbidden_topics", True):
             self.audit.log_rejection(question, user, "Security violation: Forbidden topic detected in answer.", trace_id, self.domain_id, self.tenant_id)
             yield {"type": "error", "message": "I am not authorized to reveal secret information as per policy."}
             return

        reasoning = self._build_reasoning_trace(nlp_analysis, arbitration, retrieval_trace, answer_plan, retrieved_docs, grounding_report)
        
        confidence = self._calculate_confidence(arbitration, validation, retrieved_docs)
        
        yield {
            "type": "final",
            "validation": asdict(validation) if hasattr(validation, "__dataclass_fields__") else validation,
            "reasoning": reasoning,
            "confidence": confidence
        }
        
        # 📝 Audit to JSONL
        total_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
        self.audit.log_query(
            query=question,
            user=user,
            intent=arbitration.final_intent,
            decision={"action": "approved" if validation.valid else "flagged", "final_intent": arbitration.final_intent},
            trace_id=trace_id,
            domain_id=self.domain_id,
            tenant_id=self.tenant_id,
            performance={"total_time_ms": total_time}
        )

        # 💾 Audit to PostgreSQL Transactional Tables
        try:
            from data.database import SessionLocal
            from api.models import (
                Query, ReasoningTrace, GeneratedAnswer, RuleExecutionHistory,
                AnswerPlan, ValidationReport, RetrievalEvent, ModelUsageMetric,
                AuditLog, SecurityEvent
            )
            
            db = SessionLocal()
            
            # Save Query
            new_query = Query(
                id=trace_id,
                user_id=user.id if hasattr(user, "id") else None,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                raw_question=question,
                detected_language=target_language or "en",
            )
            db.add(new_query)
            db.flush()
            
            # Save Trace
            new_trace = ReasoningTrace(
                id=trace_id,
                query_id=trace_id,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                nlp_output=reasoning.get("nlp_analysis"),
                intent_arbitration=reasoning.get("intent_arbitration"),
                rules_triggered={"applied": []},  # Extracted from expert engine
                retrieval_path=reasoning.get("retrieval_path"),
                answer_plan=reasoning.get("answer_plan"),
                validation={"score": reasoning.get("validation", {}).get("score", 0.0), "generation_model": "gemma:2b"}
            )
            db.add(new_trace)
            
            # Save Generated Answer
            new_answer = GeneratedAnswer(
                id=trace_id,
                query_id=trace_id,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                answer_text=full_answer,
                confidence=confidence,
                valid=validation.valid if hasattr(validation, 'valid') else True
            )
            db.add(new_answer)
            
            # Save Answer Plan
            plan_dict = reasoning.get("answer_plan", {})
            new_plan = AnswerPlan(
                id=uuid.uuid4().hex,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                goal=plan_dict.get("goal", "Answer query"),
                steps=plan_dict.get("steps", []),
                excluded_topics=plan_dict.get("excluded_topics", [])
            )
            db.add(new_plan)

            # Save ValidationReport
            db.add(ValidationReport(
                id=uuid.uuid4().hex,
                answer_id=trace_id,
                validation_score=reasoning.get("validation", {}).get("score", 0.0),
                issues=reasoning.get("validation", {}).get("issues", []),
                action_taken="approved" if validation.valid else "rejected"
            ))

            # Save Retrieval Events
            for idx, doc in enumerate(retrieved_docs):
                db.add(RetrievalEvent(
                    id=uuid.uuid4().hex,
                    query_id=trace_id,
                    domain_id=self.domain_id,
                    tenant_id=self.tenant_id,
                    relevance_score=doc.get("score", 0.9),
                    allowed=True
                ))

            # Save Model Usage Metric
            db.add(ModelUsageMetric(
                query_id=trace_id,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                model_name="gemma:2b",
                prompt_tokens=len(prompt) // 4,
                completion_tokens=len(full_answer) // 4,
                total_tokens=(len(prompt) + len(full_answer)) // 4,
                inference_time_ms=int(total_time)
            ))

            # Save Audit Log
            db.add(AuditLog(
                id=uuid.uuid4().hex,
                user_id=user.id if hasattr(user, "id") else None,
                domain_id=self.domain_id,
                tenant_id=self.tenant_id,
                action="CHAT_QUERY",
                target="HybridPipeline",
                meta_info={"trace_id": trace_id, "intent": arbitration.final_intent}
            ))
            
            # Security Event (if flagged)
            if hasattr(security_check, "allowed") and not security_check.allowed:
                db.add(SecurityEvent(
                    id=uuid.uuid4().hex,
                    event_type="PROMPT_INJECTION_OR_POLICY_VIOLATION",
                    user_id=user.id if hasattr(user, "id") else None,
                    domain_id=self.domain_id,
                    tenant_id=self.tenant_id,
                    severity="high",
                    details={"reason": getattr(security_check, "reason", "Security flagged")}
                ))
            
            db.commit()
            db.close()
            print(f"💾 Successfully saved DB logs for query {trace_id}")

            # 💾 Cache Result (Governance-aware)
            try:
                final_res = HybridResponse(
                    answer=full_answer,
                    reasoning=reasoning,
                    validation=asdict(validation) if hasattr(validation, "__dataclass_fields__") else validation,
                    confidence=confidence,
                    detected_language=target_language or "en"
                )
                cache.set(cache_key, asdict(final_res), ttl=3600)
                print(f"💾 Cached streamed response for {cache_key}")
            except Exception as cache_e:
                print(f"⚠️ Cache set failed (stream): {cache_e}")

        except Exception as db_e:
            print(f"❌ Failed to save to PostgreSQL logs: {db_e}")

    def _build_constrained_prompt(self, plan: AnswerPlan, question: str, target_language: Optional[str] = None) -> str:
        # Load domain name for persona (optionally)
        domain_info = self.expert_agent.domain_id
        
        prompt_parts = [
            f"You are an expert assistant for the domain: {domain_info}.",
            f"\nQuestion: {question}",
            f"\n{self.planner.format_plan_for_prompt(plan)}",
            "\n\nCONSTRAINTS:",
            "- Formulate your answer based on the steps, but DO NOT include the step headers in the response",
            "- Use ONLY provided evidence",
            "- Do NOT hallucinate",
            "- Cite sources if provided"
        ]
        
        if target_language and target_language != 'en':
            prompt_parts.append(f"- Write answer in {target_language}")
            
        prompt_parts.append("\nAnswer:")
        return "\n".join(prompt_parts)

    def _create_rejection_response(self, reason: str, trace_id: str) -> HybridResponse:
        return HybridResponse(
            answer=f"Request rejected: {reason}",
            reasoning={"trace_id": trace_id},
            validation={"valid": False, "score": 0},
            confidence=1.0
        )

    def _build_reasoning_trace(self, nlp_analysis, arbitration, retrieval_trace, answer_plan, retrieved_docs, grounding_report) -> Dict[str, Any]:
        return {
            "nlp_analysis": {
                "keywords": nlp_analysis.keywords,
                "entities": nlp_analysis.entities if hasattr(nlp_analysis, "entities") else {},
                "semantic_roles": nlp_analysis.semantic_roles if hasattr(nlp_analysis, "semantic_roles") else {},
                "question_type": nlp_analysis.question_type if hasattr(nlp_analysis, "question_type") else "general"
            },
            "intent_arbitration": {
                "final_intent": arbitration.final_intent,
                "confidence": arbitration.confidence,
                "reason": arbitration.reason if hasattr(arbitration, "reason") else "Expert rule arbitration"
            },
            "retrieval_path": retrieval_trace,
            "answer_plan": {
                "goal": answer_plan.goal,
                "steps": answer_plan.steps,
                "excluded_topics": answer_plan.excluded_topics,
                "max_length": answer_plan.max_length,
                "structure": answer_plan.structure_type
            },
            "documents": [
                {
                    "name": doc.get("name"),
                    "score": doc.get("score"),
                    "sections": [s["section"] for s in doc.get("sections", [])],
                    "best_chunk": doc.get("best_chunk", "")
                }
                for doc in retrieved_docs
            ]
        }

    def _calculate_confidence(self, arbitration, validation, retrieved_docs) -> float:
        val_score = validation.score if hasattr(validation, 'score') else validation.get('score', 0.5)
        # If we have retrieved documents, boost confidence
        retrieval_boost = 0.2 if retrieved_docs else 0.0
        return min(1.0, (arbitration.confidence + val_score + retrieval_boost) / 2)
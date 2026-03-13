"""
Intent Arbitration Layer - Layer 3 of Hybrid Architecture
Responsibilities:
- Receive multiple intent hypotheses from NLP
- Apply expert agent validation
- Resolve conflicts using ontology rules
- Select final intent with justification

This is where NLP and Expert Agent truly meet.
This is SYMBOLIC CONTROL over PROBABILISTIC NLP.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ArbitrationResult:
    """Result of intent arbitration"""
    final_intent: str
    confidence: float
    reason: str
    rejected_intents: List[Dict[str, Any]]
    validation_details: Dict[str, Any]


class IntentArbitrator:
    """
    Intent Arbitration - The bridge between probabilistic NLP and deterministic expert agent.
    NLP proposes, Expert validates, Arbitrator decides.
    """
    
    def __init__(self, expert_agent):
        self.expert = expert_agent
        print("⚖️  Intent Arbitrator initialized")
    
    def arbitrate(self, nlp_analysis, user=None) -> ArbitrationResult:
        """
        Main arbitration method.
        Takes NLP hypotheses and returns a single validated intent.
        Enhanced with user context for formal ontology validation.
        """
        hypotheses = nlp_analysis.intent_hypotheses
        
        if not hypotheses:
            return self._fallback_arbitration()
        
        # Sort by confidence (NLP's opinion)
        sorted_hypotheses = sorted(hypotheses, key=lambda x: x["confidence"], reverse=True)
        
        # Try to validate each hypothesis with expert agent
        for hypothesis in sorted_hypotheses:
            intent = hypothesis["intent"]
            confidence = hypothesis["confidence"]
            
            # Expert validation with user context
            if self.expert.is_valid_intent(hypothesis, nlp_analysis, user):
                # Check for logical conflicts with other high-confidence intents
                conflicts = self._check_conflicts(hypothesis, sorted_hypotheses)
                
                if not conflicts:
                    # This intent is valid and has no conflicts
                    validation = self.expert.validate_intent(intent, nlp_analysis, user)
                    
                    return ArbitrationResult(
                        final_intent=intent,
                        confidence=confidence,
                        reason=f"Highest confidence ({confidence:.2f}) + no rule conflict",
                        rejected_intents=[h for h in hypotheses if h != hypothesis],
                        validation_details=validation
                    )
                else:
                    # Has conflicts, try to resolve using formal ontology
                    resolved = self._resolve_conflicts_enhanced(hypothesis, conflicts)
                    if resolved:
                        validation = self.expert.validate_intent(resolved["intent"], nlp_analysis, user)
                        return ArbitrationResult(
                            final_intent=resolved["intent"],
                            confidence=resolved["confidence"],
                            reason=f"Conflict resolved in favor of {resolved['intent']} (priority-based)",
                            rejected_intents=[h for h in hypotheses if h["intent"] != resolved["intent"]],
                            validation_details=validation
                        )
        
        # No valid intent found, use fallback
        return self._fallback_arbitration()
    
    def _check_conflicts(self, hypothesis: Dict[str, Any], all_hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check if this intent conflicts with other high-confidence intents.
        Uses ontology exclusion rules.
        """
        intent = hypothesis["intent"]
        conflicts = []
        
        # Get exclusions for this intent
        exclusions = self.expert.get_exclusions(intent)
        
        # Check if any other high-confidence intent is in exclusions
        for other in all_hypotheses:
            if other == hypothesis:
                continue
            
            # Only consider reasonably confident alternatives
            if other["confidence"] > 0.3:
                other_intent = other["intent"]
                
                # Check if excluded
                if other_intent in exclusions:
                    conflicts.append(other)
                
                # Check reverse exclusion
                other_exclusions = self.expert.get_exclusions(other_intent)
                if intent in other_exclusions:
                    conflicts.append(other)
        
        return conflicts
    
    def _resolve_conflicts(self, hypothesis: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Resolve conflicts between intents.
        Uses priority and specificity from ontology.
        """
        intent = hypothesis["intent"]
        
        # Get concept for this intent
        if intent not in self.expert.ontology:
            return None
        
        concept = self.expert.ontology[intent]
        
        # Compare with conflicting intents
        for conflict in conflicts:
            conflict_intent = conflict["intent"]
            
            if conflict_intent not in self.expert.ontology:
                continue
            
            conflict_concept = self.expert.ontology[conflict_intent]
            
            # Higher priority wins
            if concept.priority > conflict_concept.priority:
                continue  # Current hypothesis wins
            elif concept.priority < conflict_concept.priority:
                return conflict  # Conflict wins
            else:
                # Same priority, use specificity
                specificity_order = {"high": 3, "medium": 2, "low": 1}
                if specificity_order.get(concept.specificity, 0) >= specificity_order.get(conflict_concept.specificity, 0):
                    continue  # Current hypothesis wins
                else:
                    return conflict  # Conflict wins
        
        # No conflict won, return original
        return hypothesis
    
    def _resolve_conflicts_enhanced(self, hypothesis: Dict[str, Any], conflicts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Enhanced conflict resolution using formal ontology validator.
        Falls back to legacy method if validator unavailable.
        """
        # Try using formal ontology validator
        if hasattr(self.expert, 'ontology_validator') and self.expert.ontology_validator:
            all_intents = [hypothesis["intent"]] + [c["intent"] for c in conflicts]
            resolution = self.expert.resolve_intent_conflicts(all_intents)
            
            resolved_intent = resolution["resolved_intent"]
            
            # Find the hypothesis for the resolved intent
            for h in [hypothesis] + conflicts:
                if h["intent"] == resolved_intent:
                    return h
        
        # Fallback to legacy resolution
        return self._resolve_conflicts(hypothesis, conflicts)
    
    def _fallback_arbitration(self) -> ArbitrationResult:
        """Fallback when no valid intent is found"""
        return ArbitrationResult(
            final_intent="General",
            confidence=0.5,
            reason="No valid intent found, using General fallback",
            rejected_intents=[],
            validation_details={"valid": True, "fallback": True}
        )
    
    def explain_arbitration(self, result: ArbitrationResult) -> str:
        """Generate human-readable explanation of arbitration"""
        explanation = [
            f"🎯 Final Intent: {result.final_intent}",
            f"📊 Confidence: {result.confidence}",
            f"💡 Reason: {result.reason}",
        ]
        
        if result.rejected_intents:
            explanation.append(f"❌ Rejected: {', '.join([h['intent'] for h in result.rejected_intents[:3]])}")
        
        return "\n".join(explanation)


# Example usage
if __name__ == "__main__":
    from agents.expert_agent import ExpertAgent
    from core.nlp_core import AdvancedNLPCore, NLPAnalysis
    
    # Initialize components
    nlp = AdvancedNLPCore()
    expert = ExpertAgent()
    arbitrator = IntentArbitrator(expert)
    
    # Test queries
    test_queries = [
        "How do I create a new Next.js project?",
        "How to deploy to Vercel?",
        "What is SSR in Next.js?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        # NLP analysis
        analysis = nlp.analyze(query)
        
        print(f"\n📊 NLP Hypotheses:")
        for hyp in analysis.intent_hypotheses[:3]:
            print(f"  - {hyp['intent']}: {hyp['confidence']}")
        
        # Arbitration
        result = arbitrator.arbitrate(analysis)
        
        print(f"\n{arbitrator.explain_arbitration(result)}")

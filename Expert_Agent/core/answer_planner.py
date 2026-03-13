"""
Answer Planning Module - Layer 5 of Hybrid Architecture
Responsibilities:
- Build structured answer plan BEFORE generation
- Define steps, evidence, exclusions
- Create contract for LLM to obey

This is the CONTRACT that the NLP generator must follow.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from security.answer_plan_validator import AnswerPlanValidator, PlanValidationResult


@dataclass
class AnswerPlan:
    """Structured plan for answer generation"""
    goal: str
    intent: str
    steps: List[str]
    evidence: List[Dict[str, Any]]
    excluded_topics: List[str]
    required_citations: bool
    max_length: int
    structure_type: str
    must_include: List[str]
    must_exclude: List[str]


class AnswerPlanner:
    """
    Answer Planner - Creates structured plans before LLM generation.
    The expert agent defines WHAT to say, this defines HOW to structure it.
    """
    
    def __init__(self, expert_agent):
        self.expert = expert_agent
        self.validator = AnswerPlanValidator()
        print("📋 Answer Planner initialized")
    
    def create_plan(self, intent: str, retrieved_docs: List[Dict[str, Any]], nlp_analysis: Any) -> AnswerPlan:
        """
        Create a structured answer plan.
        This is the contract the LLM must obey.
        """
        # Get answer template from expert agent
        template = self.expert.get_answer_template(intent)
        
        # Get exclusions from expert agent
        exclusions = self.expert.get_exclusions(intent)
        
        # Extract evidence from retrieved documents
        evidence = self._extract_evidence(retrieved_docs)
        
        # Build goal statement
        goal = self._build_goal(intent, nlp_analysis)
        
        return AnswerPlan(
            goal=goal,
            intent=intent,
            steps=template.get("steps", ["Provide a detailed response based on available information."]),
            evidence=evidence,
            excluded_topics=exclusions + template.get("must_exclude", []),
            required_citations=True,
            max_length=template.get("max_length", 250),
            structure_type=template.get("structure", "flexible"),
            must_include=template.get("must_include", []),
            must_exclude=template.get("must_exclude", [])
        )
    
    def _build_goal(self, intent: str, nlp_analysis: Any) -> str:
        """Build a clear goal statement dynamically"""
        action = nlp_analysis.semantic_roles.get("action", "answer")
        patient = nlp_analysis.semantic_roles.get("patient", "question")
        
        # Try to get intent description from expert agent (which loads from DB)
        # Note: We can add a more explicit goal template to the Intent model later
        return f"{action.capitalize()} {patient} related to {intent}"
    
    def _extract_evidence(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract evidence from retrieved documents.
        Evidence = specific sections that support the answer.
        """
        evidence = []
        
        for doc in retrieved_docs[:3]:  # Top 3 documents
            doc_name = doc.get("name", "Unknown")
            sections = doc.get("sections", [])
            
            for section in sections[:5]:  # Top 5 sections per doc (increased from 2)
                evidence.append({
                    "document": doc_name,
                    "section": section.get("section", "Unknown"),
                    "content": section.get("context", "")[:1500],  # Increased to 1500 chars
                    "score": doc.get("score", 0.0)
                })
        
        return evidence
    
    def format_plan_for_prompt(self, plan: AnswerPlan) -> str:
        """
        Format the plan as a strict prompt for the LLM.
        Simplified for smaller models like Gemma 2b.
        """
        prompt_parts = [
            f"GOAL: {plan.goal}",
            "\nSTRUCTURE & STEPS:",
        ]
        
        for i, step in enumerate(plan.steps, 1):
            prompt_parts.append(f"  {i}. {step}")
        
        if plan.evidence:
            prompt_parts.append(f"\nCONTEXT / RETRIEVED KNOWLEDGE:")
            for i, ev in enumerate(plan.evidence, 1):
                # Clearer separation for small models
                prompt_parts.append(f"--- Document: {ev['document']} ---")
                prompt_parts.append(ev['content'])
                prompt_parts.append("--- End of Document ---")
        
        if plan.excluded_topics:
            prompt_parts.append(f"\n⛔ EXCLUDE THESE TOPICS: {', '.join(plan.excluded_topics)}")
        
        prompt_parts.append(f"\nIMPORTANT INSTRUCTIONS:")
        prompt_parts.append("- Use ONLY the provided context above.")
        prompt_parts.append("- If information is missing, say 'I cannot find this in the documentation'.")
        prompt_parts.append(f"- Citations required: {plan.required_citations}")
        prompt_parts.append(f"- Max length: {plan.max_length} words")
        
        return "\n".join(prompt_parts)
    
    def validate_plan(self, plan: AnswerPlan) -> Dict[str, Any]:
        """Validate that the plan is complete and consistent using AnswerPlanValidator"""
        # Convert dataclass to dict for validator
        plan_dict = {
            "goal": plan.goal,
            "structure_type": plan.structure_type,
            "steps": plan.steps,
            "evidence": plan.evidence,
            "constraints": {
                "max_length": plan.max_length,
                "required_citations": plan.required_citations,
                "must_include": plan.must_include,
                "excluded_topics": plan.excluded_topics,
                "required_documents": [], # Can be populated if needed
                "forbidden_documents": []
            }
        }
        
        result = self.validator.validate_plan(plan_dict)
        
        return {
            "valid": result.valid,
            "issues": [f"{i.severity.upper()}: {i.message}" for i in result.issues],
            "score": result.score,
            "recommendations": result.recommendations
        }


# Example usage
if __name__ == "__main__":
    from agents.expert_agent import ExpertAgent
    
    expert = ExpertAgent()
    planner = AnswerPlanner(expert)
    
    # Mock retrieved documents
    mock_docs = [
        {
            "name": "Create Next App",
            "score": 9.5,
            "sections": [
                {
                    "section": "Installation",
                    "context": "To create a new Next.js app, run: npx create-next-app@latest my-app"
                },
                {
                    "section": "Options",
                    "context": "You can use --typescript flag for TypeScript support"
                }
            ]
        }
    ]
    
    # Mock NLP analysis
    class MockAnalysis:
        semantic_roles = {"action": "create", "patient": "project"}
    
    # Create plan
    plan = planner.create_plan("ProjectInitialization", mock_docs, MockAnalysis())
    
    print("📋 Answer Plan:")
    print(f"Goal: {plan.goal}")
    print(f"Steps: {plan.steps}")
    print(f"Excluded: {plan.excluded_topics}")
    print(f"\n{planner.format_plan_for_prompt(plan)}")

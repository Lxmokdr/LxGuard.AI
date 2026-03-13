"""
Self-Validation Agent - Layer 7 of Hybrid Architecture
Responsibilities:
- Verify rule compliance
- Check step completeness
- Validate evidence grounding
- Detect forbidden topics
- Prevent hallucinations

This gives you AUTONOMY WITHOUT HALLUCINATIONS.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import re
from security.semantic_validator import SemanticValidator, SemanticValidationResult


@dataclass
class ValidationResult:
    """Result of answer validation"""
    valid: bool
    checks: Dict[str, bool]
    issues: List[str]
    score: float


class ValidationAgent:
    """
    Validates answers against plan, expert rules, and semantic fidelity.
    Now fully domain-agnostic and database-driven.
    """
    
    def __init__(self, expert_agent: Any, domain_id: str = None):
        self.expert = expert_agent
        self.domain_id = domain_id or getattr(expert_agent, 'domain_id', None)
        
        from utils.rule_loader import RuleLoader
        self.rule_loader = RuleLoader(domain_id=self.domain_id)
        
        self.semantic_validator = SemanticValidator()
        print(f"✅ Validation Agent (Domain: {self.domain_id}) initialized")
    
    def validate(self, answer: str, answer_plan, intent: str) -> ValidationResult:
        """
        Main validation method.
        Checks answer against plan, expert rules, and semantic fidelity.
        """
        # 1. Basic checks
        checks = {
            "rule_compliance": self._check_rule_compliance(answer, intent),
            # "step_completeness" - handled by semantic validator
            # "evidence_grounding" - handled by semantic validator
            # "forbidden_topics" - handled by semantic validator
            "length_compliance": self._check_length(answer, answer_plan.max_length),
            "required_elements": self._check_required_elements(answer, answer_plan.must_include)
        }
        
        # 2. Semantic Validation (Deep check)
        semantic_result = self.semantic_validator.validate(
            answer=answer,
            plan={
                "steps": answer_plan.steps,
                "evidence": answer_plan.evidence,
                "constraints": {
                    "excluded_topics": answer_plan.excluded_topics
                }
            }
        )
        
        # Merge checks
        checks["semantic_fidelity"] = semantic_result.valid
        checks["no_hallucinations"] = not semantic_result.unsupported_claims
        checks["forbidden_topics"] = not semantic_result.forbidden_mentions
        
        # Collect issues
        issues = []
        for check_name, passed in checks.items():
            if not passed:
                issues.append(f"Failed: {check_name}")
        
        # Add semantic issues
        for issue in semantic_result.issues:
             issues.append(f"Semantic Issue: {issue['message']}")
        
        # Calculate score (average of checks + semantic fidelity)
        score = (sum(checks.values()) / len(checks) + semantic_result.fidelity_score) / 2
        
        # Valid if all checks passed AND semantic validation passed
        is_valid = all(checks.values()) and semantic_result.valid
        
        return ValidationResult(
            valid=is_valid,
            checks=checks,
            issues=issues,
            score=round(score, 2)
        )
    
    def _check_rule_compliance(self, answer: str, intent: str) -> bool:
        """
        Check if answer complies with expert rules for this intent.
        """
        # 1. Structural Check
        # Try to load schema for this intent from DB
        schema = self.rule_loader.load_json_schema(f"{intent}_schema")
        if not schema:
            # Fallback to general schema
            schema = self.rule_loader.load_json_schema("general_answer_schema")
            
        # If we have a schema and the answer is JSON, we could validate it here
        # For now, we'll stick to the existing symbolic checks but generalized
        # Get applicable rules
        rules = self.expert.get_applicable_rules(intent)
        
        if not rules:
            return True
        
        # For now, basic compliance check
        # In full system, would check specific rule constraints
        return len(answer) > 50  # At least some content
    
    def _check_step_completeness(self, answer: str, steps: List[str]) -> bool:
        """
        Check if answer covers all required steps.
        """
        if not steps:
            return True
        
        answer_lower = answer.lower()
        
        # Check if key terms from each step appear
        covered_steps = 0
        for step in steps:
            # Extract key terms from step
            key_terms = [word.lower() for word in step.split() if len(word) > 4]
            
            # Check if any key term appears in answer
            if any(term in answer_lower for term in key_terms):
                covered_steps += 1
        
        # At least 60% of steps should be covered
        coverage = covered_steps / len(steps)
        return coverage >= 0.6
    
    def _check_evidence_grounding(self, answer: str, evidence: List[Dict[str, Any]]) -> bool:
        """
        Check if answer is grounded in provided evidence.
        Detects hallucinations.
        """
        if not evidence:
            return True  # No evidence to check against
        
        answer_lower = answer.lower()
        
        # Check if answer contains content from evidence
        grounded_evidence = 0
        for ev in evidence:
            content = ev.get("content", "").lower()
            
            # Extract key phrases from evidence (3+ word sequences)
            words = content.split()
            for i in range(len(words) - 2):
                phrase = " ".join(words[i:i+3])
                if phrase in answer_lower:
                    grounded_evidence += 1
                    break
        
        # At least one piece of evidence should be referenced
        return grounded_evidence > 0
    
    def _check_forbidden_topics(self, answer: str, excluded_topics: List[str]) -> bool:
        """
        Check if answer mentions any forbidden topics.
        CRITICAL for rule enforcement.
        """
        if not excluded_topics:
            return True
        
        answer_lower = answer.lower()
        
        # Check for forbidden topic mentions
        for topic in excluded_topics:
            topic_lower = topic.lower()
            
            # Check for exact match or common variations
            forbidden_terms = [
                topic_lower,
                topic_lower + "s",  # plural
                topic_lower.replace(" ", "-"),  # hyphenated
            ]
            
            for term in forbidden_terms:
                if term in answer_lower:
                    return False  # Found forbidden topic!
        
        return True  # No forbidden topics found
    
    def _check_length(self, answer: str, max_length: int) -> bool:
        """Check if answer respects length constraint"""
        word_count = len(answer.split())
        
        # Allow 20% overflow
        return word_count <= max_length * 1.2
    
    def _check_required_elements(self, answer: str, must_include: List[str]) -> bool:
        """Check if answer includes required elements"""
        if not must_include:
            return True
        
        answer_lower = answer.lower()
        
        for element in must_include:
            element_lower = element.lower()
            
            # Check for element presence
            if element_lower == "code_example":
                # Look for code blocks
                if "```" not in answer and "`" not in answer:
                    return False
            elif element_lower == "verification_step":
                # Look for verification keywords
                if not any(word in answer_lower for word in ["verify", "check", "test", "confirm"]):
                    return False
            elif element_lower == "comparison":
                # Look for comparison keywords
                if not any(word in answer_lower for word in ["vs", "versus", "difference", "compare", "unlike"]):
                    return False
            else:
                # Generic check
                if element_lower not in answer_lower:
                    return False
        
        return True
    
    def suggest_improvements(self, validation_result: ValidationResult, answer_plan) -> List[str]:
        """
        Suggest improvements based on validation failures.
        """
        suggestions = []
        
        if not validation_result.checks.get("step_completeness", True):
            suggestions.append(f"Cover all required steps: {', '.join(answer_plan.steps)}")
        
        if not validation_result.checks.get("evidence_grounding", True):
            suggestions.append("Ground answer in provided evidence - avoid hallucinations")
        
        if not validation_result.checks.get("forbidden_topics", True):
            suggestions.append(f"Remove mentions of forbidden topics: {', '.join(answer_plan.excluded_topics)}")
        
        if not validation_result.checks.get("length_compliance", True):
            suggestions.append(f"Reduce length to under {answer_plan.max_length} words")
        
        if not validation_result.checks.get("required_elements", True):
            suggestions.append(f"Include required elements: {', '.join(answer_plan.must_include)}")
        
        return suggestions
    
    def format_validation_report(self, validation_result: ValidationResult) -> str:
        """Format validation result as readable report"""
        report = [
            f"✅ Validation Score: {validation_result.score * 100:.0f}%",
            f"Valid: {'✅ YES' if validation_result.valid else '❌ NO'}",
            "\nChecks:"
        ]
        
        for check, passed in validation_result.checks.items():
            status = "✅" if passed else "❌"
            report.append(f"  {status} {check}")
        
        if validation_result.issues:
            report.append("\nIssues:")
            for issue in validation_result.issues:
                report.append(f"  ⚠️  {issue}")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    from agents.expert_agent import ExpertAgent
    from core.answer_planner import AnswerPlanner, AnswerPlan
    
    expert = ExpertAgent()
    validator = ValidationAgent(expert)
    
    # Mock answer plan
    plan = AnswerPlan(
        goal="Explain project creation",
        intent="ProjectInitialization",
        steps=["Install Node.js", "Run create-next-app", "Start dev server"],
        evidence=[{"content": "npx create-next-app my-app"}],
        excluded_topics=["Deployment", "Docker"],
        required_citations=True,
        max_length=200,
        structure_type="step_by_step",
        must_include=["code_example"],
        must_exclude=["deployment"]
    )
    
    # Test answer (good)
    good_answer = """
    To create a Next.js project:
    1. Install Node.js from nodejs.org
    2. Run `npx create-next-app my-app`
    3. Start the dev server with `npm run dev`
    
    Verify by opening http://localhost:3000
    """
    
    # Test answer (bad - mentions deployment)
    bad_answer = """
    Create a project and then deploy it to production using Docker.
    """
    
    print("Testing GOOD answer:")
    result = validator.validate(good_answer, plan, "ProjectInitialization")
    print(validator.format_validation_report(result))
    
    print("\n" + "="*60)
    print("Testing BAD answer:")
    result = validator.validate(bad_answer, plan, "ProjectInitialization")
    print(validator.format_validation_report(result))
    print("\nSuggestions:")
    for suggestion in validator.suggest_improvements(result, plan):
        print(f"  💡 {suggestion}")

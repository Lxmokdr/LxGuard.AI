"""
Semantic Validator - Post-Generation Semantic Validation
Responsibilities:
- Compare generated answer vs plan (semantic similarity)
- Detect missing or added steps
- Identify unsupported claims
- Detect forbidden topic mentions
- Trigger regeneration or rejection

This ensures ANSWER FIDELITY to the plan.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class SemanticValidationResult:
    """Result of semantic validation"""
    valid: bool
    fidelity_score: float  # 0-1, how well answer matches plan
    issues: List[Dict[str, Any]]
    missing_steps: List[str]
    added_content: List[str]
    unsupported_claims: List[str]
    forbidden_mentions: List[str]
    should_regenerate: bool
    should_reject: bool
    reason: str


class SemanticValidator:
    """
    Post-generation semantic validator.
    Ensures generated answers match the plan and don't hallucinate.
    """
    
    def __init__(self, 
                 min_fidelity_threshold: float = 0.7,
                 max_regeneration_attempts: int = 1):
        self.min_fidelity_threshold = min_fidelity_threshold
        self.max_regeneration_attempts = max_regeneration_attempts
        print(f"🔍 Semantic Validator initialized (min fidelity: {min_fidelity_threshold})")
    
    def validate(self, 
                answer: str, 
                plan: Dict[str, Any],
                attempt_number: int = 0) -> SemanticValidationResult:
        """
        Validate generated answer against plan.
        
        Args:
            answer: Generated answer text
            plan: Answer plan dictionary
            attempt_number: Current regeneration attempt (0 = first try)
        
        Returns:
            SemanticValidationResult with validation details
        """
        issues = []
        
        # 1. Check step coverage
        missing_steps, step_coverage_score = self._check_step_coverage(answer, plan)
        if missing_steps:
            for step in missing_steps:
                issues.append({
                    "type": "missing_step",
                    "severity": "error",
                    "message": f"Plan step not addressed: {step}"
                })
        
        # 2. Detect added content (not in plan)
        added_content = self._detect_added_content(answer, plan)
        if added_content:
            for content in added_content:
                issues.append({
                    "type": "added_content",
                    "severity": "warning",
                    "message": f"Content not in plan: {content}"
                })
        
        # 3. Check for unsupported claims
        unsupported_claims = self._detect_unsupported_claims(answer, plan)
        if unsupported_claims:
            for claim in unsupported_claims:
                issues.append({
                    "type": "unsupported_claim",
                    "severity": "error",
                    "message": f"Claim without evidence: {claim}"
                })
        
        # 4. Check for forbidden topics
        forbidden_mentions = self._detect_forbidden_topics(answer, plan)
        if forbidden_mentions:
            for mention in forbidden_mentions:
                issues.append({
                    "type": "forbidden_topic",
                    "severity": "critical",
                    "message": f"Forbidden topic mentioned: {mention}"
                })
        
        # 5. Calculate fidelity score
        fidelity_score = self._calculate_fidelity_score(
            step_coverage_score,
            len(missing_steps),
            len(added_content),
            len(unsupported_claims),
            len(forbidden_mentions)
        )
        
        # 6. Determine action
        should_regenerate, should_reject, reason = self._determine_action(
            fidelity_score,
            issues,
            attempt_number
        )
        
        valid = fidelity_score >= self.min_fidelity_threshold and not should_reject
        
        return SemanticValidationResult(
            valid=valid,
            fidelity_score=fidelity_score,
            issues=issues,
            missing_steps=missing_steps,
            added_content=added_content,
            unsupported_claims=unsupported_claims,
            forbidden_mentions=forbidden_mentions,
            should_regenerate=should_regenerate,
            should_reject=should_reject,
            reason=reason
        )
    
    def _check_step_coverage(self, answer: str, plan: Dict[str, Any]) -> Tuple[List[str], float]:
        """Check if all plan steps are covered in the answer"""
        steps = plan.get("steps", [])
        if not steps:
            return [], 1.0
        
        answer_lower = answer.lower()
        missing_steps = []
        covered_count = 0
        
        for step in steps:
            # Extract key terms from step
            step_terms = self._extract_key_terms(step)
            
            # Check if any key terms appear in answer
            found = any(term.lower() in answer_lower for term in step_terms)
            
            if found:
                covered_count += 1
            else:
                missing_steps.append(step)
        
        coverage_score = covered_count / len(steps) if steps else 1.0
        return missing_steps, coverage_score
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text (simple keyword extraction)"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'}
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return top terms (by length, assuming longer = more specific)
        key_terms.sort(key=len, reverse=True)
        return key_terms[:5]
    
    def _detect_added_content(self, answer: str, plan: Dict[str, Any]) -> List[str]:
        """Detect content in answer that's not in the plan"""
        added = []
        
        # Get all plan content
        plan_text = " ".join(plan.get("steps", []))
        if "evidence" in plan:
            for ev in plan["evidence"]:
                plan_text += " " + ev.get("content", "")
        
        plan_terms = set(self._extract_key_terms(plan_text))
        answer_terms = set(self._extract_key_terms(answer))
        
        # Find terms in answer but not in plan
        new_terms = answer_terms - plan_terms
        
        # Only flag significant additions (terms that appear multiple times)
        answer_lower = answer.lower()
        for term in new_terms:
            if answer_lower.count(term) >= 2:  # Appears at least twice
                added.append(term)
        
        return added[:5]  # Limit to top 5
    
    def _detect_unsupported_claims(self, answer: str, plan: Dict[str, Any]) -> List[str]:
        """Detect claims in answer without evidence support"""
        unsupported = []
        
        # Get evidence content
        evidence_text = ""
        if "evidence" in plan:
            for ev in plan["evidence"]:
                evidence_text += " " + ev.get("content", "")
        
        if not evidence_text:
            # No evidence = all claims are unsupported
            # Extract sentences that look like factual claims
            sentences = re.split(r'[.!?]+', answer)
            for sent in sentences[:3]:  # Check first 3 sentences
                if len(sent.strip()) > 20 and any(word in sent.lower() for word in ['is', 'are', 'will', 'can', 'must']):
                    unsupported.append(sent.strip()[:100])
            return unsupported
        
        evidence_lower = evidence_text.lower()
        
        # Extract sentences from answer
        sentences = re.split(r'[.!?]+', answer)
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20:  # Skip short sentences
                continue
            
            # Check if sentence has support in evidence
            sent_terms = self._extract_key_terms(sent)
            supported = any(term in evidence_lower for term in sent_terms[:3])
            
            if not supported and any(word in sent.lower() for word in ['is', 'are', 'will', 'can', 'must']):
                unsupported.append(sent[:100])  # Truncate
        
        return unsupported[:3]  # Limit to top 3
    
    def _detect_forbidden_topics(self, answer: str, plan: Dict[str, Any]) -> List[str]:
        """Detect mentions of forbidden topics"""
        forbidden = []
        
        excluded_topics = plan.get("constraints", {}).get("excluded_topics", [])
        if not excluded_topics:
            return []
        
        answer_lower = answer.lower()
        
        for topic in excluded_topics:
            # Check for exact match or word boundary match
            topic_lower = topic.lower()
            if topic_lower in answer_lower:
                # Find context (sentence containing the topic)
                sentences = re.split(r'[.!?]+', answer)
                for sent in sentences:
                    if topic_lower in sent.lower():
                        forbidden.append(f"{topic} (in: {sent.strip()[:80]}...)")
                        break
        
        return forbidden
    
    def _calculate_fidelity_score(self,
                                  step_coverage: float,
                                  missing_count: int,
                                  added_count: int,
                                  unsupported_count: int,
                                  forbidden_count: int) -> float:
        """Calculate overall fidelity score"""
        base_score = step_coverage
        
        # Penalties
        base_score -= missing_count * 0.15
        base_score -= added_count * 0.05
        base_score -= unsupported_count * 0.1
        base_score -= forbidden_count * 0.3  # Heavy penalty
        
        return max(0.0, min(1.0, base_score))
    
    def _determine_action(self,
                         fidelity_score: float,
                         issues: List[Dict[str, Any]],
                         attempt_number: int) -> Tuple[bool, bool, str]:
        """
        Determine whether to regenerate or reject.
        
        Returns: (should_regenerate, should_reject, reason)
        """
        # Check for critical issues (forbidden topics)
        critical_issues = [i for i in issues if i.get("severity") == "critical"]
        if critical_issues:
            return False, True, f"Critical violation: {critical_issues[0]['message']}"
        
        # Check fidelity score
        if fidelity_score < self.min_fidelity_threshold:
            if attempt_number < self.max_regeneration_attempts:
                return True, False, f"Low fidelity score ({fidelity_score:.2f}), regenerating..."
            else:
                return False, True, f"Low fidelity score ({fidelity_score:.2f}) after {attempt_number + 1} attempts"
        
        # Check error count
        errors = [i for i in issues if i.get("severity") == "error"]
        if len(errors) > 2:
            if attempt_number < self.max_regeneration_attempts:
                return True, False, f"{len(errors)} errors found, regenerating..."
            else:
                return False, True, f"Too many errors ({len(errors)}) after {attempt_number + 1} attempts"
        
        return False, False, "Answer passes semantic validation"
    
    def format_validation_report(self, result: SemanticValidationResult) -> str:
        """Format validation result as human-readable report"""
        lines = []
        
        if result.valid:
            lines.append("✅ ANSWER VALID")
        else:
            lines.append("❌ ANSWER INVALID")
        
        lines.append(f"Fidelity Score: {result.fidelity_score:.2f} (threshold: {self.min_fidelity_threshold})")
        lines.append(f"Action: {result.reason}")
        
        if result.missing_steps:
            lines.append(f"\n⚠️  Missing Steps ({len(result.missing_steps)}):")
            for step in result.missing_steps:
                lines.append(f"  - {step}")
        
        if result.unsupported_claims:
            lines.append(f"\n⚠️  Unsupported Claims ({len(result.unsupported_claims)}):")
            for claim in result.unsupported_claims:
                lines.append(f"  - {claim}")
        
        if result.forbidden_mentions:
            lines.append(f"\n🚫 Forbidden Topics ({len(result.forbidden_mentions)}):")
            for mention in result.forbidden_mentions:
                lines.append(f"  - {mention}")
        
        if result.added_content:
            lines.append(f"\n💡 Added Content ({len(result.added_content)}):")
            for content in result.added_content[:3]:
                lines.append(f"  - {content}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    validator = SemanticValidator(min_fidelity_threshold=0.7)
    
    # Test plan
    plan = {
        "goal": "Explain how to create a Next.js project",
        "steps": [
            "Install Node.js and npm",
            "Run create-next-app command",
            "Navigate to project directory",
            "Start development server"
        ],
        "evidence": [
            {
                "document": "installation.md",
                "section": "Creating a Project",
                "content": "To create a new Next.js app, run: npx create-next-app@latest my-app. This will set up a new project with all dependencies."
            }
        ],
        "constraints": {
            "max_length": 300,
            "required_citations": True,
            "excluded_topics": ["deployment", "production"]
        }
    }
    
    # Good answer
    good_answer = """
    To create a new Next.js project, first ensure you have Node.js and npm installed.
    Then run the command: npx create-next-app@latest my-app
    Navigate to your project directory with: cd my-app
    Finally, start the development server using: npm run dev
    """
    
    result = validator.validate(good_answer, plan)
    print("GOOD ANSWER TEST:")
    print(validator.format_validation_report(result))
    
    print("\n" + "="*60 + "\n")
    
    # Bad answer (mentions forbidden topic)
    bad_answer = """
    To create a Next.js project, run npx create-next-app.
    After that, you should deploy it to production using Vercel.
    """
    
    result = validator.validate(bad_answer, plan)
    print("BAD ANSWER TEST:")
    print(validator.format_validation_report(result))

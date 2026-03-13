"""
Answer Plan Validator - Validates answer plans against formal schema
Responsibilities:
- Validate plan structure against JSON Schema
- Check constraint violations
- Enforce required citations
- Detect missing evidence
- Ensure plan completeness

This ensures PLAN QUALITY before generation.
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: str  # 'error', 'warning'
    field: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class PlanValidationResult:
    """Result of plan validation"""
    valid: bool
    issues: List[ValidationIssue]
    score: float  # 0-1, overall plan quality
    recommendations: List[str]


class AnswerPlanValidator:
    """
    Validates answer plans against formal schema.
    Ensures plans are complete, consistent, and enforceable.
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            # Default to config/answer_plan.schema.json relative to the root Expert_Agent dir
            self.schema_path = Path(__file__).parent.parent / "config" / "answer_plan.schema.json"
            
        self.schema = self._load_schema()
        print(f"✅ Answer Plan Validator initialized (schema: {self.schema_path.name})")
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON Schema"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load schema: {e}")
            return {}
    
    def validate_plan(self, plan: Dict[str, Any]) -> PlanValidationResult:
        """
        Validate an answer plan against the schema.
        
        Args:
            plan: Answer plan dictionary
        
        Returns:
            PlanValidationResult with validation details
        """
        issues = []
        
        # 1. Schema Validation
        schema_issues = self._validate_against_schema(plan)
        issues.extend(schema_issues)
        
        # 2. Constraint Validation
        constraint_issues = self._validate_constraints(plan)
        issues.extend(constraint_issues)
        
        # 3. Evidence Validation
        evidence_issues = self._validate_evidence(plan)
        issues.extend(evidence_issues)
        
        # 4. Completeness Validation
        completeness_issues = self._validate_completeness(plan)
        issues.extend(completeness_issues)
        
        # 5. Consistency Validation
        consistency_issues = self._validate_consistency(plan)
        issues.extend(consistency_issues)
        
        # Determine validity (no errors)
        errors = [i for i in issues if i.severity == 'error']
        valid = len(errors) == 0
        
        # Calculate quality score
        score = self._calculate_quality_score(plan, issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(plan, issues)
        
        return PlanValidationResult(
            valid=valid,
            issues=issues,
            score=score,
            recommendations=recommendations
        )
    
    def _validate_against_schema(self, plan: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate plan against JSON Schema"""
        issues = []
        
        # Check required fields
        required_fields = self.schema.get("required", [])
        for field in required_fields:
            if field not in plan:
                issues.append(ValidationIssue(
                    severity='error',
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Add '{field}' to the plan"
                ))
        
        # Validate field types and constraints
        properties = self.schema.get("properties", {})
        
        # Validate goal
        if "goal" in plan:
            goal = plan["goal"]
            if not isinstance(goal, str):
                issues.append(ValidationIssue(
                    severity='error',
                    field='goal',
                    message="Goal must be a string"
                ))
            elif len(goal) < 10:
                issues.append(ValidationIssue(
                    severity='error',
                    field='goal',
                    message="Goal is too short (minimum 10 characters)"
                ))
            elif len(goal) > 500:
                issues.append(ValidationIssue(
                    severity='warning',
                    field='goal',
                    message="Goal is very long (maximum 500 characters recommended)"
                ))
        
        # Validate structure_type
        if "structure_type" in plan:
            valid_structures = ["step_by_step", "conceptual_then_example", "example_driven", "reference", "flexible"]
            if plan["structure_type"] not in valid_structures:
                issues.append(ValidationIssue(
                    severity='error',
                    field='structure_type',
                    message=f"Invalid structure_type: {plan['structure_type']}",
                    suggestion=f"Use one of: {', '.join(valid_structures)}"
                ))
        
        # Validate steps
        if "steps" in plan:
            steps = plan["steps"]
            if not isinstance(steps, list):
                issues.append(ValidationIssue(
                    severity='error',
                    field='steps',
                    message="Steps must be a list"
                ))
            elif len(steps) == 0:
                issues.append(ValidationIssue(
                    severity='error',
                    field='steps',
                    message="At least one step is required"
                ))
            elif len(steps) > 10:
                issues.append(ValidationIssue(
                    severity='warning',
                    field='steps',
                    message="Too many steps (maximum 10 recommended)"
                ))
        
        return issues
    
    def _validate_constraints(self, plan: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate plan constraints"""
        issues = []
        
        if "constraints" not in plan:
            issues.append(ValidationIssue(
                severity='error',
                field='constraints',
                message="Constraints object is required"
            ))
            return issues
        
        constraints = plan["constraints"]
        
        # Validate max_length
        if "max_length" not in constraints:
            issues.append(ValidationIssue(
                severity='error',
                field='constraints.max_length',
                message="max_length is required"
            ))
        elif not isinstance(constraints["max_length"], int):
            issues.append(ValidationIssue(
                severity='error',
                field='constraints.max_length',
                message="max_length must be an integer"
            ))
        elif constraints["max_length"] < 50:
            issues.append(ValidationIssue(
                severity='warning',
                field='constraints.max_length',
                message="max_length is very short (minimum 50 recommended)"
            ))
        elif constraints["max_length"] > 1000:
            issues.append(ValidationIssue(
                severity='warning',
                field='constraints.max_length',
                message="max_length is very long (maximum 1000 recommended)"
            ))
        
        # Validate required_citations
        if "required_citations" not in constraints:
            issues.append(ValidationIssue(
                severity='error',
                field='constraints.required_citations',
                message="required_citations is required"
            ))
        elif not isinstance(constraints["required_citations"], bool):
            issues.append(ValidationIssue(
                severity='error',
                field='constraints.required_citations',
                message="required_citations must be a boolean"
            ))
        
        # Validate excluded_topics
        if "excluded_topics" in constraints:
            if not isinstance(constraints["excluded_topics"], list):
                issues.append(ValidationIssue(
                    severity='error',
                    field='constraints.excluded_topics',
                    message="excluded_topics must be a list"
                ))
        
        return issues
    
    def _validate_evidence(self, plan: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate evidence quality and completeness"""
        issues = []
        
        if "evidence" not in plan or not plan["evidence"]:
            issues.append(ValidationIssue(
                severity='warning',
                field='evidence',
                message="No evidence provided",
                suggestion="Add supporting evidence to improve answer quality"
            ))
            return issues
        
        evidence = plan["evidence"]
        
        for i, ev in enumerate(evidence):
            # Check required fields
            if "document" not in ev:
                issues.append(ValidationIssue(
                    severity='error',
                    field=f'evidence[{i}].document',
                    message="Evidence must have a document field"
                ))
            
            if "section" not in ev:
                issues.append(ValidationIssue(
                    severity='error',
                    field=f'evidence[{i}].section',
                    message="Evidence must have a section field"
                ))
            
            if "content" not in ev:
                issues.append(ValidationIssue(
                    severity='error',
                    field=f'evidence[{i}].content',
                    message="Evidence must have content"
                ))
            elif len(ev["content"]) < 20:
                issues.append(ValidationIssue(
                    severity='warning',
                    field=f'evidence[{i}].content',
                    message="Evidence content is very short"
                ))
            elif len(ev["content"]) > 2000:
                issues.append(ValidationIssue(
                    severity='warning',
                    field=f'evidence[{i}].content',
                    message="Evidence content is very long (will be truncated)"
                ))
            
            # Check relevance score if present
            if "relevance_score" in ev:
                score = ev["relevance_score"]
                if not isinstance(score, (int, float)):
                    issues.append(ValidationIssue(
                        severity='error',
                        field=f'evidence[{i}].relevance_score',
                        message="relevance_score must be a number"
                    ))
                elif not 0 <= score <= 1:
                    issues.append(ValidationIssue(
                        severity='error',
                        field=f'evidence[{i}].relevance_score',
                        message="relevance_score must be between 0 and 1"
                    ))
                elif score < 0.3:
                    issues.append(ValidationIssue(
                        severity='warning',
                        field=f'evidence[{i}].relevance_score',
                        message="Evidence has low relevance score"
                    ))
        
        return issues
    
    def _validate_completeness(self, plan: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate plan completeness"""
        issues = []
        
        # Check if steps have supporting evidence
        if "steps" in plan and "evidence" in plan:
            steps = plan["steps"]
            evidence = plan["evidence"]
            
            if len(evidence) == 0 and len(steps) > 0:
                issues.append(ValidationIssue(
                    severity='warning',
                    field='evidence',
                    message=f"Plan has {len(steps)} steps but no evidence",
                    suggestion="Add evidence to support the steps"
                ))
            elif len(evidence) < len(steps) / 2:
                issues.append(ValidationIssue(
                    severity='warning',
                    field='evidence',
                    message="Insufficient evidence for number of steps",
                    suggestion=f"Consider adding more evidence (have {len(evidence)}, steps: {len(steps)})"
                ))
        
        # Check if required citations are enforced but no evidence
        if "constraints" in plan:
            constraints = plan["constraints"]
            if constraints.get("required_citations") and not plan.get("evidence"):
                issues.append(ValidationIssue(
                    severity='error',
                    field='evidence',
                    message="Citations are required but no evidence provided",
                    suggestion="Add evidence or disable required_citations"
                ))
        
        return issues
    
    def _validate_consistency(self, plan: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate internal consistency"""
        issues = []
        
        if "constraints" not in plan:
            return issues
        
        constraints = plan["constraints"]
        
        # Check for contradictions
        if "required_documents" in constraints and "forbidden_documents" in constraints:
            required = set(constraints["required_documents"])
            forbidden = set(constraints["forbidden_documents"])
            conflicts = required & forbidden
            
            if conflicts:
                issues.append(ValidationIssue(
                    severity='error',
                    field='constraints',
                    message=f"Documents appear in both required and forbidden: {conflicts}",
                    suggestion="Remove from one list"
                ))
        
        # Check if evidence uses forbidden documents
        if "evidence" in plan and "forbidden_documents" in constraints:
            forbidden = set(constraints["forbidden_documents"])
            for i, ev in enumerate(plan["evidence"]):
                if ev.get("document") in forbidden:
                    issues.append(ValidationIssue(
                        severity='error',
                        field=f'evidence[{i}]',
                        message=f"Evidence uses forbidden document: {ev['document']}",
                        suggestion="Remove this evidence or update forbidden list"
                    ))
        
        return issues
    
    def _calculate_quality_score(self, plan: Dict[str, Any], issues: List[ValidationIssue]) -> float:
        """Calculate overall plan quality score (0-1)"""
        base_score = 1.0
        
        # Deduct for errors and warnings
        for issue in issues:
            if issue.severity == 'error':
                base_score -= 0.2
            elif issue.severity == 'warning':
                base_score -= 0.05
        
        # Bonus for good practices
        if plan.get("evidence") and len(plan["evidence"]) >= 2:
            base_score += 0.1
        
        if plan.get("metadata", {}).get("grounding_sufficient"):
            base_score += 0.1
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, base_score))
    
    def _generate_recommendations(self, plan: Dict[str, Any], issues: List[ValidationIssue]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on issues
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        
        if error_count > 0:
            recommendations.append(f"Fix {error_count} critical error(s) before using this plan")
        
        if warning_count > 3:
            recommendations.append(f"Address {warning_count} warning(s) to improve plan quality")
        
        # Based on plan content
        if not plan.get("evidence"):
            recommendations.append("Add evidence to support the answer")
        
        if plan.get("steps") and len(plan["steps"]) > 7:
            recommendations.append("Consider reducing number of steps for clarity")
        
        if plan.get("constraints", {}).get("max_length", 0) > 500:
            recommendations.append("Consider reducing max_length for more concise answers")
        
        return recommendations
    
    def format_validation_report(self, result: PlanValidationResult) -> str:
        """Format validation result as human-readable report"""
        lines = []
        
        if result.valid:
            lines.append("✅ PLAN VALID")
        else:
            lines.append("❌ PLAN INVALID")
        
        lines.append(f"Quality Score: {result.score:.2f}/1.00")
        
        if result.issues:
            lines.append(f"\n📋 Issues ({len(result.issues)}):")
            for issue in result.issues:
                icon = "❌" if issue.severity == 'error' else "⚠️ "
                lines.append(f"  {icon} [{issue.field}] {issue.message}")
                if issue.suggestion:
                    lines.append(f"      💡 {issue.suggestion}")
        
        if result.recommendations:
            lines.append(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                lines.append(f"  - {rec}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    validator = AnswerPlanValidator()
    
    # Test plan (valid)
    valid_plan = {
        "goal": "Explain how to create a new Next.js project",
        "structure_type": "step_by_step",
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
                "content": "To create a new Next.js app, run: npx create-next-app@latest my-app",
                "relevance_score": 0.95
            }
        ],
        "constraints": {
            "max_length": 300,
            "required_citations": True,
            "must_include": ["npx", "create-next-app"],
            "excluded_topics": ["deployment", "production"]
        },
        "metadata": {
            "intent": "ProjectInitialization",
            "user_role": "employee",
            "risk_level": "low",
            "grounding_sufficient": True,
            "coverage_score": 0.85
        }
    }
    
    # Validate
    result = validator.validate_plan(valid_plan)
    print(validator.format_validation_report(result))
    
    print("\n" + "="*60 + "\n")
    
    # Test plan (invalid)
    invalid_plan = {
        "goal": "Test",  # Too short
        "structure_type": "invalid_type",  # Invalid
        "steps": [],  # Empty
        "constraints": {
            "max_length": "300",  # Wrong type
            # missing required_citations
        }
    }
    
    result = validator.validate_plan(invalid_plan)
    print(validator.format_validation_report(result))

import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from agents.expert_agent import ExpertAgent, ProductionRule
from utils.explanation import ExplanationGenerator
from api.auth import User, UserRole

def test_rule_conflict_detection():
    print("\n--- ⚖️ Testing Rule Conflict Detection ---")
    agent = ExpertAgent()
    
    # 1. Manually inject a conflict: Ambiguity (Same intent, same priority)
    print("Injecting Ambiguity (Same intent 'Deployment', same priority 10)...")
    agent.rules.append(ProductionRule(
        id="RULE_CONFLICT_1",
        condition=["Deployment"],
        action={"topic": "deployment"},
        priority=10,
        description="Conflicting rule 1",
        excludes=[]
    ))
    agent.rules.append(ProductionRule(
        id="RULE_CONFLICT_2",
        condition=["Deployment"],
        action={"topic": "deployment"},
        priority=10,
        description="Conflicting rule 2",
        excludes=[]
    ))
    
    # 2. Manually inject a conflict: Logical Contradiction (Required vs Forbidden)
    print("Injecting Logical Contradiction (Doc 'deployment.md' both Required and Forbidden for 'Vercel')...")
    agent.rules.append(ProductionRule(
        id="RULE_CONTRADICT_1",
        condition=["Vercel"],
        action={"required_docs": ["deployment.md"]},
        priority=5,
        description="Contradictory rule 1",
        excludes=[]
    ))
    agent.rules.append(ProductionRule(
        id="RULE_CONTRADICT_2",
        condition=["Vercel"],
        action={"forbidden_docs": ["deployment.md"]},
        priority=5,
        description="Contradictory rule 2",
        excludes=[]
    ))
    
    conflicts = agent.check_rule_conflicts()
    
    found_ambiguity = any(c['type'] == 'ambiguity' for c in conflicts)
    found_contradiction = any(c['type'] == 'logical_contradiction' for c in conflicts)
    
    if found_ambiguity: print("✅ Success: Ambiguity detected.")
    if found_contradiction: print("✅ Success: Logical contradiction detected.")
    
    if not found_ambiguity or not found_contradiction:
        print("❌ Failed: Some conflicts were not detected.")

def test_structured_json_generation():
    print("\n--- 🛡️ Testing Structured JSON Generation ---")
    # Mock inference engine
    generator = ExplanationGenerator(domain_id="test-domain", inference_engine=None, use_local=False) 
    # Note: use_local=False to avoid calling Ollama if we just want to see the prompt or mock the response
    # Actually, let's mock the _call_ollama method to simulate LLM output
    
    original_call = generator._call_ollama
    def mock_call(prompt, format_json=False):
        if format_json:
            return '{"answer": "To deploy, use vercel command.", "implementation": "1. Run vercel. 2. Follow prompts.", "security_warnings": ["Check environment variables."], "confidence_score": 0.95}'
        return "Regular text answer."
    
    generator._call_ollama = mock_call
    
    inference_result = {
        "question": "How do I deploy Next.js securely?",
        "top_sections": [],
        "activated_rules": []
    }
    
    print("Testing High-Risk Intent (Risk Level: critical)...")
    response = generator.generate_explanation(inference_result, risk_level="critical")
    print("Output Snippet:")
    print(response[:200] + "...")
    
    if "### 🛡️ Secure Answer" in response and "### ⚠️ Security Compliance" in response:
        print("✅ Success: Structured JSON was parsed and formatted correctly.")
    else:
        print("❌ Failed: Output was not properly structured.")

if __name__ == "__main__":
    test_rule_conflict_detection()
    test_structured_json_generation()

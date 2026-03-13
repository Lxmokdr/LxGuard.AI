import sys
import argparse
import uvicorn
from typing import Dict, Any, Optional
from termcolor import colored

# Import Components
from data.ontology_builder import OntologyBuilder
from engines.ontology_engine import OntologyEngine
from engines.llm_engine import LLMEngine
from core.router import IntentRouter

class DualModeAgent:
    """
    Main Orchestrator for the Dual-Mode Agent.
    """
    
    def __init__(self, build_ontology: bool = False, docs_dir: str = "docs"):
        print(colored("\n🚀 Initializing Dual-Mode Hybrid Agent...", "cyan", attrs=["bold"]))
        
        # Initialize Engines
        ontology_path = "knowledge_base/ontology.ttl"
        
        # Optional: Rebuild Ontology
        if build_ontology:
            print(colored("🔨 Rebuilding Ontology from documents...", "yellow"))
            builder = OntologyBuilder(ontology_path=ontology_path)
            builder.process_directory(docs_dir)
            
        self.router = IntentRouter()
        self.expert_engine = OntologyEngine(ontology_path=ontology_path)
        self.llm_engine = LLMEngine()
        
        print(colored("✅ Agent System Ready.\n", "green", attrs=["bold"]))

    def ask(self, query: str, force_mode: str = "auto") -> Dict[str, Any]:
        """
        Process user query.
        force_mode: 'auto', 'expert', 'llm'
        """
        print(colored(f"\n❓ User: {query}", "white", attrs=["bold"]))
        
        mode = force_mode
        meta = {}
        
        # 1. Analyze and Route
        suggested_mode, meta = self.router.route(query)
        
        # Override if forced (except 'auto')
        if mode == "auto":
            mode = suggested_mode
        else:
            print(colored(f"⚠️  Forcing Mode: {mode.upper()} (suggested: {suggested_mode.upper()})", "yellow"))
            
        # 2. Dispatch
        response = {}
        
        if mode == "expert":
            print(colored("🛡️  Mode: EXPERT (Secure)", "blue"))
            response = self.expert_engine.query(query, meta.get("entities"))
        elif mode == "llm":
            print(colored("🤖 Mode: LLM (General)", "magenta"))
            response = self.llm_engine.query(query)
        elif mode == "ambiguous":
             print(colored("⚠️  Mode: AMBIGUOUS - Defaulting to Expert safely", "yellow"))
             # Fallback to expert for safety, or ask user (CLI just falls back)
             response = self.expert_engine.query(query, meta.get("entities"))
        
        # 3. Output
        print(colored(f"💡 Answer ({response.get('source')}):", "green"))
        print(response.get("answer"))
        return response

def main():
    parser = argparse.ArgumentParser(description="Dual-Mode Hybrid Agent")
    parser.add_argument("--build", action="store_true", help="Rebuild ontology from docs")
    parser.add_argument("--docs", default="docs", help="Path to documents")
    parser.add_argument("--mode", default="auto", choices=["auto", "expert", "llm"], help="Force specific mode")
    args = parser.parse_args()
    
    # If no specific mode or query is provided, we can run the server
    # or if the user explicitly wants to run the server.
    # For now, let's keep the uvicorn run but move it after parsing
    # so --help works.
    if len(sys.argv) == 1:
        uvicorn.run("api.api_hybrid:app", host="0.0.0.0", port=8001, reload=True)
        return
    
    agent = DualModeAgent(build_ontology=args.build, docs_dir=args.docs)
    
    if args.query:
        agent.ask(args.query, force_mode=args.mode)
    else:
        # Interactive Loop
        print("Type 'exit' to quit.")
        while True:
            try:
                user_input = input("\n> ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                agent.ask(user_input, force_mode=args.mode)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()

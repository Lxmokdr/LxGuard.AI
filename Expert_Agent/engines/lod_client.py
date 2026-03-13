
import requests
import urllib.parse
from typing import Dict, Any, Optional, List

class LODClient:
    """
    Client for querying Linked Open Data (LOD) via SPARQL.
    Defaults to DBpedia.
    """
    
    def __init__(self, endpoint: str = "https://dbpedia.org/sparql"):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "HybridKnowledgeAgent/1.0 (Educational; +http://localhost)"
        })
        
        # Hardcoded fallbacks for demo stability (if DBpedia is flaky/empty)
        self.fallbacks = {
            "React_(JavaScript_library)": "React is a free and open-source front-end JavaScript library for building user interfaces based on components. It is maintained by Meta (formerly Facebook) and a community of individual developers and companies. React can be used as a base in the development of single-page, mobile, or server-rendered applications with frameworks like Next.js.",
            "NextJS": "Next.js is an open-source web development framework created by the private company Vercel providing React-based web applications with server-side rendering and static website generation.",
            "Tim_Berners-Lee": "Sir Timothy John Berners-Lee is an English computer scientist usually credited with the invention of the World Wide Web. He is a professorial fellow of computer science at the University of Oxford and a professor at the Massachusetts Institute of Technology (MIT)."
        }
        
    def query(self, sparql_query: str) -> Dict[str, Any]:
        """Execute a raw SPARQL query"""
        params = {
            "query": sparql_query,
            "format": "json"
        }
        
        try:
            response = self.session.get(self.endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  LOD Query Failed: {e}")
            return {}

    def get_entity_abstract(self, entity_name: str) -> Optional[str]:
        """
        Get the abstract of an entity from DBpedia.
        Refined to handle case sensitivity and common variations.
        """
        print(f"🔍 LOD Lookup: Searching for '{entity_name}'")
        
        # 1. Manual Overrides for known entities (to avoid guessing)
        entity_lower = entity_name.lower().strip()
        overrides = {
            "react": "React_(JavaScript_library)",
            "next.js": "NextJS",
            "next js": "NextJS",
            "nextjs": "NextJS",
            "typescript": "TypeScript",
            "javascript": "JavaScript",
            "tim berners-lee": "Tim_Berners-Lee"
        }
        
        if entity_lower in overrides:
             entity_formatted = overrides[entity_lower]
             print(f"   Using manual override: '{entity_name}' -> '{entity_formatted}'")
        else:
             entity_formatted = entity_name.replace(" ", "_")

        # 2. Try strict label search first (Fastest & Most Accurate)
        # Check both the raw name and the formatted name
        labels_to_try = [entity_formatted, entity_name]
        
        for label in labels_to_try:
            print(f"   Trying exact label match for: '{label}'")
            # Try abstract first, then comment
            query_label = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            
            SELECT ?desc WHERE {{
                ?s rdfs:label "{label}"@en .
                {{
                    ?s dbo:abstract ?desc .
                }}
                UNION
                {{
                     ?s rdfs:comment ?desc .
                }}
                FILTER (lang(?desc) = 'en')
            }}
            LIMIT 1
            """
            
            data = self.query(query_label)
            bindings = data.get("results", {}).get("bindings", [])
            
            if bindings:
                abstract = bindings[0]["desc"]["value"]
                print(f"   ✅ Found via exact label '{label}' (length: {len(abstract)})")
                return abstract

        # 3. Fallback to direct resource URI (if label search fails)
        print(f"   Label search failed, trying direct resource URI: {entity_formatted}")
        query_uri = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?desc WHERE {{
            {{
                <http://dbpedia.org/resource/{entity_formatted}> dbo:abstract ?desc .
            }}
            UNION
            {{
                <http://dbpedia.org/resource/{entity_formatted}> rdfs:comment ?desc .
            }}
            FILTER (lang(?desc) = 'en')
        }}
        LIMIT 1
        """
        
        data = self.query(query_uri)
        bindings = data.get("results", {}).get("bindings", [])
        
        if bindings:
             abstract = bindings[0]["desc"]["value"]
             print(f"   ✅ Found via direct URI (length: {len(abstract)})")
             return abstract

        # 4. Fallback to hardcoded data (Safety Net for Verified URIs)
        if entity_formatted in self.fallbacks:
             print(f"   ⚠️ Connection/Data issue. Check failed. Using Fallback for: {entity_formatted}")
             return self.fallbacks[entity_formatted]

        # 5. SEARCH FALLBACK: If direct lookup fails, try searching by label (Case Insensitive)
        print(f"   Direct lookup failed, trying label search...")
        search_query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?abstract WHERE {{
            ?res rdfs:label ?label .
            ?res dbo:abstract ?abstract .
            FILTER (lcase(str(?label)) = lcase("{entity_name}") && lang(?abstract) = 'en')
        }}
        LIMIT 1
        """
        
        data = self.query(search_query)
        bindings = data.get("results", {}).get("bindings", [])
        
        if bindings:
            abstract = bindings[0]["abstract"]["value"]
            print(f"   ✅ Found via label search (length: {len(abstract)})")
            return abstract
        
        print(f"   ❌ No results found for '{entity_name}'")
        return None

if __name__ == "__main__":
    client = LODClient()
    print("Testing DBpedia query for 'React (software)'...")
    abstract = client.get_entity_abstract("React_(software)")
    print(f"Result (truncated): {abstract[:200]}..." if abstract else "Not found")

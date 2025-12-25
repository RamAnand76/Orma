from ddgs import DDGS
from ..base import BaseTool

class DdgsTool(BaseTool):
    name = "search_web"
    description = "Searches the web for realtime info. BEST for current events and facts."
    
    def execute(self, query: str) -> str:
        try:
            results_text = []
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=5)
                
                if not results:
                    return "No results found."

                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    url = r.get("href", "")
                    results_text.append(f"TITLE: {title}\nCONTENT: {body}\nURL: {url}\n")
            
            return "\n".join(results_text)
            
        except Exception as e:
            return f"DDGS Search Error: {e}"

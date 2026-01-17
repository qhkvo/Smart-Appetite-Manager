import httpx
import logging
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)

async def check_local_flyers(
    item_name: str,
    location: str = "K1N, Ottawa, Ontario",
    tool_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Fetches real-time local grocery deals using SerpApi's Google Shopping engine."""
    
    # 1. Securely fetch your API key from tool_config (set in your YAML)
    api_key = tool_config.get("serpapi_key") if tool_config else None
    if not api_key:
        return {"status": "error", "message": "SerpApi key is missing."}

    # 2. Configure the search parameters for Ottawa
    params = {
        "engine": "google_shopping",
        "q": f"{item_name} grocery",
        "location": location,
        "gl": "ca",          # Google Canada
        "hl": "en",          # English
        "on_sale": "1",      # IMPORTANT: Focuses on flyer-style deals
        "api_key": api_key
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://serpapi.com/search.json", params=params)
            resp.raise_for_status()
            results = resp.json().get("shopping_results", [])

        if not results:
            return {"status": "not_found", "message": f"No sales found for {item_name}."}

        # 3. Format the top deal for your Agent
        best_deal = results[0]
        return {
            "status": "success",
            "store": best_deal.get("source"),
            "price": best_deal.get("price"),
            "item": best_deal.get("title"),
            "link": best_deal.get("product_link"),
            "source": "Live Google Shopping Data"
        }

    except Exception as e:
        log.error(f"[ShopperTools] API failure: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
"""Small client for the OpenFoodFacts API.

Each function returns a dict shaped like our inventory items
(without id/price/stock), or None if nothing was found.
It raises OpenFoodFactsError if the API cannot be reached.
"""
import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}


class OpenFoodFactsError(Exception):
    """Raised when the external API fails (network error, bad response)."""


def _clean(product, barcode=None):
    """Keep only the fields we care about."""
    return {
        "product_name": product.get("product_name") or "Unknown",
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "barcode": barcode or product.get("code", ""),
    }


def _get(url, params=None):
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except (requests.exceptions.RequestException, ValueError) as exc:
        raise OpenFoodFactsError(f"OpenFoodFacts request failed: {exc}") from exc


def fetch_by_barcode(barcode):
    data = _get(f"{BASE_URL}/api/v2/product/{barcode}.json")
    if data.get("status") != 1:
        return None
    return _clean(data["product"], barcode)


def search_by_name(name):
    data = _get(
        f"{BASE_URL}/cgi/search.pl",
        params={"search_terms": name, "search_simple": 1,
                "action": "process", "json": 1, "page_size": 1},
    )
    products = data.get("products", [])
    if not products:
        return None
    return _clean(products[0])
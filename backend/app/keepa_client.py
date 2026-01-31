import keepa
from app import config


def get_client():
    if not config.KEEPA_API_KEY:
        raise RuntimeError("Missing KEEPA_API_KEY")
    return keepa.Keepa(config.KEEPA_API_KEY)


def product_finder_by_category(client, category_id, bsr_threshold=50000, page=0, per_page=50):
    params = {
        "category": int(category_id),
        "salesRankRange": [1, int(bsr_threshold)],
        "sort": "salesrank",
        "perPage": int(per_page),
        "page": int(page),
    }
    return client.product_finder(params)


def fetch_category_tree(category_id, domain='IN', include_parents=False):
    """
    Fetch category tree from Keepa API.
    
    Args:
        category_id: Parent category ID (e.g., 1350387031 for Toys & Games)
        domain: Amazon domain ('IN', 'US', etc.)
        include_parents: Whether to include parent categories
    
    Returns:
        dict: Category data with metrics (productCount, avgBuyBox, isFBAPercent, etc.)
    """
    client = get_client()
    return client.category_lookup(category_id, domain=domain, include_parents=include_parents)

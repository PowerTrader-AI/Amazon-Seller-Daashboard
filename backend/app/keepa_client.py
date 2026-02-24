import keepa
from app import config


def get_client():
    if not config.KEEPA_API_KEY:
        raise RuntimeError("Missing KEEPA_API_KEY")
    return keepa.Keepa(config.KEEPA_API_KEY)


def product_finder_by_category(client, category_id, bsr_threshold=50000, page=0, per_page=50, domain="IN"):
    """
    Fetch best-selling products from a specific category using Keepa's best_sellers_query API.
    
    Args:
        client: Keepa API client
        category_id: Root category ID (e.g., 1350388031 for Toys & Games on Amazon India)
        bsr_threshold: Max sales rank to include (unused - best_sellers returns up to 100k top sellers)
        page: Page number for pagination (start index)
        per_page: Results per page (max 100 for best sellers)
        domain: Amazon domain ('IN', 'US', etc.)
    
    Returns:
        list: List of ASIN strings (best sellers first)
    
    Note: Uses best_sellers_query which returns the most popular products sorted by sales.
    Returns up to 100,000 ASINs for root categories.
    """
    # Adjust per_page - best_sellers returns full list, so we paginate client-side
    per_page = min(per_page, 100)
    
    # Fetch all best sellers for the category
    all_asins = client.best_sellers_query(
        category=str(category_id),
        domain=domain,
        wait=True
    )
    
    # Apply pagination
    start_idx = page * per_page
    end_idx = start_idx + per_page
    
    return all_asins[start_idx:end_idx]


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

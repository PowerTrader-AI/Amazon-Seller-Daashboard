"""
Keepa Product Cache - Database Layer
Handles 7-day caching of Keepa API data to minimize token usage
Works with SQLite database
"""

import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_cached_products(conn, asin_list: List[str], domain: int = 1) -> Tuple[List[Dict], List[str]]:
    """
    Retrieve products from cache. Returns cached products and list of ASINs needing refresh.
    
    Args:
        conn: Database connection
        asin_list: List of ASINs to fetch
        domain: Amazon domain (1=US, 2=UK, etc)
    
    Returns:
        Tuple of (cached_products, missing_asins)
    """
    if not asin_list:
        return [], []
    
    placeholders = ','.join(['?' for _ in asin_list])
    query = f"""
        SELECT 
            asin, title, brand, images_csv, domain_id,
            csv, current_price_cents, current_sales_rank, 
            current_rating, current_review_count,
            cached_at, expires_at,
            author, availability_amazon, binding, categories, color,
            description, features, product_group, product_type,
            sales_rank_reference, has_reviews, 
            manufacturer, model, parent_asin, size,
            item_height, item_length, item_width, item_weight
        FROM keepa_products_cache
        WHERE asin IN ({placeholders})
          AND domain_id = ?
          AND (expires_at IS NULL OR expires_at > datetime('now'))
    """
    
    cursor = conn.cursor()
    cursor.execute(query, asin_list + [domain])
    rows = cursor.fetchall()
    
    cached_products = []
    cached_asins = set()
    
    for row in rows:
        cached_asins.add(row[0])
        product = {
            'asin': row[0],
            'title': row[1],
            'brand': row[2],
            'imagesCSV': row[3],
            'domainId': row[4],
            'csv': json.loads(row[5]) if row[5] else None,
            'currentPrice': row[6] / 100.0 if row[6] else 0,
            'currentSalesRank': row[7] or 0,
            'currentRating': float(row[8]) if row[8] else 0,
            'currentReviewCount': row[9] or 0,
            'cachedAt': row[10] if isinstance(row[10], str) else (row[10].isoformat() if row[10] else None),
            'expiresAt': row[11] if isinstance(row[11], str) else (row[11].isoformat() if row[11] else None),
            # Can add more fields as needed
        }
        cached_products.append(product)
    
    missing_asins = [asin for asin in asin_list if asin not in cached_asins]
    
    logger.info(f"Cache: {len(cached_products)} found, {len(missing_asins)} missing")
    
    return cached_products, missing_asins


def save_keepa_product(conn, product_data: Dict, domain: int = 1) -> bool:
    """
    Save/update a Keepa product in cache with all 70 fields.
    
    Args:
        conn: Database connection
        product_data: Full Keepa API product response
        domain: Amazon domain
    
    Returns:
        bool: Success status
    """
    try:
        from datetime import datetime, timedelta
        
        # Extract current metrics from CSV array
        current_price = None
        current_rank = None
        current_rating = None
        current_reviews = None
        
        csv_array = product_data.get('csv')
        if csv_array:
            # CSV[0]: Price
            if len(csv_array) > 0 and csv_array[0]:
                price_hist = csv_array[0]
                if isinstance(price_hist, list) and len(price_hist) > 0:
                    latest = price_hist[-1]
                    if isinstance(latest, list) and len(latest) >= 2:
                        current_price = latest[1] if latest[1] != -1 else None
            
            # CSV[3]: Sales rank
            if len(csv_array) > 3 and csv_array[3]:
                rank_hist = csv_array[3]
                if isinstance(rank_hist, list) and len(rank_hist) > 0:
                    latest = rank_hist[-1]
                    if isinstance(latest, list) and len(latest) >= 2:
                        current_rank = latest[1] if latest[1] != -1 else None
            
            # CSV[16]: Rating (×10)
            if len(csv_array) > 16 and csv_array[16]:
                rating_hist = csv_array[16]
                if isinstance(rating_hist, list) and len(rating_hist) > 0:
                    latest = rating_hist[-1]
                    if isinstance(latest, list) and len(latest) >= 2:
                        current_rating = latest[1] / 10.0 if latest[1] != -1 else None
            
            # CSV[17]: Review count
            if len(csv_array) > 17 and csv_array[17]:
                review_hist = csv_array[17]
                if isinstance(review_hist, list) and len(review_hist) > 0:
                    latest = review_hist[-1]
                    if isinstance(latest, list) and len(latest) >= 2:
                        current_reviews = latest[1] if latest[1] != -1 else None
        
        # Calculate expiration: 7 days from now
        now = datetime.now()
        expires_at = (now + timedelta(days=7)).isoformat()
        
        # Insert or update with all 70 fields
        query = """
            INSERT OR REPLACE INTO keepa_products_cache (
                asin, domain_id,
                author, availability_amazon, binding, brand, buy_box_seller_id_history,
                categories, category_tree, color, coupon, csv, description,
                ean_list, ebay_listing_ids, edition, fba_fees, features, format,
                frequently_bought_together, g, has_reviews, images_csv,
                is_adult_product, is_b2b, is_eligible_for_super_saver_shipping,
                is_eligible_for_trade_in, is_redirect_asin, is_sns,
                item_height, item_length, item_weight, item_width, languages,
                last_ebay_update, last_price_change, last_rating_update, last_update,
                launchpad, listed_since, live_offers_order, manufacturer, model,
                new_price_is_map, number_of_items, number_of_pages, offers_successful,
                package_height, package_length, package_quantity, package_weight, package_width,
                parent_asin, part_number, product_group, product_type, promotions,
                publication_date, release_date, root_category,
                sales_rank_reference, sales_rank_reference_history, sales_ranks,
                size, title, tracking_since, type, upc_list, variation_csv, variations,
                current_price_cents, current_sales_rank, current_rating, current_review_count,
                cached_at, expires_at, updated_at
            ) VALUES (
                ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                datetime('now'), ?, datetime('now')
            )
        """
        
        # Prepare values (all 70 fields + extracted metrics)
        values = (
            product_data.get('asin'),
            domain,
            # 70 Keepa fields in order
            product_data.get('author'),
            product_data.get('availabilityAmazon'),
            product_data.get('binding'),
            product_data.get('brand'),
            json.dumps(product_data.get('buyBoxSellerIdHistory')) if product_data.get('buyBoxSellerIdHistory') else None,
            json.dumps(product_data.get('categories')) if product_data.get('categories') else None,
            json.dumps(product_data.get('categoryTree')) if product_data.get('categoryTree') else None,
            product_data.get('color'),
            json.dumps(product_data.get('coupon')) if product_data.get('coupon') else None,
            json.dumps(product_data.get('csv')) if product_data.get('csv') else None,
            product_data.get('description'),
            json.dumps(product_data.get('eanList')) if product_data.get('eanList') else None,
            json.dumps(product_data.get('ebayListingIds')) if product_data.get('ebayListingIds') else None,
            product_data.get('edition'),
            json.dumps(product_data.get('fbaFees')) if product_data.get('fbaFees') else None,
            json.dumps(product_data.get('features')) if product_data.get('features') else None,
            product_data.get('format'),
            json.dumps(product_data.get('frequentlyBoughtTogether')) if product_data.get('frequentlyBoughtTogether') else None,
            product_data.get('g'),
            product_data.get('hasReviews'),
            product_data.get('imagesCSV'),
            product_data.get('isAdultProduct'),
            product_data.get('isB2B'),
            product_data.get('isEligibleForSuperSaverShipping'),
            product_data.get('isEligibleForTradeIn'),
            product_data.get('isRedirectASIN'),
            product_data.get('isSNS'),
            product_data.get('itemHeight'),
            product_data.get('itemLength'),
            product_data.get('itemWeight'),
            product_data.get('itemWidth'),
            json.dumps(product_data.get('languages')) if product_data.get('languages') else None,
            product_data.get('lastEbayUpdate'),
            product_data.get('lastPriceChange'),
            product_data.get('lastRatingUpdate'),
            product_data.get('lastUpdate'),
            product_data.get('launchpad'),
            product_data.get('listedSince'),
            json.dumps(product_data.get('liveOffersOrder')) if product_data.get('liveOffersOrder') else None,
            product_data.get('manufacturer'),
            product_data.get('model'),
            product_data.get('newPriceIsMAP'),
            product_data.get('numberOfItems'),
            product_data.get('numberOfPages'),
            product_data.get('offersSuccessful'),
            product_data.get('packageHeight'),
            product_data.get('packageLength'),
            product_data.get('packageQuantity'),
            product_data.get('packageWeight'),
            product_data.get('packageWidth'),
            product_data.get('parentAsin'),
            product_data.get('partNumber'),
            product_data.get('productGroup'),
            product_data.get('productType'),
            json.dumps(product_data.get('promotions')) if product_data.get('promotions') else None,
            product_data.get('publicationDate'),
            product_data.get('releaseDate'),
            product_data.get('rootCategory'),
            product_data.get('salesRankReference'),
            json.dumps(product_data.get('salesRankReferenceHistory')) if product_data.get('salesRankReferenceHistory') else None,
            json.dumps(product_data.get('salesRanks')) if product_data.get('salesRanks') else None,
            product_data.get('size'),
            product_data.get('title'),
            product_data.get('trackingSince'),
            product_data.get('type'),
            json.dumps(product_data.get('upcList')) if product_data.get('upcList') else None,
            product_data.get('variationCSV'),
            json.dumps(product_data.get('variations')) if product_data.get('variations') else None,
            # Extracted metrics
            current_price,
            current_rank,
            current_rating,
            current_reviews,
            # expires_at
            expires_at
        )
        
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        
        logger.info(f"✅ Saved ASIN {product_data.get('asin')} to cache (expires: 7 days)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving product to cache: {str(e)}")
        conn.rollback()
        return False


def get_cache_stats(conn) -> Dict:
    """Get cache statistics for SQLite."""
    cursor = conn.cursor()
    
    # SQLite doesn't support FILTER clause, use CASE instead
    cursor.execute("""
        SELECT 
            COUNT(*) as total_products,
            SUM(CASE WHEN expires_at > datetime('now') THEN 1 ELSE 0 END) as fresh_products,
            SUM(CASE WHEN expires_at <= datetime('now') THEN 1 ELSE 0 END) as stale_products,
            COUNT(DISTINCT domain_id) as domains,
            SUM(search_count) as total_searches,
            MIN(cached_at) as oldest_cache,
            MAX(cached_at) as newest_cache
        FROM keepa_products_cache
    """)
    
    row = cursor.fetchone()
    
    if not row:
        return {
            'totalProducts': 0,
            'freshProducts': 0,
            'staleProducts': 0,
            'domains': 0,
            'totalSearches': 0,
            'oldestCache': None,
            'newestCache': None
        }
    
    return {
        'totalProducts': row[0] or 0,
        'freshProducts': row[1] or 0,
        'staleProducts': row[2] or 0,
        'domains': row[3] or 0,
        'totalSearches': row[4] or 0,
        'oldestCache': row[5] if row[5] else None,
        'newestCache': row[6] if row[6] else None
    }

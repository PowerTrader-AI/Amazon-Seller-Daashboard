"""
Category analysis endpoints for Amazon Toys category.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import logging
from app.keepa_client import fetch_category_tree
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/category", tags=["category"])

# Cache for category data (24 hour expiration)
_category_cache = {}
_cache_expiry = {}
CACHE_DURATION = 86400  # 24 hours

def get_cached_categories(category_id: int, domain: str = 'IN'):
    """
    Fetch categories from Keepa API with 24-hour caching.
    """
    cache_key = f"{category_id}_{domain}"
    current_time = time.time()
    
    # Check cache
    if cache_key in _category_cache and current_time < _cache_expiry.get(cache_key, 0):
        return _category_cache[cache_key]
    
    # Fetch from Keepa
    categories = fetch_category_tree(category_id, domain=domain, include_parents=False)
    
    # Cache it
    _category_cache[cache_key] = categories
    _cache_expiry[cache_key] = current_time + CACHE_DURATION
    
    return categories

# Fallback: Toys category data from Keepa (if API fails)
TOYS_CATEGORIES_FALLBACK = {
    "Toys & Games": {
        "category_id": "1350381031",
        "products": 83894,
        "avg_price": 3681.11,
        "sales_rank": 739,
        "buy_box_drop": 0.49,
        "review_count": 560,
        "fba_share": 84,
        "subcategories": {
            "Action & Toy Figures": {
                "category_id": "1378568031",
                "products": 170736,
                "avg_price": 2576.85,
                "sales_rank": 20,
                "buy_box_drop": -0.66,
                "review_count": 635,
                "fba_share": 84
            },
            "Arts & Crafts": {
                "category_id": "1378132031",
                "products": 204949,
                "avg_price": 667.47,
                "sales_rank": 14,
                "buy_box_drop": 0.02,
                "review_count": 279,
                "fba_share": 92
            },
            "Baby & Toddler Toys": {
                "category_id": "1378175031",
                "products": 193594,
                "avg_price": 933.64,
                "sales_rank": 1,
                "buy_box_drop": 0.05,
                "review_count": 326,
                "fba_share": 86
            },
            "Bikes, Trikes & Ride-Ons": {
                "category_id": "1378198031",
                "products": 55990,
                "avg_price": 3997.77,
                "sales_rank": 2,
                "buy_box_drop": 0.00,
                "review_count": 512,
                "fba_share": 75
            },
            "Building & Construction Toys": {
                "category_id": "1378216031",
                "products": 42287,
                "avg_price": 3147.46,
                "sales_rank": 6,
                "buy_box_drop": 0.10,
                "review_count": 798,
                "fba_share": 77
            },
            "Collectible Toys": {
                "category_id": "2816715003",
                "products": 59207,
                "avg_price": 1823.16,
                "sales_rank": 312,
                "buy_box_drop": -0.74,
                "review_count": 284,
                "fba_share": 82
            },
            "Dolls & Accessories": {
                "category_id": "1378260031",
                "products": 186176,
                "avg_price": 1776.73,
                "sales_rank": 19,
                "buy_box_drop": 0.15,
                "review_count": 600,
                "fba_share": 88
            },
            "Dress Up & Pretend Play": {
                "category_id": "1378451031",
                "products": 364997,
                "avg_price": 1046.95,
                "sales_rank": 17,
                "buy_box_drop": -0.25,
                "review_count": 211,
                "fba_share": 88
            },
            "Electronic Toys": {
                "category_id": "1378290031",
                "products": 44346,
                "avg_price": 2179.41,
                "sales_rank": 3,
                "buy_box_drop": 0.47,
                "review_count": 379,
                "fba_share": 76
            },
            "Games": {
                "category_id": "1378311031",
                "products": 218569,
                "avg_price": 1542.04,
                "sales_rank": 8,
                "buy_box_drop": -0.37,
                "review_count": 544,
                "fba_share": 89
            },
            "Learning & Education": {
                "category_id": "1378342031",
                "products": 118423,
                "avg_price": 1158.94,
                "sales_rank": 7,
                "buy_box_drop": -0.33,
                "review_count": 403,
                "fba_share": 89
            },
            "Marble Runs": {
                "category_id": "1378189031",
                "products": 2332,
                "avg_price": 763.25,
                "sales_rank": 13472,
                "buy_box_drop": 0.00,
                "review_count": 74,
                "fba_share": 71,
                "opportunity_score": 95  # LOW competition, good margins
            },
            "Model Building Kits": {
                "category_id": "1378364031",
                "products": 50266,
                "avg_price": 2447.29,
                "sales_rank": 392,
                "buy_box_drop": -1.04,
                "review_count": 223,
                "fba_share": 90,
                "opportunity_score": 88  # MEDIUM competition, high margins
            },
            "Model Trains & Accessories": {
                "category_id": "1378384031",
                "products": 25029,
                "avg_price": 3457.75,
                "sales_rank": 1262,
                "buy_box_drop": -0.92,
                "review_count": 265,
                "fba_share": 89
            },
            "Musical Toy Instruments": {
                "category_id": "1378411031",
                "products": 24760,
                "avg_price": 1200.11,
                "sales_rank": 72,
                "buy_box_drop": 0.66,
                "review_count": 233,
                "fba_share": 83,
                "opportunity_score": 92  # MEDIUM competition, good margins
            },
            "Novelty & Gag Toys": {
                "category_id": "1378417031",
                "products": 117897,
                "avg_price": 638.85,
                "sales_rank": 4,
                "buy_box_drop": 0.31,
                "review_count": 214,
                "fba_share": 88
            },
            "Party Supplies": {
                "category_id": "1378424031",
                "products": 305222,
                "avg_price": 374.39,
                "sales_rank": 483,
                "buy_box_drop": -0.42,
                "review_count": 98,
                "fba_share": 85
            },
            "Puppets & Puppet Theatres": {
                "category_id": "1378463031",
                "products": 6806,
                "avg_price": 1396.43,
                "sales_rank": 152,
                "buy_box_drop": -0.26,
                "review_count": 223,
                "fba_share": 86
            },
            "Puzzles": {
                "category_id": "1378470031",
                "products": 101086,
                "avg_price": 775.89,
                "sales_rank": 12,
                "buy_box_drop": 0.04,
                "review_count": 350,
                "fba_share": 89
            },
            "Remote & App-Controlled Toys": {
                "category_id": "1378480031",
                "products": 163616,
                "avg_price": 2529.95,
                "sales_rank": 9,
                "buy_box_drop": 0.32,
                "review_count": 184,
                "fba_share": 77
            },
            "School Supplies": {
                "category_id": "1378490031",
                "products": 87486,
                "avg_price": 531.11,
                "sales_rank": 46,
                "buy_box_drop": 0.20,
                "review_count": 216,
                "fba_share": 89
            },
            "Soft Toys": {
                "category_id": "1378445031",
                "products": 213426,
                "avg_price": 964.92,
                "sales_rank": 1,
                "buy_box_drop": -0.29,
                "review_count": 508,
                "fba_share": 90
            },
            "Sport & Outdoor": {
                "category_id": "1378509031",
                "products": 195287,
                "avg_price": 1531.82,
                "sales_rank": 20,
                "buy_box_drop": -0.13,
                "review_count": 381,
                "fba_share": 82
            },
            "Toy Vehicles": {
                "category_id": "1378242031",
                "products": 238308,
                "avg_price": 1358.78,
                "sales_rank": 13,
                "buy_box_drop": 0.56,
                "review_count": 211,
                "fba_share": 89
            }
        }
    }
}


@router.get("/tree")
def get_category_tree():
    """
    Get the full Toys category tree with metrics.
    """
    return {
        "success": True,
        "categories": TOYS_CATEGORIES
    }


@router.get("/analysis")
def get_category_analysis():
    """
    Get analyzed category data with opportunity scores (LIVE from Keepa API).
    """
    try:
        # Fetch the "Categories" node which contains all 24 toy subcategories
        categories_node = get_cached_categories(1350381031, domain='IN')
        
        # Keepa returns string keys, not integers
        categories_key = '1350381031'
        if categories_key not in categories_node:
            logger.error("Categories node not found")
            return get_category_analysis_fallback()
        
        # Get the list of child category IDs
        children_ids = categories_node[categories_key].get('children', [])
        logger.info(f"Found {len(children_ids)} toy subcategories")
        
        if not children_ids:
            logger.warning("No children found, using fallback")
            return get_category_analysis_fallback()
        
        opportunities = []
        
        # Fetch each subcategory
        for child_id in children_ids:
            try:
                cat_result = get_cached_categories(child_id, domain='IN')
                # Check both string and int keys
                child_key = str(child_id)
                if child_key not in cat_result:
                    continue
                
                cat_data = cat_result[child_key]
            except Exception as e:
                logger.warning(f"Failed to fetch category {child_id}: {str(e)}")
                continue
            
            # Extract Keepa metrics
            products = cat_data.get('productCount', 0)
            avg_price = cat_data.get('avgBuyBox', 0) / 100  # Convert from cents to rupees
            fba_share = cat_data.get('isFBAPercent', 0)
            sales_rank = cat_data.get('highestRank', 999999)
            review_count = cat_data.get('avgReviewCount', 0)
            buy_box_deviation = cat_data.get('avgBuyBoxDeviation', 0) / 100
            delta_30_days = cat_data.get('avgDeltaPercent30BuyBox', 0)
            seller_count = cat_data.get('sellerCount', 0)  # Total unique sellers
            avg_offers_new = cat_data.get('avgOfferCountNew', 0)  # Avg sellers per product
            amazon_offers_pct = cat_data.get('soldByAmazonPercent', 0)  # Amazon competition
            
            # Skip categories with no products
            if products == 0:
                continue
            
            # Calculate opportunity score components
            
            # 1. Competition score (40% weight) - IMPROVED formula
            # Components:
            # - Product count (50% of competition)
            # - Seller count/density (30% of competition)
            # - Average offers per product (20% of competition)
            
            product_competition = max(0, 100 - (products / 5000))
            seller_density = (seller_count / max(products, 1)) * 100  # Sellers per product
            seller_competition = max(0, 100 - (seller_density * 20))  # Lower density = better
            
            # Offers competition: Lower avg offers = easier to get buy box
            # Assumption: 2-3 offers = easy, 5+ = moderate, 10+ = hard
            offers_competition = max(0, 100 - (avg_offers_new * 8))  # Each offer reduces score
            
            competition_score = (
                product_competition * 0.50 +
                seller_competition * 0.30 +
                offers_competition * 0.20
            )
            
            # 2. Margin score (20% weight) - UPDATED for Indian market price sensitivity
            # Sweet spot: ₹500-2000 (best conversion)
            # Acceptable: ₹2000-3500 (decent margin, some price resistance)
            # High risk: >₹3500 (low conversion due to price sensitivity)
            if avg_price < 500:
                margin_score = avg_price / 5  # Low margin products
            elif avg_price <= 2000:
                margin_score = 100  # Sweet spot for Indian market
            elif avg_price <= 3500:
                margin_score = 100 - ((avg_price - 2000) / 15)  # Declining score
            else:
                margin_score = max(0, 100 - ((avg_price - 3500) / 50))  # Penalty for high prices
            
            # 3. FBA score (20% weight)
            fba_score = fba_share
            
            # 4. Stability score (10% weight)
            stability_score = max(0, 100 - abs(delta_30_days))
            
            # 5. Entry barrier score (10% weight) - Based on avg review count
            # Logic: Lower avg reviews = easier for new sellers to rank
            # <100 reviews = excellent (score 100)
            # 100-300 = good (score 75-100)
            # 300-500 = moderate (score 50-75)
            # >500 = hard (score <50)
            if review_count < 100:
                entry_barrier_score = 100
            elif review_count < 300:
                entry_barrier_score = 100 - ((review_count - 100) / 200 * 25)
            elif review_count < 500:
                entry_barrier_score = 75 - ((review_count - 300) / 200 * 25)
            else:
                entry_barrier_score = max(0, 50 - ((review_count - 500) / 500 * 50))
            
            # 6. Amazon competition penalty
            # If Amazon sells >20% of category, it's risky
            amazon_penalty = 0
            if amazon_offers_pct > 20:
                amazon_penalty = (amazon_offers_pct - 20) * 0.5  # -0.5 points per percentage above 20%
            
            # Overall opportunity score (weights sum to 100%)
            opportunity_score = (
                competition_score * 0.40 +
                margin_score * 0.20 +
                fba_score * 0.20 +
                stability_score * 0.10 +
                entry_barrier_score * 0.10 -
                amazon_penalty
            )
            
            # Competition level
            if products < 30000:
                competition = "LOW"
            elif products < 100000:
                competition = "MEDIUM"
            else:
                competition = "HIGH"
            
            opportunities.append({
                "name": cat_data.get('name', 'Unknown'),
                "category_id": str(child_id),
                "products": products,
                "seller_count": seller_count,
                "avg_offers_per_product": round(avg_offers_new, 2),
                "amazon_offers_pct": round(amazon_offers_pct, 1),
                "avg_price": round(avg_price, 2),
                "sales_rank": sales_rank,
                "fba_share": round(fba_share, 0),
                "review_count": round(review_count, 0),
                "opportunity_score": round(opportunity_score, 1),
                "competition": competition,
                "recommended": opportunity_score >= 75,
                # Component scores for transparency
                "component_scores": {
                    "competition": round(competition_score, 1),
                    "margin": round(margin_score, 1),
                    "fba": round(fba_score, 1),
                    "stability": round(stability_score, 1),
                    "entry_barrier": round(entry_barrier_score, 1),
                    "amazon_penalty": round(amazon_penalty, 1)
                }
            })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        # Generate recommendations for each category
        for opp in opportunities:
            opp["recommendation"] = generate_recommendation(opp)
        
        logger.info(f"Successfully fetched {len(opportunities)} categories from Keepa API")
        
        return {
            "success": True,
            "opportunities": opportunities,
            "top_5": opportunities[:5],
            "data_source": "keepa_live"
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch category data: {str(e)}")
        logger.exception(e)  # Log full stack trace
        # Fallback to hardcoded data
        return get_category_analysis_fallback()


def generate_recommendation(category_data):
    """
    Generate dynamic text recommendation based on category metrics.
    Returns: recommendation_level (BUY/ANALYSE/AVOID), reason, risk_level, action_items
    """
    score = category_data['opportunity_score']
    products = category_data['products']
    sellers = category_data['seller_count']
    offers = category_data['avg_offers_per_product']
    price = category_data['avg_price']
    reviews = category_data['review_count']
    fba = category_data['fba_share']
    amazon_pct = category_data['amazon_offers_pct']
    
    # Determine recommendation level
    if score >= 85:
        recommendation = "BUY"
    elif score >= 70:
        recommendation = "ANALYSE"
    else:
        recommendation = "AVOID"
    
    # Generate reason text
    reasons = []
    
    # Competition analysis
    if offers < 1.5:
        reasons.append(f"Minimal competition ({offers:.1f} offers/product)")
    elif offers < 2.5:
        reasons.append(f"Moderate competition ({offers:.1f} offers/product)")
    else:
        reasons.append(f"High competition ({offers:.1f} offers/product)")
    
    # Price analysis
    if price < 500:
        reasons.append("Low price point (budget conscious market)")
    elif price <= 2000:
        reasons.append(f"Perfect price range ₹{price:.0f} (sweet spot)")
    elif price <= 3500:
        reasons.append(f"Higher price ₹{price:.0f} (price sensitive market)")
    else:
        reasons.append(f"Very high price ₹{price:.0f} (risky for India)")
    
    # Entry barrier analysis
    if reviews < 100:
        reasons.append("Low review barrier (easy to rank)")
    elif reviews < 300:
        reasons.append("Moderate review barrier")
    elif reviews < 500:
        reasons.append("High review barrier")
    else:
        reasons.append("Very high review barrier (hard to compete)")
    
    # Amazon threat
    if amazon_pct > 20:
        reasons.append(f"Amazon dominates ({amazon_pct}%) - RISKY")
    elif amazon_pct > 5:
        reasons.append(f"Amazon present ({amazon_pct}%)")
    else:
        reasons.append("Amazon not competing - SAFE")
    
    # FBA adoption
    if fba > 85:
        reasons.append("High FBA adoption (easy fulfillment)")
    elif fba > 70:
        reasons.append("Good FBA adoption")
    else:
        reasons.append("Lower FBA adoption (harder fulfillment)")
    
    reason_text = " | ".join(reasons)
    
    # Risk level assessment
    risk_factors = 0
    if offers > 3:
        risk_factors += 2
    if price > 3500:
        risk_factors += 2
    if reviews > 500:
        risk_factors += 1
    if amazon_pct > 20:
        risk_factors += 2
    if fba < 70:
        risk_factors += 1
    if sellers > 1000:
        risk_factors += 1
    
    if risk_factors >= 5:
        risk_level = "HIGH"
    elif risk_factors >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Action items
    action_items = []
    if recommendation == "BUY":
        action_items.append("✅ Research top products in this category")
        action_items.append("✅ Identify bestsellers with low reviews")
        if offers < 2:
            action_items.append("✅ QUICK ACTION: Launch ASAP (very low competition)")
        action_items.append("✅ Source wholesale samples")
    elif recommendation == "ANALYSE":
        action_items.append("⚠️ Deep dive analysis recommended")
        action_items.append("⚠️ Check individual ASINs before committing")
        if amazon_pct > 5:
            action_items.append("⚠️ Monitor Amazon's pricing strategy")
    else:
        action_items.append("❌ Skip this category")
        if offers > 3:
            action_items.append("❌ Too many competitors per product")
        if price > 3500:
            action_items.append("❌ Price too high for Indian market")
    
    return {
        "recommendation": recommendation,
        "reason": reason_text,
        "risk_level": risk_level,
        "action_items": action_items
    }



    """
    Fallback function using hardcoded data when Keepa API fails.
    """
    # Calculate opportunity scores
    opportunities = []
    
    for cat_name, cat_data in TOYS_CATEGORIES_FALLBACK["Toys & Games"]["subcategories"].items():
        # Opportunity score based on:
        # - Low competition (fewer products)
        # - Good margins (avg price vs typical wholesale)
        # - High FBA share (easier fulfillment)
        # - Stable pricing (low buy_box_drop volatility)
        
        products = cat_data["products"]
        avg_price = cat_data["avg_price"]
        fba_share = cat_data["fba_share"]
        buy_box_drop = abs(cat_data["buy_box_drop"])
        
        # Competition score (lower products = higher score)
        competition_score = max(0, 100 - (products / 5000))
        
        # Margin score (higher price = higher potential)
        margin_score = min(100, (avg_price / 50))
        
        # FBA score (higher FBA share = easier)
        fba_score = fba_share
        
        # Stability score (lower volatility = higher score)
        stability_score = max(0, 100 - (buy_box_drop * 100))
        
        # Overall opportunity score
        opportunity_score = (
            competition_score * 0.35 +
            margin_score * 0.25 +
            fba_score * 0.25 +
            stability_score * 0.15
        )
        
        # Competition level
        if products < 30000:
            competition = "LOW"
        elif products < 100000:
            competition = "MEDIUM"
        else:
            competition = "HIGH"
        
        opportunities.append({
            "name": cat_name,
            "category_id": cat_data["category_id"],
            "products": products,
            "avg_price": avg_price,
            "sales_rank": cat_data["sales_rank"],
            "fba_share": fba_share,
            "review_count": cat_data["review_count"],
            "opportunity_score": round(opportunity_score, 1),
            "competition": competition,
            "recommended": opportunity_score >= 75
        })
    
    # Sort by opportunity score
    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
    
    return {
        "success": True,
        "opportunities": opportunities,
        "top_5": opportunities[:5],
        "data_source": "fallback_hardcoded"
    }


@router.get("/category/{category_id}")
def get_category_details(category_id: str):
    """
    Get detailed analysis for a specific category (LIVE from Keepa).
    """
    try:
        # Fetch live data
        categories = get_cached_categories(int(category_id), domain='IN')
        
        # Find the category
        category_id_int = int(category_id)
        if category_id_int in categories:
            cat_data = categories[category_id_int]
            return {
                "success": True,
                "category": {
                    "name": cat_data.get('name', 'Unknown'),
                    "category_id": category_id,
                    "products": cat_data.get('productCount', 0),
                    "avg_price": cat_data.get('avgBuyBox', 0) / 100,
                    "fba_share": cat_data.get('isFBAPercent', 0),
                    "sales_rank": cat_data.get('highestRank', 999999),
                    "review_count": cat_data.get('avgReviewCount', 0),
                    "data_source": "keepa_live"
                }
            }
        
        raise HTTPException(status_code=404, detail="Category not found")
    
    except Exception as e:
        logger.error(f"Failed to fetch category {category_id}: {str(e)}")
        # Fallback to hardcoded data
        for cat_name, cat_data in TOYS_CATEGORIES_FALLBACK["Toys & Games"]["subcategories"].items():
            if cat_data["category_id"] == category_id:
                return {
                    "success": True,
                    "category": {
                        "name": cat_name,
                        "category_id": category_id,
                        **cat_data,
                        "data_source": "fallback_hardcoded"
                    }
                }
        
        raise HTTPException(status_code=404, detail="Category not found")


def is_branded_product(title):
    """Check if product is a well-known brand (avoid these for white-label sourcing)."""
    if not title:
        return False
    
    title_lower = title.lower()
    
    # List of major brands to avoid (focus on unbranded/generic items)
    major_brands = [
        'queen size', 'king size', 'twin size', 'full size',  # Generic brand-like sizes
        'lego', 'barbie', 'hot wheels', 'matchbox',  # Major toy brands
        'mattel', 'hasbro', 'fisher', 'fisher-price',  # Major manufacturers
        'ravensburger', 'melissa', 'doug',  # Well-known toy makers
        'melissa & doug',
        'beadsland',  # Generic re-seller brand indicator
        'kidz', 'kids', 'playstation', 'xbox', 'nintendo',
    ]
    
    for brand in major_brands:
        if brand in title_lower:
            return True
    
    # If title contains only common words and no unique identifier, likely generic
    common_words = ['set', 'pack', 'kit', 'toy', 'game', 'puzzle']
    uncommon_words = [word for word in title_lower.split() if word not in common_words]
    
    return len(uncommon_words) < 2


@router.get("/products/{category_id}")
async def get_category_products(
    category_id: int,
    bsr_threshold: int = 50000,
    per_page: int = 50,
    page: int = 0
):
    """Fetch top unbranded products from a category.
    
    Returns products sorted by bestseller rank from Keepa.
    Filters out branded/major brand products.
    
    Args:
        category_id: Keepa category ID
        bsr_threshold: Maximum bestseller rank
        per_page: Products per page
        page: Page number (0-indexed)
    """
    logger = logging.getLogger(__name__)
    
    try:
        from app.keepa_client import product_finder_by_category, get_client
        
        client = get_client()
        logger.info(f"Fetching products for category {category_id}")
        
        # Fetch top ASINs
        asin_list = product_finder_by_category(
            client,
            category_id=category_id,
            bsr_threshold=bsr_threshold,
            page=page,
            per_page=per_page
        )
        
        products = []
        if asin_list and len(asin_list) > 0:
            logger.info(f"Got {len(asin_list)} ASINs, fetching details...")
            
            try:
                product_data_list = client.query(asin_list)
                
                for product in product_data_list:
                    if not product:
                        continue
                    
                    title = product.get("title", "N/A")
                    asin = product.get("asin", "")
                    
                    # Skip branded products
                    if is_branded_product(title):
                        logger.debug(f"Skipping branded: {title[:40]}")
                        continue
                    
                    # Extract available data
                    reviews = product.get("reviews", 0)
                    rating = round(product.get("rating", 0) / 10, 1) if product.get("rating") else 0
                    fba_pct = product.get("isFBA", 0)
                    sellers = len(product.get("offers", [])) if product.get("offers") else 0
                    
                    # Get current price and rank from stats
                    stats = product.get("stats", {})
                    current = stats.get("current", {}) if stats else {}
                    current_price = current.get("price", 0)
                    sales_rank = current.get("sales", 0)
                    
                    # Calculate opportunity score
                    opportunity_score = 50  # Base score
                    
                    if reviews > 0:
                        opportunity_score += min(25, reviews / 10)  # +25 max for reviews
                    
                    if fba_pct >= 70:
                        opportunity_score += 10  # Good FBA adoption
                    
                    if sellers <= 2:
                        opportunity_score += 15  # Very low competition
                    elif sellers <= 5:
                        opportunity_score += 10
                    elif sellers > 10:
                        opportunity_score -= 5
                    
                    if sales_rank > 0 and sales_rank < 10000:
                        opportunity_score += 5  # In top 10k
                    
                    opportunity_score = min(100, max(0, opportunity_score))
                    
                    products.append({
                        "asin": asin,
                        "title": title,
                        "current_price": current_price,
                        "sales_rank": sales_rank if sales_rank > 0 else 999999,
                        "reviews": reviews,
                        "rating": rating,
                        "sellers": sellers,
                        "fba_percent": fba_pct,
                        "opportunity_score": round(opportunity_score, 1)
                    })
                    
            except Exception as e:
                logger.warning(f"Error querying products: {str(e)}")
        
        # Sort by opportunity score
        products.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return {
            "success": True,
            "category_id": category_id,
            "total_unbranded": len(products),
            "products": products[:50]
        }
        
    except Exception as e:
        logger.error(f"Error fetching products for category {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

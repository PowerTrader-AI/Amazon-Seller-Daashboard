"""
Category analysis endpoints for Amazon Toys category.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
import logging
import json
import re
from html import unescape
import requests
from app.keepa_client import fetch_category_tree
import time
import sqlite3
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/category", tags=["category"])

# In-memory cache (fast path)
_category_cache = {}
_cache_expiry = {}
CACHE_DURATION = 86400  # 24 hours

# SQLite DB path (same as main app)
_DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "amazon_sourcing.db"))


def _ensure_category_cache_table():
    """Create the keepa_category_cache table if it does not exist."""
    try:
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS keepa_category_cache (
                cache_key   TEXT PRIMARY KEY,
                payload     TEXT NOT NULL,
                expires_at  REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not ensure keepa_category_cache table: {e}")

_ensure_category_cache_table()


def get_cached_categories(category_id: int, domain: str = 'IN'):
    """
    Fetch categories from Keepa API with 24-hour caching.
    Uses in-memory dict first, then SQLite, then live Keepa call.
    """
    cache_key = f"{category_id}_{domain}"
    current_time = time.time()

    # 1. In-memory fast path
    if cache_key in _category_cache and current_time < _cache_expiry.get(cache_key, 0):
        return _category_cache[cache_key]

    # 2. SQLite persistent cache
    try:
        conn = sqlite3.connect(_DB_PATH)
        row = conn.execute(
            "SELECT payload, expires_at FROM keepa_category_cache WHERE cache_key = ?",
            (cache_key,)
        ).fetchone()
        conn.close()
        if row and current_time < row[1]:
            categories = json.loads(row[0])
            # Warm in-memory cache
            _category_cache[cache_key] = categories
            _cache_expiry[cache_key] = row[1]
            logger.debug(f"Category {cache_key} loaded from SQLite cache")
            return categories
    except Exception as e:
        logger.warning(f"SQLite category cache read failed: {e}")

    # 3. Live Keepa call
    categories = fetch_category_tree(category_id, domain=domain, include_parents=False)

    expires_at = current_time + CACHE_DURATION

    # Populate in-memory cache
    _category_cache[cache_key] = categories
    _cache_expiry[cache_key] = expires_at

    # Persist to SQLite
    try:
        conn = sqlite3.connect(_DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO keepa_category_cache (cache_key, payload, expires_at) VALUES (?, ?, ?)",
            (cache_key, json.dumps(categories), expires_at)
        )
        conn.commit()
        conn.close()
        logger.info(f"Category {cache_key} saved to SQLite cache (expires in 24h)")
    except Exception as e:
        logger.warning(f"SQLite category cache write failed: {e}")

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


@router.get("/{category_id}/bestsellers")
async def get_bestsellers_analysis(
    category_id: str,
    limit: int = 100,
    force_refresh: bool = False
):
    """
    Get best-selling products from a category with 7-dimension scoring.
    Uses 7-day caching to avoid redundant API calls.
    
    Args:
        category_id: Category ID (root or subcategory)
        limit: Max products to analyze (default 100)
    
    Returns:
        {
            "category_id": "1378568031",
            "total_available": 23332,
            "fetched": 100,
            "scored": 95,
            "from_cache": false,
            "last_synced": "2026-01-25T10:30:00Z",
            "next_sync": "2026-02-01T10:30:00Z",
            "token_cost": 235,
            "results": [...]
        }
    """
    import time
    from datetime import datetime, timedelta
    from app.db import (
        get_conn, get_category_sync_status, get_category_products_from_cache,
        set_category_syncing, save_category_sync, save_category_products,
        save_product_analysis_scores, get_product_analysis_scores, log_token_usage,
        get_asin_title, save_asin_title
    )
    from app.keepa_client import get_client
    from app.product_analysis import ProductAnalyzer
    
    start_time = time.time()
    
    try:
        # Get database connection
        db = get_conn()
        analysis_pool_limit = min(max(limit * 2, limit), 100)
        
        # STEP 1: Check if category cache is still fresh
        sync_status = get_category_sync_status(db, category_id, domain='IN')
        cache_is_fresh = False
        if sync_status and sync_status['status'] == 'completed' and sync_status['next_sync_at']:
            try:
                cache_is_fresh = datetime.fromisoformat(str(sync_status['next_sync_at'])) > datetime.now()
            except ValueError:
                cache_is_fresh = False
        
        if sync_status and cache_is_fresh and not force_refresh:
            # CACHE HIT! Load from database
            logger.info(f"✅ Cache hit for category {category_id}")
            
            cached_asins = get_category_products_from_cache(db, category_id, analysis_pool_limit)
            asins_to_fetch = cached_asins
            from_cache = True
            token_cost = 0
            total_available = sync_status['total_products']
            last_synced = sync_status['last_synced_at']
            next_sync = sync_status['next_sync_at']
            
            # Log cache hit
            log_token_usage(
                db, 'category_fetch', category_id, len(asins_to_fetch), 
                0, int((time.time() - start_time) * 1000), cache_hit=True
            )
            
        else:
            # CACHE MISS! Need to fetch from API
            reason = "force refresh requested" if force_refresh else "cache expired/missing"
            logger.info(f"🔄 Cache miss for category {category_id} ({reason}) - fetching from Keepa API")
            
            set_category_syncing(db, category_id)
            client = get_client()
            initial_tokens = getattr(client, 'tokens_left', None)
            
            # Fetch best-sellers list (1 token)
            all_asins = client.best_sellers_query(
                category=category_id,
                domain="IN",
                wait=False
            )
            
            if not all_asins:
                raise HTTPException(status_code=404, detail=f"No products found in category {category_id}")
            
            # Save ASIN list to database
            save_category_products(db, category_id, all_asins)
            
            asins_to_fetch = all_asins[:analysis_pool_limit]
            from_cache = False
            total_available = len(all_asins)
            last_synced = datetime.now().isoformat()
            
            # Query products (non-blocking; may partially fail if tokens are low)
            try:
                raw_products = client.query(asins_to_fetch, stats=180, rating=1, wait=False, domain='IN')
                # Keepa may omit ASINs it has no data for; fill gaps with stubs so
                # every ASIN still gets scored using its bestseller-rank position.
                asin_to_keepa = {p.get("asin"): p for p in raw_products if p and p.get("asin")}
                products = [asin_to_keepa.get(asin, {"asin": asin}) for asin in asins_to_fetch]

                final_tokens = getattr(client, 'tokens_left', None)
                tokens_used = (initial_tokens - final_tokens) if (initial_tokens and final_tokens) else 235
                token_cost = tokens_used

                # Save sync status to database
                save_category_sync(
                    db, category_id, total_available, len(raw_products),
                    tokens_used, int((time.time() - start_time)),
                    domain='IN'
                )
                next_sync = (datetime.now() + timedelta(days=7)).isoformat()

                # Log token usage
                log_token_usage(
                    db, 'category_fetch', category_id, len(asins_to_fetch),
                    tokens_used, int((time.time() - start_time) * 1000), cache_hit=False
                )
            except Exception as e:
                if 'NOT_ENOUGH_TOKEN' in str(e):
                    logger.warning(f"Token limit reached for category {category_id}. Falling back to cached results.")
                    cached_asins = get_category_products_from_cache(db, category_id, analysis_pool_limit)
                    asins_to_fetch = cached_asins
                    from_cache = True
                    token_cost = 0
                    next_sync = sync_status['next_sync_at'] if sync_status else (datetime.now() + timedelta(days=1)).isoformat()
                    if sync_status and sync_status['last_synced_at']:
                        last_synced = sync_status['last_synced_at']
                else:
                    raise
        
        # STEP 2: Score each product
        analyzer = ProductAnalyzer()
        scored_results = []

        # If from cache, only query Keepa for ASINs that don't have valid score cache
        if from_cache:
            asins_needing_keepa = []
            for asin in asins_to_fetch:
                score_row = get_product_analysis_scores(db, asin)
                if not score_row:
                    asins_needing_keepa.append(asin)

            if asins_needing_keepa:
                logger.info(f"Cache hit: {len(asins_needing_keepa)}/{len(asins_to_fetch)} ASINs need fresh Keepa data")
                client = get_client()
                try:
                    fresh_products = client.query(asins_needing_keepa, stats=180, rating=1, wait=False, domain='IN')
                    asin_to_product = {p.get("asin"): p for p in fresh_products if p and p.get("asin")}
                except Exception as e:
                    logger.warning(f"Failed to load fresh products from Keepa: {e}")
                    asin_to_product = {}
            else:
                logger.info(f"Cache hit: all {len(asins_to_fetch)} ASINs have score cache — skipping Keepa call")
                asin_to_product = {}

            # Build product list: use fresh Keepa data where available, else stub for DB score lookup
            products = [asin_to_product.get(asin, {"asin": asin}) for asin in asins_to_fetch]
        
        def extract_latest_csv_value(series: Any, divisor: float = 1.0) -> Optional[float]:
            if not isinstance(series, list) or not series:
                return None

            # Format: [[ts, value], ...]
            if isinstance(series[-1], list):
                for entry in reversed(series):
                    if isinstance(entry, list) and len(entry) >= 2:
                        value = entry[1]
                        if isinstance(value, (int, float)) and value != -1:
                            return float(value) / divisor
                return None

            # Format: [ts1, value1, ts2, value2, ...] (Keepa flattened)
            for idx in range(len(series) - 1, -1, -1):
                if idx % 2 == 1:
                    value = series[idx]
                    if isinstance(value, (int, float)) and value != -1:
                        return float(value) / divisor

            for value in reversed(series):
                if isinstance(value, (int, float)) and value != -1:
                    return float(value) / divisor

            return None

        def extract_stats_fallback(product_payload: Dict[str, Any], field_index: int, divisor: float = 1.0) -> Optional[float]:
            stats = product_payload.get('stats') or {}
            for key in ('current', 'avg30', 'avg90', 'avg180', 'avg365', 'avg'):
                values = stats.get(key)
                if isinstance(values, list) and len(values) > field_index:
                    value = values[field_index]
                    if isinstance(value, (int, float)) and value > 0:
                        return float(value) / divisor
            return None

        def convert_keepa_product(product_payload: Dict[str, Any], rank_position: int = None) -> Dict[str, Any]:
            csv_array = product_payload.get('csv') if isinstance(product_payload.get('csv'), list) else []

            price = None
            sales_rank = None
            rating = None
            review_count = None

            if len(csv_array) > 0:
                price = extract_latest_csv_value(csv_array[0], divisor=100.0)
            if len(csv_array) > 3:
                sales_rank = extract_latest_csv_value(csv_array[3], divisor=1.0)
            if len(csv_array) > 16:
                rating = extract_latest_csv_value(csv_array[16], divisor=10.0)
            if len(csv_array) > 17:
                review_count = extract_latest_csv_value(csv_array[17], divisor=1.0)

            if not price:
                price = extract_stats_fallback(product_payload, field_index=0, divisor=100.0)
            if not sales_rank:
                sales_rank = extract_stats_fallback(product_payload, field_index=3, divisor=1.0)

            asin = product_payload.get('asin', '')
            title = (product_payload.get('title') or '').strip() or f'ASIN {asin}'
            seller_count = int(product_payload.get('sellerCount') or 10)
            fba_share = float(product_payload.get('isFBAPercent') or 0)

            has_real_data = bool(
                (price and price > 0) or
                (sales_rank and sales_rank > 0 and sales_rank < 999999) or
                (review_count and review_count > 0) or
                (rating and rating > 0)
            )

            # If Keepa has no history but this ASIN appears in the bestseller list,
            # use its list position as a demand proxy so it still gets scored.
            data_quality = 'full'
            if not has_real_data and rank_position:
                # Map bestseller position → estimated sales rank
                # Position 1 → ~1 000, Position 100 → ~100 000
                sales_rank = rank_position * 1000
                data_quality = 'estimated'
            elif has_real_data and not (price and price > 0):
                data_quality = 'partial'

            has_minimum_data = has_real_data or bool(rank_position)

            return {
                'asin': asin,
                'title': title,
                'price': float(price or 0),
                'review_count': int(review_count or 0),
                'seller_count': max(1, seller_count),
                'sales_rank': int(sales_rank or 999999),
                'fba_share': fba_share,
                'fba_available_quantity': 500,
                'product_age_months': 12,
                'product_age_days': 365,
                '_has_minimum_data': has_minimum_data,
                '_data_quality': data_quality,
            }

        def is_weak_cached_score(row: Dict[str, Any]) -> bool:
            title = (row.get('title') or '').strip().upper()
            profitability = float(row.get('profitability_score') or 0)
            stability = float(row.get('stability_score') or 0)
            demand = float(row.get('demand_score') or 0)
            overall = float(row.get('overall_score') or 0)
            return (title in ('', 'N/A')) or (profitability == 0 and stability == 0 and demand <= 30 and overall <= 30)

        # In-memory title cache (avoids duplicate lookups within one request)
        _title_mem_cache: Dict[str, str] = {}
        _fresh_scrape_count = [0]  # mutable counter; only fresh HTTP fetches increment this
        _fresh_scrape_max = 20     # max new Amazon scrapes per request; DB cache hits are free

        def resolve_title(asin: str, title: Optional[str]) -> str:
            """Return best available title: Keepa > in-memory > DB cache > Amazon scrape > fallback."""
            clean_title = (title or '').strip()
            if clean_title and clean_title.upper() != 'N/A' and not clean_title.upper().startswith('ASIN '):
                resolved = clean_title[:120]
                _title_mem_cache[asin] = resolved
                return resolved

            # Check in-memory cache first (free)
            if asin in _title_mem_cache:
                return _title_mem_cache[asin]

            # Check persistent SQLite title cache (DB hit = free, no HTTP call)
            # Note: failed scrape attempts are also stored (as 'ASIN XXXXX') to prevent re-scraping
            cached_db_title = get_asin_title(db, asin)
            if cached_db_title is not None:
                title_res = cached_db_title if not cached_db_title.startswith('__pending__') and not cached_db_title.upper().startswith('ASIN ') else f'__pending__{asin}'
                _title_mem_cache[asin] = title_res
                return title_res

            # Scrape Amazon page — limited to _fresh_scrape_max NEW scrapes per request
            if _fresh_scrape_count[0] < _fresh_scrape_max:
                _fresh_scrape_count[0] += 1
                try:
                    response = requests.get(
                        f"https://www.amazon.in/dp/{asin}",
                        headers={
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                            "Accept-Language": "en-IN,en;q=0.9",
                        },
                        timeout=3,
                    )
                    if response.status_code == 200 and len(response.text) > 10000:
                        # Ignore short responses (< 10KB = CAPTCHA/robot-check page ~5KB)
                        match = re.search(r"<title>(.*?)</title>", response.text, flags=re.IGNORECASE | re.DOTALL)
                        if match:
                            scraped = unescape(match.group(1)).strip()
                            scraped = re.sub(r"\s*-\s*Amazon\.?in\s*$", "", scraped, flags=re.IGNORECASE).strip()
                            # Skip CAPTCHA titles ("Amazon.in", "Amazon") and empty titles
                            if scraped and scraped.lower() not in ('amazon.in', 'amazon') and not scraped.upper().startswith('ASIN '):
                                save_asin_title(db, asin, scraped, source='amazon')
                                _title_mem_cache[asin] = scraped[:120]
                                return scraped[:120]
                except Exception:
                    pass
                # Cache the failure with 24h TTL — prevents re-scraping this request cycle
                # and for the next 24h (transient CAPTCHAs may clear after that)
                save_asin_title(db, asin, f'__pending__{asin}', source='failed')
                _title_mem_cache[asin] = f'__pending__{asin}'  # block further attempts this request

            fallback = f'__pending__{asin}'
            _title_mem_cache[asin] = fallback
            return fallback

        # Build rank map: asin → 1-based bestseller position
        asin_rank_map = {asin: (i + 1) for i, asin in enumerate(asins_to_fetch)}

        # Score products (both from cache and fresh fetch)
        if products and len(products) > 0:
            for i, product in enumerate(products):
                if not product or product is None:
                    continue
                
                asin = product.get("asin", "")
                if not asin:
                    continue
                
                # Try to load from score cache first
                score_data = get_product_analysis_scores(db, asin)
                if score_data:
                    score_row = dict(score_data)
                    analysis_payload = {}
                    raw_analysis = score_row.get('analysis_data')

                    if raw_analysis:
                        try:
                            analysis_payload = json.loads(raw_analysis)
                        except Exception:
                            analysis_payload = {}

                    dimensions = analysis_payload.get('dimensions', {}) if isinstance(analysis_payload, dict) else {}

                    def pick_score(column_value, dim_key):
                        if column_value not in (None, 0, 0.0):
                            return float(column_value)
                        return float(dimensions.get(dim_key, {}).get('score', 0))

                    overall_score = score_row.get('overall_score')
                    if overall_score in (None, 0, 0.0):
                        overall_score = analysis_payload.get('overall_score', 0) if isinstance(analysis_payload, dict) else 0

                    raw_cached_title = (analysis_payload.get('title') or '').strip()

                    # Use resolve_title to fill DB cache progressively (DB hits are free; max 20 fresh scrapes/request)
                    cached_title = resolve_title(asin, raw_cached_title)

                    # Read data_quality from stored JSON (written at score time).
                    # For older records that pre-date data_quality storage, infer from scores.
                    if isinstance(analysis_payload, dict) and 'data_quality' in analysis_payload:
                        cached_dq = analysis_payload['data_quality']
                    else:
                        # Legacy record — infer: if profitability=0, data was partial/estimated
                        cached_prof_col = float(score_row.get('profitability_score') or 0)
                        if cached_prof_col == 0:
                            cached_dq = 'estimated'
                        else:
                            cached_dq = 'full'

                    normalized_cached = {
                        "asin": asin,
                        "title": cached_title,
                        "profitability_score": pick_score(score_row.get('profitability_score'), 'profitability'),
                        "demand_score": pick_score(score_row.get('demand_score'), 'demand'),
                        "stability_score": pick_score(score_row.get('stability_score'), 'stability'),
                        "buybox_winability_score": pick_score(score_row.get('buybox_winability_score'), 'buybox_winability'),
                        "oos_risk_score": pick_score(score_row.get('oos_risk_score'), 'oos_risk'),
                        "supply_gap_score": pick_score(score_row.get('supply_gap_score'), 'supply_gap'),
                        "non_seasonal_score": pick_score(score_row.get('non_seasonal_score'), 'non_seasonal'),
                        "overall_score": float(overall_score or 0),
                        "analysis_data": raw_analysis,
                        "calculated_at": score_row.get('calculated_at'),
                        "data_quality": cached_dq
                    }

                    # Recompute weak legacy cache rows when raw data has enough signals
                    converted_product = convert_keepa_product(product, rank_position=asin_rank_map.get(asin))
                    if is_weak_cached_score(normalized_cached) and converted_product.get('_has_minimum_data'):
                        try:
                            score_result = analyzer.analyze_asin(converted_product)
                            score_result['data_quality'] = converted_product.get('_data_quality', 'full')
                            resolved_title = resolve_title(asin, score_result.get('title'))
                            score_result['title'] = resolved_title
                            save_product_analysis_scores(db, asin, score_result)
                            scored_results.append({
                                "asin": asin,
                                "title": resolved_title,
                                "profitability_score": score_result.get('dimensions', {}).get('profitability', {}).get('score', 0),
                                "demand_score": score_result.get('dimensions', {}).get('demand', {}).get('score', 0),
                                "stability_score": score_result.get('dimensions', {}).get('stability', {}).get('score', 0),
                                "buybox_winability_score": score_result.get('dimensions', {}).get('buybox_winability', {}).get('score', 0),
                                "oos_risk_score": score_result.get('dimensions', {}).get('oos_risk', {}).get('score', 0),
                                "supply_gap_score": score_result.get('dimensions', {}).get('supply_gap', {}).get('score', 0),
                                "non_seasonal_score": score_result.get('dimensions', {}).get('non_seasonal', {}).get('score', 0),
                                "overall_score": score_result.get('overall_score', 0),
                                "analysis_data": json.dumps(score_result),
                                "calculated_at": datetime.now().isoformat(),
                                "data_quality": score_result.get('data_quality', 'full')
                            })
                        except Exception as e:
                            logger.warning(f"Failed to recompute weak cache for {asin}: {e}")
                            scored_results.append(normalized_cached)
                    elif is_weak_cached_score(normalized_cached) and not converted_product.get('_has_minimum_data'):
                        # Still include — asin_rank_map should have provided a rank estimate
                        scored_results.append(normalized_cached)
                    else:
                        scored_results.append(normalized_cached)
                else:
                    # Score the product
                    try:
                        rank_pos = asin_rank_map.get(asin)
                        converted_product = convert_keepa_product(product, rank_position=rank_pos)
                        if not converted_product.get('_has_minimum_data'):
                            # No data and not in bestseller list at all — skip
                            continue

                        score_result = analyzer.analyze_asin(converted_product)
                        dq = converted_product.get('_data_quality', 'full')
                        score_result['data_quality'] = dq

                        # Resolve title first, then save — so analysis_data has the real title
                        resolved_title = resolve_title(asin, score_result.get('title'))
                        score_result['title'] = resolved_title
                        save_product_analysis_scores(db, asin, score_result)

                        scored_results.append({
                            "asin": asin,
                            "title": resolved_title,
                            "profitability_score": score_result.get('dimensions', {}).get('profitability', {}).get('score', 0),
                            "demand_score": score_result.get('dimensions', {}).get('demand', {}).get('score', 0),
                            "stability_score": score_result.get('dimensions', {}).get('stability', {}).get('score', 0),
                            "buybox_winability_score": score_result.get('dimensions', {}).get('buybox_winability', {}).get('score', 0),
                            "oos_risk_score": score_result.get('dimensions', {}).get('oos_risk', {}).get('score', 0),
                            "supply_gap_score": score_result.get('dimensions', {}).get('supply_gap', {}).get('score', 0),
                            "non_seasonal_score": score_result.get('dimensions', {}).get('non_seasonal', {}).get('score', 0),
                            "overall_score": score_result.get('overall_score', 0),
                            "analysis_data": json.dumps(score_result),
                            "calculated_at": datetime.now().isoformat(),
                            "data_quality": dq
                        })
                    except Exception as e:
                        logger.warning(f"Failed to score {asin}: {e}")
                        continue
        
        scored_results.sort(key=lambda x: float(x.get('overall_score') or 0), reverse=True)
        scored_results = scored_results[:limit]

        return {
            "category_id": category_id,
            "total_available": total_available,
            "fetched": len(asins_to_fetch),
            "scored": len(scored_results),
            "from_cache": from_cache,
            "last_synced": last_synced,
            "next_sync": next_sync,
            "token_cost": token_cost,
            "results": scored_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing bestsellers for {category_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/{category_id}/research")
async def get_category_research(
    category_id: str,
    limit: int = 50,
    force_refresh: bool = False,
):
    """
    Clean product research endpoint — returns raw, reliable Keepa data per ASIN.
    No complex scoring. Just the facts a seller needs:
    price, BSR, reviews, rating, Amazon competing, FBA fees, brand, price trend.
    """
    from app.keepa_client import get_client
    from app.db import get_conn, get_category_products_from_cache
    import time as _time

    logger.info(f"[research] category={category_id} limit={limit}")
    start = _time.time()

    def _csv_latest(series, divisor=1.0):
        """Return the most recent non-(-1) value from a Keepa CSV series."""
        if not isinstance(series, list) or not series:
            return None
        # Nested [[ts,val], ...]
        if isinstance(series[-1], list):
            for entry in reversed(series):
                if isinstance(entry, list) and len(entry) >= 2 and entry[1] != -1:
                    return float(entry[1]) / divisor
            return None
        # Flat [ts, val, ts, val, ...]
        for i in range(len(series) - 1, -1, -1):
            if i % 2 == 1 and series[i] != -1:
                return float(series[i]) / divisor
        return None

    def _csv_avg(series, divisor=1.0, last_n=60):
        """Average of last_n non-(-1) values (pairs) from a flat/nested series."""
        if not isinstance(series, list) or not series:
            return None
        vals = []
        if isinstance(series[-1], list):
            for entry in reversed(series):
                if isinstance(entry, list) and len(entry) >= 2 and entry[1] != -1:
                    vals.append(float(entry[1]) / divisor)
                    if len(vals) >= last_n:
                        break
        else:
            for i in range(len(series) - 1, -1, -1):
                if i % 2 == 1 and series[i] != -1:
                    vals.append(float(series[i]) / divisor)
                    if len(vals) >= last_n:
                        break
        return round(sum(vals) / len(vals), 2) if vals else None

    def _stats_val(stats, key, index, divisor=1.0):
        arr = stats.get(key) if stats else None
        if isinstance(arr, list) and len(arr) > index and arr[index] not in (-1, None):
            return float(arr[index]) / divisor
        return None

    def _estimate_monthly_sales(bsr):
        """Rough monthly sales estimate for Amazon India Toys category by BSR."""
        if not bsr or bsr <= 0:
            return None
        if bsr <= 100:    return 800
        if bsr <= 500:    return 400
        if bsr <= 2000:   return 150
        if bsr <= 5000:   return 60
        if bsr <= 10000:  return 25
        if bsr <= 30000:  return 10
        if bsr <= 100000: return 4
        return 1

    def _opportunity(bsr, reviews, price, amazon_competing):
        """Simple, transparent 3-level opportunity rating."""
        reasons = []
        if amazon_competing:    reasons.append("Amazon on buy box")
        if reviews and reviews > 3000: reasons.append("High review barrier")
        if price and price > 3500:     reasons.append("Risky price for India")
        if bsr and bsr > 80000:        reasons.append("Very low demand")

        # Hard avoids
        if bsr and bsr > 80000:
            return {"label": "AVOID", "color": "#ef4444", "reason": "Very low demand (BSR > 80k)"}
        if price and price > 3500:
            return {"label": "AVOID", "color": "#ef4444", "reason": "Risky price point for India"}

        # Green: good demand + low review barrier + not dominated by Amazon
        if (not amazon_competing
                and bsr and bsr <= 5000
                and (not reviews or reviews < 200)
                and (price and 400 <= price <= 2000)):
            return {"label": "BUY ✓", "color": "#22c55e", "reason": "Low competition + strong demand + good price"}

        # Green even with some reviews if demand is very strong
        if (not amazon_competing
                and bsr and bsr <= 2000
                and (not reviews or reviews < 500)):
            return {"label": "BUY ✓", "color": "#22c55e", "reason": "Strong demand + Amazon not competing"}

        # Amber: decent opportunity
        if not amazon_competing and bsr and bsr <= 20000:
            return {"label": "ANALYSE", "color": "#f59e0b",
                    "reason": f"Decent demand" + (f", {reviews:,} reviews" if reviews else "")}

        # Amazon competing but good demand — still worth knowing
        if amazon_competing and bsr and bsr <= 10000:
            return {"label": "WATCH", "color": "#818cf8",
                    "reason": "Amazon competing — monitor for gaps or price opportunities"}

        if not amazon_competing:
            return {"label": "ANALYSE", "color": "#f59e0b", "reason": "Moderate opportunity"}

        return {"label": "AVOID", "color": "#ef4444", "reason": "; ".join(reasons) or "Low opportunity"}

    try:
        client = get_client()
        db = get_conn()

        # ── Step 1: get bestseller ASINs ──────────────────────────────────────
        fetch_limit = min(limit, 100)
        try:
            all_asins = client.best_sellers_query(
                category=category_id, domain='IN', wait=False
            )
        except Exception as e:
            if 'NOT_ENOUGH_TOKEN' in str(e):
                all_asins = get_category_products_from_cache(db, category_id, fetch_limit)
            else:
                raise

        asins = (all_asins or [])[:fetch_limit]
        if not asins:
            return {"category_id": category_id, "products": [], "count": 0, "elapsed": 0}

        # ── Step 2: query Keepa for product details ──────────────────────────
        try:
            raw = client.query(asins, stats=180, rating=1, wait=False, domain='IN')
            keepa_map = {p["asin"]: p for p in raw if p and p.get("asin")}
        except Exception as e:
            if 'NOT_ENOUGH_TOKEN' in str(e):
                keepa_map = {}
            else:
                raise

        # ── Step 3: build clean result per ASIN ──────────────────────────────
        products = []
        for rank_idx, asin in enumerate(asins):
            p = keepa_map.get(asin, {})
            csv = p.get("csv") if isinstance(p.get("csv"), list) else []
            stats = p.get("stats") or {}

            # Price — try Amazon price (csv[0]), then marketplace price (csv[1]), then stats
            price = _csv_latest(csv[0], 100.0) if len(csv) > 0 else None
            if not price:
                price = _csv_latest(csv[1], 100.0) if len(csv) > 1 else None
            if not price:
                price = (_stats_val(stats, "avg30", 0, 100.0)
                         or _stats_val(stats, "avg30", 1, 100.0)
                         or _stats_val(stats, "avg", 0, 100.0)
                         or _stats_val(stats, "avg", 1, 100.0))
            price_30d = (_stats_val(stats, "avg30", 0, 100.0)
                         or _stats_val(stats, "avg30", 1, 100.0)
                         or (_csv_avg(csv[0], 100.0, 30) if len(csv) > 0 else None)
                         or (_csv_avg(csv[1], 100.0, 30) if len(csv) > 1 else None))
            price_90d = (_stats_val(stats, "avg90", 0, 100.0)
                         or _stats_val(stats, "avg90", 1, 100.0))

            # Price trend
            price_trend = "stable"
            if price and price_30d:
                diff_pct = ((price - price_30d) / price_30d) * 100
                if diff_pct > 5:   price_trend = "up"
                elif diff_pct < -5: price_trend = "down"

            # BSR
            bsr = _stats_val(stats, "current", 3) or (_csv_latest(csv[3]) if len(csv) > 3 else None)

            # Rating & reviews  (stats.current[16]=rating*10, [17]=reviews)
            rating = _stats_val(stats, "current", 16, 10.0)
            reviews = _stats_val(stats, "current", 17)
            if not rating:
                rating = _csv_latest(csv[16], 10.0) if len(csv) > 16 else None
            if not reviews:
                reviews = _csv_latest(csv[17]) if len(csv) > 17 else None

            # Amazon competing: buyBoxIsAmazon flag (Keepa returns True or 1)
            # also check if csv[0] (Amazon retail price) has a recent non-(-1) value
            bba = stats.get("buyBoxIsAmazon")
            amazon_competing = bool(bba)  # True/1 = Amazon on buy box
            if not amazon_competing and len(csv) > 0:
                az_price = _csv_latest(csv[0], 100.0)
                amazon_competing = bool(az_price and az_price > 0)

            # Title + brand
            title = (p.get("title") or "").strip() or f"ASIN {asin}"
            brand = (p.get("brand") or "").strip() or None

            # FBA fees
            fba_fees_raw = p.get("fbaFees") or {}
            fba_fee = None
            if fba_fees_raw:
                fba_fee = round((fba_fees_raw.get("pickAndPackFee") or 0) / 100.0, 2) or None

            # Referral fee (Amazon India Toys = 9%)
            referral_pct = 9.0
            referral_fee = round(price * referral_pct / 100, 2) if price else None

            # Estimated monthly sales
            monthly_sales = _estimate_monthly_sales(int(bsr) if bsr else None)

            # Simple opportunity
            opp = _opportunity(
                bsr=int(bsr) if bsr else None,
                reviews=int(reviews) if reviews else None,
                price=price,
                amazon_competing=amazon_competing,
            )

            products.append({
                "rank":              rank_idx + 1,
                "asin":              asin,
                "title":             title,
                "brand":             brand,
                "price":             round(price, 2) if price else None,
                "price_30d_avg":     round(price_30d, 2) if price_30d else None,
                "price_90d_avg":     round(price_90d, 2) if price_90d else None,
                "price_trend":       price_trend,
                "bsr":               int(bsr) if bsr else None,
                "rating":            round(rating, 1) if rating else None,
                "reviews":           int(reviews) if reviews else None,
                "amazon_competing":  amazon_competing,
                "fba_fee":           fba_fee,
                "referral_fee":      referral_fee,
                "monthly_sales_est": monthly_sales,
                "opportunity":       opp,
                "has_data":          bool(p),
            })

        # sort: BUY first, then by BSR ascending (=highest demand first)
        label_order = {"BUY ✓": 0, "ANALYSE": 1, "WATCH": 2, "AVOID": 3}
        products.sort(key=lambda x: (
            label_order.get(x["opportunity"]["label"], 1),
            x["bsr"] if x["bsr"] else 999999
        ))

        elapsed = round(_time.time() - start, 2)
        return {
            "category_id": category_id,
            "count": len(products),
            "elapsed": elapsed,
            "products": products,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[research] error for {category_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
                product_data_list = client.query(asin_list, domain='IN')
                
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

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, constr
from typing import List, Optional, Dict, Any
import requests
import os
import logging
import json

from app import config
from app.db import (
    get_conn,
    list_selected_categories,
    replace_selected_categories,
    get_top5,
    get_latest_metrics,
    upsert_products,
    upsert_daily_metrics,
)
from app.keepa_client import get_client
from app.sourcing import run_sourcing
from app.scoring import score_breakdown
from app.ai import generate_ai_summary
from app.auth import (
    create_access_token,
    create_user,
    decode_token,
    get_user_by_username,
    verify_password,
)
from app.category_analysis import router as category_router

app = FastAPI(title="Amazon Sourcing Engine", version="1.0")

# Register category analysis router
app.include_router(category_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

auth_scheme = HTTPBearer()


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if config.AUTH_DISABLED:
        return {"sub": "local"}
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


class CategoryIn(BaseModel):
    category_id: int
    name: str


class CategoryList(BaseModel):
    categories: List[CategoryIn]


class LoginRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=64)
    password: constr(min_length=8, max_length=128)


class BatchAnalyzeRequest(BaseModel):
    asinList: List[str]
    domain: int = 1
    minRating: float = 4.0
    minSalesRank: int = 1000
    maxPrice: int = 999999


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "API is running",
        "docs": "/docs",
        "health": "/health",
        "ui": "/ui/index.html"
    }


app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="ui")


@app.get("/keepa/health")
def keepa_health():
    try:
        client = get_client()
        return {
            "status": "ok",
            "tokens_left": client.tokens_left,
            "refill_in_ms": client.status.get("refillIn"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/auth/register")
def register(payload: LoginRequest):
    existing = get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user_id = create_user(payload.username, payload.password)
    token = create_access_token({"sub": payload.username, "uid": user_id})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login")
def login(payload: LoginRequest):
    user = get_user_by_username(payload.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id, username, password_hash = user[0], user[1], user[2]
    if not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username, "uid": user_id})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/categories")
def get_categories(_: dict = Depends(require_auth)):
    conn = get_conn()
    rows = list_selected_categories(conn)
    conn.close()
    return [{"category_id": r[0], "name": r[1]} for r in rows]


@app.post("/categories")
def set_categories(payload: CategoryList, _: dict = Depends(require_auth)):
    conn = get_conn()
    replace_selected_categories(conn, [(c.category_id, c.name) for c in payload.categories])
    conn.close()
    return {"status": "updated", "count": len(payload.categories)}


@app.post("/run")
def run_now(
    bsr_threshold: Optional[int] = None,
    max_fba_offers: Optional[int] = None,
    cv_threshold: Optional[float] = None,
    _: dict = Depends(require_auth),
):
    conn = get_conn()
    categories = list_selected_categories(conn)
    conn.close()

    if not categories:
        raise HTTPException(status_code=400, detail="No categories selected")

    client = get_client()
    bsr_threshold = bsr_threshold or config.DEFAULT_BSR_THRESHOLD
    max_fba_offers = max_fba_offers or config.DEFAULT_MAX_FBA_OFFERS
    cv_threshold = cv_threshold or config.DEFAULT_CV_THRESHOLD

    product_rows, metric_rows = run_sourcing(
        client,
        categories,
        bsr_threshold=bsr_threshold,
        max_fba_offers=max_fba_offers,
        cv_threshold=cv_threshold,
    )

    conn = get_conn()
    upsert_products(conn, product_rows)
    upsert_daily_metrics(conn, metric_rows)
    conn.close()

    return {"status": "ok", "products": len(product_rows)}


@app.get("/top5")
def top5(category_id: Optional[str] = None, _: dict = Depends(require_auth)):
    conn = get_conn()
    rows = get_top5(conn, category_id)
    conn.close()
    keys = [
        "asin",
        "title",
        "brand",
        "category",
        "snapshot_date",
        "bsr",
        "buy_box_price_cents",
        "avg90_buy_box_price_cents",
        "new_fba_offer_count",
        "amazon_in_stock",
        "bsr_slope_30d",
        "price_volatility_cv",
        "confidence_score",
    ]
    return [dict(zip(keys, r)) for r in rows]


@app.get("/explain/{asin}")
def explain(asin: str, _: dict = Depends(require_auth)):
    conn = get_conn()
    row = get_latest_metrics(conn, asin)
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="ASIN not found")

    bsr, buy_box, avg90, fba_count, amazon_in_stock, bsr_slope_30d, cv, score = row
    breakdown = score_breakdown(bsr, bsr_slope_30d, cv, fba_count, not amazon_in_stock)
    summary = generate_ai_summary(score, breakdown) if config.AI_EXPLANATIONS_ENABLED else ""

    return {
        "asin": asin,
        "confidence_score": score,
        "breakdown": breakdown,
        "ai_summary": summary,
    }


@app.post("/keepa/product-finder")
def product_finder(request: Optional[Dict[str, Any]] = None):
    """Endpoint to query Keepa's Product Finder API (Search endpoint).
    
    Searches the Keepa database for products matching specified criteria.
    
    Token Cost: 10 base + 1 per 100 ASINs returned (optional +30 for stats)
    
    Request format:
    {
        "domain": 10,
        "selection": {
            "page": 0,
            "perPage": 50,
            "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
            "categories_include": [3010075031],
            "current_AMAZON_gte": 1000,
            "current_AMAZON_lte": 50000,
            "monthlySold_gte": 100,
            "brand": ["Canon", "Nikon"]
        },
        "stats": false
    }
    
    Common filters:
    - current_AMAZON_gte/lte: Price range (cents)
    - current_SALES_gte/lte: Sales rank range
    - monthlySold_gte/lte: Monthly sales volume
    - brand: Brand names
    - categories_include: Category IDs
    - isLowest: Current lowest price ever
    - hasReviews: Must have reviews
    - buyBoxIsAmazon: Amazon holds buy box
    
    See KEEPA_QUERY_FORMAT.md for all 200+ filter options.
    
    Returns:
    {
        "asinList": [list of ASINs],
        "totalResults": total count,
        "searchInsights": {...},  # if stats=true
        "tokensLeft": remaining,
        "processingTimeInMs": time
    }
    """
    logger = logging.getLogger(__name__)
    
    keepa_api_key = os.getenv("KEEPA_API_KEY")
    if not keepa_api_key:
        raise HTTPException(status_code=500, detail="Keepa API key not configured.")

    # Default selection if not provided
    if not request:
        request = {}
    
    selection = request.get("selection", {
        "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
        "productType": [0, 1, 2],
        "perPage": 50,
        "page": 0
    })
    
    domain = request.get("domain", 1)  # 1 = US Amazon
    stats = request.get("stats", False)  # Optional search insights
    
    # Format the API request - Keepa requires selection as JSON string
    url = "https://api.keepa.com/query"
    selection_json = json.dumps(selection)
    
    params = {
        "key": keepa_api_key,
        "domain": domain,
        "selection": selection_json
    }
    
    if stats:
        params["stats"] = "1"

    logger.info(f"Keepa Product Finder request - domain: {domain}, stats: {stats}")
    logger.info(f"Selection: {selection}")

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        logger.info(f"Keepa query response - Status: {response.status_code}")
        logger.info(f"ASINs returned: {len(data.get('asinList', []))}")
        logger.info(f"Total results: {data.get('totalResults', 0)}")
        
        if "error" in data:
            error_detail = data.get("error", {})
            error_msg = error_detail.get("message", "Unknown error")
            logger.error(f"Keepa API error: {error_msg}")
            raise HTTPException(status_code=400, detail=f"Keepa API error: {error_msg}")
        
        asin_list = data.get("asinList", [])
        
        # Build response matching Keepa's format
        response_data = {
            "asinList": asin_list,
            "totalResults": data.get("totalResults", 0),
            "tokensLeft": data.get("tokensLeft", 0),
            "processingTimeInMs": data.get("processingTimeInMs", 0),
            "timestamp": data.get("timestamp", 0),
            "refillIn": data.get("refillIn", 0)
        }
        
        # Include search insights if available
        if "searchInsights" in data and data["searchInsights"]:
            response_data["searchInsights"] = data["searchInsights"]
        
        return response_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Keepa API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying Keepa API: {str(e)}")


@app.get("/keepa/category")
def get_category(domain: int = 1, category_id: int = 0, include_parents: int = 1):
    """Endpoint to fetch Keepa category tree.
    
    Args:
        domain: Amazon domain ID (1=US, 8=India, etc.)
        category_id: Category node ID (0 for root categories)
        include_parents: Include parent categories (1=yes, 0=no)
    """
    keepa_api_key = os.getenv("KEEPA_API_KEY")
    if not keepa_api_key:
        raise HTTPException(status_code=500, detail="Keepa API key not configured.")

    url = "https://api.keepa.com/category"
    params = {
        "key": keepa_api_key,
        "domain": domain,
        "category": category_id,
        "parents": include_parents
    }

    logger = logging.getLogger(__name__)
    logger.info(f"Keepa Category request - domain: {domain}, category_id: {category_id}")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Keepa Category response received")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Keepa Category API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying Keepa Category API: {str(e)}")


@app.post("/keepa/batch-analyze")
def batch_analyze_products(request_body: BatchAnalyzeRequest):
    """Batch fetch and analyze product details for multiple ASINs.
    
    🎯 7-DAY CACHE STRATEGY:
    1. Check database first (0 tokens if cached & fresh)
    2. Fetch from Keepa only for missing/stale ASINs (1 token each)
    3. Store all 70 fields in database for 7 days
    
    CSV Array Indices:
    - CSV[0]: Amazon price history [[timestamp, price], ...]
    - CSV[3]: Sales rank history [[timestamp, rank], ...]
    - CSV[16]: Rating history (×10) [[timestamp, rating*10], ...]
    - CSV[17]: Review count [[timestamp, count], ...]
    """
    logger = logging.getLogger(__name__)
    import time
    start_time = time.time()
    
    from app.keepa_cache import get_cached_products, save_keepa_product
    
    keepa_api_key = os.getenv("KEEPA_API_KEY")
    if not keepa_api_key:
        raise HTTPException(status_code=500, detail="Keepa API key not configured.")
    
    asin_list = request_body.asinList
    domain = request_body.domain
    min_rating = request_body.minRating
    min_sales_rank = request_body.minSalesRank
    max_price = request_body.maxPrice
    
    if not asin_list:
        raise HTTPException(status_code=400, detail="asinList cannot be empty")
    
    if len(asin_list) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 ASINs per request")
    
    # STEP 1: Check database cache first
    conn = get_conn()
    cached_products, missing_asins = get_cached_products(conn, asin_list, domain)
    
    logger.info(f"Cache: {len(cached_products)} cached, {len(missing_asins)} need fetching")
    
    products_analyzed = []
    tokens_left = 0
    tokens_used_total = 0
    skipped = []
    cache_hits = len(cached_products)
    api_fetches = 0
    
    # STEP 2: Process cached products (0 tokens!)
    for product in cached_products:
        try:
            # Product already has extracted metrics from cache
            current_price_dollars = product.get('currentPrice', 0)
            sales_rank = product.get('currentSalesRank', 0)
            rating = product.get('currentRating', 0)
            review_count = product.get('currentReviewCount', 0)
            
            # Apply filters
            if rating and rating < min_rating:
                logger.debug(f"[CACHED] {product['asin']}: Rating {rating} < {min_rating}")
                skipped.append((product['asin'], f"low_rating:{rating}"))
                continue
            
            if sales_rank and sales_rank > min_sales_rank:
                logger.debug(f"[CACHED] {product['asin']}: Rank {sales_rank} > {min_sales_rank}")
                skipped.append((product['asin'], f"high_rank:{sales_rank}"))
                continue
            
            if current_price_dollars and current_price_dollars > max_price:
                logger.debug(f"[CACHED] {product['asin']}: Price ${current_price_dollars} > ${max_price}")
                skipped.append((product['asin'], f"high_price:{current_price_dollars}"))
                continue
            
            # Calculate scores (same logic as before)
            if current_price_dollars == 0:
                current_price_dollars = max_price * 0.5
            
            profitability_score = min(100, (max_price / current_price_dollars * 100)) if current_price_dollars > 0 else 50
            demand_score = 50
            if sales_rank:
                demand_score = min(100, max(0, ((min_sales_rank - sales_rank) / min_sales_rank) * 100))
            
            quality_score = 50
            if rating:
                quality_score = (rating / 5.0) * 100
            
            risk_score = 0
            if review_count is not None:
                risk_score = min(100, (review_count / 100))
            
            overall_score = (
                profitability_score * 0.40 +
                demand_score * 0.35 +
                quality_score * 0.20 +
                risk_score * 0.05
            )
            
            if overall_score >= 80:
                recommendation = "🟢 STRONG"
            elif overall_score >= 70:
                recommendation = "🟡 MODERATE"
            else:
                recommendation = "🔴 WEAK"
            
            products_analyzed.append({
                "asin": product['asin'],
                "title": product.get('title', 'Unknown')[:70],
                "brand": product.get('brand', 'Unknown'),
                "currentPrice": round(current_price_dollars, 2),
                "rating": round(rating, 1) if rating else 0,
                "reviewCount": review_count or 0,
                "salesRank": sales_rank or 0,
                "profitabilityScore": round(profitability_score, 1),
                "demandScore": round(demand_score, 1),
                "qualityScore": round(quality_score, 1),
                "riskScore": round(risk_score, 1),
                "overallScore": round(overall_score, 1),
                "recommendation": recommendation,
                "imageUrl": f"https://images-na.ssl-images-amazon.com/images/I/{product.get('imagesCSV', '').split(',')[0]}" if product.get('imagesCSV') else "",
                "source": "cache"  # Mark as from cache
            })
            
        except Exception as e:
            logger.error(f"Error processing cached product: {str(e)}")
            continue
    
    # STEP 3: Fetch missing ASINs from Keepa API (costs tokens)
    logger.info(f"Fetching {len(missing_asins)} ASINs from Keepa API")
    
    for idx, asin in enumerate(missing_asins, 1):
        try:
            # Fetch product details from Keepa
            url = "https://api.keepa.com/product"
            params = {
                "key": keepa_api_key,
                "domain": domain,
                "asin": asin,
                "meta": 1  # Get full metadata
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Track tokens
            tokens_used_this = data.get("tokensConsumed", 1)
            tokens_left = data.get("tokensLeft", 0)
            tokens_used_total += tokens_used_this
            api_fetches += 1
            
            if "products" not in data or len(data["products"]) == 0:
                logger.warning(f"[{idx}/{len(missing_asins)}] {asin}: No product data")
                skipped.append((asin, "no_data"))
                continue
            
            product = data["products"][0]
            
            # STEP 4: Save to database cache (all 70 fields)
            save_keepa_product(conn, product, domain)
            
            # Extract basic info
            title = product.get("title") or product.get("parentTitle") or "Unknown"
            brand = product.get("brand", "Unknown")
            asin_from_api = product.get("asin", asin)
            
            # Extract metrics from CSV array
            current_price = None
            sales_rank = None
            rating = None
            review_count = None
            
            csv_array = product.get("csv")
            if csv_array and isinstance(csv_array, list):
                # CSV[0]: Amazon price
                if len(csv_array) > 0 and csv_array[0]:
                    price_history = csv_array[0]
                    if isinstance(price_history, list) and len(price_history) > 0:
                        latest = price_history[-1]
                        if isinstance(latest, list) and len(latest) >= 2 and latest[1] != -1:
                            current_price = latest[1]  # Price in cents
                        elif isinstance(latest, (int, float)) and latest != -1:
                            current_price = int(latest)
                
                # CSV[3]: Sales rank
                if len(csv_array) > 3 and csv_array[3]:
                    rank_history = csv_array[3]
                    if isinstance(rank_history, list) and len(rank_history) > 0:
                        latest = rank_history[-1]
                        if isinstance(latest, list) and len(latest) >= 2 and latest[1] != -1:
                            sales_rank = int(latest[1])
                        elif isinstance(latest, (int, float)) and latest != -1:
                            sales_rank = int(latest)
                
                # CSV[16]: Rating (stored as rating * 10)
                if len(csv_array) > 16 and csv_array[16]:
                    rating_history = csv_array[16]
                    if isinstance(rating_history, list) and len(rating_history) > 0:
                        latest = rating_history[-1]
                        if isinstance(latest, list) and len(latest) >= 2 and latest[1] != -1:
                            rating = int(latest[1]) / 10.0
                        elif isinstance(latest, (int, float)) and latest != -1:
                            rating = int(latest) / 10.0
                
                # CSV[17]: Review count
                if len(csv_array) > 17 and csv_array[17]:
                    review_history = csv_array[17]
                    if isinstance(review_history, list) and len(review_history) > 0:
                        latest = review_history[-1]
                        if isinstance(latest, list) and len(latest) >= 2 and latest[1] != -1:
                            review_count = int(latest[1])
                        elif isinstance(latest, (int, float)) and latest != -1:
                            review_count = int(latest)
            
            # Apply filters
            if rating is not None and rating < min_rating:
                logger.debug(f"[{idx}] {asin}: Rating {rating} < {min_rating}")
                skipped.append((asin, f"low_rating:{rating}"))
                continue
            
            if sales_rank is not None and sales_rank > min_sales_rank:
                logger.debug(f"[{idx}] {asin}: Rank {sales_rank} > {min_sales_rank}")
                skipped.append((asin, f"high_rank:{sales_rank}"))
                continue
            
            if current_price is not None and current_price / 100.0 > max_price:
                logger.debug(f"[{idx}] {asin}: Price ${current_price/100} > ${max_price}")
                skipped.append((asin, f"high_price:{current_price/100}"))
                continue
            
            # If no price data but has other data, use fallback
            if current_price is None:
                logger.debug(f"[{idx}] {asin}: No price data, using fallback")
                current_price_dollars = max_price * 0.5
            else:
                current_price_dollars = current_price / 100.0
            
            # Calculate scores
            profitability_score = min(100, (max_price / current_price_dollars * 100)) if current_price_dollars > 0 else 50
            
            demand_score = 50  # Default
            if sales_rank:
                demand_score = min(100, max(0, ((min_sales_rank - sales_rank) / min_sales_rank) * 100))
            
            quality_score = 50  # Default
            if rating:
                quality_score = (rating / 5.0) * 100
            
            risk_score = 0  # Default (no reviews = max risk)
            if review_count is not None:
                risk_score = min(100, (review_count / 100))
            
            # Overall weighted score
            overall_score = (
                profitability_score * 0.40 +
                demand_score * 0.35 +
                quality_score * 0.20 +
                risk_score * 0.05
            )
            
            # Recommendation
            if overall_score >= 80:
                recommendation = "🟢 STRONG"
            elif overall_score >= 70:
                recommendation = "🟡 MODERATE"
            else:
                recommendation = "🔴 WEAK"
            
            # Image URL
            image_url = ""
            if product.get("imagesCSV"):
                first_image = product["imagesCSV"].split(",")[0].strip()
                if first_image:
                    image_url = f"https://images-na.ssl-images-amazon.com/images/I/{first_image}"
            
            products_analyzed.append({
                "asin": asin_from_api,
                "title": title[:70] + "..." if len(title) > 70 else title,
                "brand": brand,
                "currentPrice": round(current_price_dollars, 2),
                "rating": round(rating, 1) if rating else 0,
                "reviewCount": review_count or 0,
                "salesRank": sales_rank or 0,
                "profitabilityScore": round(profitability_score, 1),
                "demandScore": round(demand_score, 1),
                "qualityScore": round(quality_score, 1),
                "riskScore": round(risk_score, 1),
                "overallScore": round(overall_score, 1),
                "recommendation": recommendation,
                "imageUrl": image_url,
                "source": "api"  # Mark as freshly fetched
            })
            
            logger.info(f"[{idx}/{len(missing_asins)}] ✅ {asin}: Score={overall_score:.1f}")
            
        except Exception as e:
            logger.error(f"[{idx}] Error analyzing {asin}: {str(e)}")
            skipped.append((asin, f"error:{str(e)[:20]}"))
            continue
    
    # Sort by score
    products_analyzed.sort(key=lambda x: x["overallScore"], reverse=True)
    
    processing_time = (time.time() - start_time) * 1000
    
    logger.info(f"Analysis complete: {len(products_analyzed)} analyzed, {len(skipped)} skipped")
    logger.info(f"Cache efficiency: {cache_hits} hits, {api_fetches} API calls, {tokens_used_total} tokens used")
    
    return {
        "products": products_analyzed,
        "totalAnalyzed": len(products_analyzed),
        "totalAsked": len(asin_list),
        "skipped": len(skipped),
        "cacheHits": cache_hits,
        "apiFetches": api_fetches,
        "tokensUsed": tokens_used_total,
        "tokensLeft": tokens_left,
        "analysisTimeMs": int(processing_time)
    }


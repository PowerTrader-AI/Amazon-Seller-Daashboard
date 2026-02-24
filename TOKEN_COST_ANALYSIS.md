# KEEPA API TOKEN COST ANALYSIS & PLAN

## 1. TOKEN COST CLARIFICATION

### best_sellers_query()
- **Cost:** 1 token PER CALL (not per ASIN)
- **Returns:** Up to 100,000 ASINs for ROOT categories, up to 3,000 ASINs for SUBCATEGORIES
- **Example:**
  - Marble Runs (subcategory): 1 token → Returns all 23,332 ASINs ✅
  - Toys & Games (root): 1 token → Returns top 100,000 ASINs (but pool has 3.19M total)

### query()
- **Cost:** 1 token per 100 ASINs (rounded up)
- **Returns:** 102 fields per product + 34 months CSV history
- **Example:**
  - Query 23,332 ASINs = ceil(23,332/100) = **234 tokens**
  - Query 100,000 ASINs = ceil(100,000/100) = **1,000 tokens**

---

## 2. WORKFLOW TOKEN COSTS

### Scenario A: Marble Runs Analysis (23,332 products)
```
Step 1: best_sellers_query(1378568031)     → 1 token
        Returns: 23,332 ASINs ✅ (all of them, < 100k limit)

Step 2: query(23,332_asins)                → 234 tokens
        Returns: All product data

TOTAL: 235 tokens
```

### Scenario B: Toys & Games Root Analysis (10,000 shown)
```
Step 1: best_sellers_query(1350388031)     → 1 token
        Returns: top 100,000 ASINs (shows top 10,000)

Step 2: query(top_10000_asins)             → 100 tokens
        Returns: All product data

TOTAL: 101 tokens
```

---

## 3. CURRENT ISSUE

### Problem
When you select Marble Runs (subcategory), the current code:
- Does NOT limit to that category
- Returns top products from ROOT (Toys & Games)
- Shows 10,000 items from wrong category pool

### Solution
Make `best_sellers_query()` accept the **actual selected category ID**:
```python
# WRONG (current):
asins = client.best_sellers_query("1350388031")  # Always root

# RIGHT (needed):
asins = client.best_sellers_query(selected_category_id)  # Use selected
```

---

## 4. ARCHITECTURE FIX NEEDED

### Endpoint: `/api/bestsellers/{category_id}`

```python
@app.get("/api/bestsellers/{category_id}")
def get_bestsellers(category_id: str, limit: int = 100):
    """
    Get best-selling products from ANY category (root or subcategory)
    
    Args:
        category_id: "1378568031" (Marble Runs), "1350388031" (Toys Root), etc.
        limit: How many top products to analyze (default 100)
    
    Returns:
        - For root categories: Top `limit` from 100,000 available
        - For subcategories: ALL products (if < 3,000 limit)
    
    Token cost:
        1 token for best_sellers_query
        ceil(fetched_asins / 100) tokens for query()
    """
    
    client = get_client()
    
    # Step 1: Get bestsellers list (1 token)
    all_asins = client.best_sellers_query(
        category=category_id,
        domain="IN",
        wait=True
    )
    
    # Step 2: Determine how many to fetch
    # If subcategory with < 3,000 items, get all
    # Otherwise, limit to specified number
    asins_to_fetch = all_asins[:limit]
    
    # Step 3: Query product details (tokens = ceil(len/100))
    products = client.query(asins_to_fetch, stats=180)
    
    # Step 4: Score each product
    analyzer = ProductAnalyzer()
    results = []
    for product in products:
        if product:
            score = analyzer.analyze_asin(product)
            results.append(score)
    
    return {
        "category_id": category_id,
        "total_available": len(all_asins),
        "fetched": len(asins_to_fetch),
        "scored": len(results),
        "results": results
    }
```

---

## 5. TOKEN TRACKING SYSTEM NEEDED

### Track per API call:
```python
{
    "service": "best_sellers_query",
    "timestamp": "2026-02-01T05:45:00Z",
    "category_id": "1378568031",
    "asins_returned": 23332,
    "tokens_used": 1,
    "domain": "IN"
},
{
    "service": "query",
    "timestamp": "2026-02-01T05:45:01Z",
    "asin_count": 100,
    "tokens_used": 1,
    "fields_requested": ["title", "brand", "price", "csv"],
    "avg_ms_per_product": 45
}
```

### Dashboard shows:
- Total tokens used (today, this week, all-time)
- Cost per service (best_sellers, query, category_lookup, etc.)
- Cost per category
- Trending queries
- Remaining tokens alert

---

## 6. IMPLEMENTATION PRIORITY

### Phase 1: Fix Subcategory Routing (FIRST - TODAY)
- [ ] Fix best-sellers endpoint to accept category_id parameter
- [ ] Ensure all subcategory products fetched when available
- [ ] Test with Marble Runs (should get all 23,332)

### Phase 2: Add Token Tracking (SECOND - TOMORROW)
- [ ] Add logging to each API call with token usage
- [ ] Create token_usage table in DB
- [ ] Build token dashboard tab

### Phase 3: Optimize Token Usage (LATER)
- [ ] Cache responses (24 hour expiry)
- [ ] Batch similar queries
- [ ] Alert when tokens low

---

## 7. COST ESTIMATE - MARBLE RUNS ANALYSIS

```
Scenario: User selects "Marble Runs" category

Step 1: best_sellers_query("1378568031")
        Returns: 23,332 products
        Cost: 1 token ✅

Step 2: query(all_23332_asins, stats=180)
        Returns: 102 fields + 34-month history each
        Cost: ceil(23,332 / 100) = 234 tokens

TOTAL COST: 235 tokens per full analysis
CURRENT BUDGET: 708 tokens remaining
ANALYSIS POSSIBLE: 3x before token depletion
```

---

## 8. KEY POINTS FOR USER

✅ **Good news:**
- best_sellers_query only costs 1 token, regardless of results
- Subcategories return all products (not limited to 100k)
- Marble Runs: all 23,332 products available

⚠️ **Cost consideration:**
- Querying all 23,332 products costs 234 tokens
- Querying 100,000 products costs 1,000 tokens
- Should probably limit analysis to "Top 100" or "Top 500"

💡 **Optimization:**
- Offer slider: "Analyze top X products (50, 100, 500, 1000)"
- Show token cost BEFORE analysis: "This will use ~50 tokens"
- Cache results so same query doesn't re-cost tokens

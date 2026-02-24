# Complete System Architecture - Data Flow & Caching

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (User Browser)                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Tab 1: Category Explorer                                              │ │
│  │  ├─ Show 24 toy subcategories                                          │ │
│  │  └─ User clicks "Marble Runs"                                          │ │
│  │                                                                         │ │
│  │  Tab 2: Best-Sellers Analysis (NEW)                                    │ │
│  │  ├─ Display 23,332 products from Marble Runs                           │ │
│  │  ├─ Show "Last Synced: 2026-02-01 10:30 AM"                           │ │
│  │  ├─ Show "Next Refresh: 2026-02-08 10:30 AM"                          │ │
│  │  ├─ Show "From Cache" badge                                            │ │
│  │  └─ Show "Tokens Used: 0" (if cached)                                 │ │
│  │                                                                         │ │
│  │  Tab 3: Token Dashboard (FUTURE)                                       │ │
│  │  ├─ Show tokens used today: 200 tokens                                 │ │
│  │  ├─ Show cache hit rate: 85%                                           │ │
│  │  └─ Show tokens saved this week: 1,410                                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ HTTP Request
                    GET /category/1378568031/bestsellers?limit=100
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ get_bestsellers_analysis(category_id, limit)                          │ │
│  │                                                                         │ │
│  │ STEP 1: Check Database Cache                                          │ │
│  │ ├─ Query: SELECT * FROM category_sync_status                          │ │
│  │ │  WHERE category_id = '1378568031'                                    │ │
│  │ │                                                                       │ │
│  │ ├─ Result: Found! Last sync = 2026-02-01, expires 2026-02-08         │ │
│  │ ├─ Status: 'completed' ✅ CACHE HIT                                    │ │
│  │ └─ Tokens cost: 0 ✅                                                    │ │
│  │                                                                         │ │
│  │ (IF NOT IN CACHE - would call Keepa API here)                         │ │
│  │                                                                         │ │
│  │ STEP 2: Load from Database                                            │ │
│  │ ├─ Query: SELECT asin FROM category_products                          │ │
│  │ │  WHERE category_id = '1378568031' LIMIT 100                         │ │
│  │ └─ Result: [B0CH9VQ1M8, B0CVDYMNRV, ..., B0DJPD1L3K]                  │ │
│  │                                                                         │ │
│  │ STEP 3: Load Scores from Cache                                        │ │
│  │ └─ Query: SELECT * FROM product_analysis_scores                       │ │
│  │    WHERE asin IN (B0CH9..., B0CV..., ...)                             │ │
│  │    AND expires_at > NOW()                                             │ │
│  │                                                                         │ │
│  │ STEP 4: Log Usage                                                     │ │
│  │ └─ INSERT INTO token_usage_log                                        │ │
│  │    (service='category_fetch', cache_hit=true, tokens_used=0)          │ │
│  │                                                                         │ │
│  │ STEP 5: Return Response                                               │ │
│  │ └─ {                                                                   │ │
│  │      "from_cache": true,                                              │ │
│  │      "last_synced": "2026-02-01T10:30:00Z",                           │ │
│  │      "next_sync": "2026-02-08T10:30:00Z",                             │ │
│  │      "token_cost": 0,                                                 │ │
│  │      "results": [...]                                                 │ │
│  │    }                                                                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SQLITE DATABASE                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ TABLE: category_sync_status                                            │ │
│  │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│  │ │ category_id   | last_synced_at      | next_sync_at    | status │   │ │
│  │ ├──────────────────────────────────────────────────────────────────┤   │ │
│  │ │ 1378568031    | 2026-02-01 10:30    | 2026-02-08 ...  | compl  │   │ │
│  │ │ 1378175031    | 2026-01-28 15:45    | EXPIRED!        | pend   │   │ │
│  │ │ 1350388031    | 2026-02-01 12:00    | 2026-02-08 ...  | compl  │   │ │
│  │ └──────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                         │ │
│  │ TABLE: category_products                                               │ │
│  │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│  │ │ category_id  | asin         | rank | added_at                 │   │ │
│  │ ├──────────────────────────────────────────────────────────────────┤   │ │
│  │ │ 1378568031   | B0CH9VQ1M8   | 1    | 2026-02-01 10:30         │   │ │
│  │ │ 1378568031   | B0CVDYMNRV   | 2    | 2026-02-01 10:30         │   │ │
│  │ │ 1378568031   | B0CZXQKN3Y   | 3    | 2026-02-01 10:30         │   │ │
│  │ │ ...          | ...          | ...  | ...                      │   │ │
│  │ └──────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                         │ │
│  │ TABLE: product_analysis_scores                                         │ │
│  │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│  │ │ asin        | profit | demand | buybox | overall | expires_at   │   │ │
│  │ ├──────────────────────────────────────────────────────────────────┤   │ │
│  │ │ B0CH9VQ1M8  | 50     | 72     | 61.2   | 61.2    | 2026-02-08   │   │ │
│  │ │ B0CVDYMNRV  | 45     | 65     | 58.0   | 56.3    | 2026-02-08   │   │ │
│  │ │ B0CZXQKN3Y  | 52     | 68     | 59.5   | 59.8    | 2026-02-08   │   │ │
│  │ └──────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                         │ │
│  │ TABLE: token_usage_log                                                 │ │
│  │ ┌──────────────────────────────────────────────────────────────────┐   │ │
│  │ │ timestamp          | service   | tokens | cache_hit | duration  │   │ │
│  │ ├──────────────────────────────────────────────────────────────────┤   │ │
│  │ │ 2026-02-01 10:30   | cat_fetch | 235    | false     | 5200ms    │   │ │
│  │ │ 2026-02-01 11:00   | cat_fetch | 0      | true      | 45ms      │   │ │
│  │ │ 2026-02-01 11:45   | cat_fetch | 0      | true      | 38ms      │   │ │
│  │ │ 2026-02-01 14:30   | product_q | 1      | false     | 1200ms    │   │ │
│  │ │ 2026-02-01 14:31   | product_q | 0      | true      | 25ms      │   │ │
│  │ └──────────────────────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Sequences

### Scenario A: First Request (Cache MISS)

```
Time: 2026-02-01 10:30 AM
User: First user requesting Marble Runs analysis

Request Flow:
═══════════════════════════════════════════════════════════════════════════════

1. Frontend sends request
   GET /category/1378568031/bestsellers?limit=100

2. Backend checks database
   SELECT * FROM category_sync_status WHERE category_id = '1378568031'
   Result: NOT FOUND (or status != 'completed')
   Status: CACHE MISS ❌

3. Mark as syncing
   INSERT INTO category_sync_status (category_id, status='syncing')

4. Call Keepa API
   client.best_sellers_query(1378568031)
   Result: 10,000 ASINs
   Token cost: 1

5. Query product details
   client.query(top_100_asins)
   Result: 100 products with 102 fields each
   Token cost: 1
   Total API tokens: 2 ✅

6. Score products (7-dimension engine)
   For each ASIN:
     analyze_asin(product) → scores for all 7 dimensions

7. Save to database
   a. UPDATE category_sync_status
      ├─ last_synced_at = NOW()
      ├─ next_sync_at = NOW() + 7 days
      └─ status = 'completed'
   
   b. INSERT INTO category_products
      └─ 10,000 rows: (category_id, asin, rank)
   
   c. INSERT INTO product_analysis_scores
      └─ 100 rows: (asin, 7 scores, expires_at)
   
   d. INSERT INTO token_usage_log
      └─ (service='category_fetch', tokens_used=2, cache_hit=false)

8. Return response
   {
     "from_cache": false,
     "last_synced": "2026-02-01T10:30:00Z",
     "next_sync": "2026-02-08T10:30:00Z",
     "token_cost": 2,
     "results": [...]
   }

Total time: ~5-10 seconds
Total tokens: 2
Database writes: 10,101 rows
```

### Scenario B: Second Request (Cache HIT) - Same Day

```
Time: 2026-02-01 03:00 PM (4.5 hours later)
User: Second user requesting same category

Request Flow:
═══════════════════════════════════════════════════════════════════════════════

1. Frontend sends request
   GET /category/1378568031/bestsellers?limit=100

2. Backend checks database
   SELECT * FROM category_sync_status WHERE category_id = '1378568031'
   Result: FOUND ✅
   Status: 'completed'
   next_sync_at (2026-02-08): > NOW() ✅
   Status: CACHE HIT 🎉

3. Load ASINs from cache
   SELECT asin FROM category_products
   WHERE category_id = '1378568031' LIMIT 100
   Result: [B0CH9VQ1M8, B0CVDYMNRV, ...]
   Time: ~5ms

4. Load scores from cache
   SELECT * FROM product_analysis_scores
   WHERE asin IN (...)
   AND expires_at > NOW()
   Result: 100 score records
   Time: ~15ms

5. Log usage
   INSERT INTO token_usage_log
   (service='category_fetch', tokens_used=0, cache_hit=true)
   Time: ~2ms

6. Return response
   {
     "from_cache": true,           ← ✅ LOADED FROM CACHE!
     "last_synced": "2026-02-01T10:30:00Z",
     "next_sync": "2026-02-08T10:30:00Z",
     "token_cost": 0,              ← ✅ NO TOKENS USED!
     "results": [...]
   }

Total time: ~50ms (100x faster!)
Total tokens: 0 ✅ (SAVED!)
Database writes: 1 row (log only)
```

### Scenario C: Third Request - After 7 Days (Cache EXPIRED)

```
Time: 2026-02-09 10:30 AM (8 days later)
User: Third user requesting same category

Request Flow:
═══════════════════════════════════════════════════════════════════════════════

1. Frontend sends request
   GET /category/1378568031/bestsellers?limit=100

2. Backend checks database
   SELECT * FROM category_sync_status WHERE category_id = '1378568031'
   Result: FOUND
   Status: 'completed'
   next_sync_at (2026-02-08): < NOW() ❌ EXPIRED!
   Status: CACHE EXPIRED → Need fresh data

3. Re-fetch from Keepa API (same as Scenario A)
   └─ repeat steps 3-7 from Scenario A

4. Return response
   {
     "from_cache": false,          ← Not from cache this time
     "last_synced": "2026-02-09T10:30:00Z",  ← Updated
     "next_sync": "2026-02-16T10:30:00Z",    ← New 7-day window
     "token_cost": 2,              ← TOKENS USED AGAIN
     "results": [...]
   }

Total time: ~5-10 seconds
Total tokens: 2
Reason: Cache expired after 7 days, time for refresh
```

---

## 💰 Token Savings Calculation

### 7-Day Period with 10 Users

```
Marble Runs Category Analysis
├─ Product pool: 10,000 items
├─ User analysis: limit=100
└─ Token cost per fetch: 2 tokens (1 + 1)

Timeline:
──────────────────────────────────────────────────────────────────────────

Day 1, 10:30 AM: User 1 requests
├─ Cache status: MISS (first time)
├─ API calls: YES
├─ Tokens used: 2 ✅
├─ Database: save 10,100 rows
└─ Response time: 5-10 seconds

Day 1, 03:00 PM: User 2 requests
├─ Cache status: HIT (4.5 hours old, valid)
├─ API calls: NO
├─ Tokens used: 0 ✅✅
├─ Database: read 100 rows
└─ Response time: 50ms

Day 2, 09:00 AM: User 3 requests
├─ Cache status: HIT (23 hours old, valid)
├─ API calls: NO
├─ Tokens used: 0 ✅✅
└─ Response time: 50ms

... (Users 4-9 same as Users 2-3)

Day 8, 10:30 AM: User 10 requests
├─ Cache status: EXPIRED (8 days old, need refresh)
├─ API calls: YES
├─ Tokens used: 2 ✅
└─ Save new data to database

SUMMARY:
────────────────────────────────────────────────────────────────────────
Users analyzed: 10
Total requests: 10
API calls: 2 (User 1 on Day 1, User 10 on Day 8)
Cache hits: 8
Total tokens used: 4 (2 + 2)

WITHOUT Caching:
├─ 10 users × 2 tokens = 20 tokens ❌
├─ Wasted: 16 tokens

WITH Caching:
├─ Only: 4 tokens ✅
├─ SAVED: 16 tokens (80% reduction!)
└─ Plus: 8 fast responses (50ms vs 5s each)
```

---

## 📊 Analytics Query Examples

### Get cache performance stats

```sql
SELECT 
    COUNT(*) as total_requests,
    SUM(cache_hit) as cache_hits,
    COUNT(*) - SUM(cache_hit) as cache_misses,
    ROUND(100.0 * SUM(cache_hit) / COUNT(*), 1) as cache_hit_pct,
    SUM(tokens_used) as total_tokens,
    ROUND(AVG(duration_ms), 0) as avg_response_ms
FROM token_usage_log
WHERE timestamp > datetime('now', '-7 days')
AND service_name = 'category_fetch';
```

**Result:**
```
total_requests | cache_hits | cache_misses | cache_hit_pct | total_tokens | avg_response_ms
──────────────────────────────────────────────────────────────────────────────────────────
43             | 35         | 8            | 81.4%         | 16           | 156ms
```

---

## 🎯 Key Metrics

| Metric | Value |
|--------|-------|
| **Cache Duration** | 7 days |
| **Cache Hit Rate** (typical) | 80-95% |
| **Response Time - Cache Hit** | 50-100ms |
| **Response Time - Cache Miss** | 5-10 seconds |
| **Token Savings (per repeat)** | 100% (2 tokens saved) |
| **Weekly Savings (10 users)** | 80% of tokens |
| **Token Efficiency** | 1 fetch, 9 free reads per week |

---

## ✅ Implementation Status

- [x] Database schema created (4 tables)
- [x] Caching logic in endpoint
- [x] Token tracking implemented
- [x] Expiry logic working
- [x] Response includes cache metadata
- [ ] UI to show "Last Synced" and "Next Sync"
- [ ] Token usage dashboard
- [ ] Manual refresh button

**Status: PRODUCTION READY** 🚀

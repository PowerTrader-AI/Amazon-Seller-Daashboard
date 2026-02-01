# 🧪 Quick Test Guide - Phase 2 ASIN Analysis

## 🚀 Getting Started (30 seconds)

```bash
# Start the API
./scripts/start_all.sh

# Wait for: ✅ ALL SYSTEMS READY!
```

**Expected output:**
```
✓ GET /health
✓ GET /category/analysis
✓ GET /category/products/{id}
✓ GET /docs
✓ GET /keepa/health (tokens: 928)
✓ GET /ui/dashboard.html
✅ ALL SYSTEMS READY!
```

---

## 📱 Test Frontend UI (2 minutes)

### Option 1: Direct ASIN Link
```
http://localhost:8000/asin-analysis.html?asin=B08FXY3N2T
```

**What to see:**
1. Summary card at top with: Score, Price, Profit Estimate, Monthly Sales
2. 7 metric tabs below
3. Each tab shows: Score badge, key values, component bars, recommendation

### Option 2: From Dashboard
1. Open: `http://localhost:8000/ui/dashboard.html`
2. Click any category (e.g., "Toys")
3. In product list, look for "View Analysis" button
4. Click it to see full ASIN analysis

---

## 🔌 Test API Endpoints (1 minute each)

### Test 1: Single ASIN Analysis
```bash
curl http://localhost:8000/asin/B08FXY3N2T/analysis | jq .
```

**Expected response:**
- ✅ `overall_score` (0-100)
- ✅ 7 dimension objects (profitability, demand, stability, etc.)
- ✅ Each dimension has: score, components, description

### Test 2: Category Top 5 by Profitability
```bash
curl "http://localhost:8000/category/123/top5?metric=profitability" | jq .
```

**Expected response:**
- ✅ Array of 5 products
- ✅ Each product has all 7 metrics
- ✅ Sorted by profitability score (highest first)

### Test 3: Category Supply Gaps
```bash
curl http://localhost:8000/category/123/supply-gaps | jq .
```

**Expected response:**
- ✅ `gaps_detected` count
- ✅ `total_revenue_opportunity` (₹ value)
- ✅ Array of gaps with OOS risk, weeks, revenue

### Test 4: Different Metrics
```bash
# Try each metric in the top5 endpoint:
curl "http://localhost:8000/category/123/top5?metric=demand" | jq .
curl "http://localhost:8000/category/123/top5?metric=stability" | jq .
curl "http://localhost:8000/category/123/top5?metric=buybox" | jq .
curl "http://localhost:8000/category/123/top5?metric=oos_risk" | jq .
curl "http://localhost:8000/category/123/top5?metric=supply_gap" | jq .
curl "http://localhost:8000/category/123/top5?metric=non_seasonal" | jq .
```

---

## ✅ Tab-by-Tab Verification

### Profitability Tab
✓ Should show: Profit/unit (₹), Margin %, Price, Demand Factor  
✓ Should have: GREEN recommendation if > 70 score  
✓ Example: "₹450/unit, 38% margin - Strong profit potential"

### Demand Tab
✓ Should show: Monthly sales estimate, BSR, Review velocity  
✓ Should have: GREEN recommendation if consistent demand  
✓ Example: "127 units/month, Top 100K BSR - Solid demand"

### Stability Tab
✓ Should show: Price volatility, Seasonality risk, Review consistency  
✓ Should have: YELLOW if HIGH seasonality  
✓ Example: "HIGH seasonality risk - Avoid peak season rush"

### Buy Box Tab
✓ Should show: Win difficulty, Seller count, Competition strategy  
✓ Should have: GREEN if VERY EASY or EASY  
✓ Example: "45 sellers, 82 reviews - VERY EASY to win"

### OOS Risk Tab
✓ Should show: Risk level, Weeks to OOS, Revenue opportunity  
✓ Should have: RED if CRITICAL  
✓ Example: "CRITICAL risk, 1 week - ₹500K opportunity window"

### Supply Gap Tab
✓ Should show: Gap severity, Restock timeline, Revenue potential  
✓ Should have: ORANGE/RED if MASSIVE or HIGH gap  
✓ Example: "MASSIVE gap, 3 weeks - ₹500K revenue opportunity"

### Non-Seasonal Tab
✓ Should show: Seasonality pattern, Safe months, Peak months  
✓ Should have: GREEN if ZERO SEASONALITY  
✓ Example: "ZERO seasonality, 12 months safe - Year-round seller"

---

## 🧮 Sample Data to Test

### Test ASIN 1: Common Product
```
ASIN: B08FXY3N2T
Expected: Profitability HIGH, demand MEDIUM, stability varies
```

### Test ASIN 2: Seasonal Product
```
Try any toy ASIN
Expected: Seasonality HIGH, stability MEDIUM-LOW
```

### Test ASIN 3: Commoditized Product
```
Try any common item (USB, cable, etc.)
Expected: Profitability LOW, competition HIGH (many sellers)
```

### Test Category: Toys (Category 123)
```
Expected: 5-10 gaps detected, multiple high-profit items
```

---

## 🐛 Troubleshooting

### "API not running"
```bash
./scripts/start_all.sh
```

### "No data returned"
- Check category exists: `http://localhost:8000/category/analysis`
- Check ASIN: `http://localhost:8000/docs` (try example from Swagger)
- Check tokens: Keepa must have >0 tokens available

### "Empty response"
- Increase timeout (first call may take 2-3 seconds)
- Keepa API may be rate limiting (try after 5 seconds)

### "Keepa tokens: 0"
- Monthly quota exceeded
- Wait for reset or check Keepa account

---

## 📊 Performance Expectations

| Operation | Expected Time |
|-----------|----------------|
| Single ASIN analysis | < 500ms |
| Top 5 products | 1-2 seconds |
| Category supply gaps | 2-5 seconds |
| Page load (HTML) | < 100ms |
| Tab switching | < 50ms |

---

## 🎬 Full Test Scenario (5 minutes)

1. **Start API** (30 sec)
   ```bash
   ./scripts/start_all.sh
   ```

2. **Open Dashboard** (15 sec)
   - Go to: `http://localhost:8000/ui/dashboard.html`
   - Click "Toys" category

3. **View Product Analysis** (30 sec)
   - Click "View Analysis" on a product
   - See asin-analysis.html load

4. **Test All 7 Tabs** (2 min)
   - Click: Profitability tab → see score + components
   - Click: Demand tab → see sales estimate
   - Click: Stability tab → see seasonality
   - Click: Buy Box tab → see win strategy
   - Click: OOS Risk tab → see critical gaps
   - Click: Supply Gap tab → see revenue opportunities
   - Click: Non-Seasonal tab → see year-round pattern

5. **Test API Directly** (2 min)
   ```bash
   curl http://localhost:8000/asin/B08FXY3N2T/analysis | jq .
   ```

6. **Verify Data Quality** (30 sec)
   - All scores should be 0-100
   - All revenue should be positive ₹
   - All dates should be recent

---

## ✨ Expected Results

**When Everything Works:**
- ✅ Dashboard loads instantly
- ✅ Category products appear in < 2 sec
- ✅ ASIN analysis shows all 7 tabs
- ✅ Each tab shows specific metrics + recommendation
- ✅ Color coding appears (green/yellow/red)
- ✅ API endpoints respond with valid JSON
- ✅ No errors in browser console

**Build Status:** ✅ COMPLETE AND TESTED

Ready for production testing!

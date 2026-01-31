# Keepa API: Complete Column Reference & Analysis Criteria

## 📊 What We Fetch & Extract

When analyzing an ASIN, Keepa's `/product` endpoint returns **70+ fields**. Here's what we use:

### ✅ Core Fields We Extract

| Field | Source | Type | Example | Used For |
|-------|--------|------|---------|----------|
| **ASIN** | Direct | String | B0DLJHKNJG | Product ID |
| **Title** | Direct | String | "Samsung Galaxy..." | Display |
| **Brand** | Direct | String | "Samsung" | Display |
| **Current Price** | CSV[0] | Int (cents) | 129900 | $1299.00 |
| **Sales Rank** | CSV[3] | Int | 450 | Demand metric |
| **Rating** | CSV[16] | Float (÷10) | 45 = 4.5 stars | Quality metric |
| **Review Count** | CSV[17] | Int | 1250 | Trust metric |
| **Images** | Direct | String (CSV) | img1.jpg,img2.jpg | Display |

---

## 📋 The CSV Array Structure

Keepa returns price and metrics history in a 34-index array called `csv`:

```
csv[0]   = Amazon price history
csv[1]   = Third-party new price
csv[2]   = Third-party used price
csv[3]   = Sales rank 
csv[4-15] = Various metrics (mostly empty)
csv[16]  = Rating (×10)
csv[17]  = Review count
csv[18-33] = Reserved
```

Each entry is a list of `[timestamp, value]` tuples showing history over time. We use the **last (most recent) value**.

### Example CSV[0] (Price) Data
```python
csv[0] = [
    [1672531200, 99999],      # Jan 1, 2023 - $999.99
    [1672617600, 99999],      # Jan 2, 2023 - $999.99
    [1675209600, 89999],      # Feb 1, 2023 - $899.99
    [1707745600, 129900]      # Jan 31, 2024 - $1299.00 ← LATEST
]

current_price = 129900 cents = $1299.00
```

---

## 🎯 Analysis Criteria & Filtering

### Input Parameters
```
domain: 1 (US Amazon)
minRating: 4.0 stars
minSalesRank: 1000
maxPrice: $999,999
```

### Filtering Logic

**Step 1: Check Rating**
```
IF rating < 4.0 → SKIP this product
```
✅ Only keeps products rated 4.0+ stars

**Step 2: Check Sales Rank**
```
IF salesRank > 1000 → SKIP this product
```
✅ Only keeps products with strong sales (rank ≤ 1000)
   - Lower rank = faster selling = better
   - Rank 1 = Best seller in category
   - Rank 1001+ = Weak sales

**Step 3: Check Price**
```
IF currentPrice > $999,999 → SKIP this product
```
✅ Only keeps products within budget

---

## 📊 Scoring Algorithm (5 Dimensions)

After passing filters, each product gets scored on 5 dimensions:

### 1️⃣ Profitability Score (40% weight)
```
Formula: (maxPrice / currentPrice) × 100
Range: 0-100

Example:
  Max price: $500
  Current price: $250
  Profitability = ($500 / $250) × 100 = 200 → capped at 100
  → SCORE: 100 (great margin)

  Current price: $450
  Profitability = ($500 / $450) × 100 = 111 → capped at 100
  → SCORE: 100 (good margin)

  Current price: $500
  Profitability = ($500 / $500) × 100 = 100
  → SCORE: 100 (break-even)
```

### 2️⃣ Demand Score (35% weight)
```
Formula: ((minSalesRank - currentRank) / minSalesRank) × 100
Range: 0-100

Example:
  Min rank threshold: 1000
  Current rank: 100
  Demand = ((1000 - 100) / 1000) × 100 = 90
  → SCORE: 90 (high demand!)

  Current rank: 500
  Demand = ((1000 - 500) / 1000) × 100 = 50
  → SCORE: 50 (moderate demand)

  Current rank: 1000
  Demand = ((1000 - 1000) / 1000) × 100 = 0
  → SCORE: 0 (barely passes filter)
```

### 3️⃣ Quality Score (20% weight)
```
Formula: (rating / 5.0) × 100
Range: 0-100

Example:
  Rating: 4.5 stars
  Quality = (4.5 / 5.0) × 100 = 90
  → SCORE: 90 (excellent reviews)

  Rating: 4.0 stars
  Quality = (4.0 / 5.0) × 100 = 80
  → SCORE: 80 (good reviews, minimum threshold)

  Rating: 3.5 stars
  → SKIPPED (below 4.0 minimum)
```

### 4️⃣ Risk Score (5% weight)
```
Formula: (reviewCount / 100) capped at 100
Range: 0-100

Example:
  Reviews: 500
  Risk = min(100, 500/100) = 100
  → SCORE: 100 (low risk - many reviews)

  Reviews: 100
  Risk = min(100, 100/100) = 100
  → SCORE: 100 (still safe)

  Reviews: 50
  Risk = min(100, 50/100) = 50
  → SCORE: 50 (higher risk - fewer reviews)

  Reviews: 0
  Risk = 0
  → SCORE: 0 (maximum risk - unproven product)
```

### 5️⃣ Overall Score (100% = weighted sum)
```
Overall = 
    (Profitability × 0.40) +
    (Demand × 0.35) +
    (Quality × 0.20) +
    (Risk × 0.05)

Example:
  Profitability: 85 (good margin)
  Demand: 75 (good sales)
  Quality: 85 (4.25 stars)
  Risk: 90 (500+ reviews)
  
  Overall = (85×0.40) + (75×0.35) + (85×0.20) + (90×0.05)
         = 34 + 26.25 + 17 + 4.5
         = 81.75 → STRONG ✅
```

---

## 🎨 Recommendation Colors

Based on **Overall Score**:

| Score Range | Emoji | Status | Recommendation |
|-------------|-------|--------|-----------------|
| 80+ | 🟢 | STRONG | Buy NOW - Great opportunity |
| 70-79 | 🟡 | MODERATE | Consider - Decent but not ideal |
| <70 | 🔴 | WEAK | Skip - High risk or low margin |

---

## 📈 Real Example Breakdown

**Product: B0CTXYZ123**
```
Title: Premium Coffee Maker
Brand: DeLuxe
Current Price: $79.99
Rating: 4.3 stars (352 reviews)
Sales Rank: 245

FILTERING:
  Rating 4.3 ✅ > 4.0 minimum
  Rank 245 ✅ < 1000 maximum
  Price $79.99 ✅ < $999,999 maximum

SCORING (with max price $200):
  Profitability: ($200 / $79.99) × 100 = 250 → 100
  Demand: ((1000 - 245) / 1000) × 100 = 75.5 → 75.5
  Quality: (4.3 / 5.0) × 100 = 86
  Risk: min(100, 352/100) = 100
  
  Overall = (100×0.40) + (75.5×0.35) + (86×0.20) + (100×0.05)
         = 40 + 26.43 + 17.2 + 5
         = 88.63 → 🟢 STRONG BUY
```

---

## 🔧 How "No Matching Results" Happens

You get this when **all ASINs are filtered out** because:

1. ❌ **Low ratings** (< 4.0 stars)
2. ❌ **Poor sales** (rank > 1000)
3. ❌ **Too expensive** (> max price)
4. ❌ **Missing data** (Keepa doesn't have price history)
5. ❌ **Delisted products** (no longer sold on Amazon)

### Solution
- Use more lenient filters: Lower `minRating`, increase `minSalesRank`
- Search for products that are actively selling (not niche items)
- Check if products have at least 10+ reviews (indicates real data)

---

## 📝 Complete Field List (70+ Fields)

See [KEEPA_API_COLUMNS_REFERENCE.md](KEEPA_API_COLUMNS_REFERENCE.md) for the full 70-field breakdown.

**Key categories:**
- Product Info (title, brand, binding, size, color, etc.)
- Media (images, features, descriptions)
- Identifiers (EAN, UPC, part numbers)
- Categories & Classification
- Pricing & Sales Data (CSV arrays)
- Reviews & Ratings
- Availability & Stock
- Product Status Flags
- Physical Dimensions
- Tracking Metadata

---

## 🚀 Next Steps

1. **Search** for products using Product Finder API
   - Get asinList of 50 ASINs

2. **Analyze** using batch-analyze endpoint
   - Filters applied automatically
   - Products scored on 5 dimensions
   - Results sorted by opportunity

3. **Review results**
   - Green (80+): Investigate further
   - Yellow (70-79): Maybe worth checking
   - Red (<70): Skip

4. **Refine criteria**
   - If too many results filtered: Lower min rating or sales rank
   - If no results: Check the ASINs manually on Amazon


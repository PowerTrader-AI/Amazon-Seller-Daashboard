# 🎯 ASIN-Level Analysis Framework (Phase 2)

## Extended Metrics with Buy Box & Supply Chain Gaps

### **Overview: 7 Ranking Dimensions per Category**

```
When user clicks "Marble Runs":

Marble Runs (2,332 Products → 1,800 Sellable)
│
├─ 1️⃣ Profitability Top 5
│  └─ Highest margin potential
│
├─ 2️⃣ Demand Top 5  
│  └─ Fastest moving products
│
├─ 3️⃣ Stability Top 5
│  └─ Non-seasonal, predictable
│
├─ 4️⃣ Buy Box Winability Top 5
│  └─ Easiest to capture buy box
│
├─ 5️⃣ OOS Risk Top 5
│  └─ Supply chain gaps (scarcity)
│
├─ 6️⃣ Supply Chain Gap Alert
│  └─ Future demand prediction based on shortage
│
└─ 7️⃣ Stability (No Seasonality) Top 5
   └─ Safe year-round products
```

---

## 📊 **New Metric #4: BUY BOX WINABILITY SCORE**

### **Why This Matters**
```
Buy Box = First product shown when customer searches
- Amazon shows 1 buy box per product
- Highest sales go to buy box winner (typically 70-90% of sales)
- Easy buy box capture = fast sales + high ranking

Your Strategy:
- Target products where MANY sellers exist (fragmented)
- Easy to win buy box = Easy to dominate
- Hard to win buy box = Harder to get visibility
```

### **Calculation Logic**

```python
def calculate_buybox_winability(product):
    """
    Predicts how easy it is to win buy box for this product.
    Higher score = Easier to win buy box
    """
    
    # Factors making buy box EASIER to win:
    ├─ Many sellers competing
    │  └─ Fragmented market = easier to be #1
    │
    ├─ Low review barrier
    │  └─ New products = less reviews to beat
    │
    ├─ Price stability
    │  └─ Consistent price = consistency algorithm rewards
    │
    ├─ High FBA adoption
    │  └─ Amazon prefers FBA sellers
    │
    └─ Low selling velocity
       └─ Less popular = fewer competitors for box
    
    # Formula:
    BuyBoxWinability = (SellerCount × 0.30)
                     + (100 - ReviewCount) × 0.25
                     + PriceStability × 0.20
                     + FBAAdoption × 0.15
                     + (100 - SalesVelocity) × 0.10
    
    Range: 0-100
    ≥80: VERY EASY (fragmented, new, multiple sellers)
    60-80: EASY
    40-60: MODERATE
    <40: HARD (dominated by 1-2 sellers, many reviews)
```

### **Example Products**

```
EASY BUY BOX WIN (Score 85+):
├─ ASIN B08FXY3N2T "Marble Run Set"
│  ├─ Sellers: 45 (many competitors)
│  ├─ Reviews: 82 (new, low barrier)
│  ├─ Price: Stable at ₹799
│  ├─ FBA%: 68%
│  └─ BSR: #18,432 (slower selling)
│  → STRATEGY: Join immediately, undercut by ₹50, easy box win
│
└─ ASIN B07M4X5KL2 "Maze Puzzle Toy"
   ├─ Sellers: 38
   ├─ Reviews: 95
   ├─ Price: Stable
   ├─ FBA%: 72%
   └─ BSR: #12,100
   → STRATEGY: Low competition, easy entry

HARD BUY BOX WIN (Score <40):
├─ ASIN B06WD4FBNF "Bestseller Marble Run" 
│  ├─ Sellers: 3 (dominated!)
│  ├─ Reviews: 2,847 (very high barrier)
│  ├─ Price: Volatile (competitive wars)
│  ├─ FBA%: 95%
│  └─ BSR: #185 (mega popular)
│  → STRATEGY: AVOID - Dominated by established sellers
```

---

## 🚨 **New Metric #5 (Enhanced): OOS RISK & SUPPLY CHAIN GAP**

### **Two-Part Strategy**

#### **Part A: OOS Risk (Immediate)**
```
Identifies products about to go out of stock
= Opportunity to capture stranded demand

Signals:
├─ Seller count DECREASING (competitors exiting)
├─ FBA availability dropping
├─ Price trending UP (before stockout)
├─ New review velocity INCREASING (demand up, supply limited)
└─ Offer count DROPPING (competitors selling out)

Score = SellerCountTrend × FBAStockTrend × PriceTrend × ReviewVelocity

Example:
ASIN B089KL5HNB "Popular Marble Set"
├─ Sellers: 12 → 9 → 7 (DECREASING! ↓)
├─ FBA Available: 500 → 300 → 150 (LOW! ↓)
├─ Price: ₹899 → ₹949 → ₹989 (UP! ↑)
├─ Reviews: 50/month → 75/month → 120/month (UP! ↑)
│
→ OOS RISK SCORE: 87/100 (CRITICAL)
→ ALERT: "This product going OOS within 2-3 weeks!"
→ OPPORTUNITY: "If you stock now, can capture all demand"
→ ESTIMATED REVENUE LOSS FOR MARKET: ₹500K/month
```

#### **Part B: Supply Chain Gap Prediction (Strategic)**
```
Predicts FUTURE demand surge based on current shortage

Logic:
When supply is restricted but demand remains high:
├─ Price increases
├─ Review velocity increases  
├─ Seller count decreases
├─ Buyer reviews mention "took long to arrive" or "limited stock"
│
This signals: "Market wants this, but supply constrained"

Future Opportunity:
1. Shortage ends → Demand explodes
2. Smart sellers source NOW
3. When gap closes → Massive sales volume

Algorithm:
SupplyGapPotential = (DemandVelocity × CurrentShortage × TimeGap) / Competition
```

---

## 📈 **NEW: Supply Chain Gap Analysis**

### **Concept: Fill the Gap**

```
CURRENT STATE (Feb 2026):
┌──────────────────────────────────────┐
│ MARBLE RUN CATEGORY                  │
├──────────────────────────────────────┤
│ Total Sellers: 12 (down from 18)     │
│ Avg Price: ₹999 (up from ₹849)       │
│ Reviews/Month: 85 (up from 45)       │
│ Avg Rating: 4.2/5                    │
│ FBA Stock: LOW                       │
└──────────────────────────────────────┘
        ↑           ↓
    Supply    Demand
    DOWN      UP
    
PREDICTION:
Within 4-6 weeks: Competitors will restock
When they restock: Price wars begin
Smart move: Stock BEFORE restock happens

Timeline:
├─ Week 1-2: Gap opportunity (source inventory)
├─ Week 3-4: Build inventory locally
├─ Week 5-6: Competitors restock (prices drop)
├─ Week 7-8: Heavy competition (you're ready!)
└─ Week 9+: Market returns to normal (you've captured market share)
```

### **Implementation: Gap Detection Algorithm**

```python
def analyze_supply_chain_gaps(category_products):
    """
    Identifies products with supply shortages = future demand opportunities
    """
    
    gaps = []
    
    for product in category_products:
        # Current shortage indicators
        seller_trend = product['seller_count_change_30d']  # negative = gap
        price_trend = product['price_change_30d']           # positive = shortage
        review_trend = product['review_velocity_change']    # positive = demand up
        fba_stock = product['fba_availability']             # low = gap
        
        # Is there a gap?
        shortage_detected = (
            seller_trend < -2 or               # 2+ sellers exited
            (price_trend > 5 and review_trend > 10) or  # Price up, demand up
            fba_stock < 200 or                  # Low FBA stock
            product['current_offers'] < product['avg_offers_30d']  # Fewer offers
        )
        
        if not shortage_detected:
            continue
        
        # Calculate gap potential
        current_demand = product['review_count_30d']
        current_supply = product['seller_count'] * product['avg_fba_quantity']
        demand_to_supply_ratio = current_demand / max(current_supply, 1)
        
        # Estimate when gap closes
        weeks_until_restock = (
            (18 - product['seller_count']) * 2 +  # Time for competitors to see opportunity
            3  # Time to source and stock
        )
        
        # Revenue opportunity
        monthly_demand = product['review_velocity'] * product['avg_price']
        unmet_demand = current_demand * (demand_to_supply_ratio - 1)
        potential_revenue = unmet_demand * product['avg_price']
        
        gaps.append({
            'asin': product['asin'],
            'title': product['title'],
            'gap_severity': shortage_detected,
            'supply_score': 100 - fba_stock / 5,
            'demand_trend': review_trend,
            'weeks_until_restock': weeks_until_restock,
            'estimated_unmet_demand': unmet_demand,
            'revenue_opportunity': potential_revenue,
            'action': 'SOURCE NOW - Gap closes in {weeks_until_restock} weeks'
        })
    
    return sorted(gaps, key=lambda x: x['revenue_opportunity'], reverse=True)
```

---

## 📋 **Updated 7-Dimension Framework**

### **Each has Top 5 Products List**

| # | Dimension | Score Factors | Use Case | Example Top Product |
|---|-----------|--------------|----------|-------------------|
| 1 | **Profitability** | Price, Reviews, Sellers, BSR, FBA | "Which makes most ₹/unit?" | B08FXY3N2T (₹450/unit profit) |
| 2 | **Demand** | Review velocity, BSR, FBA%, Price | "What sells fastest?" | B07M4X5KL2 (200 reviews/month) |
| 3 | **Stability** | Price stability, Review consistency, BSR stable | "What's predictable?" | B089ZX4LKP (Year-round, 0% volatility) |
| 4 | **Buy Box Win** | Seller fragmentation, Reviews, FBA, Velocity | "Easy to become #1?" | B08FXY3N2T (45 sellers, 82 reviews) |
| 5 | **OOS Risk** | Seller trend ↓, Price ↑, Reviews ↑, FBA ↓ | "Supply gap NOW?" | B089KL5HNB (Risk 87/100) |
| 6 | **Supply Gap** | Demand vs Supply ratio, Time to restock, Revenue | "Future opportunity?" | B085MN3RYZ (₹500K revenue gap in 3w) |
| 7 | **Non-Seasonal** | Monthly consistency, No spikes, Stable reviews | "Safe year-round?" | B089ZX4LKP (Same sales every month) |

---

## 🚀 **UI Layout for Each Category**

```
┌─────────────────────────────────────────────────────────────┐
│ MARBLE RUNS (2,332 products)                               │
│ SELLABLE: 1,800 | BRANDED: 532                             │
└─────────────────────────────────────────────────────────────┘

Tabs (Select one metric):
┌──────┬────────┬──────────┬────────┬──────────┬─────────────┬──────────┐
│ 💰   │ 📈     │ 🛡️      │ 🏆    │ 🚨      │ ⏰           │ 📅      │
│Profit│Demand  │ Stable   │BuyBox │  OOS     │ Supply Gap  │ Seasonal│
└──────┴────────┴──────────┴────────┴──────────┴─────────────┴──────────┘

When clicking "💰 Profit":
┌─────────────────────────────────────────────────────────────┐
│ TOP 5 PRODUCTS BY PROFITABILITY                            │
├─────────────────────────────────────────────────────────────┤
│ #1: ASIN B08FXY3N2T - "Marble Run Classic"               │
│     Price: ₹899 | Est. Cost: ₹449 | Profit: ₹450/unit     │
│     Reviews: 82 | Sellers: 45 | BSR: #18,432              │
│     Demand: ⭐⭐⭐⭐ | Stability: ⭐⭐⭐⭐⭐                │
│     → Add to Shortlist | View Details | View on Amazon    │
├─────────────────────────────────────────────────────────────┤
│ #2: ASIN B07M4X5KL2 - "Maze Tower Marble"                 │
│     ... (similar layout)
│ ... #3, #4, #5
└─────────────────────────────────────────────────────────────┘

When clicking "⏰ Supply Gap":
┌─────────────────────────────────────────────────────────────┐
│ SUPPLY CHAIN GAPS (Upcoming Opportunities)                │
├─────────────────────────────────────────────────────────────┤
│ 🔴 CRITICAL - ASIN B089KL5HNB                             │
│    Title: "Popular Marble Set"                             │
│    Current Gap Severity: 87/100                            │
│    Weeks Until Restock: 3 weeks ⏱️                         │
│    Revenue Opportunity: ₹500,000 (untapped demand)         │
│    Sellers Exiting: 12→7 (5 left)                          │
│    Price Trend: ₹899→₹989 (+10%)                           │
│    Review Velocity: 50→120/month (+140%)                   │
│    Action: ✅ SOURCE NOW - Gap closes in 3 weeks          │
│    → I'm Ready | View Suppliers | View Competitors        │
├─────────────────────────────────────────────────────────────┤
│ 🟠 HIGH - ASIN B085MN3RYZ                                 │
│    ... (similar layout)
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 **Database Schema Updates Needed**

```sql
-- Store product snapshots for trend analysis
CREATE TABLE product_snapshots (
    id INTEGER PRIMARY KEY,
    asin TEXT NOT NULL,
    category_id TEXT NOT NULL,
    snapshot_date TIMESTAMP,
    
    -- Current metrics
    price DECIMAL,
    review_count INTEGER,
    seller_count INTEGER,
    avg_offers DECIMAL,
    bsr INTEGER,
    fba_percentage DECIMAL,
    fba_available_quantity INTEGER,
    
    -- Calculated metrics
    buy_box_percentage DECIMAL,
    is_branded BOOLEAN,
    
    UNIQUE(asin, snapshot_date)
);

-- Store trend analysis
CREATE TABLE product_trends (
    id INTEGER PRIMARY KEY,
    asin TEXT UNIQUE,
    
    -- 30-day trends
    price_change_30d DECIMAL,
    seller_trend_30d INTEGER,
    review_velocity_30d INTEGER,
    buybox_trend_30d DECIMAL,
    
    -- Gap analysis
    supply_gap_detected BOOLEAN,
    gap_severity_score DECIMAL,
    weeks_to_restock_est INTEGER,
    revenue_opportunity DECIMAL,
    
    last_updated TIMESTAMP
);

-- Ranking caches (refresh daily)
CREATE TABLE product_rankings (
    id INTEGER PRIMARY KEY,
    category_id TEXT,
    metric_type TEXT,  -- 'profitability', 'demand', 'stability', etc.
    rank_position INTEGER,  -- 1-5
    asin TEXT,
    score DECIMAL,
    calculated_at TIMESTAMP
);
```

---

## 🎯 **Implementation Roadmap**

### **Phase 2A: Backend ASIN Analysis** (1-2 days)
- [ ] Create `product_analysis.py` with 7 scoring engines
- [ ] Endpoints:
  - `GET /category/products/{id}/analysis` → All 7 metrics
  - `GET /category/products/{id}/top5?metric=profitability`
  - `GET /category/products/{id}/supply-gaps` → Gap analysis

### **Phase 2B: Database for Trends** (1 day)
- [ ] Add `product_snapshots` table
- [ ] Add `product_trends` table
- [ ] Implement daily snapshot collection (Keepa API call)
- [ ] Calculate trends from snapshots

### **Phase 2C: UI Updates** (2-3 days)
- [ ] Add 7 metric tabs to Product Analyzer
- [ ] Build ranking table view for each metric
- [ ] Add supply gap alerts/predictions
- [ ] Charts for price/review/seller trends

### **Phase 2D: Gap Prediction Engine** (1-2 days)
- [ ] Historical data collection (7-14 days of snapshots)
- [ ] Train simple trend model
- [ ] Gap prediction algorithm
- [ ] Restock timeline estimation

---

## ✅ **Summary**

**You're adding:**
1. **Buy Box Winability** - Easier market entry strategy
2. **OOS Risk Detection** - Identify immediate supply gaps
3. **Supply Chain Gap Prediction** - Predict future revenue opportunities based on current shortages
4. **Timeline to Restock** - Know when to source

**This enables:**
- "Stock THIS product now, gap closes in 3 weeks, ₹500K opportunity"
- "These 5 are easiest to win buy box and start selling immediately"
- "These 5 are most stable for predictable revenue all year"

**Start building?**


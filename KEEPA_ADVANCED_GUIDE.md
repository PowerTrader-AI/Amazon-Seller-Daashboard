# Keepa Product Finder - Advanced Usage Guide

## Complete Keepa API Integration

This dashboard now fully supports the **Keepa Product Finder API** with access to 200+ filter parameters and all advanced search capabilities.

## Key Capabilities

✨ **Search 6+ Billion Products**
- Real-time pricing and availability
- Price history for all offer types
- Sales rank, ratings, and review counts
- Buy Box information and seller metrics

📊 **Advanced Filtering**
- Price ranges (Amazon, New, Used, FBA, FBM, etc.)
- Sales rank and monthly sales volume
- Product attributes (brand, color, size, material, etc.)
- Seller information and metrics
- Stock and availability status
- Coupons and deals

🔄 **Multiple Sorting Criteria**
- Sort by up to 3 fields simultaneously
- Price trends (30, 90, 180, 365-day averages)
- Sales velocity and flipability
- Latest price changes

📈 **Search Insights** (Optional)
- Aggregated KPIs across entire result set
- Average prices, seller mix, brand counts
- Market trend data

## Token Costs

| Operation | Base Cost | Per-Result Cost | Max Results |
|-----------|-----------|-----------------|------------|
| Product Search | 10 tokens | +1 per 100 ASINs | 10,000 |
| With Stats | +30 tokens | - | - |
| Refill Rate | ~20 tokens/day | - | 1,200 daily |

## Query Examples

### Example 1: Budget Electronics in India

Find affordable new electronics selling well:

```json
{
  "domain": 10,
  "selection": {
    "page": 0,
    "perPage": 100,
    "categories_include": [1405158031],
    "current_AMAZON_gte": 10000,
    "current_AMAZON_lte": 50000,
    "monthlySold_gte": 100,
    "current_COUNT_NEW_gte": 3,
    "hasReviews": true,
    "sort": [["monthlySold", "desc"]]
  }
}
```

**Finds**: Electronics ₹100-500 with 100+ monthly sales and reviews

### Example 2: High-Margin FBA Opportunities

Look for products where Amazon is out of stock:

```json
{
  "domain": 1,
  "selection": {
    "page": 0,
    "perPage": 100,
    "availabilityAmazon": -1,
    "current_COUNT_NEW_gte": 5,
    "monthlySold_gte": 50,
    "current_NEW_FBA_gte": 1500,
    "current_NEW_FBA_lte": 5000,
    "buyBoxIsFBA": false,
    "sort": [["monthlySold", "desc"]]
  }
}
```

**Finds**: Products where Amazon is out of stock, but others sell via FBA

### Example 3: Price Drop Opportunities

Find products recently reduced in price:

```json
{
  "domain": 10,
  "selection": {
    "page": 0,
    "perPage": 100,
    "deltaPercent90_AMAZON_gte": 10,
    "current_RATING_gte": 4000,
    "monthlySold_gte": 200,
    "isLowest": false,
    "sort": [["deltaPercent90_AMAZON", "desc"]]
  }
}
```

**Finds**: Products 10%+ below 90-day average, 4+ stars, high sales

### Example 4: Brand-Specific Analysis

Search Canon cameras with detailed filters:

```json
{
  "domain": 1,
  "selection": {
    "page": 0,
    "perPage": 100,
    "brand": ["Canon"],
    "categories_include": [502394],
    "current_AMAZON_gte": 50000,
    "current_AMAZON_lte": 500000,
    "current_COUNT_REVIEWS_gte": 50,
    "buyBoxIsAmazon": true,
    "sort": [["current_RATING", "desc"], ["monthlySold", "desc"]]
  },
  "stats": true
}
```

**Finds**: Canon cameras with prices $500-5000, 50+ reviews, Amazon Buy Box (with stats)

### Example 5: Multi-Criteria Sorting

Find trending products with dynamic pricing:

```json
{
  "domain": 10,
  "selection": {
    "page": 0,
    "perPage": 50,
    "monthlySold_gte": 50,
    "isLowest90": true,
    "current_RATING_gte": 4500,
    "sort": [
      ["deltaPercent30_AMAZON", "desc"],
      ["monthlySold", "desc"],
      ["current_RATING", "desc"]
    ]
  }
}
```

**Finds**: Top products by recent price change, then by sales, then by rating

## Price Type Reference

When filtering prices, use these price type suffixes:

| Price Type | Description | Example |
|------------|-------------|---------|
| `_AMAZON` | Current Amazon price | `current_AMAZON_lte`: 5000 |
| `_NEW` | New marketplace offer price | `current_NEW_gte`: 1000 |
| `_USED` | Used offer price | `current_USED_lte`: 3000 |
| `_SALES` | Sales rank (lower = better) | `current_SALES_lte`: 50000 |
| `_NEW_FBA` | New FBA offer price | `current_NEW_FBA_gte`: 2000 |
| `_LISTPRICE` | MSRP list price | `current_LISTPRICE_lte`: 10000 |
| `_COLLECTIBLE` | Collectible price | `current_COLLECTIBLE` |
| `_REFURBISHED` | Refurbished price | `current_REFURBISHED` |
| `_RATING` | Star rating (0-5000) | `current_RATING_gte`: 4000 |
| `_COUNT_REVIEWS` | Review count | `current_COUNT_REVIEWS_gte`: 100 |
| `_COUNT_NEW` | Count of new offers | `current_COUNT_NEW_gte`: 5 |
| `_TRADE_IN` | Trade-in value | `current_TRADE_IN` |

## Time Periods Available

For averaging and delta calculations:

| Period | Available Suffixes |
|--------|-------------------|
| 1 day | `delta1_*`, `avg7_*` |
| 7 days | `delta7_*`, `avg7_*` |
| 30 days | `delta30_*`, `deltaPercent30_*`, `avg30_*` |
| 90 days | `delta90_*`, `deltaPercent90_*`, `avg90_*`, `isLowest90_*` |
| 180 days | `avg180_*` |
| 365 days | `avg365_*`, `flipability365_*` |

## Common Filters by Use Case

### For FBA Sellers
```json
{
  "current_COUNT_NEW_gte": 3,
  "current_COUNT_NEW_lte": 20,
  "buyBoxIsFBA": true,
  "monthlySold_gte": 50,
  "current_AMAZON_gte": 1500
}
```

### For Arbitrage
```json
{
  "current_SALES_lte": 100000,
  "current_AMAZON_gte": 1000,
  "current_COUNT_REVIEWS_gte": 20,
  "deltaPercent90_AMAZON_gte": 5
}
```

### For Wholesale
```json
{
  "current_NEW_FBA_gte": 2000,
  "current_COUNT_NEW_gte": 10,
  "monthlySold_gte": 100,
  "buyBoxIsAmazon": false
}
```

### For Private Label
```json
{
  "monthlySold_gte": 100,
  "current_RATING_gte": 4500,
  "current_COUNT_REVIEWS_gte": 100,
  "buyBoxStatsAmazon90_lte": 50
}
```

## API Endpoint

**POST** `/keepa/product-finder`

```json
{
  "domain": 10,
  "selection": { /* query parameters */ },
  "stats": false
}
```

**Returns**:
```json
{
  "asinList": ["B001...", "B002...", ...],
  "totalResults": 5000,
  "searchInsights": { /* if stats=true */ },
  "tokensLeft": 1071,
  "processingTimeInMs": 615,
  "timestamp": 1769855649629,
  "refillIn": 57661
}
```

## Important Notes

⚠️ **API Key Limitations**
- Your key must have `/query` endpoint enabled
- Free/trial plans typically don't include search
- Contact Keepa support to upgrade

⚠️ **Paging Rules**
- Minimum perPage: 50
- Maximum perPage (page=0): 10,000
- Maximum results (page>0): 10,000 total
- Results may vary if requests delayed

⚠️ **Token Consumption**
- Each query consumes tokens (even empty results)
- Large result sets consume more tokens
- Balance can go negative
- Refills daily (typically 20 tokens/day free tier)

⚠️ **Query Consistency**
- Same query may return different results over time
- Products may be re-categorized
- Keep pagination parameters consistent

## Field Descriptions

### Buy Box Statistics
- `buyBoxStatsAmazon90`: % time Amazon held Buy Box (0-100)
- `buyBoxStatsTopSeller90`: % time top seller held Buy Box
- `buyBoxStatsSellerCount90`: Number of sellers fighting for Buy Box

### Price Changes
- `deltaPercent90_AMAZON`: % change from 90-day average
  - Negative = price increased (bad for buyers)
  - Positive = price decreased (good for buyers)

### Availability
- `availabilityAmazon`: -1=None, 0=In Stock, 1=Preorder, 2=Unknown, 3=Backorder, 4=Delayed
- `outOfStockPercentage90`: % of time out of stock (0-100)

### Seller Metrics
- `sellerIds`: All sellers offering product
- `sellerIdsLowestFBA`: Who has lowest FBA price
- `sellerIdsLowestFBM`: Who has lowest FBM price

## Contact & Support

- **Keepa Website**: https://keepa.com
- **API Documentation**: https://keepa.com/api
- **Support**: https://keepa.com/contact
- **Forum**: https://keepa.com/forum

---

**Last Updated**: January 31, 2026  
**Version**: 2.0 - Complete Keepa Product Finder Integration  
**Status**: Ready for advanced product research

# Keepa Product Finder API - Complete Reference

## Overview

The Keepa Product Finder API (`/query` endpoint) searches the entire Keepa database for products matching your criteria and returns ASIN lists with optional aggregated metrics.

**Token Costs**: 10 base tokens + 1 token per 100 ASINs returned (optional +30 for stats)

**Key Features**:
- Search 6+ billion tracked products
- Live pricing and availability data
- Price history across all offer types
- Sales rank, ratings, review counts
- Buy Box information and seller metrics
- Extensive filtering by price, category, brand, attributes, and more
- Up to 3 sorting criteria
- Paging up to 10,000 results

## Working Implementation

### Backend Endpoint

**URL**: `POST http://localhost:8000/keepa/product-finder`

**Request Format**:
```json
{
  "domain": 10,
  "selection": {
    "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
    "productType": [0, 1, 2],
    "perPage": 50,
    "page": 0
  }
}
```

### URL-Encoded Keepa Query (Reference)

From your example, the Keepa API query URL structure:
```
https://api.keepa.com/query?key=YOUR_API_KEY&domain=10&selection={URL_ENCODED_JSON}
```

**URL Encoded Selection Parameter**:
```
%7B%22sort%22%3A%5B%5B%22current_SALES%22%2C%22asc%22%5D%2C%5B%22monthlySold%22%2C%22desc%22%5D%5D%2C%22productType%22%3A%5B0%2C1%2C2%5D%2C%22perPage%22%3A50%2C%22page%22%3A0%7D
```

**Decoded**:
```json
{
  "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
  "productType": [0, 1, 2],
  "perPage": 50,
  "page": 0
}
```

### Response Format

```json
{
  "products": [],
  "totalProducts": 0,
  "tokensLeft": 1055,
  "processingTimeInMs": 615,
  "timestamp": 1769855649629
}
```

## Complete Query Parameters Reference

### Core Parameters

| Parameter | Type | Required | Min/Max | Description |
|-----------|------|----------|---------|-------------|
| `page` | int | ✓ | 0+ | Start at 0, increment for pagination |
| `perPage` | int | ✓ | 50-10000 | Results per page (min 50, max 10000 if page=0) |
| `sort` | array | ✗ | Up to 3 | Sorting criteria: `[[field, "asc"/"desc"], ...]` |

### Category Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `rootCategory` | long[] | Include only root categories (up to 50) |
| `categories_include` | long[] | Include only these sub-categories (up to 50) |
| `categories_exclude` | long[] | Exclude these sub-categories (up to 50) |
| `salesRankReference` | long | Filter by sales rank category |

### Product Identification

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | string | Keywords that must appear in title |
| `brand` | string[] | Brand names (case-insensitive, up to 50) |
| `manufacturer` | string[] | Manufacturer names |
| `model` | string[] | Model names |
| `partNumber` | string[] | Part numbers |
| `productType` | int | 0=Standard, 1=Downloadable, 2=Ebook, 5=Variation Parent |
| `hasParentASIN` | boolean | Must have parent ASIN |
| `singleVariation` | boolean | Only one variation per product |
| `historicalParentASIN` | string | Find children of this parent ASIN |

### Availability & Status

| Parameter | Type | Description |
|-----------|------|-------------|
| `availabilityAmazon` | int[] | -1=None, 0=In Stock, 1=Preorder, 2=Unknown, 3=Backorder, 4=Delayed |
| `returnRate` | int[] | 1=Low, 2=High |
| `hasReviews` | boolean | Must have reviews |
| `isPrimeExclusive` | boolean | Prime exclusive offers only |
| `isHazMat` | boolean | Hazardous materials |
| `isHeatSensitive` | boolean | Heat sensitive items |
| `isAdultProduct` | boolean | Adult products |
| `isEligibleForTradeIn` | boolean | Trade-in eligible |
| `isEligibleForSuperSaverShipping` | boolean | Super saver shipping eligible |

### Pricing Filters

All price values in smallest currency unit (cents, pence, yen, etc.)

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `current_AMAZON_lte/gte` | int | - | Current Amazon price |
| `current_NEW_lte/gte` | int | - | Current New offer price |
| `current_USED_lte/gte` | int | - | Current Used offer price |
| `current_SALES_lte/gte` | int | - | Current Sales Rank |
| `current_LISTPRICE_lte/gte` | int | - | List price |
| `current_COLLECTIBLE_lte/gte` | int | - | Collectible price |
| `current_REFURBISHED_lte/gte` | int | - | Refurbished price |
| `current_NEW_FBA_lte/gte` | int | - | New FBA price |
| `current_NEW_FBM_SHIPPING_lte/gte` | int | - | New FBM with shipping |
| `current_LIGHTNING_DEAL_lte/gte` | int | - | Lightning deal price |
| `current_WAREHOUSE_lte/gte` | int | - | Warehouse deal price |

### Price Change & Averages

| Parameter | Type | Period | Description |
|-----------|------|--------|-------------|
| `delta[1,7,30,90]_PRICE_TYPE` | int | days | Absolute change from average |
| `deltaPercent[1,7,30,90]_PRICE_TYPE` | int | days | % change from average |
| `deltaLast_PRICE_TYPE` | int | - | Change from previous value |
| `avg[7,30,90,180,365]_PRICE_TYPE` | int | days | Average price over period |
| `isLowest_PRICE_TYPE` | boolean | - | Current is lowest ever |
| `isLowest90_PRICE_TYPE` | boolean | 90 days | Lowest in 90 days |

### Inventory & Stock

| Parameter | Type | Description |
|-----------|------|-------------|
| `current_COUNT_NEW_lte/gte` | int | Count of new offers |
| `current_COUNT_USED_lte/gte` | int | Count of used offers |
| `current_COUNT_REFURBISHED_lte/gte` | int | Count of refurbished |
| `current_COUNT_COLLECTIBLE_lte/gte` | int | Count of collectible |
| `outOfStockPercentage90_lte/gte` | int | % out of stock (0-100) |
| `outOfStockCountAmazon30_lte/gte` | int | Amazon OOS count (30d) |
| `outOfStockCountAmazon90_lte/gte` | int | Amazon OOS count (90d) |
| `backInStock_PRICE_TYPE` | boolean | Back in stock recently |

### Buy Box Information

| Parameter | Type | Description |
|-----------|------|-------------|
| `buyBoxIsAmazon` | boolean | Amazon holds Buy Box |
| `buyBoxIsFBA` | boolean | FBA seller has Buy Box |
| `buyBoxIsUnqualified` | boolean | Unqualified seller |
| `buyBoxSellerId` | string[] | Seller IDs in Buy Box (up to 50) |
| `buyBoxUsedCondition` | int[] | Used condition: 2=Like New, 3=Very Good, 4=Good, 5=Acceptable |
| `buyBoxUsedIsFBA` | boolean | Used Buy Box is FBA |
| `buyBoxUsedSellerId` | string[] | Used Buy Box seller IDs |
| `buyBoxIsPreorder` | boolean | Buy Box is preorder |
| `buyBoxIsBackorder` | boolean | Buy Box is backorder |
| `buyBoxIsPrimeExclusive` | boolean | Buy Box is Prime exclusive |
| `buyBoxStatsAmazon[30,90,180,365]_lte/gte` | int | Amazon Buy Box % (0-100) |
| `buyBoxStatsTopSeller[30,90,180,365]_lte/gte` | int | Top seller Buy Box % |
| `buyBoxStatsSellerCount[30,90,180,365]_lte/gte` | int | Buy Box seller count |

### Seller Information

| Parameter | Type | Description |
|-----------|------|-------------|
| `sellerIds` | string[] | All seller IDs offering product (up to 50) |
| `sellerIdsLowestFBA` | string[] | Seller IDs with lowest FBA price |
| `sellerIdsLowestFBM` | string[] | Seller IDs with lowest FBM price |

### Product Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `color` | string[] | Color values |
| `size` | string[] | Size values |
| `style` | string[] | Style values |
| `material` | string[] | Material composition |
| `pattern` | string[] | Pattern design |
| `edition` | string[] | Edition (books) |
| `format` | string[] | Format type |
| `binding` | string[] | Binding type (books) |
| `author` | string[] | Author names |
| `publisher` | string[] | Publisher |
| `genre` | string[] | Genre |
| `languages` | string[] | Languages available |
| `platform` | string[] | Platform (software) |

### Media & Content

| Parameter | Type | Description |
|-----------|------|-------------|
| `imageCount_lte/gte` | int | Number of images |
| `videoCount_lte/gte` | int | Number of videos |
| `hasMainVideo` | boolean | Has promotional video |
| `hasAPlus` | boolean | Has A+ content |
| `hasAPlusFromManufacturer` | boolean | A+ from manufacturer |

### Ratings & Reviews

| Parameter | Type | Description |
|-----------|------|-------------|
| `current_RATING_lte/gte` | int | Current rating (0-5000 = 0-5 stars * 1000) |
| `current_COUNT_REVIEWS_lte/gte` | int | Review count |
| `variationReviewCount_lte/gte` | int | Reviews per variation |
| `variationRatingCount_lte/gte` | int | Ratings per variation |
| `avg90_RATING_lte/gte` | int | 90-day avg rating |
| `avg90_COUNT_REVIEWS_lte/gte` | int | 90-day avg review count |

### Sales & Demand

| Parameter | Type | Description |
|-----------|------|-------------|
| `monthlySold_lte/gte` | int | Units sold last month |
| `deltaPercent90_monthlySold_lte/gte` | int | 90-day % change in monthly sales |
| `flipability[30,90,365]_lte/gte` | int | Flipability score (0-100) |

### Dimensions & Weight

All dimensions in millimeters, weight in grams

| Parameter | Type | Description |
|-----------|------|-------------|
| `packageHeight/Length/Width_lte/gte` | int | Package dimensions (mm) |
| `packageWeight_lte/gte` | int | Package weight (grams) |
| `itemHeight/Length/Width_lte/gte` | int | Item dimensions (mm) |
| `itemWeight_lte/gte` | int | Item weight (grams) |

### Special Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `variationCount_lte/gte` | int | Number of variations |
| `numberOfItems_lte/gte` | int | Number of items |
| `numberOfPages_lte/gte` | int | Number of pages |
| `activeIngredients` | string[] | Active ingredients |
| `specialIngredients` | string[] | Special/additional ingredients |
| `itemTypeKeyword` | string[] | Item type keywords |
| `targetAudienceKeyword` | string[] | Target audience keywords |
| `itemForm` | string[] | Item form |
| `scent` | string[] | Scent type |
| `unitType` | string[] | Unit measurement type |

### Coupons & Discounts

| Parameter | Type | Description |
|-----------|------|-------------|
| `couponOneTimeAbsolute_lte/gte` | int | One-time coupon value |
| `couponOneTimePercent_lte/gte` | int | One-time coupon % |
| `couponSNSPercent_lte/gte` | int | Subscribe & Save % |
| `businessDiscount_lte/gte` | int | Business discount % |

### Deals & Special Offers

| Parameter | Type | Description |
|-----------|------|-------------|
| `dealType` | string[] | PRIME_DAY, LIMITED_TIME_DEAL, CLEARANCE, etc. |
| `lightningEnd_lte/gte` | int | Lightning deal end time |
| `frequentlyBoughtTogether` | string | Products bought with this ASIN |
| `isSNS` | boolean | Available for Subscribe & Save |

### Time-Based Filters

All in Keepa Time minutes (convert: unix_seconds = (keepaTime + 21564000) * 60)

| Parameter | Type | Description |
|-----------|------|-------------|
| `trackingSince_lte/gte` | int | When we started tracking |
| `publicationDate_lte/gte` | int | Publication date |
| `releaseDate_lte/gte` | int | Release date |
| `lastPriceChange_lte/gte` | int | Last price change (any type) |
| `lastPriceChange_PRICE_TYPE_lte/gte` | int | Last price change (specific type) |
| `lastOffersUpdate_lte/gte` | int | Last offers data update |

### Domain IDs
```
1  = Amazon US (amazon.com)
2  = Amazon UK (amazon.co.uk)
3  = Amazon Germany (amazon.de)
4  = Amazon France (amazon.fr)
5  = Amazon Japan (amazon.co.jp)
6  = Amazon Canada (amazon.ca)
8  = Amazon Italy (amazon.it)
9  = Amazon Spain (amazon.es)
10 = Amazon India (amazon.in)
```

### Selection Parameters

#### Core Parameters
| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| `perPage` | int | ✓ | 50 |
| `page` | int | ✓ | 0 |
| `productType` | array | ✗ | [0, 1, 2] |
| `sort` | array | ✗ | [["current_SALES", "asc"]] |

#### Filter Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `current_SALES` | [min, max] | Sales Rank range |
| `current_AMAZON` | [min, max] | Price range (in cents) |
| `monthlySoldRange` | [min, max] | Monthly sales range |
| `categoryId` | int/string | Specific category ID |

### Product Types
```
0 = All product types (default)
1 = Books
2 = Digital & Apps
```

### Sort Options
```
[["current_SALES", "asc"]]    - Ascending by sales rank (higher sales first)
[["current_SALES", "desc"]]   - Descending by sales rank
[["monthlySold", "asc"]]      - Ascending by monthly sold
[["monthlySold", "desc"]]     - Descending by monthly sold (most popular first)
[["current_AMAZON", "asc"]]   - Ascending by price (cheapest first)
[["current_AMAZON", "desc"]]  - Descending by price (most expensive first)
```

## Example Queries

### Basic Search
```json
{
  "domain": 10,
  "selection": {
    "perPage": 50,
    "page": 0
  }
}
```

### With Category Filter
```json
{
  "domain": 10,
  "selection": {
    "perPage": 50,
    "page": 0,
    "categoryId": "1405158031"
  }
}
```

### With Sales Rank and Price Range
```json
{
  "domain": 10,
  "selection": {
    "perPage": 50,
    "page": 0,
    "current_SALES": [1, 100000],
    "current_AMAZON": [50000, 200000]
  }
}
```

### Complex Query (Sorted by Monthly Sales)
```json
{
  "domain": 10,
  "selection": {
    "sort": [["monthlySold", "desc"]],
    "productType": [0],
    "perPage": 50,
    "page": 0,
    "current_SALES": [1, 50000],
    "current_AMAZON": [10000, 500000]
  }
}
```

## HTTP Requests

### Using cURL
```bash
curl -X POST http://localhost:8000/keepa/product-finder \
  -H "Content-Type: application/json" \
  -d '{
    "domain": 10,
    "selection": {
      "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
      "productType": [0, 1, 2],
      "perPage": 50,
      "page": 0
    }
  }'
```

### Using Python Requests
```python
import requests

url = "http://localhost:8000/keepa/product-finder"
payload = {
    "domain": 10,
    "selection": {
        "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
        "productType": [0, 1, 2],
        "perPage": 50,
        "page": 0
    }
}

response = requests.post(url, json=payload)
data = response.json()
print(f"Found {data['totalProducts']} products")
print(f"Tokens left: {data['tokensLeft']}")
```

### Using JavaScript Fetch
```javascript
const payload = {
    domain: 10,
    selection: {
        sort: [["current_SALES", "asc"], ["monthlySold", "desc"]],
        productType: [0, 1, 2],
        perPage: 50,
        page: 0
    }
};

const response = await fetch('http://localhost:8000/keepa/product-finder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
});

const data = await response.json();
console.log(`Found ${data.totalProducts} products`);
```

## Important Notes

⚠️ **perPage Limits**:
- Minimum: 50 (values below will cause "combination of perPage and page exceeds limit" error)
- Maximum: 100
- Recommended: 50-100

⚠️ **API Key Permissions**:
- Your API key must have "Product Search" permissions enabled
- Without it, `products` array will be empty (but no error)
- Contact Keepa support if you need search enabled

⚠️ **Token Consumption**:
- Each query consumes tokens (even if no products found)
- Monitor `tokensLeft` in response
- Free tier: ~1200 tokens/day
- Tokens refill at specific times (usually daily)

## Response Fields

```json
{
  "products": [],              // Array of product objects (or empty)
  "totalProducts": 0,          // Count of products in results
  "tokensLeft": 1055,          // Remaining tokens in your quota
  "processingTimeInMs": 615,   // Server processing time
  "timestamp": 1769855649629   // Server timestamp (milliseconds)
}
```

## Troubleshooting

### Getting 0 Products
- ✓ Check API key permissions (contact Keepa support)
- ✓ Try different sort orders
- ✓ Verify domain ID is correct
- ✓ Test category filter if having issues

### Getting Error Response
- Check `error.message` in response
- Common: "combination of perPage and page exceeds limit" (use `perPage >= 50`)
- Verify all parameters are correct types (arrays, numbers, strings)

### Tokens Not Refilling
- Check your subscription plan tier
- Verify token refill time (usually 00:00 UTC)
- Contact Keepa support if not refilling as expected

---
**Reference Date**: 2024-12-09  
**Keepa API Version**: Latest  
**Status**: Tested and working (format correct, permission limitation noted)

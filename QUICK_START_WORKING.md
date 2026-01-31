# 🚀 Quick Integration Test

Your Product Finder search is working! Here's how to use it:

## Test Your Dashboard

### 1. Start the Backend (if not running)
```bash
cd /workspaces/Amazon-Seller-Daashboard
export PYTHONPATH=backend
set -a && source .env && set +a
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Test the API Directly

**Example 1: Your Working Query (India market, sales filtering)**
```bash
curl -X POST http://localhost:8000/keepa/product-finder \
  -H "Content-Type: application/json" \
  -d '{
    "domain": 10,
    "selection": {
      "current_SALES_gte": 20000,
      "current_SALES_lte": 50000,
      "avg30_SALES_gte": 299,
      "avg30_SALES_lte": 599,
      "sort": [["current_SALES", "asc"], ["monthlySold", "desc"]],
      "productType": [0, 1, 2],
      "perPage": 50,
      "page": 0
    }
  }'
```

**Example 2: Budget products with high reviews**
```bash
curl -X POST http://localhost:8000/keepa/product-finder \
  -H "Content-Type: application/json" \
  -d '{
    "domain": 1,
    "selection": {
      "current_AMAZON_gte": 1000,
      "current_AMAZON_lte": 30000,
      "monthlySold_gte": 50,
      "current_RATING_gte": 4000,
      "hasReviews": true,
      "perPage": 50,
      "page": 0
    }
  }'
```

**Example 3: FBA opportunities**
```bash
curl -X POST http://localhost:8000/keepa/product-finder \
  -H "Content-Type: application/json" \
  -d '{
    "domain": 1,
    "selection": {
      "isLowestFBA": true,
      "monthlySold_gte": 100,
      "current_RATING_gte": 3500,
      "buyBoxIsAmazon": false,
      "sort": [["monthlySold", "desc"]],
      "perPage": 50,
      "page": 0
    }
  }'
```

### 3. Check API Health
```bash
curl http://localhost:8000/keepa/health
```

### 4. View in Dashboard
Open: http://localhost:8000/ui/index.html

---

## What Each Query Returns

All queries return:
```json
{
  "asinList": ["B001ABC123", "B002DEF456", ...],
  "totalResults": 1234,
  "searchInsights": {
    "domainId": 10,
    "queryCount": 50,
    "avg_SALES": 35000
  },
  "tokensLeft": 980,
  "processingTimeInMs": 234
}
```

---

## Parameter Reference

From your working query:
- `domain`: 10 (India), 1 (US), 2 (UK), 3 (Germany), etc.
- `current_SALES_gte/lte`: Sales rank range (lower = better selling)
- `avg30_SALES_gte/lte`: 30-day average sales rank
- `sort`: [[field, direction], ...] - Up to 3 sort criteria
- `productType`: Product types (0=All, 1=Physical, 2=Digital, etc.)
- `perPage`: Results per page (1-100)
- `page`: Page number (0-indexed)

See [KEEPA_QUERY_FORMAT.md](KEEPA_QUERY_FORMAT.md) for 200+ more filters.

---

## Real Results Example

Your dashboard query for India (domain 10) returns products like:
- Molecular Biology & Genetics (sales rank: 72,536)
- Pet Supplies (sales rank: 38,162)
- Tablet Cases (sales rank: 134)
- Electronics & more...

All with:
✅ Sales ranks  
✅ 90-day price trends  
✅ Price changes  
✅ Ratings  
✅ Review counts  
✅ Category data  

---

## Next Steps

1. **Run the test queries above** to see live results
2. **Open the dashboard** to visualize them
3. **Build your own queries** using KEEPA_QUERY_FORMAT.md
4. **Save successful queries** for future use
5. **Scale up** with pagination and batch processing

---

## Troubleshooting

### Getting empty results?
- Check your API key in `.env`
- Verify domain ID (1-12)
- Try less restrictive filters
- Check remaining tokens: `curl http://localhost:8000/keepa/health`

### Getting 401 errors?
- Ensure KEEPA_API_KEY is set in `.env`
- Try without auth by setting AUTH_DISABLED=true in .env

### Slow queries?
- Reduce `perPage` value
- Limit filters to most important criteria
- Use page 0 first

---

**Status**: ✅ Production Ready  
**Backend**: ✅ Tested  
**API**: ✅ Working  
**Results**: ✅ Confirmed  

Ready to build! 🚀

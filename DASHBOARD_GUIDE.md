# Amazon Product Finder Dashboard - User Guide

## Overview
A professional Product Finder tool powered by the Keepa API for sourcing Amazon products across multiple marketplaces.

## Features

### ✅ Working Features
- **Multi-Marketplace Support**: Search across 10 Amazon domains (US, UK, Germany, France, Japan, Canada, Italy, Spain, India)
- **Category Browsing**: Browse product categories for each marketplace
- **Health Check**: Real-time connection status and token balance display
- **Professional UI**: Modern dark theme with responsive design
- **API Integration**: Seamless integration with Keepa Product Finder API

### ⚠️ Current Limitation
- **Product Search**: Returns 0 products (requires premium Keepa subscription with search permissions)

## Getting Started

### 1. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8000/ui/index.html
```

### 2. Check API Status
- Look at the top status bar
- Verify "Keepa: [N] tokens" is displayed
- Connection indicator should be green

### 3. Select a Marketplace
1. Choose an Amazon domain from the dropdown
2. Wait for categories to load (~2-3 seconds)

### 4. Browse Categories
1. Select a category from the dropdown
2. Or leave blank to search all categories

### 5. Set Filters (Optional)
- **Sales Rank Range**: Min and max sales rank thresholds
- **Price Range**: Min and max prices in your local currency
- **Results Per Page**: 10-100 products per page

### 6. Search for Products
Click "Search Products" button to execute the search

## Troubleshooting

### "No products found" Message
**Cause**: Your Keepa API key doesn't have access to the product search endpoint.

**Solutions**:
1. **Check Keepa Plan**: Log into keepa.com and verify your subscription includes "Product Search API"
2. **Contact Keepa**: Request activation of the `/query` endpoint
3. **Try Alternative**: Use Keepa's web interface for searching, then lookup individual ASINs

### "API Error" Message
**Possible Causes**:
- Invalid filter combination (e.g., perPage < 100)
- Token balance exhausted
- Network connectivity issue

**Solutions**:
- Refresh the page (Ctrl+F5)
- Wait a few seconds for token refill
- Check your internet connection
- See the displayed error message for details

### Slow Performance
**Possible Causes**:
- Large result set (100+ products)
- Network latency
- Browser rendering delay

**Solutions**:
- Reduce "Results per Page" value
- Use more specific filters
- Check your internet speed

## Token System

### What are Tokens?
Tokens are Keepa's rate-limit currency. Each API call costs tokens.
- **1 token** = 1 category lookup
- **1 token** = 1 product details fetch
- **1+ tokens** = 1 search query (depending on result size)

### Token Balance
- View current balance in the top-right corner
- Tokens refill automatically over time (usually daily)
- Free tier: ~1200 tokens/day
- Premium tiers: Higher limits

### Conserving Tokens
- Use specific filters to narrow results
- Increase results per page (fewer requests)
- Avoid repeated searches

## API Endpoints Reference

### Product Finder Search
```
POST /keepa/product-finder
Content-Type: application/json

{
  "domain": 10,
  "selection": {
    "perPage": 100,
    "page": 0,
    "category": "1405158031",
    "salesRankRange": [1, 100000],
    "priceRange": [500, 50000]
  }
}
```

### Category Listing
```
GET /keepa/category?domain=10&category=0&include_parents=0
```

### Health Check
```
GET /keepa/health
```

## Domain ID Mapping
| Domain | ID | Region |
|--------|-------|--------|
| Amazon US | 1 | United States |
| Amazon UK | 2 | United Kingdom |
| Amazon DE | 3 | Germany |
| Amazon FR | 4 | France |
| Amazon JP | 5 | Japan |
| Amazon CA | 6 | Canada |
| Amazon IT | 8 | Italy |
| Amazon ES | 9 | Spain |
| Amazon IN | 10 | India |

## FAQ

**Q: Why am I getting 0 products with no error?**
A: Your API key likely doesn't have search permissions. Contact Keepa support.

**Q: How can I search without product search access?**
A: You can use Keepa's web interface to search, then lookup individual products by ASIN.

**Q: Do categories work?**
A: Yes! Category lookup works on all plans. Browse categories and select specific ones for targeted research.

**Q: What's the maximum results per page?**
A: 100 products per page. This is a Keepa API limit.

**Q: How often do tokens refill?**
A: Typically daily at 00:00 UTC, though this depends on your subscription plan.

## Advanced Usage

### Using the Category API
If you have category IDs, you can fetch sub-categories:
```
GET /keepa/category?domain=10&category=1405158031&include_parents=0
```

### Batch Lookups
For looking up multiple ASINs at once, use the health endpoint to monitor token usage:
```
GET /keepa/health
```

## Support & Contact
- **Keepa Support**: https://keepa.com/contact
- **API Documentation**: https://keepa.com/api
- **Dashboard Issues**: Check the browser console (F12) for error details

---
**Last Updated**: 2024-12-09  
**Version**: 1.0  
**Status**: Live with API limitations

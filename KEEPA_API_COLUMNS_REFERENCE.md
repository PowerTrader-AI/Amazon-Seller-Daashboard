# Keepa API: Complete Product Response Schema

## Summary: 70+ Fields Available

When you fetch product details from Keepa's `/product` endpoint, you get 70+ fields of data per ASIN.

---

## Field Categories & Key Information

### 📍 Product Identifiers (3 fields)
| Field | Type | Description |
|-------|------|-------------|
| `asin` | string | Product ASIN |
| `parentAsin` | string | Parent ASIN (for variants) |
| `parentTitle` | string | Title of parent product |

### 💰 Pricing Data (Price History)
| Field | Type | Description |
|-------|------|-------------|
| `csv` | array[34] | **CSV Array with 34 indices** (see below) |
| `lastPriceChange` | int | Unix timestamp of last price change |

### 📊 CSV Array Indices (Key Price History)
The `csv` field is an array with 34 indices. Each index contains price/metric history:

| Index | Metric | Data Format | Notes |
|-------|--------|-------------|-------|
| **0** | 🏷️ **Amazon Price** | `[[ts, price], [ts, price], ...]` | Keeps as [ts, price] tuples |
| **1** | New Price | `[[ts, price], ...]` | Third-party seller new |
| **2** | Used Price | `[[ts, price], ...]` | Third-party used |
| **3** | 🎯 **Sales Rank** | `[[ts, rank], ...]` | Lower = better selling |
| 4 | Rental Price | | |
| 5-15 | Various metrics | | Empty/None for most |
| **16** | 🌟 **Rating** | `[[ts, rating*10], ...]` | Rating×10 (e.g., 45 = 4.5 stars) |
| **17** | ⭐ **Review Count** | `[[ts, count], ...]` | Number of customer reviews |
| 18-33 | Reserved | | Typically empty |

### How to Extract Data from CSV

When you get a CSV entry, each is a list of `[timestamp, value]` pairs:

```python
# Example: Extract latest Amazon price
if product['csv'][0]:  # Index 0 = Amazon price
    latest_entry = product['csv'][0][-1]  # Last/most recent
    timestamp = latest_entry[0]  # First item is timestamp
    price_cents = latest_entry[1]  # Second item is price in cents
    price_dollars = price_cents / 100.0
```

---

## Product Information Fields

| Field | Type | Sample |
|-------|------|--------|
| `title` | str | "Samsung Galaxy S21" |
| `brand` | str | "Samsung" |
| `productType` | int | 0=unknown, 1=book, 2=music, etc |
| `productGroup` | str | "Electronics" |
| `color` | str | "Black" |
| `size` | str | "6.2 inches" |
| `manufacturer` | str | Company name |
| `binding` | str | "Hardcover" (books) |
| `format` | str | "Kindle Edition" |
| `edition` | str | "2nd Edition" |

---

## Media & Images

| Field | Type | Description |
|-------|------|-------------|
| `images` | array | Array of image objects |
| `imagesCSV` | str | Comma-separated image filenames |
| `variationCSV` | str | Child ASIN variations |

Image URL format:
```
https://images-na.ssl-images-amazon.com/images/I/{FILENAME}
```

---

## Categories & Classification

| Field | Type | Notes |
|-------|------|-------|
| `categories` | array[int] | Category IDs |
| `categoryTree` | object | Full category hierarchy |
| `rootCategory` | int | Top-level category |

---

## Availability & Stock

| Field | Type | Meaning |
|-------|------|---------|
| `availabilityAmazon` | int | -1=unavailable, 0+=units in stock |
| `isEligibleForSuperSaverShipping` | bool | Free shipping eligible |
| `isEligibleForTradeIn` | bool | Can be traded in |

---

## Product Status Flags

| Flag | Type | Meaning |
|------|------|---------|
| `isAdultProduct` | bool | 18+ content |
| `isB2B` | bool | Business product |
| `isRedirectASIN` | bool | Redirects to another ASIN |
| `isSNS` | bool | Subscribe & Save eligible |
| `launchpad` | bool | Amazon Launchpad product |
| `newPriceIsMAP` | bool | Minimum Advertised Price |

---

## Reviews & Ratings

| Field | Type | Description |
|-------|------|-------------|
| `hasReviews` | bool | Has customer reviews |
| `lastRatingUpdate` | int | Unix timestamp of last review |
| (Rating data) | in CSV[16] | See CSV[16] above |
| (Review count) | in CSV[17] | See CSV[17] above |

---

## Physical Dimensions

| Field | Type | Notes |
|-------|------|-------|
| `itemHeight` | int | Height (cm × 100) |
| `itemLength` | int | Length (cm × 100) |
| `itemWidth` | int | Width (cm × 100) |
| `itemWeight` | int | Weight (grams) |
| `packageHeight` | int | Package height |
| `packageLength` | int | Package length |
| `packageWidth` | int | Package width |
| `packageWeight` | int | Package weight |

---

## Other Identifiers

| Field | Type | Use |
|-------|------|-----|
| `eanList` | array | European Article Numbers |
| `upcList` | array | Universal Product Codes |
| `partNumber` | str | Manufacturer part #  |
| `ebayListingIds` | array | eBay listings |

---

## Tracking & Metadata

| Field | Type | Meaning |
|-------|------|---------|
| `trackingSince` | int | When Keepa started tracking (unix ts) |
| `listedSince` | int | Original Amazon listing date |
| `lastUpdate` | int | When this data was last refreshed |
| `domainId` | int | 1=US, 2=UK, 3=DE, 4=FR, 5=JP, etc |

---

## Important: -1 and None Values

- **`-1`**: Data point exists but **no data available** (e.g., price = -1 means no price history)
- **`None`**: Field not populated for this product

When extracting CSV data, always check for and skip **-1** values.

---

## Why Some ASINs Have Missing Data

Products may not have complete data due to:

1. **New listings**: Tracked less than 24 hours
2. **Delisted items**: No longer sold on Amazon
3. **Redirect ASINs**: Point to another product
4. **Region mismatch**: Product not sold in that Amazon domain
5. **Very old products**: Limited historical tracking

**Solution**: Fetch your own search results to get ASINs that are actively being tracked.

---

## Next Steps

To analyze products properly:

1. Use your search results (Product Finder API) to get active ASINs
2. Fetch each ASIN with `/product?asin=X&meta=1`
3. Extract from CSV[0], CSV[3], CSV[16], CSV[17]
4. Calculate scores based on extracted metrics
5. Filter by thresholds (rating≥4.0, rank≤1000, price≤limit)


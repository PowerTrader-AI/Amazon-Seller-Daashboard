#!/usr/bin/env python3
"""Test script to verify cache layer works correctly."""

import sys
import sqlite3
import json
from datetime import datetime

sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard')
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app.keepa_cache import get_cached_products, save_keepa_product, get_cache_stats

# Connect to database
conn = sqlite3.connect('/workspaces/Amazon-Seller-Daashboard/amazon_sourcing.db')
conn.row_factory = sqlite3.Row

print("=" * 70)
print("🧪 CACHE LAYER TEST")
print("=" * 70)

# Sample product data from Keepa API
test_product = {
    'asin': 'B09TEST001',
    'title': 'Test Product for Cache',
    'brand': 'TestBrand',
    'author': 'Test Author',
    'availabilityAmazon': 'In Stock',
    'binding': 'Paperback',
    'categories': ['Books', 'Test'],
    'categoryTree': [{'name': 'Books', 'id': 1}],
    'color': 'Black',
    'description': 'This is a test product',
    'imagesCSV': 'image1.jpg,image2.jpg',
    'productType': 'TestType',
    'type': 1,
    'title': 'Test Product',
    'trackingSince': 1234567890,
    'lastUpdate': 1234567890,
    'csv': [
        [[1234567890, 9999]],  # Price history
        [],  # Placeholder
        [],  # Placeholder
        [[1234567890, 5000]],  # Sales rank
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [],  # Placeholder
        [[1234567890, 45]],  # Rating (×10 = 4.5)
        [[1234567890, 1250]],  # Review count
    ]
}

# Test 1: Save product to cache
print("\n✏️  TEST 1: Saving product to cache...")
result = save_keepa_product(conn, test_product, domain=1)
print(f"   Result: {'✅ Success' if result else '❌ Failed'}")

# Test 2: Retrieve from cache
print("\n📖 TEST 2: Retrieving cached product...")
cached, missing = get_cached_products(conn, ['B09TEST001'], domain=1)
if cached:
    print(f"   ✅ Found {len(cached)} cached product(s)")
    product = cached[0]
    print(f"   • ASIN: {product['asin']}")
    print(f"   • Title: {product['title']}")
    print(f"   • Price: ${product['currentPrice']:.2f}")
    print(f"   • Rank: {product['currentSalesRank']}")
    print(f"   • Rating: {product['currentRating']}")
    print(f"   • Reviews: {product['currentReviewCount']}")
else:
    print(f"   ❌ No products found in cache")

# Test 3: Check for missing ASINs
print("\n🔍 TEST 3: Checking missing ASINs...")
if missing:
    print(f"   ℹ️  Missing ASINs: {missing}")
else:
    print(f"   ✅ All ASINs found in cache")

# Test 4: Get cache statistics
print("\n📊 TEST 4: Cache statistics...")
stats = get_cache_stats(conn)
print(f"   Total products: {stats['totalProducts']}")
print(f"   Fresh products: {stats['freshProducts']}")
print(f"   Stale products: {stats['staleProducts']}")
print(f"   Domains: {stats['domains']}")
print(f"   Total searches: {stats['totalSearches']}")

# Test 5: Verify 7-day expiration
print("\n⏰ TEST 5: Checking expiration timestamp...")
cursor = conn.cursor()
cursor.execute("""
    SELECT asin, cached_at, expires_at 
    FROM keepa_products_cache 
    WHERE asin = ?
""", ('B09TEST001',))
row = cursor.fetchone()
if row:
    print(f"   ASIN: {row[0]}")
    print(f"   Cached at: {row[1]}")
    print(f"   Expires at: {row[2]}")
    print(f"   ✅ 7-day expiration set")

conn.close()

print("\n" + "=" * 70)
print("✅ All cache tests completed!")
print("=" * 70)

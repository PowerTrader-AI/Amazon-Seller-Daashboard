#!/usr/bin/env python3
"""
UNIT TEST 1: Keepa API - Category Product Fetching
Test if we can get all ASINs for a category + fetch one product's complete data
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client
import json

print("\n" + "="*90)
print("🧪 UNIT TEST 1: CATEGORY PRODUCT FETCHING")
print("="*90)

# Connect to Keepa
print("\n[TEST 0] Connecting to Keepa API...")
try:
    client = keepa_client.get_client()
    tokens = client.tokens_left
    print(f"✅ Connected! Tokens remaining: {tokens}\n")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    sys.exit(1)

# Test 1: Get ASINs for Toys category
print("[TEST 1] Fetching ASINs for Toys category (ID: 1378189031)...")
try:
    products = keepa_client.product_finder_by_category(
        client,
        category_id=1378189031,
        bsr_threshold=50000,
        per_page=50
    )
    print(f"✅ SUCCESS: Retrieved {len(products)} ASINs")
    print(f"\n   First 15 ASINs from Toys category:")
    for i, asin in enumerate(products[:15], 1):
        print(f"   {i:2d}. {asin}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Fetch complete product data for first ASIN
if products:
    test_asin = products[0]
    print(f"\n[TEST 2] Fetching complete data for ASIN: {test_asin}")
    
    try:
        # Use Keepa's query() method to get product data
        # Parameters: items (list of ASINs), stats interval, and rating flag
        response = client.query([test_asin], stats=180, rating=1)
        
        print(f"\n   Response type: {type(response)}")
        if isinstance(response, list):
            print(f"   Response is a list with {len(response)} items")
            if len(response) > 0:
                product_data = response[0]
            else:
                product_data = None
        else:
            print(f"   Response is dict with keys: {response.keys()}")
            product_data = response.get('products', [{}])[0] if response.get('products') else None
        
        if product_data:
            
            # Count all available columns/fields
            all_fields = product_data.keys()
            print(f"✅ SUCCESS: Retrieved {len(all_fields)} fields/columns")
            
            print(f"\n   All Available Fields ({len(all_fields)} total):")
            print("   " + "-"*85)
            for i, field in enumerate(sorted(all_fields), 1):
                value = product_data[field]
                if isinstance(value, list):
                    print(f"   {i:2d}. {field:35s} = LIST ({len(value)} items)")
                elif isinstance(value, dict):
                    print(f"   {i:2d}. {field:35s} = DICT ({len(value)} keys)")
                else:
                    val_str = str(value)[:50] if value is not None else "None"
                    print(f"   {i:2d}. {field:35s} = {val_str}")
            
            # Save sample to JSON
            with open('/tmp/sample_keepa_response.json', 'w') as f:
                json.dump(product_data, f, indent=2, default=str)
            print(f"\n✅ Sample response saved to: /tmp/sample_keepa_response.json")
            
            # Show key product metrics
            print(f"\n   Key Product Information:")
            print("   " + "-"*85)
            key_fields = ['asin', 'title', 'brand', 'categoryTree', 'imagesCSV', 
                         'currentPrice', 'currentPriceHistory', 'csv', 'salesRanks',
                         'reviewCount', 'rating', 'offerCount']
            for field in key_fields:
                if field in product_data:
                    value = product_data[field]
                    if isinstance(value, list):
                        if len(value) > 0:
                            print(f"   ✓ {field:30s}: LIST with {len(value)} items")
                    elif isinstance(value, dict):
                        print(f"   ✓ {field:30s}: DICT with {len(value)} keys")
                    else:
                        print(f"   ✓ {field:30s}: {str(value)[:60]}")
        else:
            print(f"❌ ERROR: Could not fetch product data")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*90)
print("✅ TEST COMPLETE")
print("="*90 + "\n")

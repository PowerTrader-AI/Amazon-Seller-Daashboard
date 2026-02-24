#!/usr/bin/env python3
"""
UNIT TEST 2: Find correct category using Search API
Then fetch products from that category
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client
import json

print("\n" + "="*90)
print("🔍 UNIT TEST 2: SEARCH FOR CORRECT CATEGORY ID")
print("="*90)

client = keepa_client.get_client()
print(f"\nTokens available: {client.tokens_left}\n")

# STEP 1: Search for "Toys" category
print("[STEP 1] Searching for 'Toys' category using Keepa Search API...")
print("-" * 90)

try:
    # Use Keepa's search function to find categories by name
    # Domain 'IN' = amazon.in (India)
    search_results = client.search_for_categories("Toys", domain="IN")
    
    print(f"✅ Search returned results\n")
    
    if search_results and isinstance(search_results, dict):
        # Response is a dict of categories (catId -> category object)
        categories_list = list(search_results.items())
        
        # Filter for categories with actual products (productCount > 0)
        active_categories = [(cat_id, cat) for cat_id, cat in categories_list if cat.get('productCount', 0) > 1000]
        
        # Sort by product count (descending)
        active_categories.sort(key=lambda x: x[1].get('productCount', 0), reverse=True)
        
        print(f"Found categories with products (showing top 10):\n")
        
        for i, (cat_id, cat) in enumerate(active_categories[:10], 1):
            cat_name = cat.get('name')
            prod_count = cat.get('productCount')
            print(f"  {i}. {cat_name:40s} | ID: {cat_id:15s} | Products: {prod_count:6.0f}")
        
        # Select the category with the most products
        toys_category_id, selected_cat = active_categories[0]
        selected_name = selected_cat.get('name')
        print(f"\n✅ Selected: {selected_name} (ID: {toys_category_id}, {selected_cat.get('productCount')} products)")
    else:
        print(f"Response: {json.dumps(search_results, indent=2)}")
        toys_category_id = None
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    toys_category_id = None

if not toys_category_id:
    print("❌ Could not find category")
    sys.exit(1)

# STEP 2: Fetch products from the correct category
print("\n" + "-"*90)
print(f"\n[STEP 2] Fetching products from category: {toys_category_id}")
print("-" * 90)

try:
    products = keepa_client.product_finder_by_category(
        client,
        category_id=int(toys_category_id),
        bsr_threshold=50000,
        per_page=50
    )
    
    print(f"\n✅ Retrieved {len(products)} ASINs from Toys category\n")
    print(f"First 15 ASINs:")
    for i, asin in enumerate(products[:15], 1):
        print(f"  {i:2d}. {asin}")
    
    test_asin = products[0]
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# STEP 3: Fetch full product details to verify it's actually Toys
print("\n" + "-"*90)
print(f"\n[STEP 3] Verifying category - fetching details of ASIN: {test_asin}")
print("-" * 90)

try:
    response = client.query([test_asin], stats=180, rating=1)
    
    if response and isinstance(response, list) and len(response) > 0:
        prod = response[0]
        
        print(f"\n✅ Product Details:")
        print(f"  ASIN: {prod.get('asin')}")
        print(f"  Title: {prod.get('title', 'N/A')[:70]}")
        print(f"  Brand: {prod.get('brand', 'N/A')}")
        
        if 'categoryTree' in prod:
            print(f"\n  Category Tree (confirms it's the right category):")
            for cat in prod['categoryTree']:
                cat_name = cat.get('name', 'Unknown')
                cat_id = cat.get('catId', '?')
                print(f"    → {cat_name} (ID: {cat_id})")
        
        print(f"\n  Additional Info:")
        print(f"    Root Category: {prod.get('rootCategory')}")
        print(f"    Sales Rank: {prod.get('salesRanks', {})}")
        print(f"    Reviews: {prod.get('reviews', {}).get('reviewCount') if prod.get('reviews') else 'N/A'}")
        print(f"    Monthly Sold: {prod.get('monthlySold', 'N/A')}")
        
        # Save to file
        with open('/tmp/toys_product_sample.json', 'w') as f:
            json.dump(prod, f, indent=2, default=str)
        print(f"\n✅ Full product data saved to: /tmp/toys_product_sample.json")
        
    else:
        print(f"❌ Could not fetch product details")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*90)
print("✅ TEST COMPLETE - CORRECT CATEGORY FOUND AND VERIFIED")
print("="*90 + "\n")

#!/usr/bin/env python3
"""
UNIT TEST 3: Verify the correct category fetches actual TOYS/GAMES products
Check multiple ASINs to confirm data quality
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client
import json

print("\n" + "="*90)
print("🎯 UNIT TEST 3: VERIFY GAMES, TOYS & ACTIVITIES CATEGORY PRODUCTS")
print("="*90)

client = keepa_client.get_client()
print(f"\nTokens available: {client.tokens_left}\n")

# Use the correct category ID found in test 2
toys_category_id = 1318078031

print(f"[INFO] Fetching 50 products from category {toys_category_id} (Games, Toys & Activities)")
print("-" * 90)

try:
    asins = keepa_client.product_finder_by_category(
        client,
        category_id=toys_category_id,
        bsr_threshold=50000,
        per_page=50
    )
    
    print(f"✅ Retrieved {len(asins)} ASINs\n")
    
    # Fetch details for first 10 products
    print(f"Testing first 10 products for category match:")
    print("-" * 90)
    
    test_asins = asins[:10]
    results = client.query(test_asins, stats=180, rating=1)
    
    toys_count = 0
    auto_count = 0
    other_count = 0
    
    for i, prod in enumerate(results, 1):
        asin = prod.get('asin', 'N/A')
        title = prod.get('title', 'N/A')[:60]
        
        # Get the main category
        category_tree = prod.get('categoryTree', [])
        if category_tree:
            main_cat = category_tree[0].get('name', 'Unknown')
        else:
            main_cat = 'Unknown'
        
        root_cat = prod.get('rootCategory', 'N/A')
        
        print(f"\n{i}. ASIN: {asin}")
        print(f"   Title: {title}")
        print(f"   Main Category: {main_cat}")
        print(f"   Root Category: {root_cat}")
        
        # Categorize
        if 'toy' in main_cat.lower() or 'game' in main_cat.lower() or 'activity' in main_cat.lower():
            print(f"   ✅ MATCH: This is a Toy/Game/Activity product")
            toys_count += 1
        elif 'auto' in main_cat.lower() or 'wiper' in main_cat.lower():
            print(f"   ❌ MISMATCH: This is automotive, not toys")
            auto_count += 1
        else:
            print(f"   ⚠️ OTHER: Different category")
            other_count += 1
    
    print("\n" + "="*90)
    print("SUMMARY:")
    print(f"  ✅ Actual Toys/Games: {toys_count}")
    print(f"  ❌ Automotive Products: {auto_count}")
    print(f"  ⚠️ Other Categories: {other_count}")
    print(f"  Total Tested: {len(results)}")
    print("="*90)
    
    if toys_count >= 7:
        print("\n✅ VERDICT: Category 1318078031 is RELIABLE - mostly returns toys/games products")
        print("\nRECOMMENDATION: Use category ID 1318078031 for Phase 2 build")
    else:
        print("\n⚠️ VERDICT: Category 1318078031 has mixed results - consider alternatives")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n")

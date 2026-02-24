#!/usr/bin/env python3
"""
UNIT TEST 5: Using CORRECT Toys & Games Category ID from Keepa
Extract products from root category 1350388031 and subcategories
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client
import json

print("\n" + "="*90)
print("✅ UNIT TEST 5: CORRECT TOYS & GAMES CATEGORY (ID: 1350388031)")
print("="*90)

client = keepa_client.get_client()
print(f"\nTokens available: {client.tokens_left}\n")

# Use the CORRECT root category from your screenshot
ROOT_TOYS_CATEGORY = 1350388031

# Known subcategories from your screenshot
SUBCATEGORIES = {
    1378568031: "Toy Figures & Playsets",
    1378175031: "Baby & Toddler Toys",
    1378216031: "Building & Construction Toys",
    1378290031: "Electronic Toys",
}

print(f"[STEP 1] Fetching 50 products from ROOT category: {ROOT_TOYS_CATEGORY}")
print("-" * 90)

try:
    asins_root = keepa_client.product_finder_by_category(
        client,
        category_id=ROOT_TOYS_CATEGORY,
        bsr_threshold=50000,
        per_page=50
    )
    
    print(f"✅ Retrieved {len(asins_root)} ASINs from root category\n")
    
    # Verify first 10 are actually toys
    print(f"Verifying first 10 products from root category:")
    print("-" * 90)
    
    results = client.query(asins_root[:10], stats=1, rating=0)
    
    toys_count = 0
    sample_products = []
    
    for i, prod in enumerate(results, 1):
        asin = prod.get('asin', 'N/A')
        title = prod.get('title', 'N/A')[:55]
        cat_tree = prod.get('categoryTree', [])
        main_cat = cat_tree[0].get('name', 'Unknown') if cat_tree else 'Unknown'
        
        is_toy = any(kw in main_cat.lower() for kw in ['toy', 'game', 'baby', 'building', 'play', 'figure', 'doll', 'electronic'])
        marker = '✅' if is_toy else '❌'
        
        print(f"{marker} {i}. {asin} | {title:55s} | {main_cat}")
        
        sample_products.append({
            'asin': asin,
            'title': title,
            'category': main_cat,
            'is_toy': is_toy
        })
        
        if is_toy:
            toys_count += 1
    
    accuracy = (toys_count / len(results)) * 100
    
    print(f"\n✅ Root Category Accuracy: {toys_count}/{len(results)} ({accuracy:.0f}%)")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test one subcategory
print("\n" + "-"*90)
print(f"\n[STEP 2] Testing Subcategory: Baby & Toddler Toys (1378175031)")
print("-" * 90)

try:
    asins_baby = keepa_client.product_finder_by_category(
        client,
        category_id=1378175031,
        bsr_threshold=50000,
        per_page=50
    )
    
    print(f"✅ Retrieved {len(asins_baby)} ASINs from baby toys subcategory\n")
    
    # Verify first 5
    results_baby = client.query(asins_baby[:5], stats=1, rating=0)
    
    baby_toys_count = 0
    
    for i, prod in enumerate(results_baby, 1):
        asin = prod.get('asin', 'N/A')
        title = prod.get('title', 'N/A')[:55]
        cat_tree = prod.get('categoryTree', [])
        main_cat = cat_tree[0].get('name', 'Unknown') if cat_tree else 'Unknown'
        
        is_baby_toy = any(kw in main_cat.lower() for kw in ['baby', 'toddler', 'toy', 'play'])
        marker = '✅' if is_baby_toy else '❌'
        
        print(f"{marker} {i}. {asin} | {title:55s} | {main_cat}")
        
        if is_baby_toy:
            baby_toys_count += 1
    
    baby_accuracy = (baby_toys_count / len(results_baby)) * 100
    print(f"\n✅ Baby Toys Subcategory Accuracy: {baby_toys_count}/{len(results_baby)} ({baby_accuracy:.0f}%)")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*90)
print("✅ FINAL VERDICT")
print("="*90)
print(f"Root Category (1350388031): {accuracy:.0f}% accurate")
print(f"Baby Toys Subcategory (1378175031): {baby_accuracy:.0f}% accurate")

if accuracy >= 80 and baby_accuracy >= 80:
    print("\n✅ CONFIRMED: These are the CORRECT category IDs!")
    print("\n📋 NEXT STEPS:")
    print(f"1. Update main.py to use category ID: 1350388031 (root)")
    print(f"2. Update CATEGORY_MAP with all subcategories from screenshot")
    print(f"3. Test product_analysis.py with real toy products")
    print(f"4. Connect asin-analysis.html to API")
    print(f"5. Get user approval and commit")
    
    # Save configuration
    config = {
        'root_category_id': 1350388031,
        'root_category_name': 'Toys & Games',
        'subcategories': SUBCATEGORIES
    }
    
    with open('/tmp/correct_category_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to /tmp/correct_category_config.json")
else:
    print("\n⚠️ Still not 100% accurate - may need further investigation")

print("\n")

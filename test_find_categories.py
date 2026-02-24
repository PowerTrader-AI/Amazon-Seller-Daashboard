#!/usr/bin/env python3
"""
Find correct category IDs for Toys and other categories
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client

print("\n" + "="*90)
print("🔍 FINDING CORRECT CATEGORY IDs")
print("="*90)

client = keepa_client.get_client()

# Common category names to search for
categories_to_find = {
    'Toys': 1378189031,  # What I used (WRONG - it's Beauty!)
    'Toys & Games': 2408329031,  # Let's try this
    'Beauty': 1375306031,  # Try this for beauty
}

print("\nSearching for category information...\n")

for cat_name, cat_id in categories_to_find.items():
    print(f"Testing Category: {cat_name} (ID: {cat_id})")
    
    try:
        # Get category lookup
        result = keepa_client.fetch_category_tree(cat_id)
        
        if result:
            print(f"  ✅ Category found!")
            if 'name' in result:
                print(f"     Name: {result['name']}")
            if 'productCount' in result:
                print(f"     Product Count: {result['productCount']}")
            print()
        else:
            print(f"  ❌ No data returned\n")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")

print("="*90)
print("Common Keepa Category IDs (from documentation):")
print("="*90)
print("""
Toys & Games (US/IN): Varies by region
- Try finding via product_finder or category_lookup

Beauty & Personal Care: Different ID per region

Let me search for products in different category ranges...
""")

# Let's try to find what category our fetched ASIN actually belongs to
print("\nSearching for category of B0BPLYHDPG (the product we fetched)...")
try:
    products = client.query(['B0BPLYHDPG'], stats=30)
    if products and len(products) > 0:
        prod = products[0]
        print(f"✅ Product found: {prod.get('title', 'Unknown')[:60]}")
        if 'categoryTree' in prod:
            print(f"   Category Tree: {prod['categoryTree']}")
        if 'categories' in prod:
            print(f"   Categories: {prod['categories']}")
        if 'rootCategory' in prod:
            print(f"   Root Category: {prod['rootCategory']}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*90)

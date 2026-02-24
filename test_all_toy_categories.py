#!/usr/bin/env python3
"""
COMPREHENSIVE TOY SUBCATEGORY TEST
Tests all toy subcategories to find which return actual toy products
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client
import json

print("\n" + "="*100)
print("🎯 COMPREHENSIVE TOY SUBCATEGORY TEST - ALL CATEGORIES")
print("="*100)

client = keepa_client.get_client()
tokens_start = client.tokens_left
print(f"\nTokens available: {tokens_start}\n")

# From your Keepa screenshot and category lookup:
# Root: 1350388031 (Toys & Games) - 3,275,803 products
# Subcategories identified:

TOY_CATEGORIES = {
    # Root category
    1350388031: "Toys & Games (ROOT)",
    
    # Main subcategories from screenshot
    1378568031: "Toy Figures & Playsets",
    1378175031: "Baby & Toddler Toys",
    1378216031: "Building & Construction Toys", 
    1378290031: "Electronic Toys",
    
    # From earlier search results
    1378363031: "Special Needs Developmental Toys",
    4771546031: "Interactive Toys",
    4771548031: "Mice & Animal Toys",
    
    # Additional categories from search
    1378574031: "Action & Toy Figures",
    1378657031: "Doll Clothes & Accessories",
    1378667031: "Collectible Toys",
}

results = []

print("[TESTING] All Toy Subcategories")
print("=" * 100)

for cat_id, cat_name in sorted(TOY_CATEGORIES.items()):
    print(f"\n{cat_name.ljust(50)} | ID: {cat_id}")
    print("-" * 100)
    
    try:
        # Fetch best sellers
        asins = client.best_sellers_query(str(cat_id), domain="IN", wait=False)
        
        if not asins:
            print(f"  ❌ No products returned (0 ASINs)")
            results.append({
                'category_id': cat_id,
                'name': cat_name,
                'status': '❌ EMPTY',
                'count': 0,
                'toys_verified': 0,
                'accuracy': 0
            })
            continue
        
        print(f"  ✅ Retrieved {len(asins)} best-sellers")
        
        # Test first 5 to verify they're toys
        test_asins = asins[:5]
        
        try:
            prods = client.query(test_asins, stats=1, rating=0)
            
            toys_count = 0
            valid_count = 0
            sample_toys = []
            
            for i, prod in enumerate(prods):
                if prod is None or not prod.get('asin'):
                    continue
                    
                valid_count += 1
                asin = prod.get('asin')
                title = prod.get('title', 'NO TITLE')[:50]
                
                cat_tree = prod.get('categoryTree', [])
                if cat_tree and len(cat_tree) > 0:
                    main_cat = cat_tree[0].get('name', 'Unknown')
                else:
                    main_cat = 'NO CATEGORY'
                
                # Check if it's a toy
                is_toy = any(kw in (main_cat + ' ' + title).lower() for kw in 
                            ['toy', 'game', 'baby', 'play', 'figure', 'doll', 
                             'building', 'puzzle', 'lego', 'action', 'collectible',
                             'interactive', 'scooter', 'ride', 'infant', 'toddler'])
                
                marker = '✅' if is_toy else '❌'
                print(f"    {marker} {asin}: {title:50s} | {main_cat[:40]}")
                
                if is_toy:
                    toys_count += 1
                    sample_toys.append(asin)
            
            accuracy = (toys_count / valid_count * 100) if valid_count > 0 else 0
            
            print(f"\n  📊 Verified: {toys_count}/{valid_count} are toys ({accuracy:.0f}% accuracy)")
            
            status = '✅ EXCELLENT' if accuracy >= 80 else '✅ GOOD' if accuracy >= 60 else '⚠️ MIXED' if accuracy >= 40 else '❌ BAD'
            
            results.append({
                'category_id': cat_id,
                'name': cat_name,
                'status': status,
                'count': len(asins),
                'toys_verified': toys_count,
                'accuracy': accuracy,
                'sample_asins': sample_toys[:3]
            })
            
        except Exception as e:
            print(f"  ⚠️ Error verifying products: {str(e)[:60]}")
            results.append({
                'category_id': cat_id,
                'name': cat_name,
                'status': '⚠️ ERROR',
                'count': len(asins),
                'toys_verified': 0,
                'accuracy': 0
            })
            
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:80]}")
        results.append({
            'category_id': cat_id,
            'name': cat_name,
            'status': '❌ FAILED',
            'count': 0,
            'toys_verified': 0,
            'accuracy': 0
        })

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*100)
print("📊 FINAL RESULTS - RANKED BY ACCURACY")
print("="*100)

# Sort by accuracy
results_sorted = sorted(results, key=lambda x: x['accuracy'], reverse=True)

print(f"\n{'Status':<15} {'Category Name':<40} {'ID':<15} {'Count':<8} {'Verified':<12} {'Accuracy'}")
print("-" * 100)

excellent = []
good = []
mixed = []
bad = []

for r in results_sorted:
    status = r['status']
    name = r['name'][:38].ljust(38)
    cat_id = str(r['category_id']).ljust(13)
    count = str(r['count']).ljust(6)
    verified = f"{r['toys_verified']}/{5}".ljust(10)
    accuracy = f"{r['accuracy']:.0f}%"
    
    print(f"{status:<15} {name:<40} {cat_id:<15} {count:<8} {verified:<12} {accuracy}")
    
    if '✅ EXCELLENT' in status:
        excellent.append(r)
    elif '✅ GOOD' in status:
        good.append(r)
    elif '⚠️ MIXED' in status:
        mixed.append(r)
    else:
        bad.append(r)

print("\n" + "="*100)
print("🏆 RECOMMENDATIONS")
print("="*100)

if excellent:
    print("\n✅ EXCELLENT CATEGORIES (80%+ toys) - USE THESE:")
    for r in excellent:
        print(f"   • {r['name']} (ID: {r['category_id']}) - {r['accuracy']:.0f}% accurate, {r['count']} products")
        if r['sample_asins']:
            print(f"     Sample: {r['sample_asins']}")

if good:
    print("\n✅ GOOD CATEGORIES (60-79% toys) - ACCEPTABLE:")
    for r in good:
        print(f"   • {r['name']} (ID: {r['category_id']}) - {r['accuracy']:.0f}% accurate, {r['count']} products")

if mixed:
    print("\n⚠️ MIXED CATEGORIES (40-59% toys) - USE WITH CAUTION:")
    for r in mixed:
        print(f"   • {r['name']} (ID: {r['category_id']}) - {r['accuracy']:.0f}% accurate, {r['count']} products")

if bad:
    print("\n❌ POOR CATEGORIES (<40% toys) - AVOID:")
    for r in bad:
        print(f"   • {r['name']} (ID: {r['category_id']}) - {r['accuracy']:.0f}% accurate")

# ============================================================================
# CONFIGURATION RECOMMENDATION
# ============================================================================
print("\n" + "="*100)
print("⚙️ RECOMMENDED CONFIGURATION")
print("="*100)

best_categories = [r for r in results if r['accuracy'] >= 60 and r['count'] > 0]

if best_categories:
    print(f"\nUpdate keepa_client.py with:")
    print("\n```python")
    print("TOYS_CATEGORY_IDS = [")
    for r in sorted(best_categories, key=lambda x: x['accuracy'], reverse=True):
        print(f"    {r['category_id']},  # {r['name']} - {r['accuracy']:.0f}% verified")
    print("]")
    print("```")

print("\n" + "="*100)
print(f"Token Usage: {tokens_start} → {client.tokens_left} ({tokens_start - client.tokens_left} used)")
print("="*100 + "\n")

# Save results
with open('/tmp/toy_category_results.json', 'w') as f:
    json.dump(results_sorted, f, indent=2)

print("✅ Results saved to /tmp/toy_category_results.json")

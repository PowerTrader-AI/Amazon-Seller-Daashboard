#!/usr/bin/env python3
"""
UNIT TEST 4: Find the TRULY CORRECT toys category
Test multiple category IDs found in search results
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app import keepa_client
import json

print("\n" + "="*90)
print("🔍 UNIT TEST 4: FIND TRULY CORRECT TOYS CATEGORY")
print("="*90)

client = keepa_client.get_client()
print(f"\nTokens available: {client.tokens_left}\n")

# Try different categories identified in earlier searches
test_categories = [
    ("Special Needs Developmental Toys", 1378363031, 24991),
    ("Interactive Toys", 4771546031, 10262),
    ("Mice & Animal Toys", 4771548031, 2976),
]

results_summary = []

for cat_name, cat_id, expected_products in test_categories:
    print(f"\n{'='*90}")
    print(f"Testing: {cat_name} (ID: {cat_id}, {expected_products} products)")
    print(f"{'='*90}")
    
    try:
        asins = keepa_client.product_finder_by_category(
            client,
            category_id=cat_id,
            bsr_threshold=50000,
            per_page=20  # Test only 20 to save tokens
        )
        
        print(f"✅ Retrieved {len(asins)} ASINs\n")
        
        # Fetch details for products
        test_asins = asins[:5]  # Check first 5
        results = client.query(test_asins, stats=1, rating=0)
        
        toys_count = 0
        sample_products = []
        
        for prod in results:
            asin = prod.get('asin', 'N/A')
            title = prod.get('title', 'N/A')[:50]
            
            # Get the main category
            category_tree = prod.get('categoryTree', [])
            if category_tree:
                main_cat = category_tree[0].get('name', 'Unknown')
            else:
                main_cat = 'Unknown'
            
            sample_products.append(f"{asin}: {title} ({main_cat})")
            
            # Check if it's toys/games related
            if any(keyword in main_cat.lower() for keyword in ['toy', 'game', 'activity', 'animal', 'developmental', 'educational']):
                toys_count += 1
        
        accuracy = (toys_count / len(results)) * 100 if results else 0
        
        print(f"Sample Products:")
        for prod in sample_products:
            print(f"  • {prod}")
        
        print(f"\nAccuracy: {toys_count}/{len(results)} ({accuracy:.0f}%)")
        
        results_summary.append({
            'category': cat_name,
            'id': cat_id,
            'accuracy': accuracy,
            'status': '✅' if accuracy >= 80 else '⚠️' if accuracy >= 50 else '❌'
        })
        
        print(f"Status: {results_summary[-1]['status']}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results_summary.append({
            'category': cat_name,
            'id': cat_id,
            'accuracy': 0,
            'status': '❌'
        })

print("\n" + "="*90)
print("FINAL SUMMARY - CATEGORY ACCURACY RANKING")
print("="*90)

results_summary.sort(key=lambda x: x['accuracy'], reverse=True)

for i, result in enumerate(results_summary, 1):
    print(f"{result['status']} {i}. {result['category']:<40s} | ID: {result['id']} | Accuracy: {result['accuracy']:.0f}%")

best = results_summary[0]
print("\n" + "="*90)
print(f"✅ RECOMMENDED CATEGORY: {best['category']}")
print(f"   Category ID: {best['id']}")
print(f"   Accuracy: {best['accuracy']:.0f}%")
print("="*90)

# Save recommendation
with open('/tmp/recommended_category.json', 'w') as f:
    json.dump(best, f, indent=2)

print(f"\n✅ Recommendation saved to /tmp/recommended_category.json")
print("\nNEXT STEPS:")
print(f"1. Update main.py to use category ID: {best['id']}")
print(f"2. Test the ASIN analysis with real products from {best['category']}")
print(f"3. Verify scoring works correctly")
print(f"4. Get user approval before committing\n")

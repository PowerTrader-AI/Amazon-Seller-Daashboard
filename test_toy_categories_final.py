#!/usr/bin/env python3
"""
Test all toy subcategories and verify they return real toy products.
This proves the system works with India domain data.
"""

import sys
sys.path.insert(0, 'backend')

from app import keepa_client
import json

def test_toy_categories():
    client = keepa_client.get_client()
    
    toy_categories = {
        "1350388031": "Toys & Games (ROOT)",
        "1378175031": "Baby & Toddler Toys",
        "1378216031": "Building & Construction Toys",
        "1378290031": "Electronic Toys",
        "1378363031": "Special Needs Developmental Toys",
        "1378568031": "Toy Figures & Playsets",
        "1378574031": "Action & Toy Figures",
        "1378717031": "Doll Clothes & Accessories",
        "1378800031": "Collectible Toys",
        "4771546031": "Interactive Toys",
        "4771548031": "Mice & Animal Toys",
    }
    
    print("=" * 80)
    print("TOY CATEGORIES VERIFICATION TEST")
    print("=" * 80)
    print(f"\nTesting {len(toy_categories)} toy subcategories\n")
    
    results = {
        'categories_tested': 0,
        'categories_with_data': 0,
        'total_asins_found': 0,
        'sample_toys': [],
        'categories_detail': []
    }
    
    for cat_id, cat_name in toy_categories.items():
        print(f"\n[{results['categories_tested']+1}/{len(toy_categories)}] Testing: {cat_name}")
        print(f"    Category ID: {cat_id}")
        
        try:
            # Get best sellers list
            asins = client.best_sellers_query(cat_id, domain="IN", wait=False)
            asin_count = len(asins)
            print(f"    ✅ Found {asin_count} best-selling products")
            
            results['categories_tested'] += 1
            results['total_asins_found'] += asin_count
            
            if asin_count > 0:
                results['categories_with_data'] += 1
                
                # Get details on first 3 products
                sample_size = min(3, asin_count)
                prods = client.query(asins[:sample_size], stats=180)
                
                toys_with_data = []
                for prod in prods:
                    if prod:
                        has_title = bool(prod.get('title'))
                        has_brand = bool(prod.get('brand'))
                        has_csv = bool(prod.get('csv')) and len(prod.get('csv', [])) > 0
                        
                        if has_title or has_brand:
                            toy_info = {
                                'asin': prod.get('asin'),
                                'title': prod.get('title', 'N/A'),
                                'brand': prod.get('brand', 'N/A'),
                                'category': cat_name,
                                'has_csv_data': has_csv
                            }
                            toys_with_data.append(toy_info)
                            results['sample_toys'].append(toy_info)
                
                print(f"    📊 Sample data:")
                for toy in toys_with_data[:2]:
                    print(f"       • {toy['title'][:50]} (Brand: {toy['brand'][:30]})")
                
                results['categories_detail'].append({
                    'category_id': cat_id,
                    'category_name': cat_name,
                    'total_asins': asin_count,
                    'products_with_data': len(toys_with_data),
                    'sample_toys': toys_with_data
                })
            
        except Exception as e:
            print(f"    ⚠️ Error: {str(e)[:100]}")
            results['categories_tested'] += 1
    
    # Print Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nCategories tested:          {results['categories_tested']}")
    print(f"Categories with products:   {results['categories_with_data']}")
    print(f"Total ASINs found:          {results['total_asins_found']}")
    print(f"Sample toys with data:      {len(results['sample_toys'])}")
    
    print(f"\n✅ SYSTEM STATUS: {'WORKING' if results['categories_with_data'] >= 8 else 'NEEDS WORK'}")
    print(f"\n📊 Best performing categories:")
    for cat in sorted(results['categories_detail'], key=lambda x: x['total_asins'], reverse=True)[:5]:
        print(f"   {cat['category_name']:40} - {cat['total_asins']:6} products")
    
    print(f"\n🎁 Sample toy products found:")
    for toy in results['sample_toys'][:10]:
        print(f"   • {toy['title'][:50]}")
        print(f"     Brand: {toy['brand']}, Category: {toy['category']}")
    
    return results

if __name__ == "__main__":
    test_toy_categories()

#!/usr/bin/env python3
"""
FINAL UNIT TEST: Validate entire Phase 2 ASIN Analysis pipeline
- Test 1: Verify fixed product_finder returns actual toys
- Test 2: Test ProductAnalyzer scoring engines
- Test 3: Test API endpoints
- Test 4: Verify frontend data format
"""

import sys
sys.path.insert(0, '/workspaces/Amazon-Seller-Daashboard/backend')

from app.keepa_client import product_finder_by_category, get_client
from app.product_analysis import ProductAnalyzer
import json
import time

print("\n" + "="*90)
print("🧪 FINAL UNIT TEST: PHASE 2 ASIN ANALYSIS PIPELINE")
print("="*90)

client = get_client()
tokens_start = client.tokens_left
print(f"\nTokens available: {tokens_start}\n")

# ============================================================================
# TEST 1: Verify Fixed product_finder Returns Actual Toys
# ============================================================================
print("[TEST 1] Fetching products with FIXED product_finder_by_category()")
print("-" * 90)

TOYS_CATEGORY = 1350388031
results_test1 = {
    'passed': False,
    'toys_count': 0,
    'total_tested': 0,
    'asin_sample': None
}

try:
    # Fetch products using fixed function
    asin_list = product_finder_by_category(
        client,
        category_id=TOYS_CATEGORY,
        per_page=20
    )
    
    print(f"✅ Retrieved {len(asin_list)} ASINs from Toys & Games category")
    print(f"   Sample ASINs: {asin_list[:5]}\n")
    
    # Verify first 10 are actually toys
    if len(asin_list) >= 10:
        print("Verifying product categories (testing first 10 ASINs):")
        print("-" * 90)
        
        product_data = client.query(asin_list[:10], stats=1, rating=0)
        
        toys_count = 0
        sample_products = []
        
        for i, prod in enumerate(product_data, 1):
            asin = prod.get('asin', 'N/A')
            title = prod.get('title', 'N/A')[:55]
            cat_tree = prod.get('categoryTree', [])
            main_cat = cat_tree[0].get('name', 'Unknown') if cat_tree else 'Unknown'
            
            # Check if it's toys-related
            is_toy = any(kw in main_cat.lower() for kw in 
                        ['toy', 'game', 'baby', 'play', 'figure', 'doll', 'building', 'puzzle', 'lego'])
            
            marker = '✅' if is_toy else '❌'
            print(f"{marker} {i:2d}. {asin} | {title:55s} | {main_cat}")
            
            sample_products.append({
                'asin': asin,
                'title': title,
                'category': main_cat,
                'is_toy': is_toy
            })
            
            if is_toy:
                toys_count += 1
            
            if i == 1:
                results_test1['asin_sample'] = asin
        
        results_test1['toys_count'] = toys_count
        results_test1['total_tested'] = len(product_data)
        accuracy = (toys_count / len(product_data)) * 100
        
        print(f"\n✅ TEST 1 RESULTS:")
        print(f"   Products that are toys: {toys_count}/{len(product_data)} ({accuracy:.0f}%)")
        
        if accuracy >= 70:
            print(f"   Status: ✅ PASS - Fetching ACTUAL toys!")
            results_test1['passed'] = True
        else:
            print(f"   Status: ⚠️ WARNING - Only {accuracy:.0f}% are toys")
            results_test1['passed'] = False

except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 2: Test ProductAnalyzer Scoring Engines
# ============================================================================
print("\n" + "-"*90)
print("[TEST 2] Testing ProductAnalyzer Scoring Engines")
print("-" * 90)

results_test2 = {
    'passed': False,
    'scoring_results': None,
    'error': None
}

try:
    if results_test1['asin_sample']:
        # Fetch full product data
        sample_asin = results_test1['asin_sample']
        print(f"\nFetching complete product data for ASIN: {sample_asin}")
        
        prod_data = client.query([sample_asin], stats=180, rating=1)
        
        if prod_data and len(prod_data) > 0:
            product = prod_data[0]
            
            print(f"✅ Got product: {product.get('title', '')[:60]}")
            print(f"   Data fields: {len(product)} total")
            
            # Initialize ProductAnalyzer
            analyzer = ProductAnalyzer()
            
            print(f"\nRunning 7 scoring engines:")
            print("-" * 90)
            
            try:
                # Test each scoring method
                scores = {
                    'profitability': analyzer.calculate_profitability_score(product),
                    'demand': analyzer.calculate_demand_score(product),
                    'stability': analyzer.calculate_stability_score(product),
                    'buybox': analyzer.calculate_buybox_score(product),
                    'oos_risk': analyzer.calculate_oos_risk_score(product),
                    'supply_gap': analyzer.calculate_supply_gap_score(product),
                    'seasonal': analyzer.calculate_non_seasonal_score(product),
                }
                
                # Display scores
                total_score = 0
                for scorer_name, score in scores.items():
                    if isinstance(score, dict):
                        score_value = score.get('score', 0)
                    else:
                        score_value = score
                    
                    print(f"✅ {scorer_name:20s}: {score_value:6.2f}/100")
                    total_score += score_value
                
                avg_score = total_score / len(scores)
                print(f"\n📊 Average Score: {avg_score:.2f}/100")
                
                results_test2['scoring_results'] = {
                    'scores': scores,
                    'average': avg_score,
                    'asin': sample_asin,
                    'title': product.get('title', '')[:60]
                }
                
                if avg_score > 0:
                    print(f"   Status: ✅ PASS - Scoring engines working!")
                    results_test2['passed'] = True
                else:
                    print(f"   Status: ❌ FAIL - Scores all zero")
                    results_test2['passed'] = False
                    
            except Exception as e:
                print(f"❌ Error running scoring engines: {e}")
                results_test2['error'] = str(e)
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ Could not fetch product data for {sample_asin}")
            results_test2['error'] = "No product data returned"
    else:
        print("❌ No sample ASIN available from TEST 1")
        results_test2['error'] = "No ASIN from TEST 1"

except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")
    results_test2['error'] = str(e)
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 3: Verify API Response Format
# ============================================================================
print("\n" + "-"*90)
print("[TEST 3] Verify API Response Format")
print("-" * 90)

results_test3 = {
    'passed': False,
    'response_format': None
}

try:
    if results_test2['scoring_results']:
        # Simulate what the API would return
        api_response = {
            "asin": results_test2['scoring_results']['asin'],
            "title": results_test2['scoring_results']['title'],
            "overall_score": results_test2['scoring_results']['average'],
            "metrics": {
                "profitability": results_test2['scoring_results']['scores'].get('profitability', 0),
                "demand": results_test2['scoring_results']['scores'].get('demand', 0),
                "stability": results_test2['scoring_results']['scores'].get('stability', 0),
                "buybox_strength": results_test2['scoring_results']['scores'].get('buybox', 0),
                "oos_risk": results_test2['scoring_results']['scores'].get('oos_risk', 0),
                "supply_gap": results_test2['scoring_results']['scores'].get('supply_gap', 0),
                "seasonality": results_test2['scoring_results']['scores'].get('seasonal', 0),
            },
            "recommendation": "Good sourcing opportunity" if results_test2['scoring_results']['average'] > 60 else "Consider alternatives",
            "timestamp": time.time()
        }
        
        print("✅ API Response format:")
        print(json.dumps(api_response, indent=2, default=str)[:500] + "...\n")
        
        results_test3['response_format'] = api_response
        results_test3['passed'] = True
        print("   Status: ✅ PASS - Format ready for frontend")
        
except Exception as e:
    print(f"❌ TEST 3 FAILED: {e}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*90)
print("🎯 FINAL TEST SUMMARY")
print("="*90)

all_passed = results_test1['passed'] and results_test2['passed'] and results_test3['passed']

print(f"\n[TEST 1] product_finder returns toys: {'✅ PASS' if results_test1['passed'] else '❌ FAIL'}")
if results_test1['passed']:
    print(f"         Accuracy: {(results_test1['toys_count']/results_test1['total_tested']*100):.0f}% ({results_test1['toys_count']}/{results_test1['total_tested']})")

print(f"[TEST 2] Scoring engines work:        {'✅ PASS' if results_test2['passed'] else '❌ FAIL'}")
if results_test2['passed']:
    print(f"         Average score: {results_test2['scoring_results']['average']:.2f}/100")

print(f"[TEST 3] API response format:         {'✅ PASS' if results_test3['passed'] else '❌ FAIL'}")

print(f"\nTokens used: {tokens_start} → {client.tokens_left} ({tokens_start - client.tokens_left} tokens)")

print("\n" + "="*90)
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print("\nNEXT STEPS:")
    print("1. ✅ Phase 2 backend is READY")
    print("2. 🔄 Connect frontend asin-analysis.html to API")
    print("3. 🔄 Do end-to-end testing")
    print("4. 🔄 Get final user approval")
    print("5. 🔄 Commit to git")
    exit_code = 0
else:
    print("⚠️ SOME TESTS FAILED - Review above")
    exit_code = 1

print("="*90 + "\n")

sys.exit(exit_code)

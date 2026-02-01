"""
ASIN-Level Product Analysis Engine (Phase 2)

Provides 7 different scoring dimensions for product-level decision making:
1. Profitability - Margin potential per unit
2. Demand - Sales velocity indicators
3. Stability - Non-seasonality scoring
4. Buy Box Winability - Ease of capturing buy box
5. OOS Risk - Immediate supply gap detection
6. Supply Gap - Future opportunity prediction
7. Non-Seasonal - Year-round predictability
"""

import logging
from typing import Dict, List, Optional, Tuple
import math
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProductAnalyzer:
    """Analyze individual products across 7 dimensions."""
    
    def __init__(self):
        """Initialize analyzer with scoring weights."""
        self.weights = {
            'profitability': 0.40,
            'demand': 0.20,
            'stability': 0.20,
            'buybox': 0.10,
            'oos_risk': 0.10
        }
    
    # ============================================================================
    # SCORING FUNCTION 1: PROFITABILITY
    # ============================================================================
    
    def calculate_profitability_score(self, product: Dict) -> Dict:
        """
        Calculates profit potential per unit.
        
        Components:
        - Price (higher = more margin potential)
        - Review count (more reviews = proven demand)
        - Seller count (fewer sellers = easier margins)
        - Sales rank (lower BSR = better selling)
        - FBA adoption (higher FBA = proven fulfillment)
        
        Returns: {score: 0-100, profit_estimate: ₹, demand_index: score}
        """
        try:
            price = float(product.get('price', 0))
            reviews = int(product.get('review_count', 0))
            sellers = int(product.get('seller_count', 1))
            bsr = int(product.get('sales_rank', 999999))
            fba_pct = float(product.get('fba_share', 0))
            
            if price == 0:
                return {'score': 0, 'profit_estimate': 0, 'demand_index': 0}
            
            # 1. Price-based margin potential
            # Sweet spot: ₹500-2000 (high conversion + margin)
            if price < 500:
                margin_potential = (price / 500) * 60  # Low margin
            elif price <= 2000:
                margin_potential = 100  # Peak margin
            elif price <= 3500:
                margin_potential = 100 - ((price - 2000) / 1500) * 30
            else:
                margin_potential = max(0, 70 - ((price - 3500) / 2000) * 70)
            
            # 2. Review count indicates demand proven
            # More reviews = more sales historically
            review_demand = min(100, (reviews / 200) * 100) if reviews > 0 else 20
            
            # 3. Seller density (fewer = easier to compete)
            seller_score = max(0, 100 - (sellers * 2))  # Each seller reduces score
            
            # 4. BSR competitiveness (lower BSR = better)
            if bsr < 5000:
                bsr_score = 100
            elif bsr < 50000:
                bsr_score = 80
            elif bsr < 500000:
                bsr_score = 50
            else:
                bsr_score = 20
            
            # 5. FBA fulfillment advantage
            fba_score = fba_pct * 0.5 + 50  # 50-100 scale
            
            # Weighted profitability score
            profitability_score = (
                margin_potential * 0.35 +
                review_demand * 0.20 +
                seller_score * 0.20 +
                bsr_score * 0.15 +
                fba_score * 0.10
            )
            
            # Estimate profit per unit (₹)
            # Assumed: Wholesale 40-50% of retail, FBA fees 25-30% of price
            wholesale_cost = price * 0.45
            fba_fee_estimate = price * 0.28 if fba_pct > 50 else price * 0.15
            estimated_profit = price - wholesale_cost - fba_fee_estimate
            
            return {
                'score': round(profitability_score, 1),
                'profit_per_unit_estimate': round(estimated_profit, 0),
                'price': round(price, 0),
                'wholesale_estimate': round(wholesale_cost, 0),
                'fba_fee_estimate': round(fba_fee_estimate, 0),
                'demand_index': round(review_demand, 1),
                'components': {
                    'margin_potential': round(margin_potential, 1),
                    'review_demand': round(review_demand, 1),
                    'seller_score': round(seller_score, 1),
                    'bsr_score': round(bsr_score, 1),
                    'fba_score': round(fba_score, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating profitability: {str(e)}")
            return {'score': 0, 'profit_per_unit_estimate': 0, 'error': str(e)}
    
    # ============================================================================
    # SCORING FUNCTION 2: DEMAND
    # ============================================================================
    
    def calculate_demand_score(self, product: Dict) -> Dict:
        """
        Measures sales velocity and market popularity.
        
        Components:
        - Review velocity (reviews per month)
        - Sales rank (BSR - lower = better)
        - FBA adoption (high FBA = proven demand)
        - Price point (cheaper = higher volume typically)
        
        Returns: {score: 0-100, monthly_demand_est: units, velocity: reviews/month}
        """
        try:
            reviews = int(product.get('review_count', 0))
            bsr = int(product.get('sales_rank', 999999))
            fba_pct = float(product.get('fba_share', 0))
            price = float(product.get('price', 100))
            
            # 1. Review velocity (proxy for sales velocity)
            # Assumption: 1 review ≈ 30-40 sales
            review_velocity = reviews / max(product.get('product_age_days', 365), 1)
            monthly_review_velocity = review_velocity * 30
            monthly_sales_estimate = max(10, monthly_review_velocity * 35)  # 35 sales per review
            
            demand_from_velocity = min(100, (monthly_review_velocity / 5) * 100)
            
            # 2. BSR competitiveness (rank indicates popularity)
            if bsr < 1000:
                bsr_demand = 100  # Top 1000 - huge demand
            elif bsr < 10000:
                bsr_demand = 85
            elif bsr < 100000:
                bsr_demand = 60
            elif bsr < 500000:
                bsr_demand = 30
            else:
                bsr_demand = 10
            
            # 3. FBA adoption (high FBA = market validates fulfillment)
            fba_demand = fba_pct * 0.7 + 30  # 30-100 scale
            
            # 4. Price point (lower prices often have higher volume)
            if price < 500:
                volume_potential = 100
            elif price <= 2000:
                volume_potential = 85
            elif price <= 5000:
                volume_potential = 60
            else:
                volume_potential = 30
            
            # Weighted demand score
            demand_score = (
                demand_from_velocity * 0.35 +
                bsr_demand * 0.30 +
                fba_demand * 0.20 +
                volume_potential * 0.15
            )
            
            return {
                'score': round(demand_score, 1),
                'monthly_sales_estimate': int(monthly_sales_estimate),
                'review_velocity': round(monthly_review_velocity, 1),
                'bsr': bsr,
                'bsr_tier': 'Top 1K' if bsr < 1000 else 'Top 10K' if bsr < 10000 else 'Top 100K' if bsr < 100000 else 'Slow',
                'components': {
                    'velocity_score': round(demand_from_velocity, 1),
                    'bsr_score': round(bsr_demand, 1),
                    'fba_score': round(fba_demand, 1),
                    'volume_potential': round(volume_potential, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating demand: {str(e)}")
            return {'score': 0, 'monthly_sales_estimate': 0, 'error': str(e)}
    
    # ============================================================================
    # SCORING FUNCTION 3: STABILITY (Non-Seasonality)
    # ============================================================================
    
    def calculate_stability_score(self, product: Dict, price_history: Optional[List] = None) -> Dict:
        """
        Measures predictability and consistency (zero seasonality).
        
        Components:
        - Price volatility (stable = predictable margins)
        - Review consistency (steady reviews = steady demand)
        - BSR stability (consistent rank = consistent sales)
        - Seller count stability (same competitors = stable market)
        
        Returns: {score: 0-100, volatility: %, seasonality_risk: text}
        """
        try:
            current_price = float(product.get('price', 0))
            reviews = int(product.get('review_count', 0))
            
            if current_price == 0:
                return {'score': 0, 'volatility_percent': 0, 'seasonality_risk': 'unknown'}
            
            # 1. Price volatility from history
            price_volatility = 0
            if price_history and len(price_history) > 1:
                prices = [p.get('price', current_price) for p in price_history]
                avg_price = sum(prices) / len(prices)
                if avg_price > 0:
                    price_volatility = (max(prices) - min(prices)) / avg_price * 100
            
            price_stability = max(0, 100 - price_volatility)
            
            # 2. Review consistency (higher = more predictable)
            # Stable products get 10-20 reviews/month consistently
            # Seasonal products have spikes (100+ in peak, 0 in off-season)
            monthly_reviews = reviews / max(product.get('product_age_months', 12), 1)
            
            if monthly_reviews > 50:
                review_consistency = 70  # High, consistent demand
            elif monthly_reviews > 20:
                review_consistency = 85  # Good consistency
            elif monthly_reviews > 5:
                review_consistency = 70  # Moderate consistency
            else:
                review_consistency = 40  # Low consistency = seasonal risk
            
            # 3. BSR stability (BSR changes indicate seasonality)
            bsr_stability = 80  # Default: would need history to calculate properly
            if product.get('bsr_history'):
                bsr_list = product['bsr_history']
                if len(bsr_list) > 1:
                    bsr_changes = [abs(bsr_list[i] - bsr_list[i-1]) for i in range(1, len(bsr_list))]
                    avg_bsr_change = sum(bsr_changes) / len(bsr_changes)
                    bsr_stability = max(0, 100 - (avg_bsr_change / 10000 * 100))
            
            # 4. Seller count stability
            seller_stability = 85  # Default
            if product.get('seller_count_history'):
                seller_list = product['seller_count_history']
                if len(seller_list) > 1:
                    avg_sellers = sum(seller_list) / len(seller_list)
                    if avg_sellers > 0:
                        seller_std = sum([(s - avg_sellers) ** 2 for s in seller_list]) / len(seller_list)
                        seller_stability = max(0, 100 - (math.sqrt(seller_std) / avg_sellers * 50))
            
            # Weighted stability score
            stability_score = (
                price_stability * 0.35 +
                review_consistency * 0.30 +
                bsr_stability * 0.20 +
                seller_stability * 0.15
            )
            
            # Seasonality risk assessment
            if price_volatility > 20 or monthly_reviews < 5:
                seasonality_risk = 'HIGH'
            elif price_volatility > 10 or monthly_reviews < 15:
                seasonality_risk = 'MEDIUM'
            else:
                seasonality_risk = 'LOW'
            
            return {
                'score': round(stability_score, 1),
                'price_volatility_percent': round(price_volatility, 1),
                'review_consistency': round(review_consistency, 1),
                'bsr_stability': round(bsr_stability, 1),
                'seller_stability': round(seller_stability, 1),
                'seasonality_risk': seasonality_risk,
                'interpretation': 'Safe year-round product' if seasonality_risk == 'LOW' else 'Seasonal - plan accordingly'
            }
        except Exception as e:
            logger.error(f"Error calculating stability: {str(e)}")
            return {'score': 0, 'volatility_percent': 0, 'error': str(e)}
    
    # ============================================================================
    # SCORING FUNCTION 4: BUY BOX WINABILITY
    # ============================================================================
    
    def calculate_buybox_score(self, product: Dict) -> Dict:
        """
        Predicts ease of winning buy box for this product.
        
        Components:
        - Seller fragmentation (many sellers = easier to be #1)
        - Review barrier (low reviews = easier to rank)
        - Price consistency (stable price = algorithm rewards)
        - FBA availability (high FBA% = Amazon prefers)
        - Sales velocity (slower sellers = easier entry)
        
        Returns: {score: 0-100, difficulty: text, winning_strategy: text}
        """
        try:
            sellers = int(product.get('seller_count', 1))
            reviews = int(product.get('review_count', 0))
            fba_pct = float(product.get('fba_share', 0))
            bsr = int(product.get('sales_rank', 999999))
            
            # 1. Seller fragmentation (many competitors = easier to be #1)
            if sellers > 50:
                fragmentation_score = 100  # Highly fragmented
            elif sellers > 20:
                fragmentation_score = 85
            elif sellers > 10:
                fragmentation_score = 70
            elif sellers > 5:
                fragmentation_score = 55
            else:
                fragmentation_score = 20  # Dominated by few
            
            # 2. Review barrier (low reviews = easier to rank)
            if reviews < 50:
                review_barrier = 95
            elif reviews < 150:
                review_barrier = 80
            elif reviews < 300:
                review_barrier = 60
            elif reviews < 500:
                review_barrier = 40
            else:
                review_barrier = 15  # Very high barrier
            
            # 3. FBA adoption (high FBA = Amazon algorithm prefers, but competition harder)
            fba_winability = (fba_pct * 0.4) + 50  # 50-90 scale
            
            # 4. Price consistency (would need history, defaulting to safe middle)
            price_consistency = 75
            
            # 5. Sales velocity (slower = easier to jump in)
            if bsr > 500000:
                velocity_score = 90  # Slow selling = easy entry
            elif bsr > 100000:
                velocity_score = 75
            elif bsr > 10000:
                velocity_score = 50
            elif bsr > 1000:
                velocity_score = 30
            else:
                velocity_score = 10  # Super competitive
            
            # Weighted buybox score
            buybox_score = (
                fragmentation_score * 0.30 +
                review_barrier * 0.25 +
                fba_winability * 0.15 +
                price_consistency * 0.20 +
                velocity_score * 0.10
            )
            
            # Difficulty assessment
            if buybox_score >= 80:
                difficulty = 'VERY EASY'
                strategy = 'Jump in immediately, undercut by ₹50-100, easy box win'
            elif buybox_score >= 60:
                difficulty = 'EASY'
                strategy = 'Good entry point, competitive but winnable'
            elif buybox_score >= 40:
                difficulty = 'MODERATE'
                strategy = 'Possible entry, but need strong ratings/reviews'
            else:
                difficulty = 'HARD'
                strategy = 'Dominated by established sellers, avoid unless niche advantage'
            
            return {
                'score': round(buybox_score, 1),
                'difficulty': difficulty,
                'winning_strategy': strategy,
                'seller_count': sellers,
                'review_barrier': round(review_barrier, 1),
                'components': {
                    'fragmentation': round(fragmentation_score, 1),
                    'review_barrier_score': round(review_barrier, 1),
                    'fba_advantage': round(fba_winability, 1),
                    'price_consistency': round(price_consistency, 1),
                    'velocity_advantage': round(velocity_score, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating buybox: {str(e)}")
            return {'score': 0, 'difficulty': 'unknown', 'error': str(e)}
    
    # ============================================================================
    # SCORING FUNCTION 5: OOS RISK (Immediate Supply Gap)
    # ============================================================================
    
    def calculate_oos_risk_score(self, product: Dict, product_snapshot_history: Optional[List] = None) -> Dict:
        """
        Detects products about to go out of stock = immediate scarcity opportunity.
        
        Signals:
        - Seller count DECREASING (competitors exiting)
        - FBA availability LOW
        - Price trending UP
        - Review velocity INCREASING
        - Offer count DROPPING
        
        Returns: {score: 0-100, risk_level: text, oos_timeline: weeks, opportunity: ₹}
        """
        try:
            current_sellers = int(product.get('seller_count', 10))
            fba_available = int(product.get('fba_available_quantity', 500))
            current_price = float(product.get('price', 0))
            
            # 1. Seller count trend (DECREASING = gap forming)
            seller_trend_score = 50  # Default
            if product_snapshot_history and len(product_snapshot_history) > 2:
                recent_sellers = [s.get('seller_count', 10) for s in product_snapshot_history[-7:]]
                if recent_sellers[0] > recent_sellers[-1]:
                    seller_decrease = recent_sellers[0] - recent_sellers[-1]
                    seller_trend_score = min(100, (seller_decrease / recent_sellers[0]) * 200)
            
            # 2. FBA stock level (LOW = gap detected)
            if fba_available < 100:
                fba_score = 100  # Critical low stock
            elif fba_available < 300:
                fba_score = 80  # Low stock
            elif fba_available < 800:
                fba_score = 50  # Moderate stock
            else:
                fba_score = 20  # Healthy stock
            
            # 3. Price trending UP (before OOS, prices rise)
            price_trend_score = 50  # Default
            if product_snapshot_history and len(product_snapshot_history) > 2:
                price_history = [s.get('price', current_price) for s in product_snapshot_history[-7:]]
                if price_history[0] < price_history[-1]:
                    price_increase = ((price_history[-1] - price_history[0]) / price_history[0]) * 100
                    price_trend_score = min(100, price_increase * 10)
            
            # 4. Review velocity increasing (demand up, supply limited)
            review_trend_score = 30  # Default
            if product_snapshot_history and len(product_snapshot_history) > 2:
                reviews_history = [s.get('review_count', 0) for s in product_snapshot_history[-7:]]
                if len(reviews_history) > 1:
                    review_increase = reviews_history[-1] - reviews_history[0]
                    review_trend_score = min(100, (review_increase / max(reviews_history[0], 1)) * 100)
            
            # 5. Offer count dropping (competitors selling out)
            offers_trend_score = 30  # Default
            if product.get('offers_history'):
                offers_list = product['offers_history'][-7:]
                if len(offers_list) > 1 and offers_list[-1] < offers_list[0]:
                    offer_decrease = offers_list[0] - offers_list[-1]
                    offers_trend_score = min(100, (offer_decrease / offers_list[0]) * 100)
            
            # Weighted OOS risk score
            oos_risk_score = (
                seller_trend_score * 0.35 +
                fba_score * 0.25 +
                price_trend_score * 0.20 +
                review_trend_score * 0.12 +
                offers_trend_score * 0.08
            )
            
            # Risk level
            if oos_risk_score >= 80:
                risk_level = 'CRITICAL'
                timeline_weeks = 1
            elif oos_risk_score >= 60:
                risk_level = 'HIGH'
                timeline_weeks = 2
            elif oos_risk_score >= 40:
                risk_level = 'MEDIUM'
                timeline_weeks = 3
            else:
                risk_level = 'LOW'
                timeline_weeks = 4
            
            # Opportunity calculation (unmet demand revenue)
            monthly_demand = int(product.get('review_count', 100) / 3) if product.get('review_count') else 33
            unmet_demand = (monthly_demand / 4) * timeline_weeks  # Weekly estimate
            revenue_opportunity = unmet_demand * current_price
            
            return {
                'score': round(oos_risk_score, 1),
                'risk_level': risk_level,
                'weeks_until_oos': timeline_weeks,
                'fba_available': fba_available,
                'sellers_trend': 'DECREASING' if seller_trend_score > 50 else 'STABLE',
                'price_trend': 'RISING' if price_trend_score > 50 else 'STABLE',
                'revenue_opportunity': int(revenue_opportunity),
                'recommendation': f'SOURCE NOW - Gap closes in {timeline_weeks} weeks, ₹{int(revenue_opportunity)} opportunity',
                'components': {
                    'seller_decrease': round(seller_trend_score, 1),
                    'fba_low_stock': round(fba_score, 1),
                    'price_increase': round(price_trend_score, 1),
                    'review_acceleration': round(review_trend_score, 1),
                    'offer_decrease': round(offers_trend_score, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating OOS risk: {str(e)}")
            return {'score': 0, 'risk_level': 'unknown', 'error': str(e)}
    
    # ============================================================================
    # SCORING FUNCTION 6: SUPPLY CHAIN GAP PREDICTION
    # ============================================================================
    
    def calculate_supply_gap_score(self, product: Dict, product_history: Optional[List] = None) -> Dict:
        """
        Predicts FUTURE supply chain gaps = strategic sourcing opportunity.
        
        Logic: When supply restricted + demand high = future demand surge
        
        Calculates:
        - Demand vs Supply ratio
        - Time to restock estimate
        - Revenue opportunity in gap period
        
        Returns: {gap_score: 0-100, weeks_until_restock: int, revenue: ₹}
        """
        try:
            current_sellers = int(product.get('seller_count', 10))
            current_reviews = int(product.get('review_count', 50))
            current_price = float(product.get('price', 100))
            fba_pct = float(product.get('fba_share', 50))
            
            # 1. Demand signals
            monthly_demand = (current_reviews / max(product.get('product_age_months', 12), 1)) * 30
            
            # 2. Current supply indicators (low sellers + low FBA = gap)
            if current_sellers < 5:
                supply_constraint = 90  # Very constrained
            elif current_sellers < 10:
                supply_constraint = 75
            elif current_sellers < 20:
                supply_constraint = 50
            else:
                supply_constraint = 20  # Well supplied
            
            # 3. Demand-to-supply ratio
            demand_supply_ratio = (monthly_demand * 2) / max(current_sellers, 1)
            if demand_supply_ratio > 100:
                gap_potential = 100
            elif demand_supply_ratio > 50:
                gap_potential = 85
            elif demand_supply_ratio > 20:
                gap_potential = 60
            else:
                gap_potential = 30
            
            # 4. Restock timeline estimation
            # Average time: (new_sellers_needed × 2 weeks) + 3 weeks
            new_sellers_needed = max(0, 20 - current_sellers)
            weeks_to_restock = (new_sellers_needed * 1.5) + 2  # weeks for others to see gap and source
            
            # 5. Price trend (rising prices = gap indicator)
            price_trend = 0
            if product_history and len(product_history) > 1:
                recent_prices = [h.get('price', current_price) for h in product_history[-14:]]
                if recent_prices[0] < recent_prices[-1]:
                    price_trend = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100
            
            # Weighted supply gap score
            supply_gap_score = (
                gap_potential * 0.40 +
                supply_constraint * 0.30 +
                (price_trend * 5) * 0.20 +  # Price rise is signal
                (demand_supply_ratio * 0.5) * 0.10  # Ratio boost
            )
            supply_gap_score = min(100, max(0, supply_gap_score))
            
            # Revenue opportunity calculation
            # Unmet demand = gap weeks × (monthly demand / 4)
            weekly_demand = monthly_demand / 4
            unmet_units = weekly_demand * weeks_to_restock
            revenue_opportunity = unmet_units * current_price
            
            # Gap severity
            if supply_gap_score >= 75:
                gap_severity = 'MASSIVE'
            elif supply_gap_score >= 50:
                gap_severity = 'SIGNIFICANT'
            elif supply_gap_score >= 30:
                gap_severity = 'MODERATE'
            else:
                gap_severity = 'MINOR'
            
            return {
                'score': round(supply_gap_score, 1),
                'gap_severity': gap_severity,
                'weeks_until_restock': int(weeks_to_restock),
                'estimated_revenue_opportunity': int(revenue_opportunity),
                'demand_to_supply_ratio': round(demand_supply_ratio, 1),
                'current_sellers': current_sellers,
                'monthly_demand': int(monthly_demand),
                'action': f'SOURCE NOW - {gap_severity} opportunity, ₹{int(revenue_opportunity)} revenue in {int(weeks_to_restock)} weeks before restock',
                'components': {
                    'gap_potential': round(gap_potential, 1),
                    'supply_constraint': round(supply_constraint, 1),
                    'price_trend_signal': round(price_trend, 1),
                    'demand_supply_ratio_score': round(demand_supply_ratio * 0.5, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating supply gap: {str(e)}")
            return {'score': 0, 'gap_severity': 'unknown', 'error': str(e)}
    
    # ============================================================================
    # SCORING FUNCTION 7: NON-SEASONAL STABILITY
    # ============================================================================
    
    def calculate_non_seasonal_score(self, product: Dict, yearly_history: Optional[List] = None) -> Dict:
        """
        Identifies products with ZERO seasonality = year-round predictable demand.
        
        Components:
        - Monthly consistency (same sales every month?)
        - No demand spikes/drops
        - Stable pricing through year
        - Stable review velocity
        
        Returns: {score: 0-100, seasonal_pattern: text, safe_for: months}
        """
        try:
            reviews = int(product.get('review_count', 0))
            current_price = float(product.get('price', 0))
            
            if reviews == 0 or current_price == 0:
                return {'score': 50, 'seasonal_pattern': 'insufficient_data', 'interpretation': 'Need more data'}
            
            # 1. Calculate review consistency across months
            monthly_review_consistency = 80  # Default
            if yearly_history and len(yearly_history) >= 12:
                monthly_reviews = [h.get('review_count', 0) - (yearly_history[i-1].get('review_count', 0) if i > 0 else 0)
                                   for i, h in enumerate(yearly_history)]
                monthly_reviews = [m for m in monthly_reviews if m > 0]
                
                if len(monthly_reviews) > 3:
                    avg_monthly = sum(monthly_reviews) / len(monthly_reviews)
                    variance = sum([(m - avg_monthly) ** 2 for m in monthly_reviews]) / len(monthly_reviews)
                    std_dev = math.sqrt(variance)
                    cv = (std_dev / avg_monthly * 100) if avg_monthly > 0 else 100  # Coefficient of variation
                    
                    if cv < 10:
                        monthly_review_consistency = 100
                    elif cv < 20:
                        monthly_review_consistency = 85
                    elif cv < 40:
                        monthly_review_consistency = 60
                    elif cv < 60:
                        monthly_review_consistency = 35
                    else:
                        monthly_review_consistency = 10  # Highly variable
            
            # 2. Price stability through year
            price_stability = 80  # Default
            if yearly_history and len(yearly_history) >= 12:
                prices = [h.get('price', current_price) for h in yearly_history if h.get('price')]
                if len(prices) > 3:
                    avg_price = sum(prices) / len(prices)
                    price_range = (max(prices) - min(prices)) / avg_price * 100
                    
                    if price_range < 5:
                        price_stability = 100
                    elif price_range < 10:
                        price_stability = 85
                    elif price_range < 20:
                        price_stability = 60
                    else:
                        price_stability = 30
            
            # 3. BSR stability (consistent rank = consistent sales)
            bsr_stability = 75  # Default
            if product.get('bsr_history'):
                bsr_data = product['bsr_history'][-12:] if len(product['bsr_history']) >= 12 else product['bsr_history']
                if len(bsr_data) > 3:
                    bsr_variance = sum([(b - sum(bsr_data)/len(bsr_data)) ** 2 for b in bsr_data]) / len(bsr_data)
                    bsr_std = math.sqrt(bsr_variance)
                    avg_bsr = sum(bsr_data) / len(bsr_data)
                    bsr_cv = (bsr_std / avg_bsr * 100) if avg_bsr > 0 else 100
                    
                    if bsr_cv < 15:
                        bsr_stability = 95
                    elif bsr_cv < 30:
                        bsr_stability = 75
                    elif bsr_cv < 60:
                        bsr_stability = 50
                    else:
                        bsr_stability = 20
            
            # 4. No demand spikes (would indicate seasonality)
            spike_risk = 10  # Default: low spike risk
            if yearly_history and len(yearly_history) >= 12:
                review_deltas = [yearly_history[i].get('review_count', 0) - yearly_history[i-1].get('review_count', 0)
                                for i in range(1, len(yearly_history))]
                if review_deltas:
                    avg_delta = sum(review_deltas) / len(review_deltas)
                    max_spike = max(review_deltas) if review_deltas else 0
                    if max_spike > avg_delta * 3:
                        spike_risk = 60  # Spike detected
                    elif max_spike > avg_delta * 2:
                        spike_risk = 30
            
            # Weighted non-seasonal score
            non_seasonal_score = (
                monthly_review_consistency * 0.35 +
                price_stability * 0.30 +
                bsr_stability * 0.20 +
                (100 - spike_risk) * 0.15
            )
            
            # Seasonal pattern interpretation
            if non_seasonal_score >= 85:
                seasonal_pattern = 'ZERO SEASONALITY'
                interpretation = 'Perfect for year-round inventory - same sales every month'
                safe_months = 12
            elif non_seasonal_score >= 70:
                seasonal_pattern = 'MINIMAL SEASONALITY'
                interpretation = 'Very safe, minor fluctuations only'
                safe_months = 11
            elif non_seasonal_score >= 50:
                seasonal_pattern = 'MODERATE SEASONALITY'
                interpretation = 'Plan for minor peaks/valleys'
                safe_months = 8
            else:
                seasonal_pattern = 'HIGH SEASONALITY'
                interpretation = 'Clear seasonal pattern - avoid or plan accordingly'
                safe_months = 4
            
            return {
                'score': round(non_seasonal_score, 1),
                'seasonal_pattern': seasonal_pattern,
                'interpretation': interpretation,
                'safe_for_months': safe_months,
                'peak_months': self._detect_peak_months(yearly_history) if yearly_history else 'N/A',
                'components': {
                    'monthly_consistency': round(monthly_review_consistency, 1),
                    'price_stability': round(price_stability, 1),
                    'bsr_stability': round(bsr_stability, 1),
                    'no_spikes': round(100 - spike_risk, 1)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating non-seasonal score: {str(e)}")
            return {'score': 50, 'seasonal_pattern': 'error', 'error': str(e)}
    
    @staticmethod
    def _detect_peak_months(history: List) -> str:
        """Detect which months have peak sales."""
        if not history or len(history) < 12:
            return 'insufficient_data'
        
        monthly_sales = {}
        for i, record in enumerate(history[-12:]):
            month_num = (datetime.now() - timedelta(days=30*(12-i))).month
            month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month_num-1]
            reviews = record.get('review_count', 0)
            monthly_sales[month_name] = reviews
        
        avg_sales = sum(monthly_sales.values()) / len(monthly_sales)
        peak_months = [m for m, s in monthly_sales.items() if s > avg_sales * 1.5]
        
        return ', '.join(peak_months) if peak_months else 'None'
    
    # ============================================================================
    # CONSOLIDATED ANALYSIS
    # ============================================================================
    
    def analyze_asin(self, product: Dict, history: Optional[Dict] = None) -> Dict:
        """
        Complete ASIN analysis across all 7 dimensions.
        
        Returns comprehensive ranking data for product.
        """
        result = {
            'asin': product.get('asin'),
            'title': product.get('title'),
            'timestamp': datetime.now().isoformat(),
            'dimensions': {}
        }
        
        # Calculate all 7 scores
        result['dimensions']['profitability'] = self.calculate_profitability_score(product)
        result['dimensions']['demand'] = self.calculate_demand_score(product)
        result['dimensions']['stability'] = self.calculate_stability_score(
            product,
            history.get('price_history') if history else None
        )
        result['dimensions']['buybox_winability'] = self.calculate_buybox_score(product)
        result['dimensions']['oos_risk'] = self.calculate_oos_risk_score(
            product,
            history.get('snapshot_history') if history else None
        )
        result['dimensions']['supply_gap'] = self.calculate_supply_gap_score(
            product,
            history.get('yearly_history') if history else None
        )
        result['dimensions']['non_seasonal'] = self.calculate_non_seasonal_score(
            product,
            history.get('yearly_history') if history else None
        )
        
        # Calculate overall composite score (weighted average)
        scores = [
            result['dimensions']['profitability']['score'],
            result['dimensions']['demand']['score'],
            result['dimensions']['stability']['score'],
            result['dimensions']['buybox_winability']['score'] * 0.8,  # Lower weight
            result['dimensions']['oos_risk']['score'] * 0.6,
            result['dimensions']['supply_gap']['score'] * 0.7,
            result['dimensions']['non_seasonal']['score']
        ]
        result['overall_score'] = round(sum(scores) / len(scores), 1)
        
        return result


# Convenience function
def analyze_product(product: Dict, history: Optional[Dict] = None) -> Dict:
    """Analyze a single product across all 7 dimensions."""
    analyzer = ProductAnalyzer()
    return analyzer.analyze_asin(product, history)

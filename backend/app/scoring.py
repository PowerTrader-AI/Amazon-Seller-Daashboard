import numpy as np


def price_volatility_cv(prices):
    prices = np.array([p for p in prices if p is not None], dtype=float)
    if len(prices) < 2:
        return None
    mean = prices.mean()
    if mean == 0:
        return None
    return float(prices.std(ddof=1) / mean)


def bsr_slope(bsr_values):
    values = [v for v in bsr_values if v is not None]
    if len(values) < 2:
        return None
    x = np.arange(len(values))
    y = np.array(values, dtype=float)
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)


def confidence_score(bsr, bsr_slope_30d, cv, new_fba_offer_count, amazon_out_of_stock):
    score = 50

    if bsr is not None:
        if bsr < 10000:
            score += 20
        elif bsr < 50000:
            score += 10
        else:
            score -= 10

    if amazon_out_of_stock:
        score += 10

    if new_fba_offer_count is not None:
        if new_fba_offer_count < 5:
            score += 10
        elif new_fba_offer_count > 12:
            score -= 10

    if cv is not None:
        if cv < 0.1:
            score += 15
        elif cv > 0.25:
            score -= 10

    if bsr_slope_30d is not None:
        if bsr_slope_30d < 0:
            score += 10
        elif bsr_slope_30d > 0:
            score -= 5

    return max(0, min(100, int(score)))


def score_breakdown(bsr, bsr_slope_30d, cv, new_fba_offer_count, amazon_out_of_stock):
    parts = []
    if bsr is not None:
        parts.append(f"BSR {bsr}")
    if amazon_out_of_stock:
        parts.append("Amazon OOS")
    if new_fba_offer_count is not None:
        parts.append(f"FBA offers {new_fba_offer_count}")
    if cv is not None:
        parts.append(f"CV {cv:.2f}")
    if bsr_slope_30d is not None:
        parts.append(f"BSR slope {bsr_slope_30d:.2f}")
    return "; ".join(parts)

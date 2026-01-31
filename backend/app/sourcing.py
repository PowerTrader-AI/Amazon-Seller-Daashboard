from datetime import date
from app.keepa_client import product_finder_by_category
from app.scoring import price_volatility_cv, bsr_slope, confidence_score


def parse_keepa_stats(product):
    stats = product.get("stats", {})
    current_buy_box = stats.get("current", {}).get("buyBoxPrice")
    avg90_buy_box = stats.get("avg90", {}).get("buyBoxPrice")

    new_fba_offer_count = product.get("newFBAOfferCount")
    amazon_offer_count = product.get("amazonOfferCount")
    amazon_out_of_stock = amazon_offer_count == -1

    buy_box_history = stats.get("buyBoxPrice", [])
    bsr_history = stats.get("salesRank", [])

    cv = price_volatility_cv(buy_box_history)
    bsr_slope_30d = bsr_slope(bsr_history[-30:]) if len(bsr_history) >= 30 else bsr_slope(bsr_history)

    score = confidence_score(
        bsr=product.get("salesRank"),
        bsr_slope_30d=bsr_slope_30d,
        cv=cv,
        new_fba_offer_count=new_fba_offer_count,
        amazon_out_of_stock=amazon_out_of_stock,
    )

    return {
        "current_buy_box": current_buy_box,
        "avg90_buy_box": avg90_buy_box,
        "new_fba_offer_count": new_fba_offer_count,
        "amazon_out_of_stock": amazon_out_of_stock,
        "cv": cv,
        "bsr_slope_30d": bsr_slope_30d,
        "score": score,
    }


def run_sourcing(client, categories, bsr_threshold, max_fba_offers, cv_threshold):
    product_rows = []
    metric_rows = []
    today = date.today()

    for category_id, category_name in categories:
        res = product_finder_by_category(client, category_id, bsr_threshold=bsr_threshold)
        products = res.get("products", [])

        for p in products:
            stats = parse_keepa_stats(p)

            if p.get("salesRank") is None or p.get("salesRank") >= bsr_threshold:
                continue
            if not stats["amazon_out_of_stock"]:
                continue
            if stats["new_fba_offer_count"] is None or stats["new_fba_offer_count"] >= max_fba_offers:
                continue
            if stats["cv"] is None or stats["cv"] >= cv_threshold:
                continue
            if stats["bsr_slope_30d"] is None or stats["bsr_slope_30d"] >= 0:
                continue

            product_rows.append((
                p.get("asin"),
                p.get("title"),
                p.get("brand"),
                str(category_id),
            ))

            metric_rows.append((
                p.get("asin"),
                today,
                p.get("salesRank"),
                stats["current_buy_box"],
                stats["avg90_buy_box"],
                stats["new_fba_offer_count"],
                not stats["amazon_out_of_stock"],
                stats["bsr_slope_30d"],
                stats["cv"],
                stats["score"],
            ))

    return product_rows, metric_rows

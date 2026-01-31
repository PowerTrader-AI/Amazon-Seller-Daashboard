from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app import config
from app.db import (
    get_conn,
    list_selected_categories,
    replace_selected_categories,
    get_top5,
    get_latest_metrics,
    upsert_products,
    upsert_daily_metrics,
)
from app.keepa_client import get_client
from app.sourcing import run_sourcing
from app.scoring import score_breakdown
from app.ai import generate_ai_summary

app = FastAPI(title="Amazon Sourcing Engine", version="1.0")


class CategoryIn(BaseModel):
    category_id: int
    name: str


class CategoryList(BaseModel):
    categories: List[CategoryIn]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def get_categories():
    conn = get_conn()
    rows = list_selected_categories(conn)
    conn.close()
    return [{"category_id": r[0], "name": r[1]} for r in rows]


@app.post("/categories")
def set_categories(payload: CategoryList):
    conn = get_conn()
    replace_selected_categories(conn, [(c.category_id, c.name) for c in payload.categories])
    conn.close()
    return {"status": "updated", "count": len(payload.categories)}


@app.post("/run")
def run_now(
    bsr_threshold: Optional[int] = None,
    max_fba_offers: Optional[int] = None,
    cv_threshold: Optional[float] = None,
):
    conn = get_conn()
    categories = list_selected_categories(conn)
    conn.close()

    if not categories:
        raise HTTPException(status_code=400, detail="No categories selected")

    client = get_client()
    bsr_threshold = bsr_threshold or config.DEFAULT_BSR_THRESHOLD
    max_fba_offers = max_fba_offers or config.DEFAULT_MAX_FBA_OFFERS
    cv_threshold = cv_threshold or config.DEFAULT_CV_THRESHOLD

    product_rows, metric_rows = run_sourcing(
        client,
        categories,
        bsr_threshold=bsr_threshold,
        max_fba_offers=max_fba_offers,
        cv_threshold=cv_threshold,
    )

    conn = get_conn()
    upsert_products(conn, product_rows)
    upsert_daily_metrics(conn, metric_rows)
    conn.close()

    return {"status": "ok", "products": len(product_rows)}


@app.get("/top5")
def top5(category_id: Optional[str] = None):
    conn = get_conn()
    rows = get_top5(conn, category_id)
    conn.close()
    keys = [
        "asin",
        "title",
        "brand",
        "category",
        "snapshot_date",
        "bsr",
        "buy_box_price_cents",
        "avg90_buy_box_price_cents",
        "new_fba_offer_count",
        "amazon_in_stock",
        "bsr_slope_30d",
        "price_volatility_cv",
        "confidence_score",
    ]
    return [dict(zip(keys, r)) for r in rows]


@app.get("/explain/{asin}")
def explain(asin: str):
    conn = get_conn()
    row = get_latest_metrics(conn, asin)
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="ASIN not found")

    bsr, buy_box, avg90, fba_count, amazon_in_stock, bsr_slope_30d, cv, score = row
    breakdown = score_breakdown(bsr, bsr_slope_30d, cv, fba_count, not amazon_in_stock)
    summary = generate_ai_summary(score, breakdown) if config.AI_EXPLANATIONS_ENABLED else ""

    return {
        "asin": asin,
        "confidence_score": score,
        "breakdown": breakdown,
        "ai_summary": summary,
    }

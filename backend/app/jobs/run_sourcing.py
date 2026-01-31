from app import config
from app.db import get_conn, list_selected_categories, upsert_products, upsert_daily_metrics
from app.keepa_client import get_client
from app.sourcing import run_sourcing


def main():
    conn = get_conn()
    categories = list_selected_categories(conn)
    conn.close()

    if not categories:
        raise RuntimeError("No categories selected")

    client = get_client()
    product_rows, metric_rows = run_sourcing(
        client,
        categories,
        bsr_threshold=config.DEFAULT_BSR_THRESHOLD,
        max_fba_offers=config.DEFAULT_MAX_FBA_OFFERS,
        cv_threshold=config.DEFAULT_CV_THRESHOLD,
    )

    conn = get_conn()
    upsert_products(conn, product_rows)
    upsert_daily_metrics(conn, metric_rows)
    conn.close()


if __name__ == "__main__":
    main()

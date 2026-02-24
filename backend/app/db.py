import sqlite3
import os
from app import config


def get_conn():
    db_url = os.getenv("DATABASE_URL", "sqlite:///./amazon_sourcing.db")
    db_path = db_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def upsert_products(conn, rows):
    if not rows:
        return
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO products (asin, title, brand, category)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (asin) DO UPDATE SET
            title = excluded.title,
            brand = excluded.brand,
            category = excluded.category
        """,
        rows,
    )
    conn.commit()


def upsert_daily_metrics(conn, rows):
    if not rows:
        return
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO product_daily_metrics (
            asin, snapshot_date, bsr, buy_box_price_cents,
            avg90_buy_box_price_cents, new_fba_offer_count,
            amazon_in_stock, bsr_slope_30d, price_volatility_cv,
            confidence_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (asin, snapshot_date) DO UPDATE SET
            bsr = excluded.bsr,
            buy_box_price_cents = excluded.buy_box_price_cents,
            avg90_buy_box_price_cents = excluded.avg90_buy_box_price_cents,
            new_fba_offer_count = excluded.new_fba_offer_count,
            amazon_in_stock = excluded.amazon_in_stock,
            bsr_slope_30d = excluded.bsr_slope_30d,
            price_volatility_cv = excluded.price_volatility_cv,
            confidence_score = excluded.confidence_score
        """,
        rows,
    )
    conn.commit()


def list_selected_categories(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.category_id, c.name
        FROM selected_categories sc
        JOIN categories c ON c.category_id = sc.category_id
        WHERE sc.is_active = 1
        ORDER BY c.name
        """
    )
    return cursor.fetchall()


def replace_selected_categories(conn, categories):
    cursor = conn.cursor()
    cursor.execute("UPDATE selected_categories SET is_active = 0")
    for cat in categories:
        cursor.execute(
            """
            INSERT INTO categories (category_id, name)
            VALUES (?, ?)
            ON CONFLICT (category_id) DO UPDATE SET name = excluded.name
            """,
            (cat[0], cat[1]),
        )
        cursor.execute(
            """
            INSERT INTO selected_categories (category_id, is_active)
            VALUES (?, 1)
            ON CONFLICT (category_id) DO UPDATE SET is_active = 1
            """,
            (cat[0],),
        )
    conn.commit()


def get_top5(conn, category_id=None):
    cursor = conn.cursor()
    if category_id:
        cursor.execute(
            """
            SELECT p.asin, p.title, p.brand, p.category, m.snapshot_date,
                   m.bsr, m.buy_box_price_cents, m.avg90_buy_box_price_cents,
                   m.new_fba_offer_count, m.amazon_in_stock,
                   m.bsr_slope_30d, m.price_volatility_cv, m.confidence_score
            FROM product_daily_metrics m
            JOIN products p ON p.asin = m.asin
            WHERE p.category = ?
            ORDER BY m.confidence_score DESC
            LIMIT 5
            """,
            (category_id,),
        )
    else:
        cursor.execute(
            """
            SELECT p.asin, p.title, p.brand, p.category, m.snapshot_date,
                   m.bsr, m.buy_box_price_cents, m.avg90_buy_box_price_cents,
                   m.new_fba_offer_count, m.amazon_in_stock,
                   m.bsr_slope_30d, m.price_volatility_cv, m.confidence_score
            FROM product_daily_metrics m
            JOIN products p ON p.asin = m.asin
            ORDER BY m.confidence_score DESC
            LIMIT 5
            """
        )
    return cursor.fetchall()


def get_latest_metrics(conn, asin):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT m.bsr, m.buy_box_price_cents, m.avg90_buy_box_price_cents,
               m.new_fba_offer_count, m.amazon_in_stock, m.bsr_slope_30d,
               m.price_volatility_cv, m.confidence_score
        FROM product_daily_metrics m
        WHERE m.asin = ?
        ORDER BY m.snapshot_date DESC
        LIMIT 1
        """,
        (asin,),
    )
    return cursor.fetchone()

# ============================================================================
# CACHING & TRACKING FUNCTIONS (7-day cache, token tracking)
# ============================================================================

def get_category_sync_status(conn, category_id, domain='IN'):
    """Check if category was synced in last 7 days."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT category_id, total_products, last_synced_at, next_sync_at, 
               products_fetched, token_cost, status
        FROM category_sync_status
        WHERE category_id = ? AND domain = ?
        """,
        (category_id, domain)
    )
    return cursor.fetchone()


def set_category_syncing(conn, category_id, domain='IN'):
    """Mark category as currently syncing."""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO category_sync_status 
        (category_id, domain, status)
        VALUES (?, ?, 'syncing')
        ON CONFLICT(category_id) DO UPDATE SET
            status = 'syncing',
            updated_at = CURRENT_TIMESTAMP
        """,
        (category_id, domain)
    )
    conn.commit()


def save_category_sync(conn, category_id, total_products, products_fetched, 
                       token_cost, sync_duration_seconds, domain='IN'):
    """Save category sync completion status."""
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    
    now = datetime.now()
    next_sync = now + timedelta(days=7)  # Sync again in 7 days
    
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO category_sync_status 
        (category_id, domain, total_products, products_fetched, token_cost,
         sync_duration_seconds, last_synced_at, next_sync_at, status, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP)
        ON CONFLICT(category_id) DO UPDATE SET
            total_products = excluded.total_products,
            products_fetched = excluded.products_fetched,
            token_cost = excluded.token_cost,
            sync_duration_seconds = excluded.sync_duration_seconds,
            last_synced_at = excluded.last_synced_at,
            next_sync_at = excluded.next_sync_at,
            status = 'completed',
            updated_at = CURRENT_TIMESTAMP
        """,
        (category_id, domain, total_products, products_fetched, token_cost,
         sync_duration_seconds, now, next_sync)
    )
    conn.commit()


def save_category_products(conn, category_id, asin_list):
    """Save ASIN-to-category mappings."""
    cursor = conn.cursor()
    
    # Clear old mappings for this category
    cursor.execute("DELETE FROM category_products WHERE category_id = ?", 
                  (category_id,))
    
    # Insert new mappings with rank
    rows = [(category_id, asin, idx + 1) for idx, asin in enumerate(asin_list)]
    cursor.executemany(
        """
        INSERT INTO category_products (category_id, asin, rank)
        VALUES (?, ?, ?)
        """,
        rows
    )
    conn.commit()


def get_category_products_from_cache(conn, category_id, limit=None):
    """Get cached ASINs for a category."""
    cursor = conn.cursor()
    
    if limit:
        cursor.execute(
            """
            SELECT asin, rank
            FROM category_products
            WHERE category_id = ?
            ORDER BY rank
            LIMIT ?
            """,
            (category_id, limit)
        )
    else:
        cursor.execute(
            """
            SELECT asin, rank
            FROM category_products
            WHERE category_id = ?
            ORDER BY rank
            """,
            (category_id,)
        )
    
    return [row['asin'] for row in cursor.fetchall()]


def save_product_analysis_scores(conn, asin, scores_dict):
    """Cache product analysis scores for 7 days."""
    from datetime import datetime, timedelta
    import json
    
    expires_at = datetime.now() + timedelta(days=7)

    dimensions = scores_dict.get('dimensions', scores_dict)
    overall_score = scores_dict.get('overall_score', 0)
    
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO product_analysis_scores
        (asin, profitability_score, demand_score, stability_score,
         buybox_winability_score, oos_risk_score, supply_gap_score,
         non_seasonal_score, overall_score, analysis_data, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asin) DO UPDATE SET
            profitability_score = excluded.profitability_score,
            demand_score = excluded.demand_score,
            stability_score = excluded.stability_score,
            buybox_winability_score = excluded.buybox_winability_score,
            oos_risk_score = excluded.oos_risk_score,
            supply_gap_score = excluded.supply_gap_score,
            non_seasonal_score = excluded.non_seasonal_score,
            overall_score = excluded.overall_score,
            analysis_data = excluded.analysis_data,
            expires_at = excluded.expires_at
        """,
        (
            asin,
            dimensions.get('profitability', {}).get('score', 0),
            dimensions.get('demand', {}).get('score', 0),
            dimensions.get('stability', {}).get('score', 0),
            dimensions.get('buybox_winability', {}).get('score', 0),
            dimensions.get('oos_risk', {}).get('score', 0),
            dimensions.get('supply_gap', {}).get('score', 0),
            dimensions.get('non_seasonal', {}).get('score', 0),
            overall_score,
            json.dumps(scores_dict),
            expires_at
        )
    )
    conn.commit()


def get_product_analysis_scores(conn, asin):
    """Get cached analysis scores if not expired."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            profitability_score, demand_score, stability_score,
            buybox_winability_score, oos_risk_score, supply_gap_score,
            non_seasonal_score, overall_score, analysis_data,
            calculated_at
        FROM product_analysis_scores
        WHERE asin = ? AND expires_at > datetime('now')
        """,
        (asin,)
    )
    return cursor.fetchone()


def log_token_usage(conn, service_name, category_id=None, asin_count=0, 
                   tokens_used=0, duration_ms=0, cache_hit=False, error=None):
    """Log token usage for analytics."""
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO token_usage_log
        (service_name, category_id, asin_count, tokens_used, duration_ms, 
         cache_hit, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (service_name, category_id, asin_count, tokens_used, duration_ms, 
         cache_hit, error)
    )
    conn.commit()


def get_token_usage_stats(conn, days=7):
    """Get token usage statistics for last N days."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            service_name,
            COUNT(*) as call_count,
            SUM(tokens_used) as total_tokens,
            SUM(cache_hit) as cache_hits,
            AVG(duration_ms) as avg_duration_ms
        FROM token_usage_log
        WHERE timestamp > datetime('now', '-' || ? || ' days')
        GROUP BY service_name
        ORDER BY total_tokens DESC
        """,
        (days,)
    )
    return cursor.fetchall()


def get_total_tokens_used(conn, days=None):
    """Get total tokens used in specified period."""
    cursor = conn.cursor()
    
    if days:
        cursor.execute(
            """
            SELECT SUM(tokens_used) as total
            FROM token_usage_log
            WHERE timestamp > datetime('now', '-' || ? || ' days')
            """,
            (days,)
        )
    else:
        cursor.execute(
            """
            SELECT SUM(tokens_used) as total
            FROM token_usage_log
            """
        )
    
    result = cursor.fetchone()
    return result['total'] or 0 if result else 0


def ensure_title_cache_table(conn):
    """Create asin_title_cache table if it doesn't exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS asin_title_cache (
            asin TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT DEFAULT 'amazon',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_asin_title(conn, asin: str):
    """Get cached title for an ASIN.
    
    Returns:
        - Real title string for source='amazon' entries (permanent cache)
        - None for source='failed' entries older than 24h (triggers retry)
        - Fallback 'ASIN {asin}' for source='failed' entries within 24h (blocks re-scrape)
    """
    ensure_title_cache_table(conn)
    row = conn.execute(
        "SELECT title, source, created_at FROM asin_title_cache WHERE asin = ?", (asin,)
    ).fetchone()
    if row is None:
        return None
    if row['source'] == 'failed':
        # Retry after 24 hours — transient CAPTCHA blocks may clear
        from datetime import datetime, timezone
        try:
            created = datetime.fromisoformat(row['created_at']).replace(tzinfo=timezone.utc)
        except Exception:
            created = datetime.now(timezone.utc)
        age_hours = (datetime.now(timezone.utc) - created).total_seconds() / 3600
        if age_hours > 24:
            return None  # Expired — let caller retry scraping
    return row['title']


def save_asin_title(conn, asin: str, title: str, source: str = 'amazon'):
    """Persist a resolved title for an ASIN.
    
    source='amazon'  → real title from scrape, kept indefinitely
    source='failed'  → CAPTCHA/blocked result, expires after 24h (see get_asin_title)
    """
    ensure_title_cache_table(conn)
    conn.execute(
        """
        INSERT INTO asin_title_cache (asin, title, source, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(asin) DO UPDATE SET
            title = excluded.title,
            source = excluded.source,
            created_at = CURRENT_TIMESTAMP
        """,
        (asin, title[:200], source)
    )
    conn.commit()
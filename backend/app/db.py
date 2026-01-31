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

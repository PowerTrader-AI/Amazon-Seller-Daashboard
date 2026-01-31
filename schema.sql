-- PostgreSQL schema for historical BSR and Price data
CREATE TABLE IF NOT EXISTS products (
    asin TEXT PRIMARY KEY,
    title TEXT,
    brand TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS product_daily_metrics (
    id BIGSERIAL PRIMARY KEY,
    asin TEXT NOT NULL REFERENCES products(asin),
    snapshot_date DATE NOT NULL,
    bsr INTEGER,
    buy_box_price_cents INTEGER,
    avg90_buy_box_price_cents INTEGER,
    new_fba_offer_count INTEGER,
    amazon_in_stock BOOLEAN,
    bsr_slope_30d DOUBLE PRECISION,
    price_volatility_cv DOUBLE PRECISION,
    confidence_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (asin, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_product_daily_metrics_asin_date
    ON product_daily_metrics (asin, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_product_daily_metrics_confidence
    ON product_daily_metrics (confidence_score);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS selected_categories (
    category_id INTEGER PRIMARY KEY REFERENCES categories(category_id),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Keepa API Cache Table (7-day caching strategy)
-- Stores all 70 Keepa product fields to minimize API token usage
CREATE TABLE IF NOT EXISTS keepa_products_cache (
    -- Primary identifier
    asin VARCHAR(10) PRIMARY KEY,
    domain_id INTEGER DEFAULT 1,
    
    -- Keepa Product Info (70 fields)
    author TEXT,
    availability_amazon INTEGER,
    binding VARCHAR(50),
    brand VARCHAR(100),
    buy_box_seller_id_history JSONB,
    categories JSONB,
    category_tree JSONB,
    color VARCHAR(50),
    coupon JSONB,
    csv JSONB,  -- Critical: Price/rank/rating history [34 arrays]
    description TEXT,
    ean_list JSONB,
    ebay_listing_ids JSONB,
    edition VARCHAR(50),
    fba_fees JSONB,
    features JSONB,
    format VARCHAR(50),
    frequently_bought_together JSONB,
    g INTEGER,
    has_reviews BOOLEAN,
    images_csv VARCHAR(1000),
    is_adult_product BOOLEAN,
    is_b2b BOOLEAN,
    is_eligible_for_super_saver_shipping BOOLEAN,
    is_eligible_for_trade_in BOOLEAN,
    is_redirect_asin BOOLEAN,
    is_sns BOOLEAN,
    item_height INTEGER,
    item_length INTEGER,
    item_weight INTEGER,
    item_width INTEGER,
    languages JSONB,
    last_ebay_update INTEGER,
    last_price_change INTEGER,
    last_rating_update INTEGER,
    last_update INTEGER,
    launchpad BOOLEAN,
    listed_since INTEGER,
    live_offers_order JSONB,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    new_price_is_map BOOLEAN,
    number_of_items INTEGER,
    number_of_pages INTEGER,
    offers_successful BOOLEAN,
    package_height INTEGER,
    package_length INTEGER,
    package_quantity INTEGER,
    package_weight INTEGER,
    package_width INTEGER,
    parent_asin VARCHAR(10),
    part_number VARCHAR(100),
    product_group VARCHAR(50),
    product_type INTEGER,
    promotions JSONB,
    publication_date INTEGER,
    release_date INTEGER,
    root_category INTEGER,
    sales_rank_reference INTEGER,
    sales_rank_reference_history JSONB,
    sales_ranks JSONB,
    size VARCHAR(50),
    title VARCHAR(500),
    tracking_since INTEGER,
    type VARCHAR(50),
    upc_list JSONB,
    variation_csv VARCHAR(1000),
    variations JSONB,
    
    -- Extracted key metrics (for faster analysis)
    current_price_cents INTEGER,
    current_sales_rank INTEGER,
    current_rating DECIMAL(3,1),
    current_review_count INTEGER,
    
    -- Cache control columns
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_stale BOOLEAN GENERATED ALWAYS AS (expires_at < NOW()) STORED,
    last_analyzed_at TIMESTAMPTZ,
    search_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_keepa_cache_domain ON keepa_products_cache(domain_id);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_stale ON keepa_products_cache(is_stale) WHERE is_stale = false;
CREATE INDEX IF NOT EXISTS idx_keepa_cache_expires ON keepa_products_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_rank ON keepa_products_cache(current_sales_rank) WHERE current_sales_rank > 0;
CREATE INDEX IF NOT EXISTS idx_keepa_cache_rating ON keepa_products_cache(current_rating) WHERE current_rating > 0;
CREATE INDEX IF NOT EXISTS idx_keepa_cache_searches ON keepa_products_cache(search_count DESC);

CREATE TABLE IF NOT EXISTS products (
    asin TEXT PRIMARY KEY,
    title TEXT,
    brand TEXT,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_daily_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT NOT NULL REFERENCES products(asin),
    snapshot_date DATE NOT NULL,
    bsr INTEGER,
    buy_box_price_cents INTEGER,
    avg90_buy_box_price_cents INTEGER,
    new_fba_offer_count INTEGER,
    amazon_in_stock BOOLEAN,
    bsr_slope_30d REAL,
    price_volatility_cv REAL,
    confidence_score INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Keepa API Cache Table (7-day caching strategy)
-- Stores all 70 Keepa product fields to minimize API token usage
CREATE TABLE IF NOT EXISTS keepa_products_cache (
    asin VARCHAR(10) PRIMARY KEY,
    domain_id INTEGER DEFAULT 1,
    
    -- Keepa Product Info (70 fields)
    author TEXT,
    availability_amazon INTEGER,
    binding VARCHAR(50),
    brand VARCHAR(100),
    buy_box_seller_id_history TEXT,  -- JSON
    categories TEXT,  -- JSON
    category_tree TEXT,  -- JSON
    color VARCHAR(50),
    coupon TEXT,  -- JSON
    csv TEXT,  -- JSON - Critical: Price/rank/rating history [34 arrays]
    description TEXT,
    ean_list TEXT,  -- JSON
    ebay_listing_ids TEXT,  -- JSON
    edition VARCHAR(50),
    fba_fees TEXT,  -- JSON
    features TEXT,  -- JSON
    format VARCHAR(50),
    frequently_bought_together TEXT,  -- JSON
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
    languages TEXT,  -- JSON
    last_ebay_update INTEGER,
    last_price_change INTEGER,
    last_rating_update INTEGER,
    last_update INTEGER,
    launchpad BOOLEAN,
    listed_since INTEGER,
    live_offers_order TEXT,  -- JSON
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
    promotions TEXT,  -- JSON
    publication_date INTEGER,
    release_date INTEGER,
    root_category INTEGER,
    sales_rank_reference INTEGER,
    sales_rank_reference_history TEXT,  -- JSON
    sales_ranks TEXT,  -- JSON
    size VARCHAR(50),
    title VARCHAR(500),
    tracking_since INTEGER,
    type VARCHAR(50),
    upc_list TEXT,  -- JSON
    variation_csv VARCHAR(1000),
    variations TEXT,  -- JSON
    
    -- Extracted key metrics (for faster analysis)
    current_price_cents INTEGER,
    current_sales_rank INTEGER,
    current_rating REAL,
    current_review_count INTEGER,
    
    -- Cache control columns
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    last_analyzed_at DATETIME,
    search_count INTEGER DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_keepa_cache_domain ON keepa_products_cache(domain_id);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_expires ON keepa_products_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_rank ON keepa_products_cache(current_sales_rank) WHERE current_sales_rank > 0;
CREATE INDEX IF NOT EXISTS idx_keepa_cache_rating ON keepa_products_cache(current_rating) WHERE current_rating > 0;
CREATE INDEX IF NOT EXISTS idx_keepa_cache_searches ON keepa_products_cache(search_count DESC);

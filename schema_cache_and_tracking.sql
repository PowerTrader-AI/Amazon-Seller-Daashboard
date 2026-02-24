-- Additional schema for best-sellers caching and token tracking
-- Created: 2026-02-01

-- Table: category_sync_status
-- Tracks when each category was last synced to avoid redundant API calls
CREATE TABLE IF NOT EXISTS category_sync_status (
    category_id TEXT PRIMARY KEY,
    category_name TEXT,
    domain VARCHAR(10) DEFAULT 'IN',
    total_products INTEGER,
    last_synced_at DATETIME,
    next_sync_at DATETIME,
    sync_duration_seconds INTEGER,
    products_fetched INTEGER,
    token_cost INTEGER,
    status TEXT DEFAULT 'pending',  -- 'pending', 'syncing', 'completed', 'failed'
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, domain)
);

-- Table: category_products
-- Maps ASINs to categories for quick lookup (many-to-many)
CREATE TABLE IF NOT EXISTS category_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT NOT NULL,
    asin TEXT NOT NULL,
    rank INTEGER,  -- Position in bestsellers list (1 = top)
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category_sync_status(category_id),
    UNIQUE(category_id, asin)
);

-- Table: product_analysis_scores
-- Caches the 7-dimension analysis scores to avoid recalculation
CREATE TABLE IF NOT EXISTS product_analysis_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT NOT NULL UNIQUE,
    profitability_score REAL,
    demand_score REAL,
    stability_score REAL,
    buybox_winability_score REAL,
    oos_risk_score REAL,
    supply_gap_score REAL,
    non_seasonal_score REAL,
    overall_score REAL,
    analysis_data JSON,  -- Full analysis object as JSON
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,  -- Re-calculate after 7 days
    FOREIGN KEY (asin) REFERENCES keepa_products_cache(asin)
);

-- Table: token_usage_log
-- Tracks every API call and token consumption for analytics
CREATE TABLE IF NOT EXISTS token_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    service_name TEXT NOT NULL,  -- 'best_sellers_query', 'product_query', 'category_lookup'
    category_id TEXT,
    asin_count INTEGER,
    tokens_used INTEGER,
    duration_ms INTEGER,
    cache_hit BOOLEAN DEFAULT 0,  -- Was this from cache?
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: sync_schedule
-- Manages background sync schedule for categories
CREATE TABLE IF NOT EXISTS sync_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT UNIQUE,
    sync_interval_days INTEGER DEFAULT 7,
    priority INTEGER DEFAULT 0,  -- 0=low, 1=medium, 2=high
    enabled BOOLEAN DEFAULT 1,
    last_run DATETIME,
    next_run DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category_sync_status(category_id)
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_category_sync_status_domain 
    ON category_sync_status(domain, last_synced_at);

CREATE INDEX IF NOT EXISTS idx_category_sync_status_next_sync 
    ON category_sync_status(next_sync_at) WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_category_products_rank 
    ON category_products(category_id, rank);

CREATE INDEX IF NOT EXISTS idx_product_analysis_expires 
    ON product_analysis_scores(asin, expires_at);

CREATE INDEX IF NOT EXISTS idx_token_usage_service 
    ON token_usage_log(service_name, timestamp);

CREATE INDEX IF NOT EXISTS idx_token_usage_category 
    ON token_usage_log(category_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_sync_schedule_next_run 
    ON sync_schedule(next_run) WHERE enabled = 1;

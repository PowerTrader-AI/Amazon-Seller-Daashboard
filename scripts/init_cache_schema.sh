#!/bin/bash
# Initialize database with caching and tracking schema

DB_PATH="${1:-.}/amazon_sourcing.db"

echo "Initializing cache and tracking schema..."
echo "Database: $DB_PATH"

sqlite3 "$DB_PATH" << 'EOF'

-- Table: category_sync_status
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
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, domain)
);

-- Table: category_products
CREATE TABLE IF NOT EXISTS category_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT NOT NULL,
    asin TEXT NOT NULL,
    rank INTEGER,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category_sync_status(category_id),
    UNIQUE(category_id, asin)
);

-- Table: product_analysis_scores
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
    analysis_data JSON,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (asin) REFERENCES keepa_products_cache(asin)
);

-- Table: token_usage_log
CREATE TABLE IF NOT EXISTS token_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    service_name TEXT NOT NULL,
    category_id TEXT,
    asin_count INTEGER,
    tokens_used INTEGER,
    duration_ms INTEGER,
    cache_hit BOOLEAN DEFAULT 0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: sync_schedule
CREATE TABLE IF NOT EXISTS sync_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT UNIQUE,
    sync_interval_days INTEGER DEFAULT 7,
    priority INTEGER DEFAULT 0,
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

EOF

echo "✅ Cache and tracking schema initialized successfully!"

-- Keepa Product Cache Table - Stores ALL 70 fields from Keepa API
-- 7-Day Cache Strategy: Reduces token usage by 90%

CREATE TABLE IF NOT EXISTS keepa_products_cache (
    -- Primary Key
    asin VARCHAR(10) PRIMARY KEY,
    
    -- Keepa API Fields (70 total)
    author VARCHAR(255),
    availability_amazon INT,
    binding VARCHAR(50),
    brand VARCHAR(100),
    buy_box_seller_id_history JSONB,
    categories JSONB,
    category_tree JSONB,
    color VARCHAR(50),
    coupon JSONB,
    csv JSONB,  -- ⭐ CRITICAL: Price/rank/rating history [34 indices]
    description TEXT,
    domain_id INT NOT NULL,
    ean_list JSONB,
    ebay_listing_ids JSONB,
    edition VARCHAR(50),
    fba_fees JSONB,
    features JSONB,
    format VARCHAR(50),
    frequently_bought_together JSONB,
    g INT,
    has_reviews BOOLEAN,
    images_csv TEXT,  -- ⭐ Product images
    is_adult_product BOOLEAN,
    is_b2b BOOLEAN,
    is_eligible_for_super_saver_shipping BOOLEAN,
    is_eligible_for_trade_in BOOLEAN,
    is_redirect_asin BOOLEAN,
    is_sns BOOLEAN,
    item_height INT,
    item_length INT,
    item_weight INT,
    item_width INT,
    languages JSONB,
    last_ebay_update BIGINT,
    last_price_change BIGINT,
    last_rating_update BIGINT,
    last_update BIGINT,
    launchpad BOOLEAN,
    listed_since BIGINT,
    live_offers_order JSONB,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    new_price_is_map BOOLEAN,
    number_of_items INT,
    number_of_pages INT,
    offers_successful BOOLEAN,
    package_height INT,
    package_length INT,
    package_quantity INT,
    package_weight INT,
    package_width INT,
    parent_asin VARCHAR(10),
    part_number VARCHAR(100),
    product_group VARCHAR(50),
    product_type INT,
    promotions JSONB,
    publication_date BIGINT,
    release_date BIGINT,
    root_category INT,
    sales_rank_reference INT,  -- ⭐ Current sales rank
    sales_rank_reference_history JSONB,
    sales_ranks JSONB,
    size VARCHAR(50),
    title VARCHAR(500),  -- ⭐ Product title
    tracking_since BIGINT,
    type VARCHAR(50),
    upc_list JSONB,
    variation_csv TEXT,
    variations JSONB,
    
    -- Cache Control Columns (added by us)
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),
    is_stale BOOLEAN GENERATED ALWAYS AS (NOW() > expires_at) STORED,
    last_analyzed_at TIMESTAMPTZ,
    search_count INT DEFAULT 1,
    
    -- Extracted Metrics (for faster queries)
    current_price_cents INT,  -- Extracted from csv[0]
    current_sales_rank INT,   -- Extracted from csv[3]
    current_rating DECIMAL(3,1),  -- Extracted from csv[16]
    current_review_count INT,  -- Extracted from csv[17]
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_keepa_cache_domain ON keepa_products_cache(domain_id);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_stale ON keepa_products_cache(is_stale) WHERE is_stale = false;
CREATE INDEX IF NOT EXISTS idx_keepa_cache_expires ON keepa_products_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_brand ON keepa_products_cache(brand);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_price ON keepa_products_cache(current_price_cents);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_rank ON keepa_products_cache(current_sales_rank);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_rating ON keepa_products_cache(current_rating);
CREATE INDEX IF NOT EXISTS idx_keepa_cache_search_count ON keepa_products_cache(search_count DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_keepa_cache_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.expires_at = NOW() + INTERVAL '7 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER trigger_keepa_cache_updated_at
    BEFORE UPDATE ON keepa_products_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_keepa_cache_updated_at();

-- View for fresh (non-stale) products
CREATE OR REPLACE VIEW keepa_products_fresh AS
SELECT * FROM keepa_products_cache
WHERE is_stale = false;

-- View for products needing refresh
CREATE OR REPLACE VIEW keepa_products_stale AS
SELECT asin, domain_id, title, expires_at, 
       EXTRACT(EPOCH FROM (NOW() - expires_at))/3600 as hours_overdue
FROM keepa_products_cache
WHERE is_stale = true;

COMMENT ON TABLE keepa_products_cache IS 'Keepa API product data cache with 7-day expiration. Stores all 70 Keepa fields to minimize token usage.';
COMMENT ON COLUMN keepa_products_cache.csv IS 'Keepa CSV array with 34 indices: [0]=price, [3]=sales_rank, [16]=rating*10, [17]=review_count';
COMMENT ON COLUMN keepa_products_cache.expires_at IS 'Cache expiration timestamp. Data refreshed after 7 days.';
COMMENT ON COLUMN keepa_products_cache.is_stale IS 'Auto-computed: true if NOW() > expires_at';

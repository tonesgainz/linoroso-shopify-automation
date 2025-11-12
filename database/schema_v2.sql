-- ============================================
-- LINOROSO SHOPIFY AUTOMATION DATABASE SCHEMA V2
-- Improved and tested schema
-- ============================================

USE linoroso_automation;

-- ============================================
-- CONTENT GENERATION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS generated_content (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    content_type ENUM('blog_post', 'product_description', 'social_media', 'email') NOT NULL,
    title VARCHAR(500),
    content TEXT,
    meta_description VARCHAR(255),
    keywords JSON,
    word_count INT,
    seo_score DECIMAL(5,2),
    status ENUM('draft', 'review', 'published', 'archived') DEFAULT 'draft',
    platform VARCHAR(100),
    scheduled_date DATETIME,
    published_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    metadata JSON,
    INDEX idx_content_type (content_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS content_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    content_id BIGINT NOT NULL,
    date DATE NOT NULL,
    views INT DEFAULT 0,
    clicks INT DEFAULT 0,
    impressions INT DEFAULT 0,
    engagement_rate DECIMAL(5,2),
    avg_position DECIMAL(5,2),
    conversions INT DEFAULT 0,
    revenue DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES generated_content(id) ON DELETE CASCADE,
    UNIQUE KEY unique_content_date (content_id, date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SEO & KEYWORD TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS keywords (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    search_volume INT,
    competition VARCHAR(50),
    cpc DECIMAL(10,2),
    difficulty_score INT,
    category VARCHAR(100),
    current_rank INT,
    target_rank INT,
    status ENUM('researching', 'targeting', 'ranking', 'achieved') DEFAULT 'researching',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_keyword (keyword),
    INDEX idx_category (category),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS keyword_rankings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    keyword_id BIGINT NOT NULL,
    rank_position INT,
    page_url VARCHAR(500),
    search_volume INT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE,
    INDEX idx_keyword_date (keyword_id, date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS content_calendar (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content_type ENUM('blog_post', 'product_update', 'social_media', 'email_campaign') NOT NULL,
    topic VARCHAR(255),
    target_keywords JSON,
    scheduled_date DATE NOT NULL,
    assigned_to VARCHAR(100),
    status ENUM('planned', 'in_progress', 'completed', 'cancelled') DEFAULT 'planned',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    notes TEXT,
    content_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES generated_content(id) ON DELETE SET NULL,
    INDEX idx_scheduled_date (scheduled_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- PRODUCT OPTIMIZATION
-- ============================================

CREATE TABLE IF NOT EXISTS products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    shopify_id VARCHAR(100),
    handle VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500),
    description TEXT,
    vendor VARCHAR(100),
    product_type VARCHAR(100),
    price DECIMAL(10,2),
    sku VARCHAR(100),
    tags JSON,
    images JSON,
    seo_title VARCHAR(255),
    seo_description VARCHAR(255),
    seo_score DECIMAL(5,2),
    last_optimized_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_shopify_id (shopify_id),
    INDEX idx_handle (handle),
    INDEX idx_product_type (product_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS product_optimizations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    original_title VARCHAR(500),
    optimized_title VARCHAR(500),
    original_description TEXT,
    optimized_description TEXT,
    original_seo_score DECIMAL(5,2),
    optimized_seo_score DECIMAL(5,2),
    keywords_added JSON,
    optimization_date DATETIME,
    status ENUM('pending', 'optimized', 'published', 'reverted') DEFAULT 'pending',
    performance_before JSON,
    performance_after JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_optimization_date (optimization_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS product_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    date DATE NOT NULL,
    views INT DEFAULT 0,
    add_to_cart INT DEFAULT 0,
    purchases INT DEFAULT 0,
    revenue DECIMAL(10,2),
    conversion_rate DECIMAL(5,2),
    avg_order_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_date (product_id, date),
    INDEX idx_date (date),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- AUTOMATION & SCHEDULING
-- ============================================

CREATE TABLE IF NOT EXISTS task_execution_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    task_type ENUM('content_generation', 'seo_audit', 'product_optimization', 'analytics_sync', 'social_posting') NOT NULL,
    status ENUM('running', 'completed', 'failed', 'cancelled') NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_seconds INT,
    items_processed INT DEFAULT 0,
    error_message TEXT,
    execution_details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_name (task_name),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    schedule_type ENUM('daily', 'weekly', 'monthly', 'custom') NOT NULL,
    schedule_time TIME,
    schedule_day VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_run DATETIME,
    next_run DATETIME,
    configuration JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_is_active (is_active),
    INDEX idx_next_run (next_run)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- ANALYTICS & REPORTING
-- ============================================

CREATE TABLE IF NOT EXISTS traffic_analytics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    source VARCHAR(100),
    medium VARCHAR(100),
    sessions INT DEFAULT 0,
    users INT DEFAULT 0,
    pageviews INT DEFAULT 0,
    bounce_rate DECIMAL(5,2),
    avg_session_duration INT,
    conversions INT DEFAULT 0,
    revenue DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date_source_medium (date, source, medium),
    INDEX idx_date (date),
    INDEX idx_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS seo_audits (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    audit_date DATE NOT NULL,
    total_pages INT,
    indexed_pages INT,
    avg_page_speed DECIMAL(5,2),
    mobile_friendly_score DECIMAL(5,2),
    technical_issues JSON,
    content_issues JSON,
    backlinks_count INT,
    domain_authority DECIMAL(5,2),
    recommendations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_date (audit_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SOCIAL MEDIA TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS social_media_posts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    platform ENUM('instagram', 'tiktok', 'twitter', 'facebook', 'pinterest') NOT NULL,
    post_type ENUM('image', 'video', 'carousel', 'story', 'reel') NOT NULL,
    content TEXT,
    media_urls JSON,
    hashtags JSON,
    scheduled_time DATETIME,
    posted_time DATETIME,
    status ENUM('draft', 'scheduled', 'posted', 'failed') DEFAULT 'draft',
    post_id VARCHAR(255),
    engagement_metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_platform (platform),
    INDEX idx_status (status),
    INDEX idx_scheduled_time (scheduled_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- SYSTEM CONFIGURATION
-- ============================================

CREATE TABLE IF NOT EXISTS system_settings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS api_usage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    api_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    request_count INT DEFAULT 1,
    tokens_used INT,
    cost DECIMAL(10,4),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_api_date (api_name, date),
    INDEX idx_date (date),
    INDEX idx_api_name (api_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- INITIAL DATA
-- ============================================

INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('content_generation_enabled', 'true', 'boolean', 'Enable automated content generation'),
('daily_post_target', '2', 'number', 'Target number of blog posts per day'),
('seo_audit_frequency', 'weekly', 'string', 'How often to run SEO audits'),
('auto_publish_enabled', 'false', 'boolean', 'Automatically publish generated content'),
('api_rate_limit', '50', 'number', 'API requests per minute limit'),
('content_quality_threshold', '0.75', 'number', 'Minimum quality score for auto-publishing')
ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value);

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

SELECT '✅ Database schema v2 created successfully!' as message;
SELECT 'Tables created: 16' as info;
SELECT 'Ready for automation!' as status;

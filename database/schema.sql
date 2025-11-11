-- ============================================
-- LINOROSO SHOPIFY AUTOMATION DATABASE SCHEMA
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS linoroso_automation 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE linoroso_automation;

-- ============================================
-- CONTENT GENERATION TABLES
-- ============================================

-- Generated content tracking
CREATE TABLE IF NOT EXISTS generated_content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_type ENUM('blog_post', 'product_description', 'social_media', 'email') NOT NULL,
    title VARCHAR(500),
    content TEXT,
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
) ENGINE=InnoDB;

-- Content performance metrics
CREATE TABLE IF NOT EXISTS content_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_id INT NOT NULL,
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
) ENGINE=InnoDB;

-- ============================================
-- SEO & KEYWORD TRACKING
-- ============================================

-- Keyword research and tracking
CREATE TABLE IF NOT EXISTS keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- Keyword ranking history
CREATE TABLE IF NOT EXISTS keyword_rankings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword_id INT NOT NULL,
    rank_position INT,
    page_url VARCHAR(500),
    search_volume INT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE,
    INDEX idx_keyword_date (keyword_id, date),
    INDEX idx_date (date)
) ENGINE=InnoDB;

-- Content calendar
CREATE TABLE IF NOT EXISTS content_calendar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content_type ENUM('blog_post', 'product_update', 'social_media', 'email_campaign') NOT NULL,
    topic VARCHAR(255),
    target_keywords JSON,
    scheduled_date DATE NOT NULL,
    assigned_to VARCHAR(100),
    status ENUM('planned', 'in_progress', 'completed', 'cancelled') DEFAULT 'planned',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_scheduled_date (scheduled_date),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- ============================================
-- PRODUCT OPTIMIZATION
-- ============================================

-- Product optimization tracking
CREATE TABLE IF NOT EXISTS product_optimizations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    product_title VARCHAR(500),
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
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_optimization_date (optimization_date)
) ENGINE=InnoDB;

-- Product performance metrics
CREATE TABLE IF NOT EXISTS product_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    views INT DEFAULT 0,
    add_to_cart INT DEFAULT 0,
    purchases INT DEFAULT 0,
    revenue DECIMAL(10,2),
    conversion_rate DECIMAL(5,2),
    avg_order_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_product_date (product_id, date),
    INDEX idx_date (date),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB;

-- ============================================
-- AUTOMATION & SCHEDULING
-- ============================================

-- Task execution log
CREATE TABLE IF NOT EXISTS task_execution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- Scheduled tasks
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- ============================================
-- ANALYTICS & REPORTING
-- ============================================

-- Traffic analytics
CREATE TABLE IF NOT EXISTS traffic_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- SEO audit results
CREATE TABLE IF NOT EXISTS seo_audits (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- ============================================
-- SOCIAL MEDIA TRACKING
-- ============================================

-- Social media posts
CREATE TABLE IF NOT EXISTS social_media_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- ============================================
-- SYSTEM CONFIGURATION
-- ============================================

-- System settings
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
) ENGINE=InnoDB;

-- API usage tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('content_generation_enabled', 'true', 'boolean', 'Enable automated content generation'),
('daily_post_target', '2', 'number', 'Target number of blog posts per day'),
('seo_audit_frequency', 'weekly', 'string', 'How often to run SEO audits'),
('auto_publish_enabled', 'false', 'boolean', 'Automatically publish generated content'),
('api_rate_limit', '50', 'number', 'API requests per minute limit'),
('content_quality_threshold', '0.75', 'number', 'Minimum quality score for auto-publishing')
ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value);

-- ============================================
-- VIEWS FOR REPORTING
-- ============================================

-- Content performance summary view
CREATE OR REPLACE VIEW v_content_performance_summary AS
SELECT 
    gc.id,
    gc.content_type,
    gc.title,
    gc.status,
    gc.published_date,
    SUM(cp.views) as total_views,
    SUM(cp.clicks) as total_clicks,
    SUM(cp.impressions) as total_impressions,
    AVG(cp.engagement_rate) as avg_engagement_rate,
    SUM(cp.conversions) as total_conversions,
    SUM(cp.revenue) as total_revenue
FROM generated_content gc
LEFT JOIN content_performance cp ON gc.id = cp.content_id
GROUP BY gc.id, gc.content_type, gc.title, gc.status, gc.published_date;

-- Keyword ranking trends view
CREATE OR REPLACE VIEW v_keyword_ranking_trends AS
SELECT 
    k.id,
    k.keyword,
    k.category,
    k.current_rank,
    k.target_rank,
    kr.rank_position,
    kr.date,
    LAG(kr.rank_position) OVER (PARTITION BY k.id ORDER BY kr.date) as previous_rank,
    kr.rank_position - LAG(kr.rank_position) OVER (PARTITION BY k.id ORDER BY kr.date) as rank_change
FROM keywords k
LEFT JOIN keyword_rankings kr ON k.id = kr.keyword_id
ORDER BY kr.date DESC;

-- Daily performance dashboard view
CREATE OR REPLACE VIEW v_daily_dashboard AS
SELECT 
    ta.date,
    SUM(ta.sessions) as total_sessions,
    SUM(ta.users) as total_users,
    SUM(ta.pageviews) as total_pageviews,
    AVG(ta.bounce_rate) as avg_bounce_rate,
    SUM(ta.conversions) as total_conversions,
    SUM(ta.revenue) as total_revenue
FROM traffic_analytics ta
GROUP BY ta.date
ORDER BY ta.date DESC;

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Additional composite indexes for common queries
CREATE INDEX idx_content_status_date ON generated_content(status, created_at);
CREATE INDEX idx_keyword_category_status ON keywords(category, status);
CREATE INDEX idx_task_type_status ON task_execution_log(task_type, status);

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

SELECT 'Database schema created successfully!' as message;
SELECT 'Tables created: 18' as info;
SELECT 'Views created: 3' as info;
SELECT 'Ready for Linoroso automation!' as status;

-- Initialize Cambo AI Trader Station Database
-- Create necessary extensions and initial setup

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for encryption functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create indexes for better performance (will be created by Alembic migrations as well)
-- These are additional indexes for common queries

-- User table indexes
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Portfolio table indexes  
-- CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
-- CREATE INDEX IF NOT EXISTS idx_portfolios_created_at ON portfolios(created_at);

-- Position table indexes
-- CREATE INDEX IF NOT EXISTS idx_positions_portfolio_id ON positions(portfolio_id);
-- CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
-- CREATE INDEX IF NOT EXISTS idx_positions_updated_at ON positions(updated_at);

-- Transaction table indexes
-- CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_id ON transactions(portfolio_id);
-- CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);
-- CREATE INDEX IF NOT EXISTS idx_transactions_executed_at ON transactions(executed_at);

-- Performance record indexes
-- CREATE INDEX IF NOT EXISTS idx_performance_portfolio_id ON performance_records(portfolio_id);
-- CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_records(date);

-- Alert table indexes
-- CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
-- CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active);
-- CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cambo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cambo_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO cambo_user;

-- Set default permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cambo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cambo_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO cambo_user;

-- Create application-specific roles
CREATE ROLE cambo_app_role;
GRANT CONNECT ON DATABASE cambo_ai_trader_station TO cambo_app_role;
GRANT USAGE ON SCHEMA public TO cambo_app_role;
GRANT cambo_app_role TO cambo_user;

-- Initialize settings table for application configuration
CREATE TABLE IF NOT EXISTS app_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default application settings
INSERT INTO app_settings (key, value, description) VALUES
('app_name', 'Cambo AI Trader Station', 'Application name'),
('app_version', '2.0.0', 'Current application version'),
('maintenance_mode', 'false', 'Maintenance mode flag'),
('max_users', '1000', 'Maximum number of users'),
('session_timeout', '3600', 'Session timeout in seconds'),
('rate_limit_enabled', 'true', 'Rate limiting enabled flag'),
('audit_logging', 'true', 'Audit logging enabled flag')
ON CONFLICT (key) DO NOTHING;

-- Create audit log table for security tracking
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (action, resource, details)
        VALUES (TG_OP, TG_TABLE_NAME, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (action, resource, details)
        VALUES (TG_OP, TG_TABLE_NAME, jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW)));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (action, resource, details)
        VALUES (TG_OP, TG_TABLE_NAME, row_to_json(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Database maintenance function
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete audit logs older than 1 year
    DELETE FROM audit_logs WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 year';
    
    -- Delete old performance records (keep last 2 years)
    -- This will be uncommented when performance_records table exists
    -- DELETE FROM performance_records WHERE date < CURRENT_DATE - INTERVAL '2 years';
    
    -- Vacuum analyze for performance
    VACUUM ANALYZE;
END;
$$ LANGUAGE plpgsql;

-- Create database statistics view
CREATE OR REPLACE VIEW database_stats AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY tablename, attname;

-- Create performance monitoring view
CREATE OR REPLACE VIEW performance_stats AS
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE schemaname = 'public';

-- Log successful initialization
INSERT INTO audit_logs (action, resource, details, success) 
VALUES ('DATABASE_INIT', 'database', '{"message": "Database initialized successfully"}', true);

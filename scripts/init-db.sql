-- ═══════════════════════════════════════════════════
-- Helpdesk Agent Database Schema
-- ═══════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ═══════════════════════════════════════════════════
-- Users
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    platform VARCHAR(50) DEFAULT 'web',
    external_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ═══════════════════════════════════════════════════
-- Tickets (local cache of external tickets)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id),
    subject TEXT NOT NULL,
    body TEXT,
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'normal',
    assignee VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(platform, external_id)
);

CREATE INDEX idx_tickets_user ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_platform ON tickets(platform);
CREATE INDEX idx_tickets_created ON tickets(created_at DESC);
CREATE INDEX idx_tickets_updated ON tickets(updated_at DESC);

-- ═══════════════════════════════════════════════════
-- Sessions
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    platform VARCHAR(50) DEFAULT 'web',
    message_count INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    ip_address INET
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_active ON sessions(active) WHERE active = TRUE;
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- ═══════════════════════════════════════════════════
-- Rate Limits
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS rate_limits (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    window_seconds INTEGER DEFAULT 3600
);

CREATE INDEX idx_rate_limits_session ON rate_limits(session_id, window_start DESC);
CREATE INDEX idx_rate_limits_user ON rate_limits(user_id, window_start DESC);

-- ═══════════════════════════════════════════════════
-- Audit Log
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_log_session ON audit_log(session_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);

-- ═══════════════════════════════════════════════════
-- Knowledge Base Tracking
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS kb_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    metadata JSONB DEFAULT '{}',
    indexed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source, content_hash)
);

CREATE INDEX idx_kb_source ON kb_tracking(source);

-- ═══════════════════════════════════════════════════
-- Cost Tracking
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS cost_tracking (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id),
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER DEFAULT 0,
    estimated_cost_usd NUMERIC(10,6) DEFAULT 0,
    model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cost_tracking_session ON cost_tracking(session_id);
CREATE INDEX idx_cost_tracking_date ON cost_tracking(created_at DESC);

-- ═══════════════════════════════════════════════════
-- Helper: Update updated_at timestamp
-- ═══════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_tickets_updated_at BEFORE UPDATE ON tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at();

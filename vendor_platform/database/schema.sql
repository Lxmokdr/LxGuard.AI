-- Vendor Platform Database Schema
-- Completely separate from enterprise deployments

CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    contact_email VARCHAR NOT NULL,
    organization_type VARCHAR DEFAULT 'enterprise',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS licenses (
    id VARCHAR PRIMARY KEY,
    license_key VARCHAR UNIQUE NOT NULL,
    customer_id VARCHAR REFERENCES customers(id) ON DELETE CASCADE,
    status VARCHAR DEFAULT 'active',
    expires_at TIMESTAMP,
    max_instances INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS instances (
    id VARCHAR PRIMARY KEY,
    instance_id VARCHAR UNIQUE NOT NULL,
    license_key VARCHAR REFERENCES licenses(license_key) ON DELETE SET NULL,
    hostname VARCHAR,
    version VARCHAR,
    last_seen TIMESTAMP,
    status VARCHAR DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR REFERENCES instances(instance_id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    query_count BIGINT DEFAULT 0,
    error_count BIGINT DEFAULT 0,
    uptime BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS admin_users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT NOW()
);

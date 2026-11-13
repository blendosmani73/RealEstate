-- Skema e Real Estate Data Engine.
-- Ekzekutohet automatikisht nga imazhi i PostgreSQL
-- në nisjen e parë (docker-entrypoint-initdb.d).

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    neighborhood VARCHAR(255),
    price NUMERIC(12, 2) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    area_sqm NUMERIC(10, 2) NOT NULL,
    price_per_sqm NUMERIC(12, 2) NOT NULL,
    property_type VARCHAR(100) NOT NULL,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_price_positive CHECK (price > 0),
    CONSTRAINT chk_area_positive CHECK (area_sqm > 0)
);

CREATE INDEX IF NOT EXISTS idx_properties_location
    ON properties USING btree (location);

CREATE INDEX IF NOT EXISTS idx_properties_price
    ON properties USING btree (price);

CREATE INDEX IF NOT EXISTS idx_properties_property_type
    ON properties USING btree (property_type);

CREATE INDEX IF NOT EXISTS idx_properties_created_by_id
    ON properties USING btree (created_by_id);

-- Mobile Banking Transaction Data Warehouse: PostgreSQL Star Schema

CREATE TABLE IF NOT EXISTS dim_time (
    time_key BIGSERIAL PRIMARY KEY,
    simulation_step BIGINT NOT NULL UNIQUE,
    simulation_hour INTEGER
);

CREATE TABLE IF NOT EXISTS dim_transaction_type (
    transaction_type_key BIGSERIAL PRIMARY KEY,
    transaction_type VARCHAR(30) NOT NULL UNIQUE,
    transaction_category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_sender (
    sender_key BIGSERIAL PRIMARY KEY,
    sender_account VARCHAR(40) NOT NULL UNIQUE,
    sender_account_class VARCHAR(20),
    sender_region VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_receiver (
    receiver_key BIGSERIAL PRIMARY KEY,
    receiver_account VARCHAR(40) NOT NULL UNIQUE,
    receiver_account_class VARCHAR(20),
    receiver_region VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_key BIGSERIAL PRIMARY KEY,
    external_transaction_id VARCHAR(100) UNIQUE,
    time_key BIGINT NOT NULL REFERENCES dim_time(time_key),
    sender_key BIGINT NOT NULL REFERENCES dim_sender(sender_key),
    receiver_key BIGINT NOT NULL REFERENCES dim_receiver(receiver_key),
    transaction_type_key BIGINT NOT NULL REFERENCES dim_transaction_type(transaction_type_key),
    amount NUMERIC(18,2) NOT NULL CHECK (amount >= 0),
    sender_old_balance NUMERIC(18,2),
    sender_new_balance NUMERIC(18,2),
    receiver_old_balance NUMERIC(18,2),
    receiver_new_balance NUMERIC(18,2),
    is_fraud BOOLEAN NOT NULL DEFAULT FALSE,
    is_flagged_fraud BOOLEAN NOT NULL DEFAULT FALSE,
    data_quality_status VARCHAR(20) NOT NULL DEFAULT 'VALID',
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_transactions(time_key);
CREATE INDEX IF NOT EXISTS idx_fact_sender ON fact_transactions(sender_key);
CREATE INDEX IF NOT EXISTS idx_fact_receiver ON fact_transactions(receiver_key);
CREATE INDEX IF NOT EXISTS idx_fact_type ON fact_transactions(transaction_type_key);
CREATE INDEX IF NOT EXISTS idx_fact_fraud ON fact_transactions(is_fraud);

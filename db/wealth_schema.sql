PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS person (
    person_id TEXT PRIMARY KEY,
    display_name TEXT,
    base_currency TEXT NOT NULL DEFAULT 'TWD',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset (
    asset_id TEXT PRIMARY KEY,
    owner_person_id TEXT NOT NULL,
    category TEXT NOT NULL,
    institution TEXT,
    description TEXT,
    ownership_pct NUMERIC NOT NULL CHECK (ownership_pct >= 0 AND ownership_pct <= 1),
    currency TEXT NOT NULL DEFAULT 'TWD',
    active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (owner_person_id) REFERENCES person(person_id)
);

CREATE TABLE IF NOT EXISTS liability (
    liability_id TEXT PRIMARY KEY,
    owner_person_id TEXT NOT NULL,
    linked_asset_id TEXT,
    category TEXT NOT NULL,
    institution TEXT,
    description TEXT,
    currency TEXT NOT NULL DEFAULT 'TWD',
    active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (owner_person_id) REFERENCES person(person_id),
    FOREIGN KEY (linked_asset_id) REFERENCES asset(asset_id)
);

CREATE TABLE IF NOT EXISTS evidence_source (
    source_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    evidence_level TEXT NOT NULL CHECK (evidence_level IN ('E0','E1','E2','E3','E4','E5')),
    obtained_at TEXT,
    reference_uri TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS asset_observation (
    observation_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    gross_value NUMERIC NOT NULL CHECK (gross_value >= 0),
    valuation_date TEXT NOT NULL,
    valuation_method TEXT,
    observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES asset(asset_id),
    FOREIGN KEY (source_id) REFERENCES evidence_source(source_id)
);

CREATE TABLE IF NOT EXISTS liability_observation (
    observation_id TEXT PRIMARY KEY,
    liability_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    balance NUMERIC NOT NULL CHECK (balance >= 0),
    valuation_date TEXT NOT NULL,
    observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (liability_id) REFERENCES liability(liability_id),
    FOREIGN KEY (source_id) REFERENCES evidence_source(source_id)
);

CREATE TABLE IF NOT EXISTS reconciliation_run (
    run_id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    value_tolerance NUMERIC NOT NULL DEFAULT 0.10,
    gross_assets NUMERIC NOT NULL,
    total_liabilities NUMERIC NOT NULL,
    net_worth NUMERIC NOT NULL,
    confidence NUMERIC NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

CREATE TABLE IF NOT EXISTS reconciliation_exception (
    exception_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    exception_code TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('INFO','WARN','HIGH')),
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES reconciliation_run(run_id)
);

CREATE INDEX IF NOT EXISTS idx_asset_owner ON asset(owner_person_id);
CREATE INDEX IF NOT EXISTS idx_liability_owner ON liability(owner_person_id);
CREATE INDEX IF NOT EXISTS idx_asset_obs_asset_date ON asset_observation(asset_id, valuation_date);
CREATE INDEX IF NOT EXISTS idx_liability_obs_liability_date ON liability_observation(liability_id, valuation_date);
CREATE INDEX IF NOT EXISTS idx_exception_run ON reconciliation_exception(run_id);

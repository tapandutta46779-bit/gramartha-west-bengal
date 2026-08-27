CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE geographic_identity (
    geo_id text PRIMARY KEY,
    state text NOT NULL,
    district text NOT NULL,
    block text,
    gram_panchayat text,
    municipality text,
    ward text,
    locality text NOT NULL,
    locality_type text NOT NULL,
    census_code text,
    lgd_code text,
    pin_codes text[] NOT NULL DEFAULT '{}',
    point geometry(Point, 4326),
    aliases text[] NOT NULL DEFAULT '{}',
    source_ids text[] NOT NULL DEFAULT '{}',
    quality_flags text[] NOT NULL DEFAULT '{}'
);

CREATE INDEX geographic_identity_point_gix ON geographic_identity USING gist(point);
CREATE INDEX geographic_identity_district_idx ON geographic_identity(state, district);

CREATE TABLE evidence_source (
    source_id text PRIMARY KEY,
    name text NOT NULL,
    dataset text NOT NULL,
    url text NOT NULL,
    version text NOT NULL,
    retrieved_at timestamptz NOT NULL,
    checksum_sha256 text,
    geographic_coverage text NOT NULL,
    license_or_terms text
);

CREATE TABLE evidence_record (
    evidence_id text PRIMARY KEY,
    geo_id text NOT NULL REFERENCES geographic_identity(geo_id),
    variable text NOT NULL,
    value_json jsonb NOT NULL,
    unit text NOT NULL,
    source_id text NOT NULL REFERENCES evidence_source(source_id),
    observation_date date,
    retrieved_at timestamptz NOT NULL,
    evidence_type text NOT NULL CHECK (evidence_type IN
        ('OBSERVED','SAMPLED','ESTIMATED','INFERRED','MODELLED','SYNTHETIC')),
    confidence text NOT NULL CHECK (confidence IN ('HIGH','MEDIUM','LOW','INSUFFICIENT')),
    methodology_version text NOT NULL,
    raw_reference text,
    attributes jsonb NOT NULL DEFAULT '{}',
    quality_flags text[] NOT NULL DEFAULT '{}'
);

CREATE INDEX evidence_record_geo_variable_idx ON evidence_record(geo_id, variable);

CREATE TABLE venture_analysis (
    analysis_id uuid PRIMARY KEY,
    geo_id text REFERENCES geographic_identity(geo_id),
    created_at timestamptz NOT NULL,
    status text NOT NULL,
    methodology_version text NOT NULL,
    decision_json jsonb NOT NULL
);

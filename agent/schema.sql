-- Run once against your ClickHouse Cloud service to create the database and tables.
-- $ cat schema.sql | curl -u default:$CLICKHOUSE_PASSWORD "https://$CLICKHOUSE_HOST:8443/" --data-binary @-

CREATE DATABASE IF NOT EXISTS donor_agent;

-- Committee master: committee ID → name, type, state
CREATE TABLE IF NOT EXISTS donor_agent.committees (
    cmte_id     String,
    cmte_nm     String,
    cmte_tp     String,   -- P=PAC, Q=PAC(qualified), N=PAC(non-qual), etc.
    cmte_st     String,   -- committee state
    cand_id     String    -- linked candidate ID if any
) ENGINE = ReplacingMergeTree()
ORDER BY cmte_id;

-- Cause tags: committee ID → one or more cause tags (one row per tag)
CREATE TABLE IF NOT EXISTS donor_agent.committee_causes (
    cmte_id     String,
    cause_tag   String   -- e.g. 'environment', 'education', 'healthcare'
) ENGINE = MergeTree()
ORDER BY (cause_tag, cmte_id);

-- FEC individual contributions (filtered: IND entity, amount >= $200, 2020–2024)
CREATE TABLE IF NOT EXISTS donor_agent.contributions (
    cmte_id         String,
    contributor_nm  String,
    city            String,
    state           String,
    zip_code        String,
    employer        String,
    occupation      String,
    transaction_dt  Date,
    transaction_amt Int32,
    sub_id          UInt64    -- FEC unique row ID
) ENGINE = MergeTree()
ORDER BY (state, contributor_nm, transaction_dt)
PARTITION BY toYear(transaction_dt);

-- FEC candidate master: committee → candidate → party/office
CREATE TABLE IF NOT EXISTS donor_agent.candidates (
    cand_id     String,
    cand_name   String,
    cand_party  String,   -- DEM, REP, IND, etc.
    cand_office String,   -- P=President, S=Senate, H=House
    cand_st     String,
    cand_yr     UInt16
) ENGINE = ReplacingMergeTree()
ORDER BY (cand_id, cand_yr);

-- Nonprofit board members / officers from IRS 990 filings (via ProPublica)
-- Each row = one person's role at one nonprofit for one filing year
CREATE TABLE IF NOT EXISTS donor_agent.nonprofit_affiliations (
    nonprofit_ein   String,
    nonprofit_name  String,
    nonprofit_state String,
    cause_tag       String,
    person_name     String,
    role            String,
    filing_year     UInt16,
    source_url      String
) ENGINE = ReplacingMergeTree()
ORDER BY (cause_tag, nonprofit_state, person_name, nonprofit_ein, filing_year);

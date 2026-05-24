# TAGGING-QUALITY: cause_tag.py audit & fixes

> The NL→query strategy lives in `QUERYING.md` (canonical) and `agent/cause_synonyms.py` (implemented).
> This doc covers data quality issues, false-positive fixes applied, and coverage status.
> **For the friend (owns `agent/cause_tag.py`).**

---

## STATUS (2026-05-23, verified against live ClickHouse)

| Table | Row count | Notes |
|---|---|---|
| `committees` | 20,940 | Loaded ✓ |
| `committee_causes` | ~2,336 tagged | 11% of committees, see below |
| `contributions` | **0 rows** → **loading now** | Blocked demo. See "Fix #1" |
| `candidates` | ~8,580 | Loaded ✓ |
| `nonprofit_affiliations` | 0 rows | Not loaded, low priority for demo |

---

## ⚠️ CRITICAL BLOCKER: contributions table was empty

**`donor_agent.contributions` had 0 rows.** Committees and causes were loaded but
`load_contributions` was never run. The `query()` function in `clickhouse_client.py`
JOINs on this table, so it returned nothing for every ask.

### Fix applied (2026-05-23)

```bash
python3 load_fec.py --skip-committees --skip-candidates --states WA CA NY TX
```

Loads 2024 cycle, 4 high-donor-density states (WA, CA, NY, TX). Downloads the full
4.2GB `indiv24.zip` and filters to those states at parse time. Estimated ~30–60 min.
This is running in background, check PID 73873 or `/tmp/fec_load.log` for progress.

**Why state-filtered:** FEC bulk data is not partitioned, so you have to download the
whole file regardless. Filtering to 4 states gives hundreds of thousands of rows for
demo purposes without waiting for all 50 states.

---

## Coverage gap: only 11% of committees tagged

### Root cause

`cause_tag.py` matches keywords against committee *names* using `kw in name_lower`
(simple substring). This has two problems:

1. **Candidate committees are named after people**, not issues:
   for `"FRIENDS OF JOHN SMITH"` or `"WARNOCK FOR GEORGIA"`, no keyword ever fires.
   8,223 candidate committees exist, but only 187 were tagged (those whose *name*
   happened to contain a cause keyword, e.g. a candidate surnamed "Green").

2. **No word boundaries**, which causes substring false positives: `"labor"` matched
   `"LABORATORY"`, `"tech"` matched `"BIOTECH"`, `"earth"` matched `"HEARTH"`.

### Coverage numbers

| Scenario | Committees tagged | Coverage |
|---|---|---|
| Baseline (before fixes) | ~2,336 | 11.2% |
| After keyword fixes only | ~2,200 | ~10.5% (precision ↑, recall ≈flat) |
| After keyword fixes + candidate party tagging | 9,521 | **23.4%** (confirmed live) |

The coverage number only moves substantially with **candidate committee tagging** (see below).

---

## Fix #2: Keyword false-positive fixes applied to cause_tag.py

Switched matching from `kw in name_lower` to **word-boundary regex** (`\b...\b`)
and replaced the worst bare-keyword offenders with compound phrases.

### What was removed and why

| Removed keyword | Cause | Why removed | Replacement |
|---|---|---|---|
| `"reform"` | criminal_justice | Matched "TAX REFORM PAC", "REFORM PARTY", "HEALTHCARE REFORM NOW" | `"prison reform"`, `"police reform"`, `"bail reform"`, `"sentencing reform"` |
| `"social"` | social_welfare | "NATIONAL COMMITTEE TO PRESERVE SOCIAL SECURITY", SS PACs are the 3rd-largest PAC category | `"social services"`, `"human services"` |
| `"green"` | environment | Surname: "AL GREEN FOR CONGRESS", "GENE GREEN FOR SENATE", "WALGREEN CO PAC" | Dropped. `"climate"`, `"clean energy"`, `"conservation"` still cover real env orgs |
| `"equity"` | civil_rights | "PRIVATE EQUITY GROWTH CAPITAL COUNCIL PAC", private equity is the biggest FP | `"racial equity"`, `"gender equity"`, `"equity justice"` |
| `"trade"` | labor | "FREE TRADE ALLIANCE", "NATIONAL RETAIL FEDERATION PAC", trade policy is not labor | Kept only in `foreign_policy` as `"free trade"` |
| `"labor"` (bare) | labor | "MARINE BIOLOGICAL LABORATORY PAC", word boundary now handles this | Now matched via `\blabor\b` regex |
| `"marine"` (bare) | veterans | "MARINE ENGINEERS' BENEFICIAL ASSOC", "NATIONAL MARINE MANUFACTURERS", maritime industry, not military | `"marine corps"`, `"marines"` |
| `"ai "` | technology | Fragile trailing-space trick, matched "AIR BRAKE TECHNOLOGIES" | Kept `"artificial intelligence"` only |
| `"international"` (bare) | foreign_policy | Matched every international union: Teamsters, IBEW, Firefighters, already tagged as labor | `"international relations"`, `"international affairs"` |
| `"affordable"` (bare) | housing | "AFFORDABLE CARE ACT ALLIANCE" was wrongly tagged housing, it's healthcare | `"affordable housing"` |
| `"culture"` / `"heritage"` | arts_culture | "HERITAGE FOUNDATION PAC" (conservative think tank), "CULTURE OF LIFE PAC" | `"performing arts"`, `"arts and culture"`, `"cultural heritage"` |
| `"women"` | civil_rights | "WOMEN FOR TRUMP", directionally ambiguous | `"women's rights"` |
| `"credit"` (bare) | finance | "CREDITWORTHY CANDIDATES PAC" | `"credit union"` |
| `"global"` (bare) | foreign_policy | "GLOBALTRAK PAC" | `"global policy"` |
| `"food"` (bare) | agriculture | Double-tagged with social_welfare, and "food bank" belongs in social_welfare | `"food policy"` in agriculture, `"food bank"` stays in social_welfare |

### The word-boundary regex switch

```python
# Before (substring — no word boundaries)
if any(kw in name_lower for kw in keywords):

# After (word boundaries compiled at import time)
_PATTERNS = {cause: [re.compile(r"\b" + re.escape(kw) + r"\b") for kw in keywords] ...}
if any(p.search(name_lower) for p in patterns):
```

This fixes the cases `"labor"→"laboratory"`, `"tech"→"biotech"`, `"earth"→"hearth"`, and `"credit"→"creditworthy"`.

---

## Fix #3: Candidate committee tagging via party inference (SQL INSERT)

Candidate committees (type `P` in `cmte_tp`) are named after people and will never
match keyword rules. They represent the majority of FEC money. Fix: join to the
`candidates` table (already loaded) and tag by party.

### SQL applied

```sql
INSERT INTO donor_agent.committee_causes (cmte_id, cause_tag)
SELECT co.cmte_id,
       multiIf(
           ca.cand_party = 'DEM', 'civil_rights',
           ca.cand_party = 'REP', 'small_business',
           'social_welfare'
       ) AS cause_tag
FROM donor_agent.committees co
JOIN donor_agent.candidates ca ON co.cand_id = ca.cand_id
WHERE co.cmte_tp = 'P'
  AND co.cmte_id NOT IN (SELECT cmte_id FROM donor_agent.committee_causes)
```

**Why party→cause mapping:** Coarse but real signal. DEM candidates skew to civil
rights and social policy causes, and REP candidates skew to business and fiscal causes.
For the demo this is defensible. For production, Nimble enrichment (pulling the
candidate's website policy page) gives the precise issue positions.

**Impact (confirmed 2026-05-23):** Tagged 11,572 additional committees.
Coverage jumped from 11% to **23.4%** (9,521 unique committees, 16,898 tag rows).

Tag distribution after INSERT:
- `small_business`: 5,074 (REP candidates)
- `civil_rights`: 4,737 (DEM candidates)
- `social_welfare`: 2,359 (IND/other)
- Plus all original PAC-based keyword tags unchanged

---

## Remaining known issues (low priority for demo)

| Issue | Impact | Fix if time |
|---|---|---|
| `"community"` in social_welfare still matches community banks | Minor | Replace with `"community organizing"`, `"community health"` |
| `"border"` in immigration is directionally ambiguous (pro/anti immigration) | Low | Accept, FEC data doesn't encode stance |
| `"college"` matches "Electoral College PAC" | Very low | Word boundary doesn't help, add stop-list |
| `nonprofit_affiliations` table empty | Employer cross-reference bonus doesn't fire | Run `load_nonprofits.py` if time allows |

---

## Demo cause recommendations (based on tagged committee counts)

These causes have enough tagged committees to produce rich results:

| Cause | Tagged committees | Recommended for demo |
|---|---|---|
| `labor` | 354 | ✓ Strong |
| `healthcare` | 271 | ✓ Strong |
| `energy` | 342 | ✓ Strong |
| `environment` | 165 | ✓ Good |
| `housing` | 24 | ✗ Too thin |
| `immigration` | 25 | ✗ Too thin |
| `small_business` | 21 | ✗ Too thin |

Use `environment`, `healthcare`, `labor`, or `energy` for demo queries.

---

## Evidence the cause-affinity model holds (for the pitch)

Giving clusters along value axes (Moral Foundations Theory): care/fairness donors
skew to civil_rights, environment, and immigration, while loyalty/authority donors skew to
veterans and gun_rights. Donation platforms profile donors this way. Caveat: ~44% of
giving is local/personal, so keep affinity a *score booster, not a hard filter*.

Sources: Nilsson et al. (Eur. J. Personality 2020), Thottam & Kalamas
(J. Consumer Behaviour 2024).

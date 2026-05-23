"""
Loads cause-relevant nonprofit organizations from ProPublica Nonprofit Explorer
(IRS 990 data, free API, no key required) into the `nonprofit_orgs` table.

These org names are then cross-referenced against the `employer` field in FEC
contributions — donors who both work at cause-aligned nonprofits AND give to
cause-aligned political committees are high-conviction prospects.

Usage:
    python load_nonprofits.py                          # all causes, all states
    python load_nonprofits.py --causes environment education healthcare
    python load_nonprofits.py --states WA OR CA
    python load_nonprofits.py --causes environment --orgs-per-cause 40
"""

import argparse
import os
import time

import certifi
import clickhouse_connect
import requests
from dotenv import load_dotenv

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CLICKHOUSE_HOST     = os.environ["CLICKHOUSE_HOST"]
CLICKHOUSE_PORT     = int(os.environ.get("CLICKHOUSE_PORT", 8443))
CLICKHOUSE_USER     = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ["CLICKHOUSE_PASSWORD"]
CLICKHOUSE_DB       = os.environ.get("CLICKHOUSE_DB", "donor_agent")

PROPUBLICA_BASE = "https://projects.propublica.org/nonprofits/api/v2"
PROPUBLICA_ORG_URL = "https://projects.propublica.org/nonprofits/organizations/{ein}"

CAUSE_SEARCH_TERMS: dict[str, list[str]] = {
    "environment":        ["environment", "conservation", "climate", "wildlife",
                           "clean water", "clean energy", "nature", "ocean"],
    "education":          ["education foundation", "literacy", "scholarship",
                           "school fund", "learning"],
    "healthcare":         ["health foundation", "cancer", "medical research",
                           "public health", "mental health"],
    "housing":            ["affordable housing", "homelessness", "community housing",
                           "shelter", "habitat"],
    "civil_rights":       ["civil rights", "voting rights", "equity justice", "naacp",
                           "aclu", "disability rights"],
    "immigration":        ["immigration legal", "refugee resettlement", "immigrant"],
    "social_welfare":     ["food bank", "poverty relief", "community services",
                           "hunger", "human services"],
    "arts_culture":       ["arts foundation", "cultural center", "museum foundation",
                           "arts council"],
    "labor":              ["workers rights", "labor", "workforce development"],
    "veterans":           ["veterans services", "military families", "veterans support"],
    "criminal_justice":   ["criminal justice reform", "reentry", "prison reform"],
    "agriculture":        ["sustainable agriculture", "farmland preservation",
                           "food systems"],
    "reproductive_rights": ["reproductive health", "family planning", "womens health"],
}


def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD,
        secure=True, verify=certifi.where(),
    )


def _get(url: str, params: dict = None, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            r = requests.get(
                url, params=params, timeout=30,
                headers={"User-Agent": "Tribe/1.0 (nonprofit research tool)"},
            )
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1)
    return {}


def search_orgs(term: str, state: str | None = None, page: int = 0) -> list[dict]:
    params = {"q": term, "page": page}
    if state:
        params["state[id]"] = state
    data = _get(f"{PROPUBLICA_BASE}/search.json", params=params)
    return data.get("organizations", [])


def load_cause(
    client,
    cause: str,
    terms: list[str],
    states: list[str],
    orgs_per_cause: int,
) -> int:
    seen_eins: set[str] = set()
    rows: list[tuple] = []
    target_states = states if states else [None]

    for term in terms:
        if len(seen_eins) >= orgs_per_cause:
            break
        for state in target_states:
            if len(seen_eins) >= orgs_per_cause:
                break
            for page in range(4):
                try:
                    orgs = search_orgs(term, state=state, page=page)
                except Exception as e:
                    print(f"    search error ({term}, {state}, p{page}): {e}")
                    break
                if not orgs:
                    break

                for org in orgs:
                    if len(seen_eins) >= orgs_per_cause:
                        break
                    ein = str(org.get("ein", "")).strip()
                    if not ein or ein in seen_eins:
                        continue
                    seen_eins.add(ein)

                    name       = (org.get("name") or "").strip()
                    org_state  = (org.get("state") or state or "").strip()
                    city       = (org.get("city") or "").strip()
                    revenue    = int(org.get("income_amount") or 0)
                    source_url = PROPUBLICA_ORG_URL.format(ein=ein)

                    if not name:
                        continue

                    rows.append((ein, name, city, org_state, cause, revenue, source_url))
                    print(f"    [{len(seen_eins)}/{orgs_per_cause}] {name} ({org_state})")

                time.sleep(0.3)

    if rows:
        client.insert(
            f"{CLICKHOUSE_DB}.nonprofit_orgs",
            rows,
            column_names=[
                "nonprofit_ein", "nonprofit_name", "nonprofit_city",
                "nonprofit_state", "cause_tag", "annual_revenue", "source_url",
            ],
        )
        print(f"  Inserted {len(rows)} orgs for cause={cause}.")
    else:
        print(f"  No orgs found for cause={cause}.")

    return len(rows)


def ensure_table(client):
    client.command(f"""
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB}.nonprofit_orgs (
        nonprofit_ein    String,
        nonprofit_name   String,
        nonprofit_city   String,
        nonprofit_state  String,
        cause_tag        String,
        annual_revenue   Int64,
        source_url       String
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (cause_tag, nonprofit_state, nonprofit_ein)
    """)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--causes", nargs="*",
                        default=list(CAUSE_SEARCH_TERMS.keys()))
    parser.add_argument("--states", nargs="*", default=[],
                        help="2-letter state codes (default: all states)")
    parser.add_argument("--orgs-per-cause", type=int, default=30)
    args = parser.parse_args()

    causes   = [c for c in args.causes if c in CAUSE_SEARCH_TERMS]
    states   = [s.upper() for s in args.states]
    orgs_per = args.orgs_per_cause

    if not causes:
        print("No valid causes. Choose from:", list(CAUSE_SEARCH_TERMS.keys()))
        return

    client = get_client()
    ensure_table(client)
    total = 0

    print(f"Loading nonprofit orgs: {len(causes)} causes, "
          f"states={states or 'all'}, orgs_per_cause={orgs_per}")

    for cause in causes:
        terms = CAUSE_SEARCH_TERMS[cause]
        print(f"\n=== {cause} ===")
        n = load_cause(client, cause, terms, states, orgs_per)
        total += n

    print(f"\nDone. {total} total org rows inserted.")


if __name__ == "__main__":
    main()

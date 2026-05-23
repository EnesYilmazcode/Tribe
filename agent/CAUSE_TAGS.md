# Cause Tags — Reference for the Agent

Use these exact tag strings when calling `query(cause=...)` or `query(causes=[...])`.
Each tag maps to committees whose names contain the listed keywords.

## Tag List

| Tag | What it covers |
|-----|---------------|
| `environment` | Climate, clean energy, clean water, conservation, Sierra Club, wildlife, ocean, wilderness, sustainability |
| `education` | Schools, teachers, students, universities, literacy, learning, academic programs |
| `healthcare` | Health, hospitals, cancer, mental health, disease, pharma, nurses, doctors, clinics, Medicare/Medicaid |
| `housing` | Affordable housing, homelessness, tenant rights, shelters, rental assistance, community development |
| `immigration` | Immigrant rights, refugees, asylum, DACA, border policy |
| `criminal_justice` | Prison reform, policing, incarceration, public safety, law enforcement reform |
| `civil_rights` | Civil rights, equity, equality, anti-discrimination, NAACP, voting rights, disability, LGBTQ, women's rights |
| `labor` | Unions, worker rights, wages, AFL-CIO, SEIU, Teamsters, trade policy |
| `veterans` | Veterans affairs, military, armed forces, soldier support, Navy, Army, Marines, Air Force |
| `gun_control` | Gun policy, firearms, NRA, Second Amendment, gun safety, gun violence prevention |
| `reproductive_rights` | Reproductive health, abortion, Planned Parenthood, NARAL, pro-choice, pro-life, family planning |
| `agriculture` | Farming, rural communities, crops, livestock, food policy |
| `small_business` | Small business, entrepreneurship, startups, chambers of commerce |
| `technology` | Tech, innovation, AI, digital policy, internet, cybersecurity |
| `finance` | Banking, financial regulation, Wall Street, securities, investment, credit |
| `energy` | Oil, gas, coal, pipelines, utilities, electric grid, nuclear, solar, wind |
| `foreign_policy` | Foreign affairs, international relations, Israel, Ukraine, NATO, Asia, Middle East, global trade |
| `social_welfare` | Poverty, food banks, hunger, welfare programs, community organizations, charities, nonprofits |
| `infrastructure` | Transportation, transit, highways, broadband, water systems |
| `arts_culture` | Arts, culture, museums, music, film, theater, cultural heritage |

## How to query

Single cause:
```python
from clickhouse_client import query

# Top environment donors in Washington state, $1k+ gifts
prospects = query(cause="environment", geo="WA", min_amount=1000)

# Top healthcare donors nationally, $500+ gifts
prospects = query(cause="healthcare", min_amount=500)
```

Multiple causes — call query() for each and merge/re-rank:
```python
results = {}
for cause in ["environment", "social_welfare"]:
    for p in query(cause=cause, geo="CA", min_amount=500):
        key = p["name"]
        if key not in results:
            results[key] = p
        else:
            # donor appeared in both — boost score and merge tags
            results[key]["affinity_score"] = min(100, results[key]["affinity_score"] + 15)
            results[key]["cause_tags"] = list(set(results[key]["cause_tags"] + p["cause_tags"]))

prospects = sorted(results.values(), key=lambda x: x["affinity_score"], reverse=True)
```

## What each prospect record contains

```jsonc
{
  "name": "Jane Donor",
  "affinity_score": 87,          // 0–100, log-scaled from total giving
  "cause_tags": ["environment", "social_welfare"],
  "geo": "WA",
  "city": "Seattle",
  "employer": "Microsoft",
  "occupation": "Software Engineer",
  "total_given": 45000,          // lifetime total to matching cause committees
  "donation_history": [          // individual transactions, newest first
    {
      "date": "2024-03-15",
      "amount": 5000,
      "committee_id": "C00401224",
      "committee_name": "SIERRA CLUB POLITICAL COMMITTEE",
      "cause_tags": ["environment"]
    }
  ],
  "cited_reasons": [
    {
      "text": "Gave $45,000 across 12 environment committee donations (2020–2024)",
      "source_url": "https://www.fec.gov/data/receipts/?committee_id=C00401224"
    }
  ],
  "enrichment": null             // filled by nimble_client.enrich()
}
```

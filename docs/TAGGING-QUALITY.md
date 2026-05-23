# TAGGING-QUALITY — false-positive fixes for cause_tag.py

> The NL→query strategy lives in `QUERYING.md` (canonical) and `agent/cause_synonyms.py` (implemented).
> This doc only adds the one thing those don't: specific bugs in the committee-name keyword tagging that produce wrong tags. **For the friend (owns `agent/cause_tag.py`).**

## ⚠️ CRITICAL BLOCKER (validated against real ClickHouse 2026-05-23)
**`donor_agent.contributions` is EMPTY (0 rows).** committees (20,940) and committee_causes (2,336 tagged) ARE loaded, but the individual-contribution data is not. So `query()` returns **0 results** for every ask and the platform shows nothing on real data. **Loading contributions is the critical path — nothing demos until it's done.** (Friend's side.)

## CONFIRMED false positives (sampled from real committee names, 2026-05-23)
Severity ranked worst-first:
1. **`marine` → veterans — every sampled hit wrong.** Maritime industry, not the Marines: "Marine Engineers' Beneficial Association", "Marine Fireman's Union", "National Marine Manufacturers Association", "SSA Marine Inc". Fix: require `"marine corps"` / `"u.s. marine"`.
2. **`reform` → criminal_justice.** Catches the *Reform Party* (general third party): "Reform Party of Kansas/PA/USA". Fix: drop bare word; keep `"prison reform"`, `"police reform"`.
3. **`green` → environment.** "Walgreen Co Pac", "Greenberg Traurig P.A. Pac" (law firm), "Green Party". Fix: drop; rely on `"climate"`, `"conservation"`.
4. **`social` → social_welfare.** "Socialist Workers/National Committee", union "Social Action" funds. Fix: use `"social services"`, `"human services"`.
5. **`trade` → labor — mixed.** Correct for trade *unions* ("Building Trades", "Pipe Trades") but wrong for trade *associations*. Fix: exclude `"trade association"`.
6. **`ai ` → technology — minor.** Few hits ("Air Brake Technologies"). Fix: keep `"artificial intelligence"` only.
7. **`women` → civil_rights — mostly fine** (NOW, Women's Political Caucus are real women's-rights orgs). Low priority.

Note: these matter because donors to a mis-tagged committee surface under the wrong cause (donors to "Walgreen Co Pac" would show as "environment donors").

## Predicted table (kept for reference)
Current matcher is naive substring (`kw in name_lower`), no word boundaries:

| Keyword | Wrong tag | Mis-tags | Fix |
|---|---|---|---|
| `"reform"` | criminal_justice | "Tax Reform", "Education Reform" | drop bare word; keep `"prison reform"`, `"police reform"` |
| `"social"` | social_welfare | "Social Security", "Social Media" | drop bare word; use `"social services"`, `"human services"` |
| `"trade"` | labor + foreign_policy | "Trade Association", "Board of Trade" | drop from labor; foreign_policy keep `"free trade"` only |
| `"women"` | civil_rights | "Women in Tech", "Women for Trump" | narrow to `"women's rights"`, `"gender equality"` |
| `"green"` | environment | surname "Green", "Evergreen" | drop; rely on `"climate"`, `"conservation"`, `"clean energy"` |
| `"ai "` | technology | "Air Force", "Repair", "Chair" | drop; keep `"artificial intelligence"` |
| `"gun"` | gun_control | "Gunderson", "Gunn" | word-boundary; keep `"gun safety"`, `"firearm"`, `"nra"` |
| `"food"` | agriculture | collides with "food bank" (social_welfare) | agriculture use `"food policy"`; keep `"food bank"` in social_welfare |

## One structural fix kills most of these — word-boundary regex
```python
import re
CAUSE_PATTERNS = {tag: re.compile(r"\b(?:%s)\b" % "|".join(re.escape(k) for k in kws))
                  for tag, kws in CAUSE_KEYWORDS.items()}
# tag if CAUSE_PATTERNS[tag].search(name_lower)
```
Plus: prefer multi-word keywords ("gun safety" over "gun"); add a per-tag stop-list for known traps.

## Evidence the affinity idea holds (for the pitch)
Giving clusters along value axes (Moral Foundations Theory): care/fairness donors skew to civil_rights/environment/immigration; loyalty/authority donors skew to veterans/gun_rights. Donation platforms profile donors this way. Caveat: ~44% of giving is local/personal, so keep affinity a *score booster, not a hard filter*.
Sources: Nilsson et al. (Eur. J. Personality 2020), Thottam & Kalamas (J. Consumer Behaviour 2024).

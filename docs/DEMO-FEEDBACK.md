# DEMO-FEEDBACK — issues found while demoing (2026-05-23) + plans

Three issues surfaced demoing the platform. Diagnosis + plan + owner for each.

---

## 1. Semantics — "dog shelter in LA" returned social_welfare/energy, not animals

### How the semantic system works today
- **Primary: Gemini parse** (`server/nl_parse.py`) maps the free-text ask → 1–3 of **20 fixed cause tags** + geo + min_amount. Verified working now (`gemini-flash-latest`): "dog shelter in Los Angeles" → `environment`, CA, via gemini. So the *parse* understands the sentence.
- **Fallback:** deterministic keyword/synonym match (`agent/cause_synonyms.py`) when Gemini is down.
- **Expansion:** `expand_causes()` adds adjacent causes (environment → +energy, +agriculture, +infrastructure).

### The real bottleneck (not the parse — the taxonomy + tagging)
1. **No "animal welfare" cause exists.** "dog shelter / animal rescue" has no home, so Gemini picks the nearest (`environment` = climate/conservation), which returns climate donors, not animal-shelter donors. The 20-cause vocabulary is too coarse for niche asks.
2. **Adjacency expansion injects noise.** The live `/run` expands environment → +energy, and `energy` contains mis-tagged committees (e.g. **Republican Jewish Coalition PAC** tagged `energy`). That's why you saw energy/social_welfare donors. (The cached `?demo=1` snapshot already fixed this by querying the **primary cause only**.)
3. **Tagging coverage:** even with the right tag, a cause only returns good donors if the relevant committees are tagged into it.

### Plan
- **Now (demo):** make the live `/run` query the **primary cause only** (like the snapshot) — kills the energy noise. [server/main.py — coord instance]
- **High-value:** add an **`animal_welfare`** cause tag and tag its committees (Humane Society Legislative Fund, ASPCA Advocacy, Defenders of Wildlife, etc.); consider also `disaster_relief`, `arts`. [taxonomy — Trevor, `agent/cause_tag.py`]
- **Honesty UX:** when no cause maps cleanly, have parse return a "no exact match — broadened to X" note the UI can show, so the user knows it approximated.
- **Framing:** the parse/AI is good; the gap is the **cause vocabulary + committee tagging**. That's the lever to pull for better matches.

---

## 2. FEC links pointed to the committee, not the person

### Diagnosis
Each prospect had two citations: **[0] the committee** (`/data/receipts/?committee_id=...`) and **[1] the person's** individual-contribution search. The committee link was first, so clicking it showed the PAC, not the donor's history you wanted to verify.

### Plan
- **Done (snapshot):** reordered so the **donor's individual-contribution search is the primary link** — clicking the top citation now verifies the person. ✅
- **Live `/run`:** apply the same reorder in `server/query_clean.py` (one-liner) so live runs match. [coord instance]
- **Verify the URL resolves:** FEC stores names as "LAST, FIRST", so `contributor_name=Bloom,+Ronald+H.` should filter to the person — confirm it actually lands on their contributions (switch endpoint/params if not).

---

## 3. Contact info — how to actually reach these donors

### Reality
**FEC data has no email or phone** — only name, city, state, zip, employer, occupation. So contact info must be *appended* from elsewhere; it can't come from the database.

### Plan (phased)
- **Phase 1 (stretch, buildable on `enrich_clean`):** extend the Nimble enrichment to also return a `contact` block — realistically a **LinkedIn profile, foundation/org site, or public org contact page**, NOT a scraped personal email (rarely public, and legally fraught). A per-prospect "Find contact" button could trigger this on demand.
- **Phase 2 (post-hackathon):** automated outreach — draft a personalized ask per donor (cause + giving history), human-approve, send.
- **⚠️ Legal gate (must read):** **11 CFR §104.15 bars using FEC data to *solicit*.** Contact + outreach is exactly the prohibited use if keyed off the FEC list. Keep contact info **independently web-sourced**, frame as research, and get counsel before any automated solicitation. See `docs/STRATEGY.md` and `docs/ROADMAP.md`.

---

## Owners summary
| Issue | Fix | Owner |
|---|---|---|
| Snapshot dedup + person-first link | ✅ done | Enes frontend |
| Live `/run`: primary-cause-only + person-first link | one-liners | coord (server) |
| `animal_welfare` (+ other) cause tag + committee tagging | taxonomy | Trevor (agent) |
| Contact enrichment (`enrich_clean` → `contact`) | stretch build | Enes frontend |
| Automated outreach | post-hackathon | — |

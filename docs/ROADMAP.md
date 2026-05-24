# ROADMAP: later, not now

Parking lot for features we want but are deferring past the hackathon MVP.

## Donor contact info (email / phone)  (requested 2026-05-23)
Fundraisers ultimately need to reach a prospect, so a contact block is high value.
- **FEC has none.** The individual-contributions file is name / city / state / zip /
  employer / occupation / amount / date, with no email and no phone. So contact info cannot
  come from the database, it must be appended.
- **Sources to add later:**
  - Nimble enrichment sometimes surfaces a public work email, org contact, or LinkedIn
    from the person's employer or foundation page.
  - A contact-append / people-data API (e.g. a B2B enrichment provider) keyed on
    name + employer + city.
- **Shape:** add `enrichment.contact = { email?, phone?, linkedin?, source_url }`, only
  populated from independently-sourced public records.
- **⚠️ Compliance gate (read before building):** 11 CFR §104.15 bars using FEC contributor
  data to solicit. Producing a contact list to ask FEC donors for money is the prohibited
  use. Keep contact info sourced independently of the FEC list and framed as research, or
  get counsel before shipping outreach. See `docs/STRATEGY.md` legal section.

## Automated outreach  (requested 2026-05-23, explicitly "later")
- Draft a personalized ask per prospect (cause and giving history turned into a tailored
  email), then send or queue via the user's email. Human-in-the-loop approve before send.
- Same §104.15 compliance gate as above applies, even more so, since this is solicitation.

## Other deferred ideas
- Continuous/scheduled FEC refresh as new filings post (cron trigger on `load_fec.py`).
- Embedding-based committee-name tagging to improve recall (see `docs/MATCHING-STRATEGY.md`).
- Export prospects (CSV) for a fundraiser's existing CRM.

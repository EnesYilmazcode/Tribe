"""
Downloads FEC bulk individual-contribution data and loads it into ClickHouse.

Usage:
    python load_fec.py                        # 2024 cycle, all states, amt >= $200
    python load_fec.py --states WA OR CA      # filter to specific states
    python load_fec.py --cycle 2022           # different cycle year

Streams the zip to disk first (avoids loading 4 GB into RAM), then parses
line-by-line and batch-inserts into ClickHouse.

FEC bulk data layout (pipe-delimited, no header):
  0  CMTE_ID   6 ENTITY_TP  7 NAME     8 CITY    9 STATE
 10  ZIP_CODE  11 EMPLOYER  12 OCCUPATION  13 TRANSACTION_DT
 14  TRANSACTION_AMT  20 SUB_ID
"""

import argparse
import os
import tempfile
import zipfile
from datetime import datetime

import certifi
import requests
import clickhouse_connect
from dotenv import load_dotenv

from cause_tag import build_cause_rows

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CLICKHOUSE_HOST     = os.environ["CLICKHOUSE_HOST"]
CLICKHOUSE_PORT     = int(os.environ.get("CLICKHOUSE_PORT", 8443))
CLICKHOUSE_USER     = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ["CLICKHOUSE_PASSWORD"]
CLICKHOUSE_DB       = os.environ.get("CLICKHOUSE_DB", "donor_agent")

FEC_BASE   = "https://www.fec.gov/files/bulk-downloads"
MIN_AMOUNT = 200
BATCH_SIZE = 25_000


def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD,
        secure=True, verify=certifi.where(),
    )


def stream_download(url: str, dest_path: str):
    """Stream URL to a file on disk, printing progress."""
    print(f"Downloading {url} → {dest_path}")
    r = requests.get(url, stream=True, timeout=300)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    written = 0
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 20):  # 1 MB chunks
            f.write(chunk)
            written += len(chunk)
            if total:
                pct = written * 100 // total
                print(f"\r  {pct}%  ({written // 1_000_000} MB / {total // 1_000_000} MB)", end="", flush=True)
    print(f"\n  Done ({written // 1_000_000} MB)")


def load_committees(client, cycle: int, tmp_dir: str):
    zip_path = os.path.join(tmp_dir, f"cm{str(cycle)[-2:]}.zip")
    url = f"{FEC_BASE}/{cycle}/cm{str(cycle)[-2:]}.zip"
    stream_download(url, zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".txt"))
        text = zf.read(name).decode("latin-1")

    committee_rows, cause_input = [], []
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) < 15:
            continue
        cmte_id = parts[0].strip()
        cmte_nm = parts[1].strip()
        committee_rows.append((cmte_id, cmte_nm, parts[8].strip(), parts[6].strip(), parts[14].strip()))
        cause_input.append({"cmte_id": cmte_id, "cmte_nm": cmte_nm})

    client.insert(f"{CLICKHOUSE_DB}.committees", committee_rows,
                  column_names=["cmte_id", "cmte_nm", "cmte_tp", "cmte_st", "cand_id"])
    print(f"Loaded {len(committee_rows):,} committees.")

    cause_rows = build_cause_rows(cause_input)
    if cause_rows:
        client.insert(f"{CLICKHOUSE_DB}.committee_causes", cause_rows,
                      column_names=["cmte_id", "cause_tag"])
    print(f"Tagged {len(cause_rows):,} (committee, cause) pairs.")
    os.remove(zip_path)


def parse_date(s: str):
    try:
        return datetime.strptime(s.strip(), "%m%d%Y").date()
    except ValueError:
        return None


def load_contributions(client, cycle: int, states: set[str], tmp_dir: str):
    zip_path = os.path.join(tmp_dir, f"indiv{str(cycle)[-2:]}.zip")
    url = f"{FEC_BASE}/{cycle}/indiv{str(cycle)[-2:]}.zip"
    stream_download(url, zip_path)

    print("Parsing and inserting contributions...")
    batch, total_loaded, skipped = [], 0, 0

    with zipfile.ZipFile(zip_path) as zf:
        txt_name = next(n for n in zf.namelist() if n.endswith(".txt"))
        with zf.open(txt_name) as raw:
            for raw_line in raw:
                line = raw_line.decode("latin-1").rstrip("\n\r")
                parts = line.split("|")
                if len(parts) < 21:
                    continue
                if parts[6].strip() != "IND":
                    continue
                state = parts[9].strip()
                if states and state not in states:
                    continue
                try:
                    amt = int(parts[14].strip())
                except ValueError:
                    continue
                if amt < MIN_AMOUNT:
                    continue
                dt = parse_date(parts[13])
                if dt is None:
                    continue
                try:
                    sub_id = int(parts[20].strip())
                except ValueError:
                    skipped += 1
                    continue

                batch.append((
                    parts[0].strip(),   # cmte_id
                    parts[7].strip(),   # contributor_nm
                    parts[8].strip(),   # city
                    state,
                    parts[10].strip(),  # zip_code
                    parts[11].strip(),  # employer
                    parts[12].strip(),  # occupation
                    dt,
                    amt,
                    sub_id,
                ))

                if len(batch) >= BATCH_SIZE:
                    client.insert(
                        f"{CLICKHOUSE_DB}.contributions", batch,
                        column_names=["cmte_id", "contributor_nm", "city", "state",
                                      "zip_code", "employer", "occupation",
                                      "transaction_dt", "transaction_amt", "sub_id"],
                    )
                    total_loaded += len(batch)
                    print(f"  {total_loaded:,} rows inserted...")
                    batch = []

    if batch:
        client.insert(
            f"{CLICKHOUSE_DB}.contributions", batch,
            column_names=["cmte_id", "contributor_nm", "city", "state",
                           "zip_code", "employer", "occupation",
                           "transaction_dt", "transaction_amt", "sub_id"],
        )
        total_loaded += len(batch)

    print(f"Done. {total_loaded:,} contributions loaded ({skipped} skipped).")
    os.remove(zip_path)


def load_candidates(client, cycle: int, tmp_dir: str):
    """Load FEC candidate master (cn{YY}.zip) — links cand_id → name/party/office/state."""
    yy = str(cycle)[-2:]
    zip_path = os.path.join(tmp_dir, f"cn{yy}.zip")
    url = f"{FEC_BASE}/{cycle}/cn{yy}.zip"
    stream_download(url, zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".txt"))
        text = zf.read(name).decode("latin-1")

    rows = []
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) < 15:
            continue
        cand_id    = parts[0].strip()
        cand_name  = parts[1].strip()
        cand_party = parts[2].strip()
        cand_yr    = parts[4].strip()
        cand_office= parts[8].strip()   # P/S/H
        cand_st    = parts[9].strip()
        if not cand_id or not cand_name:
            continue
        try:
            yr = int(cand_yr)
        except ValueError:
            yr = cycle
        rows.append((cand_id, cand_name, cand_party, cand_office, cand_st, yr))

    if rows:
        client.insert(f"{CLICKHOUSE_DB}.candidates", rows,
                      column_names=["cand_id", "cand_name", "cand_party",
                                    "cand_office", "cand_st", "cand_yr"])
    print(f"Loaded {len(rows):,} candidates.")
    os.remove(zip_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle",   type=int, default=2024)
    parser.add_argument("--cycles",  type=int, nargs="*",
                        help="Load multiple cycles, e.g. --cycles 2020 2022 2024")
    parser.add_argument("--states",  nargs="*", default=[])
    parser.add_argument("--skip-schema",        action="store_true")
    parser.add_argument("--skip-committees",    action="store_true")
    parser.add_argument("--skip-contributions", action="store_true")
    parser.add_argument("--skip-candidates",    action="store_true")
    args = parser.parse_args()

    cycles = args.cycles if args.cycles else [args.cycle]
    states = set(s.upper() for s in args.states)
    client = get_client()

    for cycle in cycles:
        print(f"\n{'='*50}\nLoading FEC cycle {cycle}\n{'='*50}")
        with tempfile.TemporaryDirectory() as tmp_dir:
            if not args.skip_committees:
                load_committees(client, cycle, tmp_dir)
            if not args.skip_contributions:
                load_contributions(client, cycle, states, tmp_dir)
            if not args.skip_candidates:
                load_candidates(client, cycle, tmp_dir)


if __name__ == "__main__":
    main()

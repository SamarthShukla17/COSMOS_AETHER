# main.py — AETHER-0 Batch Engine (Hardened)

from AETHER_ORCHESTRATOR.core.pipeline import fetch_star_data
from AETHER_ORCHESTRATOR.core.scout import AetherScout
import hashlib
import os
import pandas as pd
import time
import logging

# -------------------- CONFIG --------------------

BATCH_SLEEP = 1.2              # API rate protection
LOG_FILE = "aether.log"
OUTPUT_FILE = "AETHER_findings_v0.csv"
SECRET_SALT = os.environ.get("AETHER_SALT", "dev_salt")

targets = [
    "TIC 27491137",
    "TIC 38243120",
    "TIC 231666612"
    # scale to thousands
]

# -------------------- SETUP --------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def hash_target(target_id: str) -> str:
    return hashlib.sha256((target_id + SECRET_SALT).encode()).hexdigest()

scout = AetherScout()

# -------------------- INGEST PHASE --------------------

for target in targets:
    try:
        lc = fetch_star_data(target)
        scout.ingest(hash_target(target), lc)
        logging.info(f"Ingested {target}")
        time.sleep(BATCH_SLEEP)

    except Exception as e:
        logging.warning(f"Failed {target}: {str(e)}")
        continue

# -------------------- DISCOVERY PHASE --------------------

results = scout.finalize()

# -------------------- OUTPUT --------------------

if results:
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[AETHER] {len(df)} anomalous targets detected.")
else:
    print("[AETHER] No high-confidence anomalies detected.")

print(f"Report Generated: {OUTPUT_FILE}")

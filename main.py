# main.py - The AETHER Batch Engine
from AETHER_ORCHESTRATOR.core.pipeline import fetch_star_data
from AETHER_ORCHESTRATOR.core.scout import AetherScout
import pandas as pd

targets = ["TIC 27491137", "TIC 38243120", "TIC 231666612"] # Add 1000s of IDs here
scout = AetherScout()
findings = []

for target in targets:
    try:
        data = fetch_star_data(target)
        anomalies = scout.scan_for_unknowns(data)
        if len(anomalies) > 0:
            findings.append({"target": target, "count": len(anomalies)})
    except:
        continue

# Save the 'High Value' targets to a CSV for Layer 2
pd.DataFrame(findings).to_csv("AETHER_findings_v0.csv")
print("Report Generated: AETHER_findings_v0.csv")
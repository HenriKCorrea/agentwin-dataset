import requests
import json
from datetime import date

DATASET_ID = "fc53-9hrv"
DOMAIN = "data.cityofnewyork.us"
# AGENCIES = "('NYPD','FDNY','DSNY','DOE','NYCEM')"

url = f"https://{DOMAIN}/resource/{DATASET_ID}.json"
params = {
    # "$where": f"agency in{AGENCIES}",
    # "$limit": 10000,  # dataset is ~605 rows for these agencies
    "$order": "agency,station_name"
}

resp = requests.get(url, params=params, timeout=30)
resp.raise_for_status()
data = resp.json()

snapshot_path = f"datasets/raw/dcas_ev_stations_{date.today()}.json"
with open(snapshot_path, "w") as f:
    json.dump(
        {
            "fetched_date": str(date.today()),
            "source_url": url,
            "source_params": params,
            "row_count": len(data),
            "data": data,
        },
        f,
        indent=2,
    )

print(f"Fetched {len(data)} rows → {snapshot_path}")

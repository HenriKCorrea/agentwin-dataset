import os
import json
import requests
import osmnx as ox
import geopandas as gpd
from datetime import date

data = [
    {
        "url": "https://data.cityofnewyork.us/resource/gthc-hcne",
        "format": ["geojson", "csv"],
        "params": None,
        "file": "data/raw/nyc_boroughs",
    },
    {
        "url": "https://data.cityofnewyork.us/resource/fc53-9hrv",
        "format": ["geojson", "csv"],
        "params": {
            "$limit": 10000,
        },
        "file": "data/raw/dcas_ev_stations",
    },
]

for dataset in data:
    url = dataset["url"]
    file = dataset["file"]
    formats = dataset["format"]
    params = dataset["params"]

    for fmt in formats:
        path = f"{file}.{fmt}"
        meta_path = f"{path}.meta.json"
        print(f"Fetching dataset → {path}")
        resp = requests.get(f"{url}.{fmt}", params=params, timeout=30)
        resp.raise_for_status()
        row_count = len(resp.json()["features"]) if fmt == "geojson" else len(resp.text.splitlines()) - 1
        with open(path, "wb") as f:
            f.write(resp.content)
        with open(meta_path, "w") as f:
            json.dump(
                {
                    "fetched_date": str(date.today()),
                    "source_url": url,
                    "source_params": params,
                    "row_count": row_count,
                },
                f,
                indent=2,
            )

# Fetch NYC power substations from OpenStreetMap inside borough boundaries
boroughs = gpd.read_file("data/raw/nyc_boroughs.geojson")
nyc_polygon = boroughs.union_all()

ox.settings.max_query_area_size = 5e9
params = {
    "tags": {"power": "substation"},
}
gdf = ox.features_from_polygon(nyc_polygon, tags=params["tags"])

formats = ["geojson", "csv"]
for fmt in formats:
    snapshot_path = f"data/raw/osm_substations_nyc.{fmt}"
    if fmt == "geojson":
        gdf.to_file(snapshot_path, driver="GeoJSON")
    elif fmt == "csv":
        gdf.to_csv(snapshot_path, index=False)
    with open(f"{snapshot_path}.meta.json", "w") as f:
        json.dump(
            {
                "fetched_date": str(date.today()),
                "source_url": "https://www.openstreetmap.org",
                "source_params": params,
                "row_count": len(gdf),
            },
            f,
            indent=2,
        )
    print(f"Fetched {len(gdf)} substation features → {snapshot_path}")

import json
import requests
import osmnx as ox
import geopandas as gpd
from datetime import date
from pathlib import Path

# Fetch datasets from NYC Open Data
datasets = [
    {
        "url": "https://data.cityofnewyork.us/resource/gthc-hcne",
        "format": ["geojson", "csv"],
        "params": None,
        "file": "data/raw/nyc_boroughs",
        "attachments": [
            {
                "url": "https://data.cityofnewyork.us/api/views/gthc-hcne/files/4ef9855a-f485-4c02-b246-530b6b736059?download=true&filename=data_dictionary.xlsx",
                "file": "data/attachments/nyc_boroughs_data_dictionary.xlsx",
            },
            {
                "url": "https://data.cityofnewyork.us/api/views/gthc-hcne/files/f0af73fe-df03-43fe-91b3-0c0553c83008?download=true&filename=nybb_metadata.pdf",
                "file": "data/attachments/nyc_boroughs_metadata.pdf",
            }
        ]
    },
    {
        "url": "https://data.cityofnewyork.us/resource/fc53-9hrv",
        "format": ["csv"],
        "params": {
            "$limit": 10000,
        },
        "file": "data/raw/dcas_ev_stations",
        "attachments": [
            {
                "url": "https://data.cityofnewyork.us/api/views/fc53-9hrv/files/635c379a-691f-4986-8f5c-300b15cec89d?download=true&filename=NYC%20EV%20Fleet%20Station%20Network_Data%20Dictionary.xlsx",
                "file": "data/attachments/NYC_EV_Fleet_Station_Network_Data_Dictionary.xlsx",
            }
        ]
    },
]

for dataset in datasets:
    url = dataset["url"]
    file = dataset["file"]
    formats = dataset["format"]
    params = dataset["params"]

    for fmt in formats:
        Path(file).parent.mkdir(parents=True, exist_ok=True)
        path = f"{file}.{fmt}"
        meta_path = f"{path}.meta.json"

        print(f"Fetching dataset → {path}")
        resp = requests.get(f"{url}.{fmt}", params=params, timeout=30)
        resp.raise_for_status()
        row_count = (
            len(resp.json()["features"])
            if fmt == "geojson"
            else len(resp.text.splitlines()) - 1
        )
        with open(path, "wb") as f:
            f.write(resp.content)
        with open(meta_path, "w") as f:
            json.dump(
                {
                    "fetched_date": str(date.today()),
                    "source_url": url,
                    "source_params": params,
                    "row_count": row_count,
                    "attachments": dataset.get("attachments", []),
                },
                f,
                indent=2,
            )

    # Save attachments if any
    for attachment in dataset.get("attachments", []):
        attachment_url = attachment["url"]
        attachment_file = attachment["file"]
        Path(attachment_file).parent.mkdir(parents=True, exist_ok=True)
        print(f"Fetching attachment → {attachment_file}")
        resp = requests.get(attachment_url, timeout=30)
        resp.raise_for_status()
        with open(attachment_file, "wb") as f:
            f.write(resp.content)

# Fetch NYC power substations from OpenStreetMap inside borough boundaries
boroughs = gpd.read_file("data/raw/nyc_boroughs.geojson")
nyc_polygon = boroughs.union_all()

ox.settings.max_query_area_size = 5e9
ox.settings.cache_folder = "/tmp/osm_cache"

params = {
    "tags": {"power": "substation"},
}
gdf = ox.features_from_polygon(nyc_polygon, tags=params["tags"])

formats = ["geojson", "csv"]
for fmt in formats:
    snapshot_path = f"data/raw/osm_substations.{fmt}"
    Path(snapshot_path).parent.mkdir(parents=True, exist_ok=True)

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

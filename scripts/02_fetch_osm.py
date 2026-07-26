import osmnx as ox
from datetime import date

# NYC bounding box: south, west, north, east
NYC_BBOX = (40.4774, -74.2591, 40.9176, -73.7004)

# Query all substations in NYC; filter to ConEdison by operator tag
tags = {"power": "substation"}
gdf = ox.features_from_bbox(bbox=NYC_BBOX, tags=tags)

# Inspect operator tags to understand coverage
print(gdf["operator"].value_counts().head(20))

snapshot_path = f"datasets/raw/osm_substations_nyc_{date.today()}.geojson"
gdf.to_file(snapshot_path, driver="GeoJSON")
print(f"Fetched {len(gdf)} substation features → {snapshot_path}")

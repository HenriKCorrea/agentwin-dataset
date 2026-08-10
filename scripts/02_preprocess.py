import pandas as pd
import geopandas as gpd

# === dcas_ev_stations preprocessing ===

df = pd.read_csv("data/raw/dcas_ev_stations.csv")

# --- Data quality (before GeoDataFrame) ---

# 1. Drop rows without coordinates
df = df.dropna(subset=["latitude", "longitude"])

# 2. Fix dtypes
df["no_of_ports"] = df["no_of_ports"].astype(int)
df["postcode"] = df["postcode"].astype(int).astype(str).str.zfill(5)

# 3. Fill semantically empty fields (blank = "No" per data dictionary)
df["public_charger_"] = df["public_charger_"].fillna("No")
df["fee_for_city_drivers"] = df["fee_for_city_drivers"].fillna("No")

# --- Spatial ---

ev_stations = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326",
)

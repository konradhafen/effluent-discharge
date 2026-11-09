import gis
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

dirpath_effluent = Path(r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data")
fn_nhd_gpkg = r"C:\Users\vcq32\OneDrive - Texas State University\Data\NHD\NHD\NHDPlusTX\nhdplusv2_12.gpkg"
fn_sites = dirpath_effluent / "npdes_site_details_12_all.csv"
fn_effluent = dirpath_effluent / "npdes_discharge_by_site_12_all.csv"

gdf_sites_points = gis.csv_to_gpd(fn_sites, 'CWA_LAT', 'CWA_LON', "EPSG:4269")
gdf_sites_points.to_file(dirpath_effluent / "npdes_sites_4269.gpkg")
gdf_catchments_polygons = gpd.read_file(fn_nhd_gpkg, layer="Catchment")
df_flow = gpd.read_file(fn_nhd_gpkg, layer="Flow")
df_flow = df_flow[['FROMCOMID', 'TOCOMID']]
df_effluent = pd.read_csv(fn_effluent)

points_joined = gis.join_points_to_catchments(gdf_sites_points, gdf_catchments_polygons)
df_npdesid_comid = pd.DataFrame(points_joined[['NPDES_ID', 'FEATUREID']])

effluent_with_comid = pd.merge(df_effluent, df_npdesid_comid, left_on='NPDES_ID', right_on='NPDES_ID', how='left')

# for each date, sum effluent for each comid, join to network definition (df_flow) and accumulate
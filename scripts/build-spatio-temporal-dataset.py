import gis
import pandas as pd
import geopandas as gpd
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
effluent_to_from = pd.merge(effluent_with_comid, df_flow, left_on='FEATUREID', right_on='FROMCOMID', how='outer')

print(df_npdesid_comid.shape, gdf_sites_points.shape)
print(effluent_with_comid.shape, df_effluent.shape)
print(effluent_to_from.shape)
print(df_effluent.head())
print(effluent_to_from.head())
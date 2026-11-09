import gis
import geopandas as gpd

from pathlib import Path

dirpath_effluent = Path(r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data")
fn_nhd_gpkg = r"C:\Users\vcq32\OneDrive - Texas State University\Data\NHD\NHD\NHDPlusTX\nhdplusv2_12.gpkg"
fn_sites = dirpath_effluent / "npdes_site_details_12_all.csv"
fn_effluent = dirpath_effluent / "npdes_discharge_by_site_12_all.csv"

gdf_sites_points = gis.csv_to_gpd(fn_sites, 'LAT', 'LON')
gdf_catchments_polygons = gpd.read_file(fn_nhd_gpkg, layer="Catchment")

points_joined = gis.join_points_to_catchments(gdf_sites_points, gdf_catchments_polygons)
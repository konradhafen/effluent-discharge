import pandas as pd
import geopandas as gpd

from pathlib import Path


def join_points_to_catchments(points, polygons, fn_out=''):
    if points.crs != polygons.crs:
        points = points.to_crs(polygons.crs)

    joined = gpd.sjoin(
        points,
        polygons[['FEATUREID', 'geometry']],
        how='left',
        predicate='within'
    )

    if fn_out:
        joined.to_file(fn_out)
    
    return joined

def csv_to_gpd(fn, lat_n_col, lon_e_col, crs):
    df = pd.read_csv(fn)
    gdf = gpd.GeoDataFrame(df,
                           geometry=gpd.points_from_xy(df[lon_e_col], df[lat_n_col]),
                           crs=crs)
    return gdf

def nhdplusv2_to_gpkg(dirpath, fn_gpkg, dag=True):
    dirpath = Path(dirpath)
    fn_catchments = dirpath / "NHDPlusCatchment/Catchment.shp"
    fn_flowline = dirpath / "NHDSnapshot/Hydrography/NHDFlowline.shp"
    fn_vaa = dirpath / "NHDPlusAttributes/PlusFlowlineVAA.dbf"
    fn_flow = dirpath / "NHDPlusAttributes/PlusFlow.dbf"

    catchments = gpd.read_file(fn_catchments)
    flowline = gpd.read_file(fn_flowline)
    vaa = gpd.read_file(fn_vaa, ignore_geometry=True)
    flow = gpd.read_file(fn_flow, ignore_geometry=True)

    if dag:
        flowline_vaa = flowline.merge(vaa, left_on='COMID', right_on='ComID', how='left')
        flowline_vaa = flowline_vaa.loc[
            (flowline_vaa['Divergence'] != 2) & 
            (flowline_vaa['StreamCalc'] > 0) &
            (flowline_vaa['FLOWDIR'] == 'With Digitized') &
            (flowline_vaa['FTYPE'] != 'Coastline')]
        comids = flowline_vaa['COMID'].values
    else:
        comids = flowline['COMID'].values

    catchments.loc[catchments['FEATUREID'].isin(comids)].to_file(fn_gpkg, layer='Catchment')
    flowline.loc[flowline['COMID'].isin(comids)].to_file(fn_gpkg, layer="Flowline")
    gpd.GeoDataFrame(vaa.loc[vaa['ComID'].isin(comids)].assign(geometry=None), geometry='geometry').to_file(fn_gpkg, layer="VAA")
    gpd.GeoDataFrame(flow.loc[flow['FROMCOMID'].isin(comids)].assign(geometry=None), geometry='geometry').to_file(fn_gpkg, layer="Flow")

    return
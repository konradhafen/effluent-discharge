from itertools import cycle

import gis
import pandas as pd
import geopandas as gpd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path

dirpath_effluent = Path(r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data")
fn_nhd_gpkg = r"C:\Users\vcq32\OneDrive - Texas State University\Data\NHD\NHD\NHDPlusTX\nhdplusv2_12.gpkg"
fn_sites = dirpath_effluent / "npdes_site_details_12_all.csv"
fn_effluent = dirpath_effluent / "npdes_discharge_by_site_12_all.csv"
fn_out_count = dirpath_effluent / "facility_count_comid.csv"
fn_out_sum = dirpath_effluent / "effluent_by_comid.csv"
fn_out_accum = dirpath_effluent / "effluent_accumulated.csv"
fn_out_accum_mean = dirpath_effluent / "effluent_accumulated_mean.csv"

gdf_sites_points = gis.csv_to_gpd(fn_sites, 'CWA_LAT', 'CWA_LON', "EPSG:4269")
gdf_sites_points.to_file(dirpath_effluent / "npdes_sites_4269.gpkg")
gdf_catchments_polygons = gpd.read_file(fn_nhd_gpkg, layer="Catchment")
df_flow = gpd.read_file(fn_nhd_gpkg, layer="Flow")
df_flow = df_flow.dropna(subset=['FROMCOMID', 'TOCOMID'])
df_effluent = pd.read_csv(fn_effluent)
df_flow_fix = df_flow[df_flow['FROMCOMID'] != df_flow['TOCOMID']].copy()

points_joined = gis.join_points_to_catchments(gdf_sites_points, gdf_catchments_polygons)
df_npdesid_comid = pd.DataFrame(points_joined[['NPDES_ID', 'FEATUREID']])

effluent_with_comid = pd.merge(df_effluent, df_npdesid_comid, left_on='NPDES_ID', right_on='NPDES_ID', how='left')

stat = 'AVG'
effluent_with_comid['END_DATE'] = pd.to_datetime(effluent_with_comid['END_DATE'], format="%d-%b-%y")
min_date = effluent_with_comid['END_DATE'].min()
max_date = effluent_with_comid['END_DATE'].max()

effluent_to_process = effluent_with_comid[effluent_with_comid['STAT_DESC'] == stat]
effluent_to_process = effluent_to_process.groupby(['FEATUREID', 'END_DATE'])['VALUE'].sum().reset_index()
effluent_for_network = effluent_to_process.pivot(index='FEATUREID', columns='END_DATE', values='VALUE').reset_index().rename_axis(None, axis=1).fillna(0.0)
effluent_for_network.to_csv(fn_out_sum, index=False)

# facility count by comid
effluent_to_process = effluent_with_comid[effluent_with_comid['STAT_DESC'] == stat]
facility_count = effluent_to_process.groupby(['FEATUREID', 'END_DATE'])['VALUE'].count().reset_index()
facility_count_for_network = facility_count.pivot(index='FEATUREID', columns='END_DATE', values='VALUE').reset_index().rename_axis(None, axis=1).fillna(0.0)
facility_count_for_network.to_csv(fn_out_count, index=False)

effluent_for_network = effluent_for_network.set_index('FEATUREID')
effluent_for_network = effluent_for_network.fillna(0.0)
columns = effluent_for_network.columns


G = nx.DiGraph()
G.add_nodes_from(df_flow_fix['FROMCOMID'])
G.add_edges_from(zip(df_flow_fix['FROMCOMID'], df_flow_fix['TOCOMID']))

while not nx.is_directed_acyclic_graph(G):
    cyc = nx.find_cycle(G, orientation='original')
    edge_to_remove = cyc[-1][:2]
    G.remove_edge(*edge_to_remove)

ordered_nodes = list(nx.topological_sort(G))
# ordered_nodes_mean = list(nx.topological_sort(G))  # Second set of nodes for accumulating mean values. Should find a cleaner way to do this.

aligned_df = effluent_for_network.reindex(ordered_nodes, fill_value=0.0).fillna(0.0)
ordered_matrix=aligned_df.to_numpy(copy=True)
ordered_matrix = ordered_matrix * 1.54722865  # convert from MGD to CFS
ordered_matrix_mean = np.mean(ordered_matrix, axis=1, keepdims=True)

node_to_idx = {node: idx for idx, node in enumerate(ordered_nodes)}

for idx, node in enumerate(ordered_nodes):
    for downstream_node in G.successors(node):
        downstream_idx = node_to_idx[downstream_node]
        ordered_matrix[downstream_idx] += ordered_matrix[idx]

accumulated_df = pd.DataFrame(
    ordered_matrix,
    index=ordered_nodes,
    columns=columns
).loc[df_flow_fix['FROMCOMID']]


accumulated_df.to_csv(fn_out_accum, index_label='COMID')

for idx, node in enumerate(ordered_nodes):
    for downstream_node in G.successors(node):
        downstream_idx = node_to_idx[downstream_node]
        ordered_matrix_mean[downstream_idx] += ordered_matrix_mean[idx]

accumulated_df_mean = pd.DataFrame(
    ordered_matrix_mean,
    index=ordered_nodes,
    columns=['mean_cfs']
).loc[df_flow_fix['FROMCOMID']]

accumulated_df_mean.to_csv(fn_out_accum_mean, index_label='COMID')

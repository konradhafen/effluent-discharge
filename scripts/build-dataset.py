import pandas as pd
import numpy as np
from pynhd import WaterData

import utils



def get_huc8_list(huc02):
    huc08 = WaterData("huc08")
    gdf_huc08 = huc08.byfilter(f"huc8 LIKE '{huc02:02d})%'")
    huc08_list = gdf_huc08["huc8"].to_list()
    return huc08_list

def build_from_hucs(hucs, start_date, end_date, fn_facilities, fn_values):
    df_fac = None
    df_val = None

    for huc in hucs:
        df_fac_temp = utils.build_facilities_table_parallel(huc=huc, major='N', max_workers=20)
        df_val_temp = utils.build_effluent_table_parallel(df_fac_temp, start_date, end_date)

        if type(df_fac) is None:
            df_fac = df_fac_temp
        else:
            df_fac = pd.concat(df_fac, df_fac_temp)

        if type(df_val) is None:
            df_val = df_val_temp
        else:
            df_val = pd.concat(df_val, df_val_temp)

    df_fac.to_csv(fn_facilities, index=False)
    df_val.to_csv(fn_values, index=False)


start_date = '01/01/2023'
end_date =  '12/31/2026'

fn_facilities = r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data\npdes_site_details_12_all.csv"
fn_values = r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data\npdes_discharge_by_site_12_all.csv"

hucs = get_huc8_list(12)
build_from_hucs(hucs, start_date, end_date, fn_facilities, fn_values)


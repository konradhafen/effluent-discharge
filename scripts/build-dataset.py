import pandas as pd
import numpy as np
from pynhd import WaterData

import utils



def get_huc8_list(huc2):
    huc08 = WaterData("huc08")
    return huc08_list

def build_by_huc4():
    huc4s = np.arange(1201, 1212)
    df_fac = None
    for huc4 in huc4s:
        df = utils.build_facilities_table_parallel(huc=huc4, major='N', max_workers=20)

        if type(df_fac) is None:
            df_fac = df
        else:
            df_fac = pd.concat([df_fac, df])

    return df_fac


start_date = '01/01/2023'
end_date =  '12/31/2026'

fn_facilities = r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data\npdes_site_details_12_all.csv"
fn_values = r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data\npdes_discharge_by_site_12_all.csv"

df_facilities = build_by_huc4()
df_facilities.to_csv(fn_facilities, index=False)

df_values = utils.build_effluent_table_parallel(df_facilities, start_date, end_date, max_workers=20)
df_values.to_csv(fn_values)


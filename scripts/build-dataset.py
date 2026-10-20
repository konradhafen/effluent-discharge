import pandas as pd

import utils


huc8 = 12100203
huc6 = 121002
huc4 = 1210
huc2 = 12
start_date = '01/01/2023'
end_date =  '12/31/2026'

df = utils.build_facilities_table(huc2)
print(df.shape)

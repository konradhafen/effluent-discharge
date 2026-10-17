import requests
import json
import pandas as pd


huc = 12100203
npdes = 'TX0047945'

start_date = '01/01/2023'
end_date =  '12/31/2026'

URL_FACILITIES = "https://echodata.epa.gov/echo/cwa_rest_services.get_facility_info?p_maj=Y&p_huc={huc}"
URL_REPORT = "https://echodata.epa.gov/echo/dfr_rest_services.get_dfr?output=JSON&p_id={npdes}"
URL_EFFLUENT_CHART = "https://echodata.epa.gov/echo/eff_rest_services.get_effluent_chart?p_id={npdes}&outfall=001&parameter_code=50050&start_date={start_date}&end_date={end_date}"

columns = ['NPDES_ID', 'NAME', 'LAT', 'LON', 'LOC_ACCURACY', 'LOC_REFERENCE', 'DISCHARGE_TO_NAME', 
'HUC12', 'IMPAIRED_STATUS', 'IMPAIRED_YEAR', 'IMPAIRED_INFO_URL', 'IMPAIRED_REASON', 'IMPAIRED_DRINK', 
'IMPAIRED_ECO', 'IMPAIRED_AQU', 'IMPAIRED_FISH', 'IMPAIRED_REC', 'IMPAIRED_OTHER']


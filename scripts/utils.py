import concurrent.futures
import requests
import json
import pandas as pd
from pathlib import Path


URL_FACILITIES = "https://echodata.epa.gov/echo/cwa_rest_services.get_facility_info?p_maj={}&p_huc={}"
URL_REPORT = "https://echodata.epa.gov/echo/dfr_rest_services.get_dfr?output=JSON&p_id={}"
URL_EFFLUENT_CHART = "https://echodata.epa.gov/echo/eff_rest_services.get_effluent_chart?p_id={}&outfall=001&parameter_code=50050&start_date={}&end_date={}&output=JSON"

# COLUMNS_FACILITY = ['NPDES_ID', 'NAME', 'LAT', 'LON', 'LOC_ACCURACY', 'LOC_REFERENCE', 'DISCHARGE_TO_NAME', 
# 'HUC12', 'IMPAIRED_STATUS', 'IMPAIRED_YEAR', 'IMPAIRED_INFO_URL', 'IMPAIRED_REASON', 'IMPAIRED_DRINK', 
# 'IMPAIRED_ECO', 'IMPAIRED_AQU', 'IMPAIRED_FISH', 'IMPAIRED_REC', 'IMPAIRED_OTHER', 'TE_SPECIES']
FACILITY_DICT = {'NPDES_ID': 'SourceID',
              'NAME': 'CWPName', 
              'CWA_LAT': 'Latitude',
              'CWA_LON': 'Longitude',
              'CWA_DESC': 'RefPointDesc',
              'CWA_TYP': 'Universe',
              'CWA_CAT': 'Areas',
              'CWA_STATUS': 'FacilityStatus',
              'FRS_ID': 'SourceID',
              'FRS_LAT': 'Latitude',
              'FRS_LON': 'Longitude',
              'FRS_DATUM': 'HdatumDesc',
              'FRS_DESC': 'RefPointDesc',
              'FRS_ACC': 'AccuracyValue', 
              'LAT': 'Latitude83', # SpatialMetadata
              'LON': 'Latitude83', 
              'LOC_ACCURACY': 'CalculatedAccuracy', 
              'LOC_REFERENCE': 'ReferencePoint', 
              'DISCHARGE_TO_NAME': 'ICISWaterBodyNames',  # Watersheds -> WBD12s
              'HUC12': 'WBD12', 
              'TE_SPECIES': 'EsaAquaticSpeciesFlg',  
              'IMPAIRED_STATUS': 'WaterCondition',  # AssessedWaters -> AssessmentUnits
              'IMPAIRED_WATERBODY': 'AssessmentUnitName',
              'IMPAIRED_YEAR': 'ReportingCycle', 
              'IMPAIRED_INFO_URL': 'AUURL', 
              'IMPAIRED_REASON': 'CauseGroupsImpaired', 
              'IMPAIRED_DRINK': 'DrinkingWaterUse', 
              'IMPAIRED_ECO': 'EcologicalUse', 
              'IMPAIRED_AQULF': 'AquaticLifeUse', 
              'IMPAIRED_FISH': 'FishConsumptionUse', 
              'IMPAIRED_REC': 'RecreationUse', 
              'IMPAIRED_OTHER': 'OtherUse'}

EFFLUENT_DICT = {
    'NPDES_ID': 'SourceId',
    'OUTFALL': 'PermFeatureNmbr',
    'PARAM': 'ParameterCode',
    'UNIT_DESC': 'DMRUnitDesc',
    'STAT_DESC': 'StatisticalBaseTypeCode',
    'END_DATE': 'MonitoringPeriodEndDate',
    'VALUE': 'DMRValueStdUnits',
}

def get_url_as_json(url):
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data

def get_facilities_list(huc, major='Y'):
    return get_url_as_json(URL_FACILITIES.format(major, huc))

def get_detailed_facility_report(npdes):
    return get_url_as_json(URL_REPORT.format(npdes))

def get_effluent_chart(npdes, start_date, end_date):
    return get_url_as_json(URL_EFFLUENT_CHART.format(npdes, start_date, end_date))

def build_facility_row(facility_info, facility_report):
    row_dict = dict.fromkeys(list(FACILITY_DICT))
    row_dict['NPDES_ID'] = facility_info['SourceID']
    row_dict['NAME'] = facility_info['CWPName']

    results = facility_report.get('Results', {})

    if 'Permits' in results and len(results['Permits']) > 0:
        permits = results.get('Permits', [])
        cwa = True
        frs = True
        for permit in permits:
            if permit['Statute'] == "CWA" and permit['EPASystem'] == "ICIS-NPDES" and cwa:
                row_dict['CWA_LAT'] = permit[FACILITY_DICT['CWA_LAT']]
                row_dict['CWA_LON'] = permit[FACILITY_DICT['CWA_LON']]
                row_dict['CWA_DESC'] = permit[FACILITY_DICT['CWA_DESC']]
                row_dict['CWA_TYP'] = permit[FACILITY_DICT['CWA_TYP']]
                row_dict['CWA_CAT'] = permit[FACILITY_DICT['CWA_CAT']]
                row_dict['CWA_STATUS'] = permit[FACILITY_DICT['CWA_STATUS']]
                cwa = False

            elif permit['EPASystem'] == "FRS" and frs:
                row_dict['FRS_ID'] = permit[FACILITY_DICT['FRS_ID']]
                row_dict['FRS_LAT'] = permit[FACILITY_DICT['FRS_LAT']]
                row_dict['FRS_LON'] = permit[FACILITY_DICT['FRS_LON']]
                row_dict['FRS_DATUM'] = permit[FACILITY_DICT['FRS_DATUM']]
                row_dict['FRS_DESC'] = permit[FACILITY_DICT['FRS_DESC']]
                row_dict['FRS_ACC'] = permit[FACILITY_DICT['FRS_ACC']]
                frs = False
    
    if 'SpatialMetadata' in results:
        row_dict['LAT'] = results['SpatialMetadata'][FACILITY_DICT['LAT']]
        row_dict['LON'] = results['SpatialMetadata'][FACILITY_DICT['LON']]
        row_dict['LOC_ACCURACY'] = results['SpatialMetadata'][FACILITY_DICT['LOC_ACCURACY']]
        row_dict['LOC_REFERENCE'] = results['SpatialMetadata'][FACILITY_DICT['LOC_REFERENCE']]

    if 'Watersheds' in results and 'WBD12s' in results['Watersheds']:
        wbd12 = results['Watersheds']['WBD12s'][0]
        row_dict['DISCHARGE_TO_NAME'] = wbd12[FACILITY_DICT['DISCHARGE_TO_NAME']]
        row_dict['HUC12'] = wbd12[FACILITY_DICT['HUC12']]
        row_dict['TE_SPECIES'] = wbd12[FACILITY_DICT['TE_SPECIES']]

    if 'AssessedWaters' in results and 'AssessmentUnits' in results['AssessedWaters']:
        unit = results['AssessedWaters']['AssessmentUnits'][0]
        row_dict['IMPAIRED_STATUS'] = unit[FACILITY_DICT['IMPAIRED_STATUS']]
        row_dict['IMPAIRED_WATERBODY'] = unit[FACILITY_DICT['IMPAIRED_WATERBODY']]
        row_dict['IMPAIRED_YEAR'] = unit[FACILITY_DICT['IMPAIRED_YEAR']]
        row_dict['IMPAIRED_INFO_URL'] = unit[FACILITY_DICT['IMPAIRED_INFO_URL']]
        row_dict['IMPAIRED_REASON'] = unit[FACILITY_DICT['IMPAIRED_REASON']]
        row_dict['IMPAIRED_DRINK'] = unit[FACILITY_DICT['IMPAIRED_DRINK']]
        row_dict['IMPAIRED_ECO'] = unit[FACILITY_DICT['IMPAIRED_ECO']]
        row_dict['IMPAIRED_AQULF'] = unit[FACILITY_DICT['IMPAIRED_AQULF']]
        row_dict['IMPAIRED_FISH'] = unit[FACILITY_DICT['IMPAIRED_FISH']]
        row_dict['IMPAIRED_REC'] = unit[FACILITY_DICT['IMPAIRED_REC']]
        row_dict['IMPAIRED_OTHER'] = unit[FACILITY_DICT['IMPAIRED_OTHER']]
    
    return row_dict

def process_single_facility(facility_info):
    try:
        npdes_id = facility_info['SourceID']
        facility_report = get_detailed_facility_report(npdes_id)
        return build_facility_row(facility_info, facility_report)
    except Exception as e:
        print(f"Error processing NPDES {facility_info.get('SourceID')}: {e}")
        return None

def build_facilities_table_parallel(huc, major='Y', max_workers=10):
    facility_list = get_facilities_list(huc, major)
    facilities = facility_list.get('Results', {}).get('Facilities', [])

    if not facilities:
        print("No facilities found.")
        return pd.DataFrame(columns=list(FACILITY_DICT))

    all_rows = []
    print(f"Starting parallel fetch for {len(facilities)} facilities using {max_workers} threads . . .")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_facility = {
            executor.submit(process_single_facility, f_info): f_info for f_info in facilities
        }

        for i, future in enumerate(concurrent.futures.as_completed(future_to_facility), 1):
            f_info = future_to_facility[future]
            print(f"{i} of {len(facilities)} completed (NPDES: {f_info['SourceID']})")
            try:
                row_dict = future.result()
                if row_dict:
                    all_rows.append(row_dict)
            except Exception as e:
                print(f"Thread generated and exception fo NPDES {f_info['SourceID']}")

    df = pd.DataFrame(all_rows, columns=list(FACILITY_DICT))
    return df

def build_facilities_table(huc, major='Y'):
    df = pd.DataFrame(columns=list(FACILITY_DICT))
    facility_list = get_facilities_list(huc, major)

    for facility_info in facility_list['Results']['Facilities']:
        facility_report = get_detailed_facility_report(facility_info['SourceID'])
        print('NPDES', facility_info['SourceID'])
        facility_row = build_facility_row(facility_info, facility_report)
        df.loc[len(df)] = facility_row

    return df

def build_effluent_row(effluent_value, id, outfall, param):
    row_dict = dict.fromkeys(list(EFFLUENT_DICT))
    row_dict['NPDES_ID'] = id
    row_dict['OUTFALL'] = outfall
    row_dict['PARAM'] = param
    row_dict['UNIT_DESC'] = effluent_value[EFFLUENT_DICT['UNIT_DESC']]
    row_dict['STAT_DESC'] = effluent_value[EFFLUENT_DICT['STAT_DESC']]
    row_dict['END_DATE'] = effluent_value[EFFLUENT_DICT['END_DATE']]
    row_dict['VALUE'] = effluent_value[EFFLUENT_DICT['VALUE']]

    return row_dict

def process_single_effluent_id(id, start_date, end_date):
    rows = []
    try:
        effluent_chart = get_effluent_chart(id, start_date, end_date)

        if not effluent_chart or 'Results' not in effluent_chart:
            print('Effluent chart does not exist or does not contain data')
            return rows

        npdes_id = effluent_chart['Results'][EFFLUENT_DICT['NPDES_ID']]
        perm_features = effluent_chart['Results'].get('PermFeatures', [])

        if len(perm_features) > 0:
            feature = perm_features[0]
            outfall = feature[EFFLUENT_DICT['OUTFALL']]

            parameters = feature.get('Parameters', [])

            if len(parameters) > 0:
                first_param = parameters[0]
                param = first_param[EFFLUENT_DICT['PARAM']]
                effluent_values = first_param.get('DischargeMonitoringReports', [])  #### May need to check this

                for effluent_value in effluent_values:
                    effluent_row = build_effluent_row(effluent_value, npdes_id, outfall, param)
                    rows.append(effluent_row)
    except Exception as e:
        print(f"Error processing NPDES {id}: {e}")

    return rows

def build_effluent_table_parallel(df_in, start_date, end_date, npdes_col='NPDES_ID', max_workers=10):
    if isinstance(df_in, pd.DataFrame):
        df_sites = df_in
    elif Path(df_in).is_file():
        df_sites = pd.read_csv(df_in)
    else:
        raise ValueError('Input data frame or file path is not valid')

    ids = df_sites[npdes_col].dropna().unique()
    all_rows = []

    print(f"Starting parallel fetch for {len(ids)} unique IDs using {max_workers} threads...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {
            executor.submit(process_single_effluent_id, id, start_date, end_date): id for id in ids
        }

        for i, future in enumerate(concurrent.futures.as_completed(future_to_id), 1):
            id = future_to_id[future]
            # print(f"{i} of {len(ids)} API calls completed (NPDES: {id})")
            try:
                result_rows = future.result()
                all_rows.extend(result_rows)
                print(f"{i} of {len(ids)} API calls completed (NPDES: {id}) facility rows {len(result_rows)} total rows {len(all_rows)}")
            except Exception as e:
                print(f"Thread failed for NPDES {id}: {e}")

    df = pd.DataFrame(all_rows, columns=list(EFFLUENT_DICT))
    return df

def build_effluent_table(df_in, start_date, end_date, npdes_col='NPDES_ID'):
    if isinstance(df_in, pd.DataFrame):
        df_sites = df_in
    elif Path(df_in).is_file():
        df_sites = pd.read_csv(df_in)
    else:
        print('input dataframe is not valid')
    
    df = pd.DataFrame(columns=list(EFFLUENT_DICT))
    ids = df_sites[npdes_col].values
    i = 0
    for id in ids:
        i += 1
        print(i, 'of', len(ids), 'NPDES', id)
        effluent_chart = get_effluent_chart(id, start_date, end_date)
        npdes_id = effluent_chart['Results'][EFFLUENT_DICT['NPDES_ID']]
        if len(effluent_chart['Results']['PermFeatures']) > 0:
            outfall = effluent_chart['Results']['PermFeatures'][0][EFFLUENT_DICT['OUTFALL']]
            param = effluent_chart['Results']['PermFeatures'][0]['Parameters'][0][EFFLUENT_DICT['PARAM']]
            effluent_values = effluent_chart['Results']['PermFeatures'][0]['Parameters'][0]['DischargeMonitoringReports']
            for effluent_value in effluent_values:
                effluent_row = build_effluent_row(effluent_value, npdes_id, outfall, param)
                df.loc[len(df)] = effluent_row
        
    return df
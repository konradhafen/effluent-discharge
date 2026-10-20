import requests
import json
import pandas as pd
from pathlib import Path


URL_FACILITIES = "https://echodata.epa.gov/echo/cwa_rest_services.get_facility_info?p_maj=Y&p_huc={}"
URL_REPORT = "https://echodata.epa.gov/echo/dfr_rest_services.get_dfr?output=JSON&p_id={}"
URL_EFFLUENT_CHART = "https://echodata.epa.gov/echo/eff_rest_services.get_effluent_chart?p_id={}&outfall=001&parameter_code=50050&start_date={}&end_date={}&output=JSON"

# COLUMNS_FACILITY = ['NPDES_ID', 'NAME', 'LAT', 'LON', 'LOC_ACCURACY', 'LOC_REFERENCE', 'DISCHARGE_TO_NAME', 
# 'HUC12', 'IMPAIRED_STATUS', 'IMPAIRED_YEAR', 'IMPAIRED_INFO_URL', 'IMPAIRED_REASON', 'IMPAIRED_DRINK', 
# 'IMPAIRED_ECO', 'IMPAIRED_AQU', 'IMPAIRED_FISH', 'IMPAIRED_REC', 'IMPAIRED_OTHER', 'TE_SPECIES']
FACILITY_DICT = {'NPDES_ID': 'SourceID',
              'NAME': 'CWPName', 
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

def get_facilities_list(huc):
    url = URL_FACILITIES.format(huc)
    return get_url_as_json(URL_FACILITIES.format(huc))

def get_detailed_facility_report(npdes):
    return get_url_as_json(URL_REPORT.format(npdes))

def get_effluent_chart(npdes, start_date, end_date):
    return get_url_as_json(URL_EFFLUENT_CHART.format(npdes, start_date, end_date))

def build_facility_row(facility_info, facility_report):
    row_dict = dict.fromkeys(list(FACILITY_DICT))
    row_dict['NPDES_ID'] = facility_info['SourceID']
    row_dict['NAME'] = facility_info['CWPName']
    if 'SpatialMetadata' in facility_report['Results']:
        row_dict['LAT'] = facility_report['Results']['SpatialMetadata'][FACILITY_DICT['LAT']]
        row_dict['LON'] = facility_report['Results']['SpatialMetadata'][FACILITY_DICT['LON']]
        row_dict['LOC_ACCURACY'] = facility_report['Results']['SpatialMetadata'][FACILITY_DICT['LOC_ACCURACY']]
        row_dict['LOC_REFERENCE'] = facility_report['Results']['SpatialMetadata'][FACILITY_DICT['LOC_REFERENCE']]
    if 'Watersheds' in facility_report['Results']:
        if 'WBD12s' in facility_report['Results']['Watersheds']:
            row_dict['DISCHARGE_TO_NAME'] = facility_report['Results']['Watersheds']['WBD12s'][0][FACILITY_DICT['DISCHARGE_TO_NAME']]
            row_dict['HUC12'] = facility_report['Results']['Watersheds']['WBD12s'][0][FACILITY_DICT['HUC12']]
            row_dict['TE_SPECIES'] = facility_report['Results']['Watersheds']['WBD12s'][0][FACILITY_DICT['TE_SPECIES']]
    if 'AssessedWaters' in facility_report['Results']:
        if 'AssessmentUnits' in facility_report['Results']['AssessedWaters']:
            row_dict['IMPAIRED_STATUS'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_STATUS']]
            row_dict['IMPAIRED_WATERBODY'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_WATERBODY']]
            row_dict['IMPAIRED_YEAR'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_YEAR']]
            row_dict['IMPAIRED_INFO_URL'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_INFO_URL']]
            row_dict['IMPAIRED_REASON'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_REASON']]
            row_dict['IMPAIRED_DRINK'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_DRINK']]
            row_dict['IMPAIRED_ECO'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_ECO']]
            row_dict['IMPAIRED_AQULF'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_AQULF']]
            row_dict['IMPAIRED_FISH'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_FISH']]
            row_dict['IMPAIRED_REC'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_REC']]
            row_dict['IMPAIRED_OTHER'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][FACILITY_DICT['IMPAIRED_OTHER']]
    return row_dict

def build_facilities_table(huc):
    df = pd.DataFrame(columns=list(FACILITY_DICT))
    facility_list = get_facilities_list(huc)

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
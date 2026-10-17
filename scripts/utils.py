import requests
import json
import pandas as pd


URL_FACILITIES = "https://echodata.epa.gov/echo/cwa_rest_services.get_facility_info?p_maj=Y&p_huc={}"
URL_REPORT = "https://echodata.epa.gov/echo/dfr_rest_services.get_dfr?output=JSON&p_id={}"
URL_EFFLUENT_CHART = "https://echodata.epa.gov/echo/eff_rest_services.get_effluent_chart?p_id={}&outfall=001&parameter_code=50050&start_date={}&end_date={}"

# COLUMNS_FACILITY = ['NPDES_ID', 'NAME', 'LAT', 'LON', 'LOC_ACCURACY', 'LOC_REFERENCE', 'DISCHARGE_TO_NAME', 
# 'HUC12', 'IMPAIRED_STATUS', 'IMPAIRED_YEAR', 'IMPAIRED_INFO_URL', 'IMPAIRED_REASON', 'IMPAIRED_DRINK', 
# 'IMPAIRED_ECO', 'IMPAIRED_AQU', 'IMPAIRED_FISH', 'IMPAIRED_REC', 'IMPAIRED_OTHER', 'TE_SPECIES']
DICT_MATCH = {'NPDES_ID': 'SourceID',
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
    row_dict = dict.fromkeys(list(DICT_MATCH))
    row_dict['NPDES_ID'] = facility_info['SourceID']
    row_dict['NAME'] = facility_info['CWPName']
    row_dict['LAT'] = facility_report['Results']['SpatialMetadata'][DICT_MATCH['LAT']]
    row_dict['LON'] = facility_report['Results']['SpatialMetadata'][DICT_MATCH['LON']]
    row_dict['LOC_ACCURACY'] = facility_report['Results']['SpatialMetadata'][DICT_MATCH['LOC_ACCURACY']]
    row_dict['LOC_REFERENCE'] = facility_report['Results']['SpatialMetadata'][DICT_MATCH['LOC_REFERENCE']]
    row_dict['DISCHARGE_TO_NAME'] = facility_report['Results']['Watersheds']['WBD12s'][0][DICT_MATCH['DISCHARGE_TO_NAME']]
    row_dict['HUC12'] = facility_report['Results']['Watersheds']['WBD12s'][0][DICT_MATCH['HUC12']]
    row_dict['TE_SPECIES'] = facility_report['Results']['Watersheds']['WBD12s'][0][DICT_MATCH['TE_SPECIES']]
    if 'AssessmentUnits' in facility_report['Results']['AssessedWaters']:
        row_dict['IMPAIRED_STATUS'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_STATUS']]
        row_dict['IMPAIRED_WATERBODY'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_WATERBODY']]
        row_dict['IMPAIRED_YEAR'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_YEAR']]
        row_dict['IMPAIRED_INFO_URL'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_INFO_URL']]
        row_dict['IMPAIRED_REASON'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_REASON']]
        row_dict['IMPAIRED_DRINK'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_DRINK']]
        row_dict['IMPAIRED_ECO'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_ECO']]
        row_dict['IMPAIRED_AQULF'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_AQULF']]
        row_dict['IMPAIRED_FISH'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_FISH']]
        row_dict['IMPAIRED_REC'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_REC']]
        row_dict['IMPAIRED_OTHER'] = facility_report['Results']['AssessedWaters']['AssessmentUnits'][0][DICT_MATCH['IMPAIRED_OTHER']]
    return row_dict

def build_facilities_table(huc):
    df = pd.DataFrame(columns=list(DICT_MATCH))
    facility_list = get_facilities_list(huc)

    for facility_info in facility_list['Results']['Facilities']:
        facility_report = get_detailed_facility_report(facility_info['SourceID'])
        print('NPDES', facility_info['SourceID'])
        facility_row = build_facility_row(facility_info, facility_report)
        df.loc[len(df)] = facility_row

    return df
import utils
from pathlib import Path

fn_flowlines = r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data\nhdmr_flowline.gpkg"
fn_catchments = r"C:\Users\vcq32\OneDrive - Texas State University\Projects\EPA_ECHO_Effluent\data\nhdmr_catchment.gpkg"

if not Path(fn_flowlines).is_file():
    utils.get_nhdmr_flowline_forHUC2("12", fn_flowlines)

utils.get_nhdmr_catchments_from_flowlines(fn_flowlines, fn_catchments)
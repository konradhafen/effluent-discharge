import gis

from pathlib import Path


dirpath = r"C:\Users\vcq32\OneDrive - Texas State University\Data\NHD\NHD\NHDPlusTX\NHDPlus12"
fn_gpkg = r"C:\Users\vcq32\OneDrive - Texas State University\Data\NHD\NHD\NHDPlusTX\nhdplusv2_12.gpkg"

gis.nhdplusv2_to_gpkg(dirpath, fn_gpkg)
import re
import json
from oci import regions

def get_region_from_ocid(ocid, region_map={}):
    region_value = 'unknown-region'
    match = re.search(r'oc\d{1,2}.(.*?)\.', ocid)
    if match:
        region_code = match.group(1)
        if region_code:
            # region_code = "phx"/"us-chicago-1"
            region_value = regions.get_region_from_short_name(region_code)
    return region_value

def load_region_map(region_file):
    with open(region_file, 'r') as f:
        region_map = json.load(f)
    return region_map
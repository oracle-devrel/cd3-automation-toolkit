import re
import json

def get_region_from_ocid(ocid, region_map):
    match = re.search(r'oc1\.(.*?)\.', ocid)
    if match:
        region_code = match.group(1)
        return region_map.get(region_code, 'unknown-region')
    return 'unknown-region'

def load_region_map(region_file):
    with open(region_file, 'r') as f:
        region_map = json.load(f)
    return region_map
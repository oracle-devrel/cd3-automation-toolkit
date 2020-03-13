#!/bin/python
import argparse
import os
import sys
import oci
import shutil
from oci.identity import IdentityClient
#import glob
from commonTools import *

def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

parser = argparse.ArgumentParser(description="Fetches Compartment name/ocid info from OCI and pushes to variables.tf file of each region used by TF")
parser.add_argument("outdir", help="Path  to outdir containing region directories having variables_<region>.tf file that will be used by TerraForm to communicate with OCI")
parser.add_argument("--configFileName", help="Config file name" , required=False)

args = parser.parse_args()

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

outdir=args.outdir
tenancy_id = config['tenancy']
tempStr = {}
var_files={}
var_data={}

print("outdir should contain region directories and then variables_<region>.tf file inside the region directories.")
idc=IdentityClient(config)
all_regions=[]
regionsubscriptions = idc.list_region_subscriptions(tenancy_id=tenancy_id)
for rs in regionsubscriptions.data:
    for k,v in commonTools.region_dict.items():
        if (rs.region_name==v):
            all_regions.append(k)

"""for file in glob.glob(outdir + '/*/' +'variables_*.tf'):#, recursive=True):
    region=file.split("variables_")[1].split(".tf")[0]
    all_regions.append(region)
"""
for region in all_regions:
    file=outdir+"/"+region+"/variables_"+region+".tf"
    var_files[region]=file
    tempStr[region]=''
    with open(file, 'r') as f:
        var_data[region] = f.read()
    f.close()
    # Backup the existing Routes tf file
    shutil.copy(file, file + "_backup")

for compartment in paginate(idc.list_compartments, compartment_id=tenancy_id,compartment_id_in_subtree =True):
    if(compartment.lifecycle_state=='ACTIVE'):
        compartment_name=compartment.name
        compartment_ocid=compartment.id
        searchstr = "variable \"" + compartment_name + ""
        for reg in all_regions:
            if(searchstr not in var_data[reg]):
                tempStr[reg]=tempStr[reg]+"""
variable \"""" + compartment_name + """" {
        type = "string"
        default = \"""" + compartment_ocid + """"
}
"""
for reg in all_regions:
    vname = open(var_files[reg],"a")
    vname.write(tempStr[reg])
    vname.close()
    if ("linux" in sys.platform):
        os.system("dos2unix "+var_files[reg])
print("Compartment info written to all region specific variables files under outdir folder")
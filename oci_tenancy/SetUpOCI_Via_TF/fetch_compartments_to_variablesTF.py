#!/bin/python
import argparse
import oci
import shutil
from oci.identity import IdentityClient
import glob


def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

parser = argparse.ArgumentParser(description="Fetches Compartment name/ocid info from OCI and pushes to variables.tf file of each region used by TF")
parser.add_argument("outdir", help="Path   to outdir containing variables.tf file that will be used by TerraForm to communicate with OCI")
parser.add_argument("--configFileName", help="Config file name" , required=False)

args = parser.parse_args()

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

outdir=args.outdir
identityClient = IdentityClient(config)
tenancy_id = config['tenancy']
tempStr = {}
var_files={}
all_regions=[]
var_data={}

for file in glob.glob(outdir + '/*/' +'variables_*.tf', recursive=True):
    region=file.split("variables_")[1].split(".tf")[0]
    all_regions.append(region)
    var_files[region]=file
    tempStr[region]=''
    with open(file, 'r') as f:
        var_data[region] = f.read()
    f.close()
    # Backup the existing Routes tf file
    shutil.copy(file, file + "_backup")

for compartment in paginate(identityClient.list_compartments, compartment_id=tenancy_id,compartment_id_in_subtree =True):
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
print("Compartment info written to variables file under terrafor_files folder")
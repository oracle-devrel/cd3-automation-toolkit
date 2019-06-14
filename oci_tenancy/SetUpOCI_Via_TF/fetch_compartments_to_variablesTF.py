#!/bin/python
import argparse
import oci
import shutil
from oci.identity import IdentityClient

def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

parser = argparse.ArgumentParser(description="Fetches Compartment name/ocid info from OCI and pushes to variables.tf file used by TF")
parser.add_argument("variablesTF", help="Path to variables.tf file that will be used by TerraForm to communicate with OCI; mostly present in your outdir")
parser.add_argument("--configFileName", help="Config file name" , required=False)

args = parser.parse_args()

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

variablesFile=args.variablesTF
identityClient = IdentityClient(config)
tenancy_id = config['tenancy']
tempStr = ""

# Backup the existing Routes tf file
shutil.copy(variablesFile, variablesFile + "_backup")

for compartment in paginate(identityClient.list_compartments, compartment_id=tenancy_id,compartment_id_in_subtree =True):
    if(compartment.lifecycle_state=='ACTIVE'):
        compartment_name=compartment.name
        compartment_ocid=compartment.id
        tempStr=tempStr+"""
variable \"""" + compartment_name + """" {
        type = "string"
        default = \"""" + compartment_ocid + """"
}
"""

vname = open(variablesFile,"a")
vname.write(tempStr)
print("Comaprtment info written to variables file")
vname.close()

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

parser = argparse.ArgumentParser(description="Fetches Compartment name/ocid info from OCI and pushes to variables.tf file of each region used by TF")
parser.add_argument("outdir", help="Path to outdir containing variables.tf file that will be used by TerraForm to communicate with OCI")
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
tempStrASH = ""
tempStrPHX=""

ash_var_file=outdir+'/ashburn/variables.tf'
phx_var_file=outdir+'/phoenix/variables.tf'

# Backup the existing Routes tf file
shutil.copy(ash_var_file, ash_var_file + "_backup")
shutil.copy(phx_var_file, phx_var_file + "_backup")

with open(ash_var_file, 'r') as file:
    ash_vardata = file.read()

with open(phx_var_file, 'r') as file:
    phx_vardata = file.read()

for compartment in paginate(identityClient.list_compartments, compartment_id=tenancy_id,compartment_id_in_subtree =True):
    if(compartment.lifecycle_state=='ACTIVE'):


        compartment_name=compartment.name
        compartment_ocid=compartment.id
        searchstr = "variable \"" + compartment_name + ""
        if(searchstr not in ash_vardata):
            tempStrASH=tempStrASH+"""
variable \"""" + compartment_name + """" {
        type = "string"
        default = \"""" + compartment_ocid + """"
}
"""
        if (searchstr not in phx_vardata):
            tempStrPHX = tempStrPHX + """
        variable \"""" + compartment_name + """" {
                type = "string"
                default = \"""" + compartment_ocid + """"
        }
        """
ash_vname = open(ash_var_file,"a")
phx_vname = open(phx_var_file,"a")
ash_vname.write(tempStrASH)
phx_vname.write(tempStrPHX)
print("Compartment info written to variables file")
ash_vname.close()
phx_vname.close()
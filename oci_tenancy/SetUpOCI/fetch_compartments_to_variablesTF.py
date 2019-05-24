#!/bin/python
import argparse
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient

def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

parser = argparse.ArgumentParser(description="Takes in config file as optional input. This is used eg in case script is not run from OCS VM")
parser.add_argument("variablesTF", help="Path to variables.tf file used by TerraForm")
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

compartments={}
for compartment in paginate(identityClient.list_compartments, compartment_id=tenancy_id,compartment_id_in_subtree =True):
    if(compartment.lifecycle_state=='ACTIVE'):
        compartment_name=compartment.name
        compartment_ocid=compartment.id
        compartments[compartment_name]=compartment_ocid

print(compartments)


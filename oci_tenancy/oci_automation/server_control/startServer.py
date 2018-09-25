#!/bin/python

import argparse
import sys
import oci
from oci.core.compute_client import ComputeClient
from oci.identity import IdentityClient


parser = argparse.ArgumentParser(description="Compartment Id")
parser.add_argument('--compartmentName', choices=['ManagedCompartmentForPaaS','Sabre-Networking','SHS_Community_CRS','SHS_NonProd'], default='SHS_Community_CRS',required=True,help="Name of Compartment")
parser.add_argument("--serverName",help="Server name to start",required=True)

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
compartmentName = args.compartmentName
serverName = args.serverName

config = oci.config.from_file()
compartment_id = config["tenancy"]
cc = ComputeClient(config)
identity = IdentityClient(config)


response = identity.list_compartments(compartment_id=compartment_id)
compartment_list = response.data
allCompDict = dict()
for comp in compartment_list:
        allCompDict.update({comp.name:comp.id})


instance_list_response = oci.pagination.list_call_get_all_results(cc.list_instances, allCompDict.get(compartmentName))

base_list =  instance_list_response.data

#print("Hostname,IMAGE,SHAPE,Private IP,Public IP")
for instance in base_list:
		if instance.display_name.lower() == serverName.lower():
			cc.instance_action(instance.id,"START")

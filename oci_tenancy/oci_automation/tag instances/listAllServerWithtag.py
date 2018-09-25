#!/bin/python

import argparse
import sys
import oci
from oci.core.compute_client import ComputeClient
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient


parser = argparse.ArgumentParser(description="Compartment Id")
parser.add_argument('--compartmentid', choices=['ManagedCompartmentForPaaS','Sabre-Networking','SHS_Community_CRS','SHS_NonProd'], default='SHS_Community_CRS',required=True,help="List all servers with this compartment ID")
parser.add_argument("--Namespace",help="name of tag namespace",required=True)
parser.add_argument("--Tagname",help="tag name to assign to selected instance",required=True)
parser.add_argument("--tagvalue",help="tag value to assign to selected of instance",required=False,type=str)

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
compartmentid = args.compartmentid
namespace=args.Namespace
tagname=args.Tagname
tagvalue=args.tagvalue

config = oci.config.from_file()
compartment_id = config["tenancy"]
cc = ComputeClient(config)
identity = IdentityClient(config)


response = identity.list_compartments(compartment_id=compartment_id)
compartment_list = response.data
allCompDict = dict() 
for compartment in compartment_list:
	allCompDict.update({compartment.name:compartment.id})


instance_list_response = oci.pagination.list_call_get_all_results(cc.list_instances, allCompDict.get(compartmentid))

base_list =  instance_list_response.data

print("Hostname,IMAGE,SHAPE,Private IP,Public IP")
for instance in base_list:
	#print(instance.defined_tags)
	tags = instance.defined_tags
	instance_id = instance.id
	#print("namespace in tags" + namespace in tags)
	if namespace in tags and  tagname in tags[namespace]:
		responseImage = cc.get_image(image_id=instance.image_id)
		imageName = responseImage.data.display_name
		if instance.lifecycle_state != 'TERMINATED':
			vnic_list = cc.list_vnic_attachments(compartment_id=allCompDict.get(compartmentid),instance_id=instance.id).data
        		for vnic in vnic_list:
				config = oci.config.from_file()
	        		vnc = VirtualNetworkClient(config)
        			response = vnc.get_vnic(vnic_id=vnic.vnic_id)
				#print(response.data)
				pubIPAddress = response.data.public_ip
				if pubIPAddress is None:
					pubIPAddress="" 	
		        	print(instance.display_name + ","+ imageName +"," +instance.shape+","+response.data.private_ip+","+pubIPAddress)

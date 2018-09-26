#!/bin/python

#Author: Amit Shah
#Oracle Consulting
#amit.a.shah@oracle.com


import oci
from oci.core.compute_client import ComputeClient
from oci.core.virtual_network_client import VirtualNetworkClient
import argparse

parser = argparse.ArgumentParser(description="Assign tag to spcific instance")
parser.add_argument('--action', choices=['add','append','remove','removeAll'], default='add',required=True)
parser.add_argument('--AttrName', help="Attribute Name to search - must be a part of instance")
parser.add_argument('--AttrValue', help="Attribute Value to search - must be a part of instance. Name=Value is what we're going to be looking for ")
parser.add_argument('TagNameSpace', help="Namespace of tag")
parser.add_argument('TagName', help="Name of tag")
parser.add_argument('--TagValue', help="value of tag")

args = parser.parse_args()



attrName = args.AttrName
attrValuePattern = args.AttrValue
tnspace = args.TagNameSpace
tname = args.TagName
tvalue = args.TagValue

config = oci.config.from_file()
compartment_id = config["compartment_id"]
ad = config["ad_3"]

cc = ComputeClient(config)
ic = oci.identity.IdentityClient(config)

instance_list = cc.list_instances(availability_domain=ad, compartment_id=compartment_id)
tag_list = ic.list_tag_namespaces(compartment_id)

tnotfound = True
for tns in tag_list.data:
	print tns.name
	tlist = ic.list_tags(tns.id)
	print tlist.data


filteredList = []
for instance in instance_list.data:
	strAttrName=str(eval("instance."+attrName))
	#print("Attrname: " + strAttrName)
	#print(instance)
	if attrValuePattern in strAttrName:
		#print ("attribute pattern matched for instance:  "+strAttrName)
		instanceNotFound = False
		filteredList.append(instance)

for f in filteredList:
	print f.display_name + " \n" 
	existingTagList = f.defined_tags
	print existingTagList
#defined_tags = { "shs-os": {"Linux74":""}}
##defined_tags = {}
#uid = oci.core.models.UpdateInstanceDetails(defined_tags = defined_tags)
#
##response = cc.update_instance(instance_id=instance_id,update_instance_details=uid)
#print existingTagList
#
#print("shs-os" in existingTagList)


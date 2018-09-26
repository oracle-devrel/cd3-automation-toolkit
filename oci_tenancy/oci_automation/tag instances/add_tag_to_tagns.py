#!/bin/python


#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import oci
import argparse
from oci.core.compute_client import ComputeClient

parser = argparse.ArgumentParser(description="add tags to existing tag namespace")
parser.add_argument("tag_name_space",help="The namespace for which you want all these tags to be added.  Case Sensitive!")
parser.add_argument("file", help="Input file of all tags for a namespace")


if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)



config = oci.config.from_file("~/.oci/config.ashburn")
compartment_id = config["compartment_id"]
ad = config["ad_3"]

oic = oci.identity.IdentityClient(config)


args = parser.parse_args()
tag_ns = args.tag_name_space
file = args.file

tns = oic.list_tag_namespaces(compartment_id)

tnsFound = False
tid = ""
for tn in tns.data:
	print "Searching for: " +tag_ns + " tn name" + tn.name + " \n"
	if tag_ns in tn.name:
		tnsFound = True
		tid = tn.id
		print  "Found the tag name space with tid: " + tid
		break
	
#if not tnsFound: 
#	ctnsd = oci.identity.models.CreateTagNamespaceDetails(compartment_id=compartment_id, name=tag_ns, description=tag_ns)
#	response = oic.create_tag_namespace(ctnsd)
#	tid = response.data.id
#
f = open(file,"r")
for tag in f:
	name = tag.strip()
	description = name.replace("-"," ")
	print "Tag Name: " + name + " Description: " + description + "\n"
	ctd = oci.identity.models.CreateTagDetails(name=name,description=description)
	response = oic.create_tag(tag_namespace_id=tid,create_tag_details=ctd)
	print response
	



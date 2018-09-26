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


if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)



config = oci.config.from_file("~/.oci/config.ashburn")
compartment_id = config["compartment_id"]
ad = config["ad_3"]

oic = oci.identity.IdentityClient(config)


args = parser.parse_args()
tag_ns = args.tag_name_space

tns = oic.list_tag_namespaces(compartment_id)

tnsFound = False
tid = ""
for tn in tns.data:
	print "Searching for: " +tag_ns + " tn name" + tn.name + " \n"
	if tag_ns in tn.name:
		tnsFound = True
		tid = tn.id
		print  "Found the tag name space with tid: " + tid
		response =  oic.list_tags(tid)
		for def_tags in response.data:
			print def_tags.name
		print "\n\n\n ### Next Page \n\n\n"
		while response.has_next_page:
			response =  oic.list_tags(tid,page=response.next_page)
			for def_tags in response.data:
				print def_tags.name
			print "\n\n\n ### Next Page \n\n\n"
		break

	
#if not tnsFound: 
#	ctnsd = oci.identity.models.CreateTagNamespaceDetails(compartment_id=compartment_id, name=tag_ns, description=tag_ns)
#	response = oic.create_tag_namespace(ctnsd)
#	tid = response.data.id
#

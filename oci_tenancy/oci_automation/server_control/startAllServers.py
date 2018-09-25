#!/bin/python
import csv  
import shutil
import sys
import argparse
import in_place
import re
import oci
from oci.core.compute_client import ComputeClient
from oci.identity import IdentityClient

def skipCommentedLine(lines):
	"""
	A filter which skip/strip the comments and yield the
	rest of the lines
	:param lines: any object which we can iterate through such as a file
        object, list, tuple, or generator
    	"""
	for line in lines:
		comment_pattern = re.compile(r'\s*#.*$')
		line = re.sub(comment_pattern, '', line).strip()
		if line:
			yield line



parser = argparse.ArgumentParser(description="List of Servers")
parser.add_argument("--serverList",help="Comma separated list of server with respective compartment name[serverName,CompartmentName]")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
serverList = args.serverList

config = oci.config.from_file()
compartment_id = config["tenancy"]
cc = ComputeClient(config)
identity = IdentityClient(config)


response = identity.list_compartments(compartment_id=compartment_id)
compartment_list = response.data
allCompDict = dict()
for comp in compartment_list:
        allCompDict.update({comp.name:comp.id})


serverListDict = dict()	
with open(serverList) as servers:  
	#reader = csv.DictReader(servers)
        reader = csv.DictReader(skipCommentedLine(servers))
	columns = reader.fieldnames
	for row in reader:
		print[row]
		serverListDict.update({row['serverName']:row['compartmentName']})
			
			
print(serverListDict)
compSet = set(serverListDict.values())
for compartment in compSet:
	print(compartment)

	#compartmentName = 
	instance_list_response = oci.pagination.list_call_get_all_results(cc.list_instances, allCompDict.get(compartment))

	base_list =  instance_list_response.data

	for instance in base_list:
                if instance.display_name.lower() in serverListDict:
                	#cc.instance_action(instance.id,"START")
			print("Starting " + instance.display_name +" from compartment :: " +compartment)
			cc.instance_action(instance.id,"START")

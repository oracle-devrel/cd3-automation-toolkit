#!/bin/python
## Author : Murali

import sys
import time
import oci
from oci.core.compute_client import ComputeClient
from oci.core.virtual_network_client import VirtualNetworkClient
import argparse

parser = argparse.ArgumentParser(description="Assign tag to spcific instance")
parser.add_argument('file', help="Input file - \"Hostname,shs-os,shs-environment,shs-subnets\" in first heading. This gives the list of tags")


if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()



file = args.file

config = oci.config.from_file()
compartment_id = config["compartment_id"]
ad = config["ad_3"]

cc = ComputeClient(config)
ic = oci.identity.IdentityClient(config)

instance_list_response = oci.pagination.list_call_get_all_results(cc.list_instances,availability_domain=ad, compartment_id=compartment_id )
tag_ns_list = ic.list_tag_namespaces(compartment_id)

tnotfound = True
tns_list_local = []
tag_list_local = []
for tns in tag_ns_list.data:
#	print tns.name
	tns_list_local.append(tns.name)
	tlist = ic.list_tags(tns.id)
	for t in tlist.data:
		if not t.is_retired:	
			tag = tns.name + ":" + t.name
			tag_list_local.append(tag)




slist = {}
tag_namespace_headings = []
f  = open(file,'r')
i=0
for server in f:
	if i == 0:
		tnh = server.strip().split(",")
		hostname = tnh[0]
		# print len(tnh)
		for j in range(1,len(tnh)):
			tag_namespace_headings.append(tnh[j])

		# print tag_namespace_headings
	if server.strip():
		ss = server.strip().split(",")
		# print ss
		server = ss[0].strip()
		temp_str = "" 
		for k in range(1,len(ss)):
		# 	print "K : " + str(k) + " temp_str : " + temp_str
			temp_str = temp_str + "," +  tag_namespace_headings[k-1] + ":" +  ss[k]

		temp_str = temp_str.lstrip(",")
#		print temp_str
		slist[server] = temp_str

f.close()

instance_list = instance_list_response.data
print "Instance list size :" + str(len(instance_list))
print "Server List Keys Size : "  + str(len(slist.keys()))

# print "Slist keys" 
#for key in slist.keys():
	# print key + "\n"

num_tagged=0
for instance in instance_list:
	if instance.lifecycle_state == 'TERMINATED':
		continue
	name = instance.display_name
	existing_tags = instance.defined_tags
	if name in slist.keys():
		print "Server name : " + name + "Tags to attach : " + slist[name]
		if len(existing_tags.keys()) > 0 :
			print "Server Existing Tags: " + existing_tags.keys()[0]
		tlist = slist[name].split(",")
		for t in tlist:
			tsplit = t.split(":")
			ns = tsplit[0]
			#if ns in existing_tags:
			#	continue
			#else:
			tname = tsplit[1]
			tvalue = ''
			if "=" in tname:
				tvalue = tname.split("=")[1]
				tname = tname.split("=")[0]
			ndt = { ns: {tname:tvalue }}
			existing_tags.update(ndt)
		for attempt in range(10):
			try:
				uid = oci.core.models.UpdateInstanceDetails(defined_tags =  existing_tags)
				response = cc.update_instance(instance.id,uid)
				num_tagged = num_tagged + 1
			except Exception as detail:
                                print "Got error -retrying" + str(detail)
				time.sleep(2)
			else:
                                break


print "total servers tagged :"  + str(num_tagged)
		



		

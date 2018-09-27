#!/bin/python

import oci
import sys
import argparse
from oci.core.compute_client import ComputeClient

vm_details = []

def printTable(vmList):
	print("Server name,Server Type,Inital Username,Initial password,remark")
	for vm in vmList:
		print(vm["Server name"] + "," + vm["Server Type"] + "," + vm["Inital Username"]+ "," + vm["Initial password"] + "," + vm["remark"])

def getUserInitCredntials(displayname):
	remark = ""
	systemType = ""
	uname = ""
	initPwd = ""

	config = oci.config.from_file()
	compartment_id = config["compartment_id"]
	ad = config["ad_3"]

	cc = ComputeClient(config)

	response = cc.list_instances(availability_domain=ad, compartment_id=compartment_id, limit=1, display_name=displayname)
	#print(len(response.data))

	if len(response.data)==0:
		remark="Unable to find instance with name : "+ displayname
		#sys.exit(1)
	else:
		#print response.data
		instance = response.data[0]

		instance_id = instance.id
		source_details = instance.source_details
		image_id=source_details.image_id

		imagedetails =cc.get_image(image_id)
		systemType=imagedetails.data.operating_system
		#print systemType

		if systemType!='Windows':
			remark="Not a windows Instance : "+ displayname 
			#sys.exit(1)
		else:
			response = cc.get_windows_instance_initial_credentials(instance_id);
			uname = response.data.username
			initPwd = response.data.password

	#print response.data
	#print instance.source_details
			vm_details.append({
        			'Server name' : displayname,
				'Server Type'   : str(systemType) ,
        			'Inital Username'  : str(uname),
        			'Initial password'   : str(initPwd),
				'remark'   : remark
			})

	#print "Inital Username : "+ uname
	#print "Initial password : "+ initPwd


parser = argparse.ArgumentParser(description="get initial user credentials for newly created windows image")
#parser.add_argument("--displayname",help="display name of windows image",required=False)
#parser.add_argument("displayname",help="display name of windows image",required=False)
parser.add_argument('--action', choices=['servername', 'serverlist'], default='servername')
parser.add_argument("--displayname",help="display name of windows image",required=False)
parser.add_argument("--serverlistfile")
args = parser.parse_args()

if args.action != 'servername' and args.displayname:
    parser.error('--displayname can only be set when --action=servername.')
if args.action != 'serverlist' and args.serverlistfile:
    parser.error('--serverlistfile can only be set when --action=serverlist.')

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

displayname = args.displayname

#print(displayname)
if args.action == 'servername' and args.displayname is not None:
	getUserInitCredntials(displayname)
if args.action == 'serverlist' and args.serverlistfile is not None:
        with open(args.serverlistfile, 'r') as f:
		for displayname in f.readlines():
			#print("####"+displayname.strip()+"####")
			getUserInitCredntials(displayname.strip())

printTable(vm_details)

#!/bin/python
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com



import sys
import os
import argparse
import ConfigParser
######
# Required Files
# Also required is the "oci-tf.properties"
# List of Subnets - Each Subnet will get its route table.
# The subnets file can be the same one that is used for creating the sec rules and subnets
# List of destination:network_entity_id:destination_type
# destination example: Examples: 10.12.0.0/16 oci-phx-objectstorage
# destination_type example: Type of destination for the route rule. SERVICE_CIDR_BLOCK should be used if destination is a service cidrBlock. CIDR_BLOCK should be used if destination is IP address range in CIDR notation. It must be provided along with destination
# Example: 10.26.76.0/23:${oci_core_drg.drg01.id}
# Outfile
######


parser = argparse.ArgumentParser(description="Creates a routelist for each subnet. Every route in the routeslist file will be created for each of the subnets." )  
parser.add_argument("file",help="Full Path to the Subnet file. See readme for format example ")
parser.add_argument("routeslist",help="Full Path to file")
parser.add_argument("outfile",help="Output Filename")
parser.add_argument("--omcs",help="If the File is of OMCS format: \"prod-dmz-lb-ext2-10.89.69.0/24,AD2\"",action="store_true")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<4:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

config = ConfigParser.RawConfigParser()
config.read('oci-tf.properties')

filename = args.file
routesfile = args.routeslist
outfile = args.outfile

# print "filename = " + filename + " routefiles  = " + routesfile + " outfile = " + outfile 

fname = open(filename,"r")
oname = open(outfile,"w")
rname = open(routesfile,"r")


####
#ntk_comp_var=ntk_compartment_ocid
#comp_var=compartment_ocid
#vcn_var=vcn01
#####

vcn_var = config.get('Default','vcn_var')
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')

ADS = ["AD1","AD2","AD3"]


### Read the Routes file


tempStr = ""
for line in fname:
	
	if not line.startswith('#'):
		print "processing : " + line
		subnet = ""
		name = ""
                if args.omcs :

                        name_sub,AD,pubpvt,dhcp = line.split(',')
                        # line = line.split(",",1)[0]
                        subnet = name_sub.rsplit("-",1)[1].strip()
                        name = name_sub.rsplit("-",1)[0].strip()

                else :

                        [name,sub,AD,pubpvt,dhcp] = line.split(',')
                        linearr = line.split(",")
                        name = linearr[0].strip()
                        subnet = linearr[1].strip()

#		if args.omcs:
#			#### OMCS Type ####
#			line = line.split(",",1)[0]
#			subnet = line.rsplit("-",1)[1].strip()
#			name = line.rsplit("-",1)[0].strip()
#		else:
#			#### non-omcs###
#			linearr = line.split(",")
#			name = linearr[0].strip()
#			subnet = linearr[1].strip()

		ad = ADS.index(AD)
		ad_name = ad + 1
		name = name + str(ad_name)
		display_name = name +  "-" + subnet
		# print "Name: " + name + " Subnet: " + subnet + "\n"

		tempStr = """
	resource "oci_core_route_table" \"""" + name +  """"{
		compartment_id = "${var.""" + ntk_comp_var + """}"
		vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
		display_name = \""""  + display_name.strip() + """\" """

		rname.seek(0,0)
		for route in rname:
			if not route.startswith('#'):
				dest = route.split(":")[0]
				ntk_ent_id = route.split(":")[1]
				dest_type = route.split(":")[2]
				dest_type = dest_type.strip()
				tempStr = tempStr + """ 
	route_rules { 
	     destination = \"""" + dest + """\"
	     network_entity_id = \"""" + ntk_ent_id + """\"
	     destination_type = \"""" + dest_type + """\"
	}
	"""
		tempStr = tempStr + """
}
"""
		oname.write(tempStr)


fname.close()
oname.close()


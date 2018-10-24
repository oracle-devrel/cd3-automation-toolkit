#!/bin/python
# Author: Murali Nagulakonda
# Oracle Consulting
# murali.nagulakonda.venkata@oracle.com


import sys
import os
import argparse
import ConfigParser

######
# Required Files
# Also required is the "oci-tf.properties"
# List of Subnets - Each Subnet will get its route table.
# The subnets file can be the same one that is used for creating the sec rules and subnets
# Outfile
######


parser = argparse.ArgumentParser(
    description="Creates a routelist for each subnet. Every route in the routeslist file will be created for each of the subnets.")
parser.add_argument("subnetfile", help="Full Path to the Subnet file. See readme for format example ")
parser.add_argument("outfile", help="Output Filename")
parser.add_argument("--omcs", help="If the File is of OMCS format: \"prod-dmz-lb-ext2-10.89.69.0/24,AD2\"",
                    action="store_true")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

config = ConfigParser.RawConfigParser()
config.read('oci-tf.properties')

subnet_file = args.subnetfile
outfile = args.outfile

fname = open(subnet_file, "r")
oname = open(outfile, "w")

####
# Fetch config properties
vcn_var = config.get('Default', 'vcn_var')
ntk_comp_var = config.get('Default', 'ntk_comp_var')
drg_var = config.get('Default', 'drg_var')
lpg_var = config.get('Default', 'lpg_var')
sgw_var = config.get('Default', 'sgw_var')
ngw_var = config.get('Default', 'ngw_var')
igw_var = config.get('Default', 'igw_var')

configure_drg = config.get('Default', 'add_drg_route')
configure_lpg = config.get('Default', 'add_lpg_route')
drg_destination = config.get('Default', 'drg_subnet')
lpg_destination = config.get('Default', 'lpg_subnet')

tempStr = ""
ruleStr = ""

ADS = ["AD1", "AD2", "AD3"]

if configure_drg == 'true':
    ruleStr = ruleStr + """

        	route_rules { 
            destination = \"""" + drg_destination + """\"
    	    network_entity_id = "${oci_core_drg.""" + drg_var + """.id}"
    	    destination_type = "CIDR_BLOCK"
    		}
    		"""
if configure_lpg == 'true':
    ruleStr = ruleStr + """

        	route_rules { 
            destination = \"""" + lpg_destination + """\"
    	    network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_var + """.id}"
    	    destination_type = "CIDR_BLOCK"
    		}
    		"""

# Read input subnet file
for line in fname:
    if not line.startswith('#'):
        # print "processing : " + line
        subnet = ""
        name = ""
        if args.omcs:
            name_sub, AD, pubpvt, dhcp, configure_sgw, configure_ngw, configure_igw = line.split(',')
            subnet = name_sub.rsplit("-", 1)[1].strip()
            name = name_sub.rsplit("-", 1)[0].strip()

        else:
            [name, sub, AD, pubpvt, dhcp, configure_sgw, configure_ngw, configure_igw] = line.split(',')
            linearr = line.split(",")
            name = linearr[0].strip()
            subnet = linearr[1].strip()

        ad = ADS.index(AD)
        ad_name = ad + 1
        name = name + str(ad_name)
        display_name = name + "-" + subnet

        tempStr = """
			resource "oci_core_route_table" \"""" + name + """"{
			compartment_id = "${var.""" + ntk_comp_var + """}"
			vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
			display_name = \"""" + display_name.strip() + """\" """ + ruleStr

        if configure_sgw == 'true':
            tempStr = tempStr + """

			route_rules { 
	     	destination = "${data.oci_core_services.oci_services.services.0.cidr_block}"
	     	network_entity_id = "${oci_core_service_gateway.""" + sgw_var + """.id}"
	     	destination_type = "SERVICE_CIDR_BLOCK"
			}
			"""
        if configure_ngw == 'true':
            tempStr = tempStr + """ 

			route_rules { 
		   	destination = "0.0.0.0/0"
		   	network_entity_id = "${oci_core_nat_gateway.""" + ngw_var + """.id}"
		   	destination_type = "CIDR_BLOCK"
			}
			"""
        if configure_igw.strip() == 'true':
            tempStr = tempStr + """

			route_rules { 
		   	destination = "0.0.0.0/0"
		   	network_entity_id = "${oci_core_internet_gateway.""" + igw_var + """.id}"
		   	destination_type = "CIDR_BLOCK"
			}
			"""
        tempStr = tempStr + """
	}
	"""
        oname.write(tempStr)

fname.close()
oname.close()


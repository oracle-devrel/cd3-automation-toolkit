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
# "oci-tf.properties"
# Dhcp options defined in "ini" format.
# the Section name of the ini file becomes the "dhcp rule name"
# The script expects a "default" section.
# Optionally - name the dhcp section the same as the subnet name - and when creating subnets - the subnet will point to this dhcp option.
# The subnets file can be the same one that is used for creating the sec rules and subnets
# List of cidr_block:network_entity_id 
# Example: 10.26.76.0/23:${oci_core_drg.drg01.id}
# Outfile
######


parser = argparse.ArgumentParser(description="Create DHCP options terraform file")
parser.add_argument("file",help="path to dhcp file in \"ini\" format. ")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

config = ConfigParser.RawConfigParser()
config.read('oci-tf.properties')

filename = args.file
outfile = args.outfile

# print "filename = " + filename + " routefiles  = " + routesfile + " outfile = " + outfile 

oname = open(outfile,"w")


####
#ntk_comp_var=ntk_compartment_ocid
#comp_var=compartment_ocid
#vcn_var=vcn01
#####

vcn_var = config.get('Default','vcn_var')
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')

### Read the Routes file


tempStr = ""
dhcpfile = ConfigParser.RawConfigParser()
dhcpfile.read(filename)

sections = dhcpfile.sections()

for section in sections :


	display_name = section
	serverType = dhcpfile.get(section,'serverType')
	search_domain = dhcpfile.get(section,'search_domain')
	dns_servers = ""
	
	tempStr = """
resource "oci_core_dhcp_options" \"""" + section + """" {
	compartment_id = "${var.""" + ntk_comp_var + """}"
	options {
        type = "DomainNameServer"
	server_type = \"""" + serverType  + "\""

	# print serverType
	if serverType  == "CustomDnsServer" :
		dns_servers = dhcpfile.get(section,'custom_dns_servers').strip().replace(',','","')
		dns_servers = '"' + dns_servers + '"'
		tempStr = tempStr + """
	custom_dns_servers = [ """ + dns_servers + """ ] """
	
	tempStr = tempStr + """
	}
	options {
		type = "SearchDomain"
		search_domain_names = [ \"""" + search_domain + """" ]
	}
	
	vcn_id = "${oci_core_virtual_network.""" + vcn_var + """.id}"

	#Optional
	display_name = \""""  + display_name.strip() + """"
}
"""
	oname.write(tempStr)


oname.close()


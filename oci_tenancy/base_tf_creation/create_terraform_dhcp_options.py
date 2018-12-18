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
# "properties file- oci-tf.properties"
# Code will read input dhcp file name from properties file
# Dhcp options defined in "ini" format.
# the Section name of the ini file becomes the "dhcp rule name"
# The script expects a "default" section.
# Optionally - name the dhcp section the same as the subnet name - and when creating subnets - the subnet will point to this dhcp option.
# Outfile
######


parser = argparse.ArgumentParser(description="Create DHCP options terraform file")
parser.add_argument("propsfile", help="Full Path of properties file. eg oci-tf.properties in example folder")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
config = ConfigParser.RawConfigParser()
config.read(args.propsfile)

outfile = args.outfile
oname = open(outfile,"w")

vcn_var = config.get('Default','vcn_var')
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')

### Read the DHCP file

dhcpfile = ConfigParser.RawConfigParser()
dhcp_file = config.get('Default','dhcp_file')
dhcpfile.read(dhcp_file)

tempStr = ""
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
	
	vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"

	#Optional
	display_name = \""""  + display_name.strip() + """"
}
"""
	oname.write(tempStr)

oname.close()


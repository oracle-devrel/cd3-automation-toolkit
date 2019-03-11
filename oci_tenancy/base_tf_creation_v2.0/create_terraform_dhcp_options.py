#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import configparser
######
# Required Files
# "properties file- vcn-info.properties"
# Code will read input dhcp file name from properties file
# Dhcp options defined in "ini" format.
# the Section name of the ini file becomes the "dhcp rule name" with vcn_name as the prefix
# The script expects a "default" section.
# Optionally - name the dhcp section the same as the subnet name - and when creating subnets - the subnet will point to this dhcp option.
# Outfile
######


parser = argparse.ArgumentParser(description="Create DHCP options terraform file")
parser.add_argument("propsfile", help="Full Path of properties file. eg vcn-info.properties in example folder")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
outfile = args.outfile
oname = open(outfile,"w")

config = configparser.RawConfigParser()
config.optionxform = str
config.read(args.propsfile)
sections=config.sections()

#Get Global Properties from Default Section
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')

tempStr = ""
#Get VCN and DHCP file info from VCN_INFO section
vcns=config.options('VCN_INFO')
for vcn in vcns:
	vcn_data = config.get('VCN_INFO', vcn)
	vcn_data = vcn_data.split(',')
	vcn_name = vcn
	vcn_dhcp_file = vcn_data[7].strip().lower()
	### Read the DHCP file
	dhcpfile = configparser.RawConfigParser()
	dhcpfile.read(vcn_dhcp_file)

	dhcp_sections = dhcpfile.sections()
	for dhcp_sec in dhcp_sections :
		vcn_dhcp = vcn_name+"_"+dhcp_sec
		vcn_dhcp.strip().lower()
		serverType = dhcpfile.get(dhcp_sec,'serverType')
		search_domain = dhcpfile.get(dhcp_sec,'search_domain')
		dns_servers = ""
	
		tempStr = tempStr+"""
resource "oci_core_dhcp_options" \"""" + vcn_dhcp + """" {
	compartment_id = "${var.""" + ntk_comp_var + """}"
	options {
        type = "DomainNameServer"
		server_type = \"""" + serverType  + "\""

		# print serverType
		if serverType  == "CustomDnsServer" :
			dns_servers = dhcpfile.get(dhcp_sec,'custom_dns_servers').strip().replace(',','","')
			dns_servers = '"' + dns_servers + '"'
			tempStr = tempStr + """
		custom_dns_servers = [ """ + dns_servers + """ ] """
	
		tempStr = tempStr + """
	}
	options {
		type = "SearchDomain"
		search_domain_names = [ \"""" + search_domain + """" ]
	}
	vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
	display_name = \""""  + vcn_dhcp + """"
}
"""
oname.write(tempStr)
oname.close()


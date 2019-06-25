#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import configparser
import pandas as pd

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
parser.add_argument("inputfile", help="Full Path of input file. It could be either the properties file eg vcn-info.properties or CD3 excel file")
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

tempStr = ""

if('.xls' in args.inputfile):
	df_vcn = pd.read_excel(args.inputfile, sheet_name='VCNs',skiprows=1)
	df_vcn.set_index("vcn_name", inplace=True)
	df_vcn.head()
	df = pd.read_excel(args.inputfile, sheet_name='DHCP',skiprows=1)
	for i in df.index:
		vcn_name = df.iat[i,0]
		dhcp_option_name = df.iat[i,1]
		serverType = df.iat[i,2]
		search_domain = df.iat[i,3]
		custom_dns_servers = df.iat[i,4]
		vcn_dhcp = vcn_name + "_" + dhcp_option_name
		vcn_dhcp.strip().lower()

		vcn_data = df_vcn.loc[vcn_name]
		compartment_var_name = vcn_data['compartment_name']

		tempStr = tempStr + """
resource "oci_core_dhcp_options" \"""" + vcn_dhcp + """" {
		compartment_id = "${var.""" + compartment_var_name + """}"
		options {
			type = "DomainNameServer"
			server_type = \"""" + serverType + "\""

		# print serverType
		if serverType == "CustomDnsServer":
			dns_servers = custom_dns_servers.strip().replace(',', '","')
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
		display_name = \"""" + vcn_dhcp + """"
}
"""



elif('.properties' in args.inputfile):
	print("Input is vcn-info.properties")

	config = configparser.RawConfigParser()
	config.optionxform = str
	config.read(args.inputfile)
	sections=config.sections()


	#Get VCN and DHCP file info from VCN_INFO section
	vcns=config.options('VCN_INFO')
	for vcn in vcns:
		vcn_data = config.get('VCN_INFO', vcn)
		vcn_data = vcn_data.split(',')
		vcn_name = vcn
		compartment_var_name = vcn_data[11].strip()
		vcn_dhcp_file = vcn_data[7].strip().lower()
		### Read the DHCP file
		dhcpfile = configparser.RawConfigParser()
		file_read=dhcpfile.read(vcn_dhcp_file)
		if(len(file_read)!=1):
			print("input dhcp file "+vcn_dhcp_file +" for VCN "+vcn_name +" could not be opened. Please check if it exists. Skipping DHCP TF creation for this VCN.")
			continue
		dhcp_sections = dhcpfile.sections()
		for dhcp_sec in dhcp_sections :
			vcn_dhcp = vcn_name+"_"+dhcp_sec
			vcn_dhcp.strip().lower()
			serverType = dhcpfile.get(dhcp_sec,'serverType')
			search_domain = dhcpfile.get(dhcp_sec,'search_domain')
			dns_servers = ""
	
			tempStr = tempStr+"""
resource "oci_core_dhcp_options" \"""" + vcn_dhcp + """" {
	compartment_id = "${var.""" + compartment_var_name + """}"
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
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")

oname.write(tempStr)
oname.close()


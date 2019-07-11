#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import configparser
import os
import pandas as pd

######
# Required Files
# input file is cd3 or vcn-info.properties; if vcn-info.properties then Code will read input dhcp file name from properties file
# Dhcp options defined in "ini" format.
# the Section name of the ini file becomes the "dhcp rule name" with vcn_name as the prefix
# The script expects a "default" section.
# Optionally - name the dhcp section the same as the subnet name - and when creating subnets - the subnet will point to this dhcp option.
# Outdir
######


parser = argparse.ArgumentParser(description="Create DHCP options terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the properties file eg vcn-info.properties or CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir = args.outdir
prefix=args.prefix

ash_dir=outdir+"/ashburn"
phx_dir=outdir+"/phoenix"

if not os.path.exists(ash_dir):
        os.makedirs(ash_dir)

if not os.path.exists(phx_dir):
        os.makedirs(phx_dir)

outfile_ash=ash_dir + "/" + prefix + '-dhcp.tf'
outfile_phx=phx_dir + "/" + prefix + '-dhcp.tf'

oname_ash = open(outfile_ash,"w")
oname_phx = open(outfile_phx,"w")

tempStrASH = ""
tempStrPHX = ""

def processDHCP(region,vcn_name,dhcp_option_name,compartment_var_name,serverType,custom_dns_servers,search_domain):
	global tempStrASH
	global tempStrPHX

	region = region.lower().strip()
	compartment_var_name=compartment_var_name.strip()
	serverType=serverType.strip()
	search_domain=search_domain.strip()
	vcn_name=vcn_name.strip()
	dhcp_option_name=dhcp_option_name.strip()
	vcn_dhcp = vcn_name + "_" + dhcp_option_name

	data = """
	resource "oci_core_dhcp_options" \"""" + vcn_dhcp + """" {
			compartment_id = "${var.""" + compartment_var_name.strip() + """}"
			options {
				type = "DomainNameServer"
				server_type = \"""" + serverType.strip() + "\""

	# print serverType
	if serverType == "CustomDnsServer":
		dns_servers = custom_dns_servers.strip().replace(',', '","')
		dns_servers = '"' + dns_servers + '"'
		data = data + """
				custom_dns_servers = [ """ + dns_servers + """ ] """

	data = data + """
			}
			options {
				type = "SearchDomain"
				search_domain_names = [ \"""" + search_domain + """" ]
			}
			vcn_id = "${oci_core_vcn.""" + vcn_name.strip() + """.id}"
			display_name = \"""" + vcn_dhcp + """"
	}
	"""

	if (region == 'ashburn'):
		tempStrASH = tempStrASH + data
	elif (region == 'phoenix'):
		tempStrPHX = tempStrPHX + data

endNames = {'<END>', '<end>'}
if('.xls' in args.inputfile):
	df_vcn = pd.read_excel(args.inputfile, sheet_name='VCNs',skiprows=1)
	df_vcn.dropna(how='all')
	df_vcn.set_index("vcn_name", inplace=True)
	df_vcn.head()
	df = pd.read_excel(args.inputfile, sheet_name='DHCP',skiprows=1)
	df.dropna(how='all')
	for i in df.index:
		vcn_name = df.iat[i,0]
		if (vcn_name in endNames):
			break
		dhcp_option_name = df.iat[i,1]
		serverType = df.iat[i,2]
		search_domain = df.iat[i,3]
		custom_dns_servers = df.iat[i,4]

		vcn_data = df_vcn.loc[vcn_name]
		compartment_var_name = vcn_data['compartment_name']
		region=vcn_data['Region']

		processDHCP(region,vcn_name,dhcp_option_name,compartment_var_name,serverType,custom_dns_servers,search_domain)



elif('.properties' in args.inputfile):
	print("Input is vcn-info.properties")

	config = configparser.RawConfigParser()
	config.optionxform = str
	config.read(args.inputfile)
	#sections=config.sections()


	#Get VCN and DHCP file info from VCN_INFO section
	vcns=config.options('VCN_INFO')
	for vcn in vcns:
		vcn_data = config.get('VCN_INFO', vcn)
		vcn_data = vcn_data.split(',')
		vcn_name = vcn
		region=vcn_data[0].strip()
		compartment_var_name = vcn_data[12].strip()
		vcn_dhcp_file = vcn_data[8].strip().lower()
		### Read the DHCP file
		dhcpfile = configparser.RawConfigParser()
		file_read=dhcpfile.read(vcn_dhcp_file)
		if(len(file_read)!=1):
			print("input dhcp file "+vcn_dhcp_file +" for VCN "+vcn_name +" could not be opened. Please check if it exists. Skipping DHCP TF creation for this VCN.")
			continue
		dhcp_sections = dhcpfile.sections()
		for dhcp_sec in dhcp_sections :
			#vcn_dhcp = vcn_name+"_"+dhcp_sec
			#vcn_dhcp.strip().lower()
			serverType = dhcpfile.get(dhcp_sec,'serverType')
			search_domain = dhcpfile.get(dhcp_sec,'search_domain')
			custom_dns_servers=""
			try:
				custom_dns_servers = dhcpfile.get(dhcp_sec, 'custom_dns_servers')
			except Exception as e:
				print()

			processDHCP(region, vcn_name, dhcp_sec, compartment_var_name, serverType, custom_dns_servers,search_domain)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")


oname_ash.write(tempStrASH)
oname_phx.write(tempStrPHX)
oname_ash.close()
oname_phx.close()



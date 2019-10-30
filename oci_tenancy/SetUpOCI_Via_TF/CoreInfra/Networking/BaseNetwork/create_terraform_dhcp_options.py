#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import configparser
import os
import pandas as pd
import glob
import shutil
import datetime

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
parser.add_argument("--dhcp_add", help="Add new dhcp option: true or false", required=False)


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir = args.outdir
prefix=args.prefix
if args.dhcp_add is not None:
    dhcp_add = str(args.dhcp_add)
else:
    dhcp_add = "false"

outfile={}
oname={}
tfStr={}

def processDHCP(region,vcn_name,dhcp_option_name,compartment_var_name,serverType,custom_dns_servers,search_domain):

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
			display_name = \"""" + dhcp_option_name + """"
	}
	"""
	tfStr[region] = tfStr[region] + data


endNames = {'<END>', '<end>'}
if('.xls' in args.inputfile):
	df_vcn = pd.read_excel(args.inputfile, sheet_name='VCNs',skiprows=1)
	df_vcn.dropna(how='all')

	df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
	properties = df_info['Property']
	values = df_info['Value']

	all_regions = str(values[7]).strip()
	all_regions = all_regions.split(",")
	all_regions = [x.strip().lower() for x in all_regions]
	for reg in all_regions:
		tfStr[reg] = ''

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
		region=region.strip().lower()
		if region not in all_regions:
			print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
			exit(1)
		processDHCP(region,vcn_name,dhcp_option_name,compartment_var_name,serverType,custom_dns_servers,search_domain)



elif('.properties' in args.inputfile):
	print("Input is vcn-info.properties")

	config = configparser.RawConfigParser()
	config.optionxform = str
	config.read(args.inputfile)
	#sections=config.sections()

	all_regions = config.get('Default', 'regions')
	all_regions = all_regions.split(",")
	all_regions = [x.strip().lower() for x in all_regions]
	for reg in all_regions:
		tfStr[reg] = ''

	#Get VCN and DHCP file info from VCN_INFO section
	vcns=config.options('VCN_INFO')

	for vcn in vcns:
		vcn_data = config.get('VCN_INFO', vcn)
		vcn_data = vcn_data.split(',')
		vcn_name = vcn
		region=vcn_data[0].strip().lower()
		if region not in all_regions:
			print("Invalid Region")
			exit(1)
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

dhcpdata={}
if(dhcp_add=='true'):
	for reg in all_regions:
		reg_out_dir = outdir + "/" + reg
		if not os.path.exists(reg_out_dir):
			os.makedirs(reg_out_dir)
		outfile[reg] = reg_out_dir + "/" + prefix + '-dhcp.tf'

		x = datetime.datetime.now()
		date = x.strftime("%f").strip()

		if(tfStr[reg]!=''):
			if (os.path.exists(outfile[reg])):
				print("creating backup file " + outfile[reg] + "_backup" + date)
				shutil.copy(outfile[reg], outfile[reg] + "_backup" + date)
			oname[reg] = open(outfile[reg], "w")
			oname[reg].write(tfStr[reg])
			oname[reg].close()
			print(outfile[reg] + " containing TF for DHCP Options has been updated for region " + reg)

elif(dhcp_add == 'false'):
	for reg in all_regions:
		reg_out_dir = outdir + "/" + reg
		if not os.path.exists(reg_out_dir):
			os.makedirs(reg_out_dir)
		outfile[reg] = reg_out_dir + "/" + prefix + '-dhcp.tf'
		if (tfStr[reg] != ''):
			oname[reg] = open(outfile[reg], 'w')
			oname[reg].write(tfStr[reg])
			oname[reg].close()
			print(outfile[reg] + " containing TF for DHCP Options has been created for region " + reg)
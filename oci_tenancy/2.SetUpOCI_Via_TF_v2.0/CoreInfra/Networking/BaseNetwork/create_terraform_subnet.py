#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com

######
# Required Files
# Properties File: vcn-info.properties"
# Code will read input subnet file name for each vcn from properties file
# Subnets file will contain info about each subnet
# Outfile
######

import sys
import re
import os
import argparse
import configparser
import pandas as pd


parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\". "
											 "Create terraform files for subnets.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
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

outfile_ash=ash_dir + "/" + prefix + '-subnets.tf'
outfile_phx=phx_dir + "/" + prefix + '-subnets.tf'

oname_ash = open(outfile_ash,"w")
oname_phx = open(outfile_phx,"w")

fname = None

tempStrASH=""
tempStrPHX=""
tempStr ="""
data "oci_identity_availability_domains" "ADs" {
	  compartment_id = "${var.tenancy_ocid}"
}"""

ADS = ["AD1", "AD2", "AD3"]

def processSubnet(region,vcn_name,name,subnet,AD,dnslabel,pubpvt,compartment_var_name,vcn_add_defaul_seclist,seclists_per_subnet):
	global tempStrASH
	global tempStrPHX

	if (AD.strip().lower() != 'regional'):
		AD = AD.strip().upper()
		ad = ADS.index(AD)
		ad_name_int = ad + 1
		ad_name = str(ad_name_int)
		adString = """availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(
			ad) + """.name}" """
	else:
		ad_name = ""
		adString = """availability_domain = "" """
	subnet_res_name = name
	if (str(ad_name) != ''):
		name1 = name + "-ad" + str(ad_name)
	else:
		name1 = name
	if (subnet_name_attach_cidr == 'y'):
		display_name = name1 + "-" + subnet
	else:
		display_name = name

	# name = name1
	# dnslabel = re.sub('-', '', name)

	data = """
    resource "oci_core_subnet" \"""" + subnet_res_name + """" {
    	compartment_id = "${var.""" + compartment_var_name + """}" 
    	""" + adString + """			
    	route_table_id      = "${oci_core_route_table.""" + name + """.id}"
    	vcn_id = "${oci_core_vcn.""" + str(vcn_name) + """.id}" """

	seclist_ids = ""
	if vcn_add_defaul_seclist == "y":
		seclist_ids = """\"${oci_core_vcn.""" + vcn_name + """.default_security_list_id}","""
	j = 1
	while j < seclists_per_subnet:
		seclist_ids = seclist_ids + """\"${oci_core_security_list.""" + name + "-" + str(j) + """.id}","""
		j = j + 1
	while j <= seclists_per_subnet:
		seclist_ids = seclist_ids + """\"${oci_core_security_list.""" + name + "-" + str(j) + """.id}" """
		j = j + 1
	data = data + """
    	security_list_ids   = [ """ + seclist_ids + """ ]"""
	if (str(dhcp).lower() != 'nan' and str(dhcp)!=''):
		data = data + """
    	dhcp_options_id     = "${oci_core_dhcp_options.""" + str(dhcp).strip() + """.id}" """
	data = data + """
    	display_name               = \"""" + display_name + """"
    	cidr_block                 = \"""" + subnet + """\" """
	if pubpvt.lower() == "public":
		data = data + """
    	prohibit_public_ip_on_vnic = false """
	else:
		data = data + """
    	prohibit_public_ip_on_vnic = true """
	data = data + """
    	dns_label           =  \"""" + dnslabel + """"
    }
    """
	if (region == 'ashburn'):
		tempStrASH = tempStrASH + data
	elif (region == 'phoenix'):
		tempStrPHX = tempStrPHX + data

endNames = {'<END>', '<end>'}
#If input is CD3 excel file
if('.xlsx' in filename):
	NaNstr = 'NaN'
	df_vcn = pd.read_excel(filename, sheet_name='VCNs',skiprows=1)
	df_vcn.dropna(how='all')
	df_vcn.set_index("vcn_name", inplace=True)
	df_vcn.head()
	df = pd.read_excel(filename, sheet_name='Subnets',skiprows=1)
	df.dropna(how='all')

	df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)

	# Get Property Values
	properties = df_info['Property']
	values = df_info['Value']

	subnet_name_attach_cidr = str(values[4]).strip()
	if (subnet_name_attach_cidr.lower() == NaNstr.lower()):
		subnet_name_attach_cidr = 'n'

	for i in df.index:
		#Get VCN data
		compartment_var_name = df.iat[i, 0]
		if (compartment_var_name in endNames):
			break
		vcn_name=df['vcn_name'][i]
		vcn_data = df_vcn.loc[vcn_name]
		region=vcn_data['Region']
		region=region.strip().lower()
		sps=vcn_data['sec_list_per_subnet']
		seclists_per_subnet = int(sps)
		vcn_add_defaul_seclist=vcn_data['add_default_seclist']
		#Get subnet data
		name = df.iat[i, 2]
		name=name.strip()
		subnet = df.iat[i, 3]
		subnet=subnet.strip()
		AD = df.iat[i, 4]
		AD=AD.strip()
		pubpvt = df.iat[i, 5]
		pubpvt=pubpvt.strip()
		dhcp=df.iat[i,6]

		if(str(dhcp).lower() !='nan'):
			dhcp = vcn_name + "_" + dhcp
		compartment_var_name=compartment_var_name.strip()

		dnslabel = df.iat[i, 10]
		# check if subnet_dns_label is not given by user in input use subnet name
		if (str(dnslabel).lower() == NaNstr.lower()):
			regex = re.compile('[^a-zA-Z0-9]')
			subnet_dns = regex.sub('', name)
			dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns

		processSubnet(region,vcn_name,name,subnet,AD,dnslabel,pubpvt,compartment_var_name,vcn_add_defaul_seclist,seclists_per_subnet)

# If CD3 excel file is not given as input
elif('.csv' in filename):
	config = configparser.RawConfigParser()
	config.optionxform = str
	config.read(args.propsfile)
	sections=config.sections()

	#Get Global Properties from Default Section
	subnet_name_attach_cidr = config.get('Default','subnet_name_attach_cidr')

	#Get vcn and subnet file info from VCN_INFO section
	vcns=config.options('VCN_INFO')
	for vcn_name in vcns:
		vcn_data = config.get('VCN_INFO', vcn_name)
		vcn_data = vcn_data.split(',')

		region=vcn_data[0].strip.lower()
		sps = vcn_data[9].strip().lower()
		vcn_add_defaul_seclist = vcn_data[11].strip().lower()
		vcn_subnet_file = vcn_data[7].strip().lower()
		if os.path.isfile(vcn_subnet_file) == False:
			print("input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping Subnet TF creation for this VCN.")
			continue

		fname = open(vcn_subnet_file,"r")
		seclists_per_subnet = int(sps)

		# Read subnet file
		for line in fname:
			if not line.startswith('#') and line !='\n':
				[compartment_var_name,name, sub, AD, pubpvt, dhcp, SGW, NGW, IGW,dnslabel] = line.split(',')
				linearr = line.split(",")
				compartment_var_name = linearr[0].strip()
				name = linearr[1].strip()
				subnet = linearr[2].strip()
				dnslabel = linearr[9].strip()

				if(dhcp!=''):
					dhcp=vcn_name+"_"+dhcp

				# check if vcn_dns_label is not given by user in input use vcn name
				if (dnslabel == ''):
					regex = re.compile('[^a-zA-Z0-9]')
					subnet_dns = regex.sub('', name)
					dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns

					processSubnet(region, vcn_name, name, subnet, AD, dnslabel, pubpvt, compartment_var_name,vcn_add_defaul_seclist, seclists_per_subnet)
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

tempStrASH=tempStr+tempStrASH
tempStrPHX=tempStr+tempStrPHX

if fname != None:
	fname.close()
oname_ash.write(tempStrASH)
oname_phx.write(tempStrPHX)
oname_ash.close()
oname_phx.close()


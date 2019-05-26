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
parser.add_argument("propsfile", help="Full Path of properties file. eg vcn-info.properties in example folder")
parser.add_argument("outfile",help="Output Filename")
parser.add_argument("--omcs",help="If the File is of OMCS format: \"prod-dmz-lb-ext2-10.89.69.0/24,AD2\"",action="store_true")
parser.add_argument("--inputCD3", help="input CD3 excel file", required=False)


if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
outfile = args.outfile
oname = open(outfile,"w")
fname = None

excel=''
if(args.inputCD3 is not None):
    excel=args.inputCD3

config = configparser.RawConfigParser()
config.optionxform = str
config.read(args.propsfile)
sections=config.sections()

#Get Global Properties from Default Section
subnet_name_attach_cidr = config.get('Default','subnet_name_attach_cidr')

tempStr = ""
tempStr = tempStr + """
data "oci_identity_availability_domains" "ADs" {
	  compartment_id = "${var.tenancy_ocid}"
}"""
ADS = ["AD1", "AD2", "AD3"]

# If CD3 excel file is given as input
if(excel!=''):
	df_vcn = pd.read_excel(excel, sheet_name='VCNs')
	df_vcn.set_index("vcn_name", inplace=True)
	df_vcn.head()
	df = pd.read_excel(excel, sheet_name='Subnets')
	for i in df.index:
		#Get VCN data
		vcn_name=df['vcn_name'][i]
		vcn_data = df_vcn.loc[vcn_name]
		sps=vcn_data['sec_list_per_subnet']
		seclists_per_subnet = int(sps)
		vcn_add_defaul_seclist=vcn_data['add_default_seclist']
		#Get subnet data
		name = df.iat[i, 2]
		subnet = df.iat[i, 3]
		AD = df.iat[i, 4]
		pubpvt = df.iat[i, 5]
		dhcp=df.iat[i,6]
		if(str(dhcp) !='nan'):
			dhcp = vcn_name + "_" + dhcp
		compartment_var_name = df.iat[i,0]


		if (AD.strip() != 'Regional'):
			ad = ADS.index(AD)
			ad_name_int = ad + 1
			ad_name = str(ad_name_int)
			adString = """availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}" """
		else:
			ad_name = ""
			adString = """availability_domain = "" """
		subnet_res_name=name
		name1 = name + ad_name
		if (subnet_name_attach_cidr == 'y'):
			display_name = name1 + "-" + subnet
		else:
			display_name = name

		name = name1
		dnslabel = re.sub('-', '', name)
		tempStr = tempStr + """
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
		tempStr = tempStr + """
	security_list_ids   = [ """ + seclist_ids + """ ]"""
		if (str(dhcp) != 'nan'):
			tempStr=tempStr+ """
	dhcp_options_id     = "${oci_core_dhcp_options.""" + dhcp.strip() + """.id}" """
		tempStr=tempStr+ """
	display_name               = \"""" + display_name + """"
	cidr_block                 = \"""" + subnet + """\" """
		if pubpvt.lower() == "public":
			tempStr = tempStr + """
	prohibit_public_ip_on_vnic = false """
		else:
			tempStr = tempStr + """
	prohibit_public_ip_on_vnic = true """
		tempStr = tempStr + """
	dns_label           =  \"""" + dnslabel + """"
}
"""
# If CD3 excel file is not given as input
else:
	#Get vcn and subnet file info from VCN_INFO section
	vcns=config.options('VCN_INFO')
	for vcn_name in vcns:
		vcn_data = config.get('VCN_INFO', vcn_name)
		vcn_data = vcn_data.split(',')


		sps = vcn_data[8].strip().lower()
		vcn_add_defaul_seclist = vcn_data[10].strip().lower()
		vcn_subnet_file = vcn_data[6].strip().lower()
		if os.path.isfile(vcn_subnet_file) == False:
			print("input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping Subnet TF creation for this VCN.")
			continue

		fname = open(vcn_subnet_file,"r")
		seclists_per_subnet = int(sps)

		# Read subnet file
		for line in fname:
			if not line.startswith('#') and line !='\n':
				if args.omcs:

					name_sub, AD, pubpvt, dhcp = line.split(',')
					subnet = name_sub.rsplit("-", 1)[1].strip()
					name = name_sub.rsplit("-", 1)[0].strip()

				else:
					[compartment_var_name,name, sub, AD, pubpvt, dhcp, SGW, NGW, IGW] = line.split(',')
					linearr = line.split(",")
					compartment_var_name = linearr[0].strip()
					name = linearr[1].strip()
					subnet = linearr[2].strip()

				if(dhcp!=''):
					dhcp=vcn_name+"_"+dhcp

				if(AD.strip()!='Regional'):
					ad = ADS.index(AD)
					ad_name_int = ad + 1
					ad_name=str(ad_name_int)
					adString="""availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}" """
				else:
					ad_name=""
					adString="""availability_domain = "" """

				subnet_res_name=name
				name1 = name + ad_name
				if (subnet_name_attach_cidr == 'y'):
					display_name = name1 + "-" + subnet
				else:
					display_name = name

				dnslabel = re.sub('-','',name)

				name=name1
				tempStr = tempStr+"""
resource "oci_core_subnet" \"""" + subnet_res_name + """" {
	compartment_id = "${var.""" + compartment_var_name + """}" 
	"""+adString+"""			
	route_table_id      = "${oci_core_route_table.""" + name + """.id}"
	vcn_id = "${oci_core_vcn.""" + str(vcn_name) + """.id}" """
		
				seclist_ids = ""
				if vcn_add_defaul_seclist == "y" :
					seclist_ids = """\"${oci_core_vcn.""" + vcn_name + """.default_security_list_id}","""
				i = 1
				while i < seclists_per_subnet :
					seclist_ids  = seclist_ids + """\"${oci_core_security_list.""" + name + "-" + str(i) + """.id}","""
					i = i + 1
				while i <= seclists_per_subnet :
					seclist_ids  = seclist_ids + """\"${oci_core_security_list.""" + name + "-" + str(i) + """.id}" """
					i = i + 1
				tempStr = tempStr + """
	security_list_ids   = [ """ + seclist_ids + """ ] """
				if (dhcp != ''):
					tempStr=tempStr + """
	dhcp_options_id     = "${oci_core_dhcp_options.""" + dhcp.strip() + """.id}" """
				tempStr = tempStr + """
	display_name               = \"""" + display_name + """"
	cidr_block                 = \"""" + subnet + """\" """
				if pubpvt.lower() == "public":
					tempStr = tempStr + """
	prohibit_public_ip_on_vnic = false """
				else:
					tempStr = tempStr + """
	prohibit_public_ip_on_vnic = true """
				tempStr = tempStr + """
	dns_label           =  \"""" + dnslabel + """"
}

"""
oname.write(tempStr)

if fname != None:
	fname.close()
oname.close()


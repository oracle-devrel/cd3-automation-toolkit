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
parser.add_argument("outfile",help="Output Filename")


if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outfile = args.outfile
oname = open(outfile,"w")
fname = None

tempStr = ""
tempStr = tempStr + """
data "oci_identity_availability_domains" "ADs" {
	  compartment_id = "${var.tenancy_ocid}"
}"""
ADS = ["AD1", "AD2", "AD3"]

#If input is CD3 excel file
if('.xlsx' in filename):
	NaNstr = 'NaN'
	df_vcn = pd.read_excel(filename, sheet_name='VCNs',skiprows=1)
	df_vcn.set_index("vcn_name", inplace=True)
	df_vcn.head()
	df = pd.read_excel(filename, sheet_name='Subnets',skiprows=1)

	df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)

	# Get Property Values
	properties = df_info['Property']
	values = df_info['Value']

	subnet_name_attach_cidr = str(values[4]).strip()
	if (subnet_name_attach_cidr.lower() == NaNstr.lower()):
		subnet_name_attach_cidr = 'n'

	for i in df.index:
		#Get VCN data
		vcn_name=df['vcn_name'][i]
		vcn_data = df_vcn.loc[vcn_name]
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

		if(str(dhcp) !='nan'):
			dhcp = vcn_name + "_" + dhcp
		compartment_var_name = df.iat[i,0]
		compartment_var_name=compartment_var_name.strip()

		if (AD.strip() != 'Regional' and  AD.strip() != 'regional'):
			ad = ADS.index(AD)
			ad_name_int = ad + 1
			ad_name = str(ad_name_int)
			adString = """availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}" """
		else:
			ad_name = ""
			adString = """availability_domain = "" """
		subnet_res_name=name
		if (str(ad_name) != ''):
			name1 = name + "-ad" + str(ad_name)
		else:
			name1 = name
		if (subnet_name_attach_cidr == 'y'):
			display_name = name1 + "-" + subnet
		else:
			display_name = name

		#name = name1
		#dnslabel = re.sub('-', '', name)

		dnslabel = df.iat[i, 10]
		# check if subnet_dns_label is not given by user in input use subnet name
		if (str(dnslabel).lower() == NaNstr.lower()):
			regex = re.compile('[^a-zA-Z0-9]')
			subnet_dns = regex.sub('', name)
			dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns


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
					[compartment_var_name,name, sub, AD, pubpvt, dhcp, SGW, NGW, IGW,dnslabel] = line.split(',')
					linearr = line.split(",")
					compartment_var_name = linearr[0].strip()
					name = linearr[1].strip()
					subnet = linearr[2].strip()
					dnslabel = linearr[9].strip()

				if(dhcp!=''):
					dhcp=vcn_name+"_"+dhcp

				if(AD.strip()!='Regional' and  AD.strip() != 'regional'):
					ad = ADS.index(AD)
					ad_name_int = ad + 1
					ad_name=str(ad_name_int)
					adString="""availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}" """
				else:
					ad_name=""
					adString="""availability_domain = "" """

				subnet_res_name=name
				if (str(ad_name) != ''):
					name1 = name + "-ad" + str(ad_name)
				else:
					name1 = name
				if (subnet_name_attach_cidr == 'y'):
					display_name = name1 + "-" + subnet
				else:
					display_name = name

				#dnslabel = re.sub('-','',name)

				# check if vcn_dns_label is not given by user in input use vcn name
				if (dnslabel == ''):
					regex = re.compile('[^a-zA-Z0-9]')
					subnet_dns = regex.sub('', name)
					dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns


				#name=name1
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
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

oname.write(tempStr)

if fname != None:
	fname.close()
oname.close()


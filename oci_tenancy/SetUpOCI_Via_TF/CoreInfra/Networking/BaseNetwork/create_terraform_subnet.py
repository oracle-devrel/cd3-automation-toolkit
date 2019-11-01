#!/usr/bin/python3
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
import glob
import shutil
import datetime


parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\". "
											 "Create terraform files for subnets.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--subnet_add", help="Add new subnet: true or false", required=False)


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir = args.outdir
prefix=args.prefix
if args.subnet_add is not None:
    subnet_add = str(args.subnet_add)
else:
    subnet_add = "false"


fname = None
outfile={}
oname={}
tfStr={}

tempStr ="""
data "oci_identity_availability_domains" "ADs" {
	  compartment_id = "${var.tenancy_ocid}"
}"""

ADS = ["AD1", "AD2", "AD3"]

def processSubnet(region,vcn_name,name,rt_name,seclist_name,common_seclist_name,subnet,AD,dnslabel,pubpvt,compartment_var_name,vcn_add_defaul_seclist,seclists_per_subnet):
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


	data = """
    resource "oci_core_subnet" \"""" + subnet_res_name + """" {
    	compartment_id = "${var.""" + compartment_var_name + """}" 
    	""" + adString + """			
    	vcn_id = "${oci_core_vcn.""" + str(vcn_name) + """.id}" """

	if(rt_name==''):
		rt=name
	else:
		rt=rt_name
	data = data + """
		route_table_id   = "${oci_core_route_table.""" + rt + """.id}" """

	if(seclist_name==''):
		sec_name=name
	else:
		sec_name=seclist_name

	seclist_ids = ""
	#Attach Default Secuoity List
	if vcn_add_defaul_seclist == "y":
		seclist_ids = """\"${oci_core_vcn.""" + vcn_name + """.default_security_list_id}","""

	#Attach common Security List
	if (str(common_seclist_name).lower() != 'nan' and str(common_seclist_name)!=''):
		seclist_ids = seclist_ids + """\"${oci_core_security_list.""" + common_seclist_name.strip() + """.id}","""

	#Attach individual Security lists
	j = 1
	while j < seclists_per_subnet:
		seclist_ids = seclist_ids + """\"${oci_core_security_list.""" + sec_name + "-" + str(j) + """.id}","""
		j = j + 1
	while j <= seclists_per_subnet:
		seclist_ids = seclist_ids + """\"${oci_core_security_list.""" + sec_name + "-" + str(j) + """.id}" """
		j = j + 1
	data = data + """
    	security_list_ids   = [ """ + seclist_ids + """ ]"""

	if (str(dhcp).lower() != 'nan' and str(dhcp)!=''):
		data = data + """
    	dhcp_options_id     = "${oci_core_dhcp_options.""" + str(dhcp).strip() + """.id}" """
	else:
		data = data + """
		dhcp_options_id = "${oci_core_vcn.""" + vcn_name + """.default_dhcp_options_id}" """
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
	tfStr[region]=tfStr[region]+data

endNames = {'<END>', '<end>','<End>'}
#If input is CD3 excel file
if('.xls' in filename):
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

	all_regions = str(values[7]).strip()
	all_regions = all_regions.split(",")
	all_regions = [x.strip().lower() for x in all_regions]
	for reg in all_regions:
		tfStr[reg] = ''

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
		if region not in all_regions:
			print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
			exit(1)

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
		rt_name=df.iat[i,7]
		seclist_name=df.iat[i,8]
		common_seclist_name = df.iat[i, 9]

		if(str(dhcp).lower() !='nan'):
			dhcp = vcn_name + "_" + dhcp

		compartment_var_name=compartment_var_name.strip()

		dnslabel = df.iat[i, 13]
		# check if subnet_dns_label is not given by user in input use subnet name
		if (str(dnslabel).lower() == NaNstr.lower()):
			regex = re.compile('[^a-zA-Z0-9]')
			subnet_dns = regex.sub('', name)
			dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns

		if (str(rt_name).lower() != 'nan'):
			rt_name = rt_name.strip()
		else:
			rt_name = ''

		if (str(seclist_name).lower() != 'nan'):
			seclist_name = seclist_name.strip()
		else:
			seclist_name = ''

		processSubnet(region,vcn_name,name,rt_name,seclist_name,common_seclist_name,subnet,AD,dnslabel,pubpvt,compartment_var_name,vcn_add_defaul_seclist,seclists_per_subnet)

# If CD3 excel file is not given as input
elif('.properties' in filename):
	config = configparser.RawConfigParser()
	config.optionxform = str
	config.read(args.inputfile)
	sections=config.sections()

	#Get Global Properties from Default Section
	all_regions = config.get('Default', 'regions')
	all_regions = all_regions.split(",")
	all_regions = [x.strip().lower() for x in all_regions]
	for reg in all_regions:
		tfStr[reg] = ''

	subnet_name_attach_cidr = config.get('Default','subnet_name_attach_cidr')

	#Get vcn and subnet file info from VCN_INFO section
	vcns=config.options('VCN_INFO')
	for vcn_name in vcns:
		vcn_data = config.get('VCN_INFO', vcn_name)
		vcn_data = vcn_data.split(',')

		region=vcn_data[0].strip().lower()
		if region not in all_regions:
			print("Invalid Region")
			exit(1)
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
				[compartment_var_name,name, sub, AD, pubpvt, dhcp, rt_name,seclist_name,common_seclist_name,SGW, NGW, IGW,dnslabel] = line.split(',')
				linearr = line.split(",")
				compartment_var_name = linearr[0].strip()
				name = linearr[1].strip()
				subnet = linearr[2].strip()
				#dnslabel = linearr[9].strip()

				if(dhcp!=''):
					dhcp=vcn_name+"_"+dhcp

				# check if vcn_dns_label is not given by user in input use vcn name
				if (dnslabel.strip() == ''):
					regex = re.compile('[^a-zA-Z0-9]')
					subnet_dns = regex.sub('', name)
					dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns

					processSubnet(region, vcn_name, name, rt_name.strip(),seclist_name.strip(),common_seclist_name.strip(),subnet, AD, dnslabel, pubpvt, compartment_var_name,vcn_add_defaul_seclist, seclists_per_subnet)
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit()


if fname != None:
	fname.close()

subnetdata={}
if(subnet_add=='true'):
	for reg in all_regions:
		reg_out_dir = outdir + "/" + reg
		if not os.path.exists(reg_out_dir):
			os.makedirs(reg_out_dir)
		outfile[reg] = reg_out_dir + "/" + prefix + '-subnets.tf'

		x = datetime.datetime.now()
		date = x.strftime("%f").strip()

		if (tfStr[reg] != ''):
			with open(outfile[reg], 'r') as file:
				subnetdata[reg] = file.read()
			file.close()
			if(tfStr[reg] not in subnetdata[reg]):
				shutil.copy(outfile[reg], outfile[reg] + "_backup" + date)
				oname[reg] = open(outfile[reg], "a")
				oname[reg].write(tfStr[reg])
				oname[reg].close()
				print(outfile[reg] + " containing TF for Subnets has been updated for region " + reg)

elif(subnet_add == 'false'):
	for reg in all_regions:
		reg_out_dir = outdir + "/" + reg
		if not os.path.exists(reg_out_dir):
			os.makedirs(reg_out_dir)
		outfile[reg] = reg_out_dir + "/" + prefix + '-subnets.tf'
		if (tfStr[reg] != ''):
			oname[reg] = open(outfile[reg], 'w')
			tfStr[reg]=tfStr[reg]+tempStr
			oname[reg].write(tfStr[reg])
			oname[reg].close()
			print(outfile[reg] + " containing TF for Subnets has been created for region " + reg)


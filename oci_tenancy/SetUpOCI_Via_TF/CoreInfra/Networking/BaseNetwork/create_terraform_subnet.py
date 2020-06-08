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
import argparse
import configparser
import pandas as pd
import shutil
import datetime
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\". "
											 "Create terraform files for subnets.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--modify_network", help="modify network: true or false", required=False)


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir = args.outdir
prefix=args.prefix
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"


fname = None
outfile={}
oname={}
tfStr={}

ADS = ["AD1", "AD2", "AD3"]

def processSubnet(region,vcn_name,name,rt_name,seclist_names,subnet,AD,dnslabel,pubpvt,compartment_var_name,add_defaul_seclist):
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

	vcn_tf_name = commonTools.check_tf_variable(vcn_name)

	if (vcnInfo.subnet_name_attach_cidr == 'y'):
		if (str(ad_name) != ''):
			name1 = name + "-ad" + str(ad_name)
			namert = rt_name + "-ad" + str(ad_name)
		else:
			name1 = name
			namert = rt_name

		display_name = name1 + "-" + subnet
		rt_display_name=namert+ "-" + subnet

	else:
		display_name = name
		rt_display_name=rt_name

	sl_tf_names=[]
	if (vcnInfo.subnet_name_attach_cidr == 'y'):
		for sl_name in seclist_names:
			sl_name=sl_name.strip()
			if (str(ad_name) != ''):
				namesl = sl_name + "-ad" + str(ad_name)
			else:
				namesl = sl_name
			sl_display_name = namesl + "-" + subnet
			sl_tf_name=vcn_name+"_"+sl_display_name
			sl_tf_names.append(commonTools.check_tf_variable(sl_tf_name))
	else:
		for sl_name in seclist_names:
			sl_name=sl_name.strip()
			sl_display_name=sl_name
			sl_tf_name = vcn_name + "_" + sl_display_name
			sl_tf_names.append(commonTools.check_tf_variable(sl_tf_name))

	subnet_tf_name=vcn_name+"_"+display_name
	subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)
	rt_tf_name = vcn_name+"_"+rt_display_name
	rt_tf_name = commonTools.check_tf_variable(rt_tf_name)

	data = """
    resource "oci_core_subnet"  \"""" + subnet_tf_name + """" {
    	compartment_id = "${var.""" + compartment_var_name + """}" 
    	""" + adString + """			
    	vcn_id = "${oci_core_vcn.""" + str(vcn_tf_name) + """.id}" """

	if(rt_name!="n"):
		data = data + """
		route_table_id   = "${oci_core_route_table.""" + rt_tf_name + """.id}" """

	seclist_ids=""
	#Attach Default Security List
	if add_defaul_seclist.strip() == "y":
		seclist_ids =  """\"${oci_core_vcn.""" + vcn_tf_name + """.default_security_list_id}","""
	#Attach other security list IDs
	if(seclist_names[0]!="n"):
		index=0
		for seclist_id in sl_tf_names:
			if(index==len(sl_tf_names)):
				seclist_ids = seclist_ids + """\"${oci_core_security_list.""" +  seclist_id  + """.id}" """
			else:
				seclist_ids = seclist_ids + """\"${oci_core_security_list.""" +  seclist_id + """.id}", """
			index=index+1

		data = data + """
			security_list_ids   = [ """ + seclist_ids + """ ]"""

	if (str(dhcp).lower() != 'nan' and str(dhcp)!=''):
		data = data + """
    	dhcp_options_id     = "${oci_core_dhcp_options.""" + str(dhcp).strip() + """.id}" """
	else:
		data = data + """
		dhcp_options_id = "${oci_core_vcn.""" + vcn_tf_name + """.default_dhcp_options_id}" """
	data = data + """
    	display_name               = \"""" + display_name + """"
    	cidr_block                 = \"""" + subnet + """\" """
	if pubpvt.lower() == "public":
		data = data + """
    	prohibit_public_ip_on_vnic = false """
	else:
		data = data + """
    	prohibit_public_ip_on_vnic = true """
	if(dnslabel.lower()!="n"):
		data = data + """
    	dns_label           =  \"""" + dnslabel + """"
    """
	data=data+"""
    }
    """
	tfStr[region]=tfStr[region]+data

#If input is CD3 excel file
if('.xls' in filename):
	vcnInfo = parseVCNInfo(filename)
	vcns = parseVCNs(filename)

	df = pd.read_excel(filename, sheet_name='Subnets',skiprows=1)
	df = df.dropna(how='all')
	df = df.reset_index(drop=True)

	for reg in vcnInfo.all_regions:
		tfStr[reg] = ''


	for i in df.index:
		region=df.iat[i,0]
		if (region in commonTools.endNames):
			break

		compartment_var_name = df.iat[i, 1]
		vcn_name=str(df['vcn_name'][i]).strip()
		if (vcn_name.strip() not in vcns.vcn_names):
			print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
			exit(1)

		region=region.strip().lower()
		if region not in vcnInfo.all_regions:
			print("\nERROR!!! Invalid Region; It should be one of the values mentioned in VCN Info tab..Exiting!")
			exit(1)


		#Get subnet data
		name = df.iat[i, 3]
		name=name.strip()
		subnet = df.iat[i, 4]
		subnet=subnet.strip()
		AD = df.iat[i, 5]
		AD=AD.strip()
		pubpvt = df.iat[i, 6]
		pubpvt=pubpvt.strip()
		dhcp=df.iat[i,7]
		rt_name=df.iat[i,8]
		seclist_names=df.iat[i,9]
		add_default_seclist = df.iat[i, 10]

		if(str(add_default_seclist).lower()=='nan'):
			add_default_seclist='y'

		if(str(dhcp).lower() !='nan'):
			dhcp = vcn_name + "_" + dhcp
			dhcp = commonTools.check_tf_variable(dhcp)

		compartment_var_name=compartment_var_name.strip()
		# Added to check if compartment name is compatible with TF variable name syntax
		compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

		dnslabel = df.iat[i, 16]
		# check if subnet_dns_label is not given by user in input use subnet name
		if (str(dnslabel).lower() == 'nan'):
			regex = re.compile('[^a-zA-Z0-9]')
			subnet_dns = regex.sub('', name)
			# truncate all digits from start of dns_label
			index = 0
			for c in subnet_dns:
				if c.isdigit() == True:
					index = index + 1
					continue
				else:
					break
			subnet_dns = subnet_dns[index:]
			dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns

		if (str(rt_name).lower() != 'nan'):
			rt_name = rt_name.strip()
		else:
			# route table name not provided; use subnet name as route table name
			rt_name = name
		sl_names = []
		if (str(seclist_names).lower() != 'nan'):
			sl_names = seclist_names.split(",")
		else:
			# seclist name not provided; use subnet name as seclist name
			sl_names.append(name)

		processSubnet(region,vcn_name,name,rt_name,sl_names,subnet,AD,dnslabel,pubpvt,compartment_var_name,add_default_seclist)

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
if(modify_network=='true'):
	for reg in vcnInfo.all_regions:
		reg_out_dir = outdir + "/" + reg
		if not os.path.exists(reg_out_dir):
			os.makedirs(reg_out_dir)
		outfile[reg] = reg_out_dir + "/" + prefix + '-subnets.tf'

		x = datetime.datetime.now()
		date = x.strftime("%f").strip()
		if(os.path.exists(outfile[reg])):
			print("creating backup file " + outfile[reg] + "_backup" + date)
			shutil.copy(outfile[reg], outfile[reg] + "_backup" + date)
		oname[reg] = open(outfile[reg], "w")
		oname[reg].write(tfStr[reg])
		oname[reg].close()
		print(outfile[reg] + " containing TF for Subnets has been updated for region " + reg)

elif(modify_network == 'false'):
	for reg in vcnInfo.all_regions:
		reg_out_dir = outdir + "/" + reg
		if not os.path.exists(reg_out_dir):
			os.makedirs(reg_out_dir)
		outfile[reg] = reg_out_dir + "/" + prefix + '-subnets.tf'
		if (tfStr[reg] != ''):
			oname[reg] = open(outfile[reg], 'w')
			tfStr[reg]=tfStr[reg]
			oname[reg].write(tfStr[reg])
			oname[reg].close()
			print(outfile[reg] + " containing TF for Subnets has been created for region " + reg)


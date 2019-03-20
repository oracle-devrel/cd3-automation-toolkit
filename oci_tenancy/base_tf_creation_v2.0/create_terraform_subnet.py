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


parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\". "
											 "Create terraform files for subnets.")
parser.add_argument("propsfile", help="Full Path of properties file. eg vcn-info.properties in example folder")
parser.add_argument("outfile",help="Output Filename")
parser.add_argument("--omcs",help="If the File is of OMCS format: \"prod-dmz-lb-ext2-10.89.69.0/24,AD2\"",action="store_true")

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

config = configparser.RawConfigParser()
config.optionxform = str
config.read(args.propsfile)
sections=config.sections()

#Get Global Properties from Default Section
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')


tempStr = ""
tempStr = tempStr + """
data "oci_identity_availability_domains" "ADs" {
	  compartment_id = "${var.tenancy_ocid}"
}"""
ADS = ["AD1", "AD2", "AD3"]

#Get vcn and subnet file info from VCN_INFO section
vcns=config.options('VCN_INFO')
for vcn_name in vcns:
	vcn_data = config.get('VCN_INFO', vcn_name)
	vcn_data = vcn_data.split(',')

	vcn_cidr = vcn_data[0].strip().lower()
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
		if not line.startswith('#'):
			if args.omcs:

				name_sub, AD, pubpvt, dhcp = line.split(',')
				subnet = name_sub.rsplit("-", 1)[1].strip()
				name = name_sub.rsplit("-", 1)[0].strip()

			else:

				[name, sub, AD, pubpvt, dhcp, SGW, NGW, IGW] = line.split(',')
				linearr = line.split(",")
				name = linearr[0].strip()
				subnet = linearr[1].strip()

			dhcp=vcn_name+"_"+dhcp

			if(AD.strip()!='Regional'):
				ad = ADS.index(AD)
				ad_name_int = ad + 1
				ad_name=str(ad_name_int)
				adString="""availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}" """
			else:
				ad_name=""
				adString="""availability_domain = "" """

			name = name + ad_name
			display_name = name +  "-" + subnet
			dnslabel = re.sub('-','',name)


			tempStr = tempStr+"""
resource "oci_core_subnet" \"""" + name + """" {
	compartment_id = "${var.""" + ntk_comp_var + """}" 
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
	security_list_ids   = [ """ + seclist_ids + """ ] 
	dhcp_options_id     = "${oci_core_dhcp_options.""" + dhcp.strip() + """.id}"
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


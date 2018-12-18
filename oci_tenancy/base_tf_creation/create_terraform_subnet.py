#!/bin/python
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com

######
# Required Files
# Properties File: oci-tf.properties"
# Code will read input subnet file name from properties file
# Subnets file will contain info about each subnet
# Outfile
######

import sys
import re

import argparse
import ConfigParser


parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\".  Create terraform files for subnets.")
parser.add_argument("propsfile", help="Full Path of properties file. eg oci-tf.properties in example folder")
parser.add_argument("outfile",help="Output Filename")
parser.add_argument("--omcs",help="If the File is of OMCS format: \"prod-dmz-lb-ext2-10.89.69.0/24,AD2\"",action="store_true")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

config = ConfigParser.RawConfigParser()
config.read(args.propsfile)

subnet_file = config.get('Default','subnet_file')
outfile = args.outfile

fname = open(subnet_file,"r")
oname = open(outfile,"w")

vcn_var = config.get('Default','vcn_var')
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')
vcn_add = config.get('Default','add_vcn_to_all_sec_lists')

sps = config.get('Default','sec_list_per_subnet')
seclists_per_subnet = int(sps)

tempStr = """
data "oci_identity_availability_domains" "ADs" {
  compartment_id = "${var.""" + comp_var + """}"
}

"""
oname.write(tempStr)

tempStr = ""
ADS = ["AD1","AD2","AD3"]

# Read subnet file
for line in fname:
	if not line.startswith('#') :
                if args.omcs :

			name_sub,AD,pubpvt,dhcp = line.split(',')
                        # line = line.split(",",1)[0]
                        subnet = name_sub.rsplit("-",1)[1].strip()
                        name = name_sub.rsplit("-",1)[0].strip()

                else :

			[name,sub,AD,pubpvt,dhcp,SGW,NGW,IGW] = line.split(',')
                        linearr = line.split(",")
                        name = linearr[0].strip()
                        subnet = linearr[1].strip()


		ad = ADS.index(AD)
		ad_name = ad + 1
		name = name + str(ad_name)
                display_name = name +  "-" + subnet
		dnslabel = re.sub('-','',name)

		tempStr = """
resource "oci_core_subnet" \"""" + name + """" {
	compartment_id = "${var.""" + ntk_comp_var + """}"
	availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
	route_table_id      = "${oci_core_route_table.""" + name + """.id}"
	vcn_id = "${oci_core_vcn.""" + str(vcn_var) + """.id}" """
		
		seclist_ids = ""
		if vcn_add == "true" :
			seclist_ids = """\"${oci_core_vcn.""" + vcn_var + """.default_security_list_id}","""	
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


fname.close()
oname.close()


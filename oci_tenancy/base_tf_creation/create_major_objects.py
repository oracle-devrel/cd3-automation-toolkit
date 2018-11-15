#!/bin/python

#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import os
import argparse
import ConfigParser
######
# Required Files
# "oci-tf.properties"
# Create the major terraform objects - DRG, VCN & IGW for the VCN 
# Outfile
######


parser = argparse.ArgumentParser(description="Create major-objects (VCN, IGW for the VCN & DRG ) terraform file")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

if not os.path.exists('oci-tf.properties'):
	print "Cant find the file 'oci-tf.properties.\nMake sure to create the file and try again."
	exit(-1)


config = ConfigParser.RawConfigParser()
config.read('oci-tf.properties')

outfile = args.outfile

# print "filename = " + filename + " routefiles  = " + routesfile + " outfile = " + outfile 

oname = open(outfile,"w")


####
#ntk_comp_var=ntk_compartment_ocid
#comp_var=compartment_ocid
#vcn_var=vcn01
#####

ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')

vcn_var = config.get('Default','vcn_var').strip()
vcn_display_name = config.get('Default','vcn_display_name').strip()
vcn_cidr = config.get('Default','vcn_cidr').strip()
vcn_dns_label = config.get('Default','vcn_dns_label').strip()


drg_var = config.get('Default','drg_var').strip()
drg_display_name = config.get('Default','drg_display_name').strip()

igw_var = config.get('Default','igw_var').strip()
igw_display_name = config.get('Default','igw_display_name').strip()

lpg_var = config.get('Default','lpg_var').strip()
lpg_display_name = config.get('Default','lpg_display_name').strip()
lpg_ocs_ocid = config.get('Default','lpg_ocs_ocid').strip()

sgw_var = config.get('Default','sgw_var').strip()
sgw_display_name = config.get('Default','sgw_display_name').strip()

ngw_var = config.get('Default','ngw_var').strip()
ngw_display_name = config.get('Default','ngw_display_name').strip()



tempStr = """
resource "oci_core_vcn" \"""" + vcn_var + """" {
	cidr_block = \"""" + vcn_cidr + """"
	compartment_id = "${var.""" + ntk_comp_var + """}"

	display_name = \"""" + vcn_display_name + """"
	dns_label = \"""" + vcn_dns_label + """"
}

resource "oci_core_internet_gateway" \"""" + igw_var + """" {
	compartment_id = "${var.""" + ntk_comp_var + """}"
	display_name = \"""" + igw_display_name + """"
	vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
}

resource "oci_core_drg" \"""" + drg_var + """" {
	compartment_id = "${var.""" + ntk_comp_var + """}"
        #Optional
	display_name = \"""" + drg_display_name + """"
}

resource "oci_core_local_peering_gateway"  \"""" + lpg_var + """" {
        #Required
        display_name = \"""" + lpg_display_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
        peer_id = \"""" + lpg_ocs_ocid + """" 
}

data "oci_core_services" "oci_services" {
}
resource "oci_core_service_gateway"  \"""" + sgw_var + """" {
        services {
        #Required
        service_id = "${data.oci_core_services.oci_services.services.0.id}"
        }
        display_name = \"""" + sgw_display_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
}

resource "oci_core_nat_gateway" \"""" + ngw_var + """" {
        display_name = \"""" + ngw_display_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
}




"""
oname.write(tempStr)
oname.close()


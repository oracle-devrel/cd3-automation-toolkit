#!/bin/python

#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import csv
import argparse
import re
import configparser

######
# Required Files
# "csv file- vcn-info.properties"
# Create the major terraform objects - DRG, IGW, NGW, SGW, LPGs for the VCN
# Outfile
######

parser = argparse.ArgumentParser(description="Create major-objects (VCN, IGW, NGW, DRG, LPGs etc for the VCN) terraform file")
parser.add_argument("propsfile", help="Full Path of props file. eg vcn-info.properties in example folder ")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
outfile = args.outfile
oname = open(outfile,"w")

config = configparser.RawConfigParser()
config.optionxform = str
file_read=config.read(args.propsfile)

if(len(file_read)!=1):
        print(args.propsfile +" doesn't not exist or it could not be opened. Please check input params and try again..")
        exit(1)
sections=config.sections()

#Get Global Properties from Default Section
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')

tempStr = ""
tempStr = tempStr + """
data "oci_core_services" "oci_services" {
}"""

#Get VCN Info from VCN_INFO section
vcns=config.options('VCN_INFO')

#Create VCN transit routing mapping based on Hub-Spoke
vcn_transit_route_mapping=dict()
hub_vcn_name=''
for vcn_name in vcns:
    vcn_data = config.get('VCN_INFO', vcn_name)
    vcn_data = vcn_data.split(',')
    hub_spoke_none = vcn_data[5].strip().lower()
    if(hub_spoke_none=='hub'):
        vcn_transit_route_mapping.setdefault(vcn_name,[])
        hub_vcn_name=vcn_name

for vcn_name in vcns:
    vcn_data = config.get('VCN_INFO', vcn_name)
    vcn_data = vcn_data.split(',')
    hub_spoke_none = vcn_data[5].strip().lower()
    if(hub_spoke_none=='spoke'):
        vcn_transit_route_mapping[hub_vcn_name].append(vcn_name)

hub_count=0
for vcn_name in vcns:
        vcn_data=config.get('VCN_INFO',vcn_name)
        vcn_data=vcn_data.split(',')

        vcn_cidr=vcn_data[0].strip().lower()
        regex = re.compile('[^a-zA-Z0-9]')
        vcn_dns_label = regex.sub('', vcn_name)
        vcn_drg=vcn_data[1].strip().lower()
        vcn_igw = vcn_data[2].strip().lower()
        vcn_ngw = vcn_data[3].strip().lower()
        vcn_sgw = vcn_data[4].strip().lower()
        hub_spoke_none = vcn_data[5].strip().lower()

        if(hub_spoke_none=='hub' and vcn_drg!='y'):
                print("VCN marked as Hub should have DRG configured..Modify the input file and try again")
                exit(1)
        if(hub_spoke_none=='hub'):
                hub_count=hub_count+1
        if(hub_count>1):
                print("Ideally there should be only one Hub VCN in a region. Modify the input file and try again")
                exit(1)

        tempStr = tempStr + """
resource "oci_core_vcn" \"""" + vcn_name + """" {
	cidr_block = \"""" + vcn_cidr + """"
	compartment_id = "${var.""" + ntk_comp_var + """}"
	display_name = \"""" + vcn_name + """"
	dns_label = \"""" + vcn_dns_label + """"
}
"""
        if vcn_igw == "y":
                igw_name=vcn_name+"_igw"
                tempStr = tempStr + """
resource "oci_core_internet_gateway" \"""" + igw_name + """" {
	    compartment_id = "${var.""" + ntk_comp_var + """}"
	    display_name = \"""" + igw_name + """"
	    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
}
"""

        if vcn_drg == "y":
                drg_name=vcn_name+"_drg"
                rt_var=drg_name+"_rt"
                tempStr = tempStr + """
resource "oci_core_drg" \"""" + drg_name + """" {
        compartment_id = "${var.""" + ntk_comp_var + """}"
        display_name = \"""" + drg_name + """"
}
resource "oci_core_drg_attachment" "drg_attachment" {
        drg_id = "${oci_core_drg.""" + drg_name + """.id}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
"""
                if(hub_spoke_none=='hub'):
                    tempStr=tempStr+"""
        route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
}
"""
                else:
                        tempStr=tempStr+"""
}"""
        if vcn_sgw == "y":
                sgw_name = vcn_name + "_sgw"
                tempStr = tempStr + """
resource "oci_core_service_gateway"  \"""" + sgw_name + """" {
        services {
        service_id = "${data.oci_core_services.oci_services.services.0.id}"
        }
        display_name = \"""" + sgw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
}
"""
        if vcn_ngw == 'y':
                ngw_name = vcn_name + "_ngw"
                tempStr = tempStr + """
resource "oci_core_nat_gateway" \"""" + ngw_name + """" {
        display_name = \"""" + ngw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
}
"""
#Create LPGs as per Section VCN_PEERING
peering_dict = dict(config.items('VCN_PEERING'))
ocs_vcn_lpg_ocids=peering_dict['ocs_vcn_lpg_ocid']
ocs_vcn_lpg_ocids=ocs_vcn_lpg_ocids.split(",")
peering_dict.pop('ocs_vcn_lpg_ocid')
peering_dict.pop('ocs_vcn_cidr')
peering_dict.pop('add_sec_rules_ping')

for left_vcn,value in peering_dict.items():
        right_vcns=value.split(",")
        for right_vcn in right_vcns:
                #Create LPG for VCN on left and peer with OCS VCN
                if(right_vcn=='ocs_vcn'):
                        lpg_name = left_vcn + "_ocs_lpg"
                        tempStr = tempStr + """
resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
        display_name = \"""" + lpg_name + """"
        vcn_id = "${oci_core_vcn.""" + left_vcn + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
"""
                        if(ocs_vcn_lpg_ocids[0]!=''):
                                tempStr=tempStr+"""
        peer_id = \"""" + ocs_vcn_lpg_ocids[0] + """"
}
"""
                                ocs_vcn_lpg_ocids.pop(0)
                        else:
                                tempStr=tempStr+"""
}
"""
                else:
                        #create LPG for VCNs on right
                        lpg_name=right_vcn+"_"+left_vcn+"_lpg"
                        tempStr = tempStr + """
resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
        display_name = \"""" + lpg_name + """"
        vcn_id = "${oci_core_vcn.""" + right_vcn + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
"""
                        if(right_vcn==hub_vcn_name and left_vcn in vcn_transit_route_mapping[hub_vcn_name]):
                                rt_var=lpg_name+"_rt"
                                tempStr=tempStr+"""
        route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
}
"""
                        else:
                                tempStr=tempStr+"""
}
"""
                        #create LPG for VCN on left corresponding to above and establish peering
                        lpg_name=left_vcn+"_"+right_vcn+"_lpg"
                        peer_lpg_name=right_vcn+"_"+left_vcn+"_lpg"
                        tempStr = tempStr + """
resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
        display_name = \"""" + lpg_name+ """"
        vcn_id = "${oci_core_vcn.""" + left_vcn + """.id}"
        compartment_id = "${var.""" + ntk_comp_var + """}"
        peer_id = "${oci_core_local_peering_gateway.""" + peer_lpg_name + """.id}"
"""
                        if (left_vcn == hub_vcn_name and right_vcn in vcn_transit_route_mapping[hub_vcn_name]):
                                rt_var = lpg_name + "_rt"
                                tempStr = tempStr + """
        route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
}
                        """
                        else:
                                tempStr = tempStr + """
}
"""
oname.write(tempStr)
oname.close()


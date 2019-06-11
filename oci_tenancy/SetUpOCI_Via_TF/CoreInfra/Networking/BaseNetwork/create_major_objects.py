#!/bin/python

#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import re
import configparser
import pandas as pd

######
# Required Files
# "csv file- vcn-info.properties"
# Create the major terraform objects - DRG, IGW, NGW, SGW, LPGs for the VCN
# Optional input - CD3 excel file
# Outfile
######

parser = argparse.ArgumentParser(description="Create major-objects (VCN, IGW, NGW, DRG, LPGs etc for the VCN) terraform file")
parser.add_argument("propsfile", help="Full Path of props file. eg vcn-info.properties in example folder ")
parser.add_argument("outfile",help="Output Filename")
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

excel=''
if(args.inputCD3 is not None):
    excel=args.inputCD3


config = configparser.RawConfigParser()
config.optionxform = str
file_read=config.read(args.propsfile)

if(len(file_read)!=1):
        print(args.propsfile +" doesn't not exist or it could not be opened. Please check input params and try again..")
        exit(1)
sections=config.sections()

#Get Global Properties from Default Section
drg_ocid = config.get('Default','drg_ocid')

tempStr = ""
tempStr = tempStr + """
data "oci_core_services" "oci_services" {
}"""

# Create VCN transit routing mapping based on Hub-Spoke
vcn_transit_route_mapping=dict()
vcn_compartment={}
hub_vcn_name=''

# If CD3 exceel file is given as input
if(excel!=''):
        NaNstr = 'NaN'
        df = pd.read_excel(excel, sheet_name='VCNs')

        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        vcns = df['vcn_name']

        for i in df.index:
                vcn_name=df['vcn_name'][i]

                # Cheeck to see if vcn_name is empty in Subnets Sheet
                if (str(vcn_name).lower() == NaNstr.lower()):
                        print("vcn_name cannot be left empty in VCNs sheet in CD3..exiting...")
                        exit()


                hub_spoke_none=df['hub_spoke_none'][i]
                if (hub_spoke_none == 'hub'):
                        vcn_transit_route_mapping.setdefault(vcn_name, [])
                        hub_vcn_name = vcn_name
        for i in df.index:
                vcn_name=df['vcn_name'][i]
                hub_spoke_none=df['hub_spoke_none'][i]
                if (hub_spoke_none == 'spoke'):
                        vcn_transit_route_mapping[hub_vcn_name].append(vcn_name)

# If CD3 excel file is not given as input
else:
        # Get VCN Info from VCN_INFO section
        vcns = config.options('VCN_INFO')

        for vcn_name in vcns:
                vcn_data = config.get('VCN_INFO', vcn_name)
                vcn_data = vcn_data.split(',')
                hub_spoke_none = vcn_data[5].strip().lower()
                if (hub_spoke_none == 'hub'):
                        vcn_transit_route_mapping.setdefault(vcn_name, [])
                        hub_vcn_name = vcn_name
        for vcn_name in vcns:
            vcn_data = config.get('VCN_INFO', vcn_name)
            vcn_data = vcn_data.split(',')
            hub_spoke_none = vcn_data[5].strip().lower()
            if(hub_spoke_none=='spoke'):
                vcn_transit_route_mapping[hub_vcn_name].append(vcn_name)


#Iterate over all VCNs
hub_count=0

# If CD3 excel file is given as input
if(excel!=''):
        NaNstr = 'NaN'
        for i in df.index:
                vcn_name = df['vcn_name'][i]
                regex = re.compile('[^a-zA-Z0-9]')
                vcn_dns_label = regex.sub('', vcn_name)
                vcn_cidr = df['vcn_cidr'][i]
                vcn_drg = df['drg_required(y|n)'][i]
                vcn_igw = df['igw_required(y|n)'][i]
                vcn_ngw = df['ngw_required(y|n)'][i]
                vcn_sgw = df['sgw_required(y|n)'][i]
                hub_spoke_none = df['hub_spoke_none'][i]
                sec_list_per_subnet = df['sec_list_per_subnet'][i]
                sec_rule_per_seclist = df['sec_rule_per_seclist'][i]
                add_default_seclist = df['add_default_seclist'][i]
                compartment_var_name = df['compartment_name'][i]
                vcn_compartment[vcn_name]=compartment_var_name

                # Check to see if any column is empty in Subnets Sheet
                if (str(vcn_name).lower() == NaNstr.lower() or str(vcn_cidr).lower() == NaNstr.lower() or
                        str(vcn_drg).lower() == NaNstr.lower() or str(vcn_igw).lower() == NaNstr.lower()
                        or str(vcn_ngw).lower() == NaNstr.lower() or str(vcn_sgw).lower() == NaNstr.lower()
                        or str(hub_spoke_none).lower() == NaNstr.lower() or str(sec_list_per_subnet).lower() == NaNstr.lower()
                        or str(sec_rule_per_seclist).lower() == NaNstr.lower() or str(add_default_seclist).lower() == NaNstr.lower()
                        or str(compartment_var_name).lower() == NaNstr.lower()):
                        print("Column Values or Rows cannot be left empty in VCNs sheet in CD3..exiting...")
                        exit()

                if (hub_spoke_none == 'hub' and vcn_drg != 'y'):
                        print("VCN marked as Hub should have DRG configured..Modify the input file and try again")
                        exit(1)
                if (hub_spoke_none == 'hub'):
                        hub_count = hub_count + 1
                if (hub_count > 1):
                        print("Ideally there should be only one Hub VCN in a region. Modify the input file and try again")
                        exit(1)

                tempStr = tempStr + """
resource "oci_core_vcn" \"""" + vcn_name + """" {
        cidr_block = \"""" + vcn_cidr + """"
        compartment_id = "${var.""" + compartment_var_name + """}"
        display_name = \"""" + vcn_name + """"
        dns_label = \"""" + vcn_dns_label + """"
}
"""
                if vcn_igw == "y":
                        igw_name = vcn_name + "_igw"
                        tempStr = tempStr + """
resource "oci_core_internet_gateway" \"""" + igw_name + """" {
        compartment_id = "${var.""" + compartment_var_name + """}"
        display_name = \"""" + igw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
}
"""

                if vcn_drg == "y":
                        drg_name = vcn_name + "_drg"
                        drg_display = "DRG"
                        rt_var = drg_name + "_rt"

                        # Create new DRG
                        if (drg_ocid == ''):
                                tempStr = tempStr + """
resource "oci_core_drg" \"""" + drg_name + """" {
        compartment_id = "${var.""" + compartment_var_name + """}"
        display_name = \"""" + drg_display + """"
}
resource "oci_core_drg_attachment" "drg_attachment" {
        drg_id = "${oci_core_drg.""" + drg_name + """.id}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
"""
                        # Use existing DRG
                        if (drg_ocid != ''):
                                tempStr = tempStr + """
resource "oci_core_drg_attachment" "drg_attachment" {
        drg_id = \"""" + drg_ocid + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
"""
                        if (hub_spoke_none == 'hub'):
                                tempStr = tempStr + """
        route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
}
                """
                        else:
                                tempStr = tempStr + """
}"""
                if vcn_sgw == "y":
                        sgw_name = vcn_name + "_sgw"
                        tempStr = tempStr + """
resource "oci_core_service_gateway"  \"""" + sgw_name + """" {
        services {
        service_id = "${data.oci_core_services.oci_services.services.1.id}"
        }
        display_name = \"""" + sgw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        compartment_id = "${var.""" + compartment_var_name + """}"
}
"""
                if vcn_ngw == 'y':
                        ngw_name = vcn_name + "_ngw"
                        tempStr = tempStr + """
resource "oci_core_nat_gateway" \"""" + ngw_name + """" {
        display_name = \"""" + ngw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        compartment_id = "${var.""" + compartment_var_name + """}"
}
"""

# If CD3 excel file is not given as input
else:
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
                compartment_var_name = vcn_data[11].strip()
                vcn_compartment[vcn_name]=compartment_var_name


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
	compartment_id = "${var.""" + compartment_var_name + """}"
	display_name = \"""" + vcn_name + """"
	dns_label = \"""" + vcn_dns_label + """"
}
"""
                if vcn_igw == "y":
                        igw_name=vcn_name+"_igw"
                        tempStr = tempStr + """
resource "oci_core_internet_gateway" \"""" + igw_name + """" {
        compartment_id = "${var.""" + compartment_var_name + """}"
        display_name = \"""" + igw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
}
"""

                if vcn_drg == "y":
                        drg_name=vcn_name+"_drg"
                        drg_display="DRG"
                        rt_var=drg_name+"_rt"

                        #Create new DRG
                        if(drg_ocid==''):
                                tempStr = tempStr + """
resource "oci_core_drg" \"""" + drg_name + """" {
        compartment_id = "${var.""" + compartment_var_name + """}"
        display_name = \"""" + drg_display + """"
}
resource "oci_core_drg_attachment" "drg_attachment" {
        drg_id = "${oci_core_drg.""" + drg_name + """.id}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
"""
                        #Use existing DRG
                        if(drg_ocid!=''):
                                tempStr=tempStr+"""
resource "oci_core_drg_attachment" "drg_attachment" {
        drg_id = \"""" + drg_ocid + """"
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
        compartment_id = "${var.""" + compartment_var_name + """}"
}
"""
                if vcn_ngw == 'y':
                        ngw_name = vcn_name + "_ngw"
                        tempStr = tempStr + """
resource "oci_core_nat_gateway" \"""" + ngw_name + """" {
        display_name = \"""" + ngw_name + """"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        compartment_id = "${var.""" + compartment_var_name + """}"
}
"""
#Create LPGs as per Section VCN_PEERING
peering_dict = dict(config.items('VCN_PEERING'))
ocs_vcn_lpg_ocids=peering_dict['ocs_vcn_lpg_ocid']
ocs_vcn_lpg_ocids=ocs_vcn_lpg_ocids.split(",")
peering_dict.pop('ocs_vcn_lpg_ocid')
peering_dict.pop('ocs_vcn_cidr')
peering_dict.pop('add_ping_sec_rules_onprem')
peering_dict.pop('add_ping_sec_rules_vcnpeering')

for left_vcn,value in peering_dict.items():
        right_vcns=value.split(",")
        for right_vcn in right_vcns:
                #Create LPG for VCN on left and peer with OCS VCN
                if(right_vcn=='ocs_vcn'):
                        lpg_name = left_vcn + "_ocs_lpg"
                        compartment_var_name=vcn_compartment[left_vcn]
                        tempStr = tempStr + """
resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
        display_name = \"""" + lpg_name + """"
        vcn_id = "${oci_core_vcn.""" + left_vcn + """.id}"
        compartment_id = "${var.""" + compartment_var_name + """}"
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
                        compartment_var_name=vcn_compartment[right_vcn]
                        tempStr = tempStr + """
resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
        display_name = \"""" + lpg_name + """"
        vcn_id = "${oci_core_vcn.""" + right_vcn + """.id}"
        compartment_id = "${var.""" + compartment_var_name + """}"
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
                        compartment_var_name=vcn_compartment[left_vcn]
                        tempStr = tempStr + """
resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
        display_name = \"""" + lpg_name+ """"
        vcn_id = "${oci_core_vcn.""" + left_vcn + """.id}"
        compartment_id = "${var.""" + compartment_var_name + """}"
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


#!/usr/bin/python3

#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import re
import configparser
import os
import pandas as pd

######
# Required Files
# input file containing VCN info either vcn-info.properties or CD3 excel
# Create the major terraform objects - DRG, IGW, NGW, SGW, LPGs for the VCN
# Outdir
# prefix
######

parser = argparse.ArgumentParser(description="Create major-objects (VCN, IGW, NGW, DRG, LPGs etc for the VCN) terraform file")
parser.add_argument("inputfile",help="Full Path of input file either props file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.inputfile
outdir = args.outdir
prefix = args.prefix

outfile = {}
oname = {}
tfStr = {}
oname_def_dhcp = {}

# Create VCN transit routing mapping based on Hub-Spoke
# vcn_transit_route_mapping=dict()
peering_dict = dict()
vcn_compartment = {}
vcn_region = {}
hub_vcn_names = []
spoke_vcn_names = []

datastr = """
data "oci_core_services" "oci_services" {
}"""

endNames = {'<END>', '<end>','<End>'}

def createLPGs(peering_dict):
    for left_vcn, value in peering_dict.items():
        region = vcn_region[left_vcn]
        data = ""
        right_vcns = value.split(",")
        for right_vcn in right_vcns:
            # Create LPG for VCN on left and peer with OCS VCN
            if (right_vcn == 'ocs_vcn'):
                lpg_name = left_vcn + "_ocs_lpg"
                compartment_var_name = vcn_compartment[left_vcn]
                data = """
    resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
            display_name = \"""" + lpg_name + """"
            vcn_id = "${oci_core_vcn.""" + left_vcn + """.id}"
            compartment_id = "${var.""" + compartment_var_name + """}"
    """
                if (ocs_vcn_lpg_ocids[0] != ''):
                    data = data + """
            peer_id = \"""" + ocs_vcn_lpg_ocids[0] + """"
    }
    """
                    ocs_vcn_lpg_ocids.pop(0)
                else:
                    data = data + """
    }
    """
            else:
                # create LPG for VCNs on right
                lpg_name = right_vcn + "_" + left_vcn + "_lpg"
                compartment_var_name = vcn_compartment[right_vcn]
                data = data + """
    resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
            display_name = \"""" + lpg_name + """"
            vcn_id = "${oci_core_vcn.""" + right_vcn + """.id}"
            compartment_id = "${var.""" + compartment_var_name + """}"
    """
                if (right_vcn in hub_vcn_names and left_vcn in spoke_vcn_names):
                    rt_var = lpg_name + "_rt"
                    data = data + """
                                        route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
                                }
                                """
                else:
                    data = data + """
}
"""

                # create LPG for VCN on left corresponding to above and establish peering
                lpg_name = left_vcn + "_" + right_vcn + "_lpg"
                peer_lpg_name = right_vcn + "_" + left_vcn + "_lpg"
                compartment_var_name = vcn_compartment[left_vcn]
                data = data + """
    resource "oci_core_local_peering_gateway"  \"""" + lpg_name + """" {
            display_name = \"""" + lpg_name + """"
            vcn_id = "${oci_core_vcn.""" + left_vcn + """.id}"
            compartment_id = "${var.""" + compartment_var_name + """}"
            peer_id = "${oci_core_local_peering_gateway.""" + peer_lpg_name + """.id}"
    """
                if (left_vcn in hub_vcn_names and right_vcn in spoke_vcn_names):
                    rt_var = lpg_name + "_rt"
                    data = data + """
            route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
    }
                            """
                else:
                    data = data + """
    }
    """
        tfStr[region] = tfStr[region] + data


def processVCN(region, vcn_name, vcn_cidr, vcn_drg, vcn_igw, vcn_ngw, vcn_sgw, hub_spoke_none, compartment_var_name,
               vcn_dns_label):

    region = region.lower().strip()
    vcn_name = vcn_name.strip()
    vcn_cidr = vcn_cidr.strip()
    vcn_drg = vcn_drg.strip()
    vcn_igw = vcn_igw.strip()
    vcn_ngw = vcn_ngw.strip()
    vcn_sgw = vcn_sgw.strip()
    hub_spoke_none = hub_spoke_none.strip()
    compartment_var_name = compartment_var_name.strip()
    vcn_dns_label = vcn_dns_label.strip()

    #Create TF object for default DHCP options

    dhcp_data= """
    resource "oci_core_default_dhcp_options" "default-dhcp-options_""" + vcn_name + """" {
        manage_default_resource_id  = "${oci_core_vcn.""" + vcn_name + """.default_dhcp_options_id}"
        options {
            type = "DomainNameServer"
            server_type = "VcnLocalPlusInternet"
        }
    }
    """
    oname_def_dhcp[region].write(dhcp_data)

    #Wite major objects data
    data = """
          resource "oci_core_vcn" \"""" + vcn_name + """" {
                    cidr_block = \"""" + vcn_cidr + """"
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    display_name = \"""" + vcn_name + """"
                    dns_label = \"""" + vcn_dns_label + """"
            }
            """
    if vcn_igw != "n":
        # use default name
        if (vcn_igw == "y"):
            igw_name = vcn_name + "_igw"
        # use name provided in input
        else:
            igw_name = vcn_igw
        data = data + """
            resource "oci_core_internet_gateway" \"""" + igw_name + """" {
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    display_name = \"""" + igw_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            }
            """

    if vcn_drg != "n":
        # use default name
        if (vcn_drg == "y"):
            drg_attach_name = vcn_name + "_drg_attach"
            drg_name = vcn_name + "_drg"
            drg_display = vcn_name + "_drg"
        # use name provided in input
        else:
            drg_attach_name = vcn_drg + "_attach"
            drg_name = vcn_drg
            drg_display = vcn_drg

        rt_var = drg_name + "_rt"

        # Create new DRG
        if (drg_ocid == ''):
            data = data + """
            resource "oci_core_drg" \"""" + drg_name + """" {
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    display_name = \"""" + drg_display + """"
            }
            resource "oci_core_drg_attachment" \"""" + drg_attach_name + """" {
                    drg_id = "${oci_core_drg.""" + drg_name + """.id}"
                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            """
        # Use existing DRG
        if (drg_ocid != ''):
            data = data + """
            resource "oci_core_drg_attachment" \"""" + drg_attach_name + """" {
                    drg_id = \"""" + drg_ocid + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            """
        if (hub_spoke_none == 'hub'):
            data = data + """
                    route_table_id = "${oci_core_route_table.""" + rt_var + """.id}"
            }
                            """
        else:
            data = data + """
            }"""
    if vcn_sgw != "n":
        # use default name
        if (vcn_sgw == "y"):
            sgw_name = vcn_name + "_sgw"
        # use name provided in input
        else:
            sgw_name = vcn_sgw

        data = data + """
            resource "oci_core_service_gateway"  \"""" + sgw_name + """" {
                    services {
                    service_id = "${data.oci_core_services.oci_services.services.0.id}"
                    }
                    display_name = \"""" + sgw_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
                    compartment_id = "${var.""" + compartment_var_name + """}"
            }
            """
    if vcn_ngw != 'n':
        # use default name
        if (vcn_ngw == "y"):
            ngw_name = vcn_name + "_ngw"
        # use name provided in input
        else:
            ngw_name = vcn_ngw

        data = data + """
            resource "oci_core_nat_gateway" \"""" + ngw_name + """" {
                    display_name = \"""" + ngw_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
                    compartment_id = "${var.""" + compartment_var_name + """}"
            }
            """
    tfStr[region] = tfStr[region] + data


# If input is CD3 excel file
if ('.xls' in filename):
    NaNstr = 'NaN'
    df = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    df.dropna(how='all')
    df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)

    # Get Property Values

    properties = df_info['Property']
    values = df_info['Value']

    drg_ocid = str(values[1]).strip()

    if (drg_ocid.lower() == NaNstr.lower()):
        drg_ocid = ''

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    for reg in all_regions:
        tfStr[reg] = ''
        oname_def_dhcp[reg] = open(outdir + "/" + reg + "/VCNs_Default_DHCP.tf", "w")

    # Get VCN Peering info in dict
    for j in df_info.index:
        if (j > 8):
            peering_dict[properties[j]] = values[j]

    # Get Hub and Spoke VCN Names
    for i in df.index:

        region = df['Region'][i]

        if (region in endNames):
            break
        region = region.strip().lower()
        if region not in all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)
        vcn_name = df['vcn_name'][i]

        # Check to see if vcn_name is empty in Subnets Sheet
        if (str(vcn_name).lower() == NaNstr.lower()):
            print("vcn_name/row cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        hub_spoke_none = df['hub_spoke_none'][i]
        if (hub_spoke_none == 'hub'):
            hub_vcn_names.append(vcn_name)
        if (hub_spoke_none == 'spoke'):
            spoke_vcn_names.append(vcn_name)

    # Process VCNs
    NaNstr = 'NaN'
    for i in df.index:
        region = df['Region'][i]
        if (region in endNames):
            break
        region = region.strip().lower()

        vcn_name = df['vcn_name'][i]
        vcn_cidr = df['vcn_cidr'][i]
        vcn_drg = df['drg_required'][i]
        vcn_igw = df['igw_required'][i]
        vcn_ngw = df['ngw_required'][i]
        vcn_sgw = df['sgw_required'][i]
        hub_spoke_none = df['hub_spoke_none'][i]
        sec_list_per_subnet = df['sec_list_per_subnet'][i]
        sec_rule_per_seclist = df['sec_rule_per_seclist'][i]
        add_default_seclist = df['add_default_seclist'][i]
        compartment_var_name = df['compartment_name'][i]
        vcn_compartment[vcn_name] = compartment_var_name
        vcn_region[vcn_name] = region

        vcn_dns_label = df['dns_label'][i]
        # check if vcn_dns_label is not given by user in input use vcn name
        if (str(vcn_dns_label).lower() == NaNstr.lower()):
            regex = re.compile('[^a-zA-Z0-9]')
            vcn_dns = regex.sub('', vcn_name)
            vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns
        # Check to see if any column is empty in Subnets Sheet
        if (str(vcn_name).lower() == NaNstr.lower() or str(vcn_cidr).lower() == NaNstr.lower() or
                str(vcn_drg).lower() == NaNstr.lower() or str(vcn_igw).lower() == NaNstr.lower()
                or str(vcn_ngw).lower() == NaNstr.lower() or str(vcn_sgw).lower() == NaNstr.lower()
                or str(hub_spoke_none).lower() == NaNstr.lower() or str(sec_list_per_subnet).lower() == NaNstr.lower()
                or str(sec_rule_per_seclist).lower() == NaNstr.lower() or str(add_default_seclist).lower() == NaNstr.lower()
                or str(compartment_var_name).lower() == NaNstr.lower()):
            print("Column Values(except dns_label) or Rows cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        processVCN(region, vcn_name, vcn_cidr, vcn_drg, vcn_igw, vcn_ngw, vcn_sgw, hub_spoke_none, compartment_var_name,vcn_dns_label)

    createLPGs(peering_dict)

# If CD3 excel file is not given as input
elif ('.properties' in filename):
    config = configparser.RawConfigParser()
    config.optionxform = str
    file_read = config.read(args.inputfile)

    if (len(file_read) != 1):
        print(
                    args.propsfile + " doesn't not exist or it could not be opened. Please check input params and try again..")
        exit(1)
    sections = config.sections()

    # Get Global Properties from Default Section
    drg_ocid = config.get('Default', 'drg_ocid')
    all_regions = config.get('Default', 'regions')
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    for reg in all_regions:
        tfStr[reg] = ''

    # Get VCN Info from VCN_INFO section
    vcns = config.options('VCN_INFO')

    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        region = vcn_data[0].strip().lower()
        if region not in all_regions:
            print("Invalid Region")
            exit(1)
        hub_spoke_none = vcn_data[5].strip().lower()
        if (hub_spoke_none == 'hub'):
            hub_vcn_names.append(vcn_name)
        if (hub_spoke_none == 'spoke'):
            spoke_vcn_names.append(vcn_name)

    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        region = vcn_data[0].strip().lower()
        vcn_cidr = vcn_data[1].strip().lower()
        regex = re.compile('[^a-zA-Z0-9]')
        vcn_dns_label = regex.sub('', vcn_name)
        vcn_drg = vcn_data[2].strip().lower()
        vcn_igw = vcn_data[3].strip().lower()
        vcn_ngw = vcn_data[4].strip().lower()
        vcn_sgw = vcn_data[5].strip().lower()
        hub_spoke_none = vcn_data[6].strip().lower()
        compartment_var_name = vcn_data[12].strip()
        vcn_compartment[vcn_name] = compartment_var_name
        vcn_region[vcn_name] = region

        vcn_dns_label = vcn_data[13].strip()
        # check if vcn_dns_label is not given by user in input use vcn name
        if (vcn_dns_label == ''):
            regex = re.compile('[^a-zA-Z0-9]')
            vcn_dns = regex.sub('', vcn_name)
            vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns

        # if(hub_spoke_none=='hub' and vcn_drg!='y'):
        #        print("\nVCN marked as Hub should have DRG configured..Modify the input file and try again")
        #        exit(1)

        processVCN(region, vcn_name, vcn_cidr, vcn_drg, vcn_igw, vcn_ngw, vcn_sgw, hub_spoke_none,
                   compartment_var_name, vcn_dns_label)

    # Create LPGs as per Section VCN_PEERING
    peering_dict = dict(config.items('VCN_PEERING'))
    ocs_vcn_lpg_ocids = peering_dict['ocs_vcn_lpg_ocid']
    ocs_vcn_lpg_ocids = ocs_vcn_lpg_ocids.split(",")
    peering_dict.pop('ocs_vcn_lpg_ocid')
    peering_dict.pop('ocs_vcn_cidr')
    peering_dict.pop('add_ping_sec_rules_onprem')
    peering_dict.pop('add_ping_sec_rules_vcnpeering')

    createLPGs(peering_dict)
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit(1)

for reg in all_regions:
    oname_def_dhcp[reg].close()
    print("VCNs_Default_DHCP.tf containing TF for default DHCP options for VCNs has been created for region " + reg)
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
    if (tfStr[reg] != ''):
        tfStr[reg] = tfStr[reg] + datastr
        oname[reg] = open(outfile[reg], 'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for VCN major objects has been created for region " + reg)

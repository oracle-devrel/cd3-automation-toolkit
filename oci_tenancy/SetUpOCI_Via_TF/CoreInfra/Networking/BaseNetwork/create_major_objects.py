#!/usr/bin/python3

#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import re
import configparser
import pandas as pd
import datetime
import shutil
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

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
parser.add_argument("--modify_network", help="modify network: true or false", required=False)
parser.add_argument("--nongf_tenancy", help="non greenfield tenancy: true or false", required=False)

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.inputfile
outdir = args.outdir
prefix = args.prefix
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"
nongf_tenancy = args.nongf_tenancy


outfile = {}
oname = {}
tfStr = {}
dhcpStr = {}
outfile_dhcp = {}
oname_def_dhcp = {}
oname_datafile = {}

global dhcp_data
dhcp_data = ""


datastr = """
data "oci_core_services" "oci_services" {
}
data "oci_identity_availability_domains" "ADs" {
	  compartment_id = "${var.tenancy_ocid}"
}"""



def establishPeering(peering_dict):
    for left_vcn, value in peering_dict.items():
        region = vcns.vcn_region[left_vcn]
        outfile = outdir + "/" + region + "/" + prefix + '-major-objs.tf'

        right_vcns = value.split(",")

        for right_vcn in right_vcns:
            right_vcn=right_vcn.strip()
            right_vcn_tf_name = commonTools.tfname.sub("-", right_vcn)

            try:
                if(vcns.vcn_lpg_names[left_vcn][0].lower()=='n' or vcns.vcn_lpg_names[right_vcn][0].lower()=='n'):
                    print("\nERROR!!! Cannot specify n for lpg_required field of VCN if it is part of VCN peering..Exiting!")
                    exit(1)
            except IndexError:
                print("\nERROR!!! Insufficient LPGs declared for either "+left_vcn + " or "+right_vcn + ". Check lpg_required column in VCNs tab..Exiting!")
                exit(1)
            searchString = """##peer_id for lpg """ + left_vcn+"_"+vcns.vcn_lpg_names[left_vcn][0]+"##"
            vcns.vcn_lpg_names[left_vcn].pop(0)
            lpg_name=vcns.vcn_lpg_names[right_vcn][0]
            lpg_tf_name = commonTools.tfname.sub("-", lpg_name)

            peerStr = """peer_id = "${oci_core_local_peering_gateway.""" + right_vcn_tf_name+"_"+lpg_tf_name + """.id}" """
            vcns.vcn_lpg_names[right_vcn].pop(0)

            # Update file contents
            with open(outfile) as f:
                data = f.read()
            f.close()
            updated_data = re.sub(searchString, peerStr, data)
            with open(outfile, 'w') as f:
                f.write(updated_data)
            f.close()
    #print("VCN Peering Done")


def processVCN(region, vcn_name, vcn_cidr, vcn_drg, vcn_igw, vcn_ngw, vcn_sgw, vcn_lpg, hub_spoke_none, compartment_var_name,
               vcn_dns_label,dhcp_data):
    region = region.lower().strip()
    vcn_name = vcn_name.strip()
    vcn_tf_name=commonTools.tfname.sub("-",vcn_name)
    vcn_cidr = vcn_cidr.strip()
    vcn_drg = vcn_drg.strip()
    vcn_igw = vcn_igw.strip()
    vcn_ngw = vcn_ngw.strip()
    vcn_sgw = vcn_sgw.strip()
    vcn_lpg = vcn_lpg.strip()
    hub_spoke_none = hub_spoke_none.strip()
    compartment_var_name = compartment_var_name.strip()
    vcn_dns_label = vcn_dns_label.strip()

    #Create TF object for default DHCP options
    dhcpname= vcn_name+"_Default DHCP Options for "+vcn_name
    dhcp_tf_name = commonTools.tfname.sub("-", dhcpname)

    dhcp_data = dhcp_data + """
    resource "oci_core_default_dhcp_options" \"""" + dhcp_tf_name + """" {
        manage_default_resource_id  = "${oci_core_vcn.""" + vcn_tf_name + """.default_dhcp_options_id}"
        options {
            type = "DomainNameServer"
            server_type = "VcnLocalPlusInternet"
        }
    }
    """

    #Wite major objects data
    data = """
          resource "oci_core_vcn" \"""" + vcn_tf_name + """" {
                    cidr_block = \"""" + vcn_cidr + """"
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    display_name = \"""" + vcn_name + """"
            """
    if(vcn_dns_label.lower()!="n"):
        data=data+ """
                    dns_label = \"""" + vcn_dns_label + """"
        """
    data=data+"""
        }
        """
    if vcn_igw != "n":
        # use default name
        if (vcn_igw == "y"):
            igw_name = vcn_name + "_igw"
        # use name provided in input
        else:
            igw_name = vcn_igw
        igw_tf_name = commonTools.tfname.sub("-", igw_name)

        data = data + """
            resource "oci_core_internet_gateway" \"""" + vcn_tf_name+"_"+igw_tf_name + """" {
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    display_name = \"""" + igw_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
            }
            """

    if vcn_drg != "n":
        # use default name
        if (vcn_drg == "y"):
            drg_name = vcn_name + "_drg"
            drg_display = vcn_name + "_drg"
        # use name provided in input
        else:
            drg_name = vcn_drg
            drg_display = vcn_drg
        drg_tf_name = commonTools.tfname.sub("-", drg_name)

        drg_rt_name=""
        #if(nongf_tenancy=="true"):
        if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
            with open(outdir + "/" + region + "/obj_names.safe") as f:
                for line in f:
                    if("drginfo::::"+vcn_name+"::::"+drg_display in line):
                        drg_rt_name = line.split("::::")[3].strip()
                        break
        if(drg_rt_name==""):
            #rt_var = vcn_name+"_"+drg_name + "_rt"
            rt_var =vcn_name+"_Route Table associated with DRG-"+drg_name
        else:
            rt_var = vcn_name + "_" + drg_rt_name

        drg_attach_name = ""
        #if (nongf_tenancy == "true"):
        if(os.path.exists(outdir + "/" + region + "/obj_names.safe")):
            with open(outdir + "/" + region + "/obj_names.safe") as f:
                for line in f:
                    if ("drgattachinfo::::" + vcn_name + "::::" + drg_display in line):
                        drg_attach_name = line.split("::::")[3].strip()
                        break
        if (drg_attach_name == ""):
            # rt_var = vcn_name+"_"+drg_name + "_rt"
            drg_attach_name = drg_name + "_attach"

        drg_attach_tf_name = commonTools.tfname.sub("-", drg_attach_name)
        rt_tf_name = commonTools.tfname.sub("-", rt_var)
        # Create new DRG
        #if (drg_ocid == ''):
        data = data + """
            resource "oci_core_drg" \"""" + vcn_tf_name+"_"+drg_tf_name + """" {
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    display_name = \"""" + drg_display + """"
            }
            resource "oci_core_drg_attachment" \"""" + vcn_tf_name+"_"+drg_attach_tf_name + """" {
                    drg_id = "${oci_core_drg.""" + vcn_tf_name+"_"+drg_tf_name + """.id}"
                    vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
                    display_name = \"""" + drg_attach_name + """"
            """
        if (hub_spoke_none == 'hub'):
            data = data + """
                    route_table_id = "${oci_core_route_table.""" + rt_tf_name + """.id}"
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
        sgw_tf_name = commonTools.tfname.sub("-", sgw_name)

        data = data + """
            resource "oci_core_service_gateway"  \"""" + vcn_tf_name+"_"+sgw_tf_name + """" {
                    services {
                    #service_id = "${data.oci_core_services.oci_services.services.0.id}"
                    service_id =  contains(split("-","${data.oci_core_services.oci_services.services.0.cidr_block}"),"all") == true ? "${data.oci_core_services.oci_services.services.0.id}" : "${data.oci_core_services.oci_services.services.1.id}"
                    }
                    display_name = \"""" + sgw_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
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
        ngw_tf_name = commonTools.tfname.sub("-", ngw_name)

        data = data + """
            resource "oci_core_nat_gateway" \"""" + vcn_tf_name+"_"+ngw_tf_name + """" {
                    display_name = \"""" + ngw_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
                    compartment_id = "${var.""" + compartment_var_name + """}"
            }
            """
    if(vcn_lpg!='n'):
        for lpg_name in vcns.vcn_lpg_names[vcn_name]:
            lpg_tf_name = commonTools.tfname.sub("-", lpg_name)
            lpg_rt_name = ""
            #if (nongf_tenancy == "true"):
            if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
                with open(outdir + "/" + region + "/obj_names.safe") as f:
                    for line in f:
                        if ("lpginfo::::" + vcn_name + "::::" + lpg_name in line):
                            lpg_rt_name = line.split("::::")[3].strip()

            if (lpg_rt_name == ""):
                #rt_var = vcn_name + "_" + lpg_name + "_rt"
                rt_var = vcn_name+"_Route Table associated with LPG-"+lpg_name
            else:
                rt_var = vcn_name + "_" + lpg_rt_name
            print(rt_var)
            rt_tf_name = commonTools.tfname.sub("-", rt_var)
            data = data + """
            resource "oci_core_local_peering_gateway" \"""" + vcn_tf_name+"_"+lpg_tf_name + """" {
                    display_name = \"""" + lpg_name + """"
                    vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    ##peer_id for lpg """ + vcn_name+"_"+lpg_name+"##"
            if(hub_spoke_none == 'hub'):
                data = data + """
                    route_table_id = "${oci_core_route_table.""" + rt_tf_name + """.id}"
                }
                """
            else:
                data=data+"""
            }
            """

    tfStr[region] = tfStr[region] + data
    dhcpStr[region] = dhcpStr[region] + dhcp_data


# If input is CD3 excel file
if ('.xls' in filename):
    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    for reg in vcnInfo.all_regions:
        tfStr[reg] = ''
        dhcpStr[reg] = ''

    df = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # Process VCNs
    for i in df.index:
        region = df['Region'][i]
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()
        if region not in vcnInfo.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the values mentioned in VCN Info tab..Exiting!")
            exit(1)


        vcn_name = df['vcn_name'][i]
        vcn_cidr = df['vcn_cidr'][i]
        vcn_drg = df['drg_required'][i]
        #drg_var_name = tfname.sub('', vcn_drg)

        vcn_igw = df['igw_required'][i]
        vcn_ngw = df['ngw_required'][i]
        vcn_sgw = df['sgw_required'][i]
        vcn_lpg = df['lpg_required'][i]
        hub_spoke_none = df['hub_spoke_peer_none'][i]
        compartment_var_name = df['compartment_name'][i]
        vcn_dns_label = df['dns_label'][i]

        # check if vcn_dns_label is not given by user in input use vcn name
        if (str(vcn_dns_label).lower() == 'nan'):
            regex = re.compile('[^a-zA-Z0-9]')
            vcn_dns = regex.sub('', vcn_name)
            vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns

        # Check to see if any column is empty in Subnets Sheet
        if (str(vcn_name).lower() == 'nan' or str(vcn_cidr).lower() == 'nan' or
                str(vcn_drg).lower() == 'nan' or str(vcn_igw).lower() == 'nan'
                or str(vcn_ngw).lower() == 'nan' or str(vcn_sgw).lower() == 'nan'
                or str(vcn_lpg).lower() == 'nan'
                or str(hub_spoke_none).lower() == 'nan'
                or str(compartment_var_name).lower() == 'nan'):
            print("Column Values(except dns_label) or Rows cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        processVCN(region, vcn_name.strip(), vcn_cidr.strip(), vcn_drg.strip(), vcn_igw.strip(), vcn_ngw.strip(), vcn_sgw.strip(), vcn_lpg.strip(), hub_spoke_none.strip(), compartment_var_name.strip(),vcn_dns_label,dhcp_data)

# If CD3 excel file is not given as input
elif ('.properties' in filename):
    vcns=parseVCNs(filename)
    config = configparser.RawConfigParser()
    config.optionxform = str
    file_read = config.read(args.inputfile)

    if (len(file_read) != 1):
        print(args.propsfile + " doesn't exist or it could not be opened. Please check input params and try again..")
        exit(1)

    for reg in vcns.all_regions:
        tfStr[reg] = ''

    # Get VCN Info from VCN_INFO section
    vcns = config.options('VCN_INFO')

    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        region = vcn_data[0].strip().lower()
        if region not in vcns.all_regions:
            print("Invalid Region")
            exit(1)
        hub_spoke_peer_none = vcn_data[7].strip().split(":")
        if (hub_spoke_peer_none[0] == 'hub'):
            hub_vcn_names.append(vcn_name)
            peering_dict[vcn_name] = ''
        if (hub_spoke_peer_none[0] == 'spoke'):
            hub_name = hub_spoke_peer_none[1]
            peering_dict[hub_name] = peering_dict[hub_name] + vcn_name + ","
            spoke_vcn_names.append(vcn_name)
    for k, v in peering_dict.items():
        if (v[-1] == ','):
            v = v[:-1]
            peering_dict[k] = v

    print(peering_dict)
    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        region = vcn_data[0].strip().lower()
        vcn_cidr = vcn_data[1].strip().lower()
        regex = re.compile('[^a-zA-Z0-9]')
        vcn_dns_label = regex.sub('', vcn_name)
        vcn_drg = vcn_data[2].strip()
        vcn_igw = vcn_data[3].strip()
        vcn_ngw = vcn_data[4].strip()
        vcn_sgw = vcn_data[5].strip()
        vcn_lpg = vcn_data[6].strip().split(":")

        hub_spoke_peer_none = vcn_data[7].strip().lower()
        compartment_var_name = vcn_data[11].strip()
        vcn_compartment[vcn_name] = compartment_var_name
        vcn_region[vcn_name] = region

        vcn_dns_label = vcn_data[11].strip()
        # check if vcn_dns_label is not given by user in input use vcn name
        if (vcn_dns_label == ''):
            regex = re.compile('[^a-zA-Z0-9]')
            vcn_dns = regex.sub('', vcn_name)
            vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns

        # if(hub_spoke_none=='hub' and vcn_drg!='y'):
        #        print("\nVCN marked as Hub should have DRG configured..Modify the input file and try again")
        #        exit(1)

        processVCN(region, vcn_name, vcn_cidr, vcn_drg, vcn_igw, vcn_ngw, vcn_sgw, vcn_lpg,hub_spoke_peer_none,
                   compartment_var_name, vcn_dns_label,dhcp_data)

    # Create LPGs as per Section VCN_PEERING
    """peering_dict = dict(config.items('VCN_PEERING'))
    ocs_vcn_lpg_ocids = peering_dict['ocs_vcn_lpg_ocid']
    ocs_vcn_lpg_ocids = ocs_vcn_lpg_ocids.split(",")
    peering_dict.pop('ocs_vcn_lpg_ocid')
    peering_dict.pop('ocs_vcn_cidr')
    peering_dict.pop('add_ping_sec_rules_onprem')
    peering_dict.pop('add_ping_sec_rules_vcnpeering')
"""

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit(1)

if(modify_network=='true'):
    for reg in vcnInfo.all_regions:
        reg_out_dir = outdir + "/" + reg

        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
        outfile_dhcp[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"

        x = datetime.datetime.now()
        date = x.strftime("%f").strip()

        if(os.path.exists(outfile[reg])):
            print("creating backup file " + outfile[reg] + "_backup" + date)
            shutil.copy(outfile[reg], outfile[reg] + "_backup" + date)
        if (os.path.exists(outfile[reg])):
            print("creating backup file " + outfile_dhcp[reg] + "_backup" + date)
            shutil.copy(outfile[reg], outfile_dhcp[reg] + "_backup" + date)


        oname[reg] = open(outfile[reg], "w")
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for major objects has been updated for region " + reg)

        oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w")
        oname_def_dhcp[reg].write(dhcpStr[reg])
        oname_def_dhcp[reg].close()
        print(outfile_dhcp[reg] + " containing TF for default DHCP options for VCNs has been updated for region " + reg)


elif(modify_network == 'false'):
    for reg in vcnInfo.all_regions:
        reg_out_dir = outdir + "/" + reg

        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)


        outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
        outfile_dhcp[reg] = reg_out_dir +  "/VCNs_Default_DHCP.tf"

        oname_datafile[reg]=open(reg_out_dir + "/oci-data.tf","w")
        oname_datafile[reg].write(datastr)
        print(reg_out_dir + "/oci-data.tf" + " containing TF for oci-data has been created for region " + reg)

        if(dhcpStr[reg]!=''):
            oname_def_dhcp[reg] = open(outfile_dhcp[reg],"w")
            oname_def_dhcp[reg].write(dhcpStr[reg])
            oname_def_dhcp[reg].close()
            print(outfile_dhcp[reg]+" containing TF for default DHCP options for VCNs has been created for region " + reg)

        if (tfStr[reg] != ''):
            tfStr[reg] = tfStr[reg]
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for VCN major objects has been created for region " + reg)

#if(nongf_tenancy=="false"):
establishPeering(vcns.peering_dict)

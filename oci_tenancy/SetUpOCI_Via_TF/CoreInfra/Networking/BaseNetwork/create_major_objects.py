#!/usr/bin/python3

# Author: Suruchi
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import argparse
import re
import configparser
import pandas as pd
import datetime
import shutil
import os
from jinja2 import Environment, FileSystemLoader

sys.path.append(os.getcwd() + "/../../..")
from commonTools import *

######
# Required Files
# input file containing VCN info either vcn-info.properties or CD3 excel
# Create the major terraform objects - DRG, IGW, NGW, SGW, LPGs for the VCN
# Outdir
# prefix
######

## Start Processing

parser = argparse.ArgumentParser(
    description="Create major-objects (VCN, IGW, NGW, DRG, LPGs etc for the VCN) terraform file")
parser.add_argument("inputfile",
                    help="Full Path of input file either props file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--modify_network", help="modify network: true or false", required=False)
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

# Declare Variables
filename = args.inputfile
outdir = args.outdir
prefix = args.prefix
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName = ""

ct = commonTools()
ct.get_subscribedregions(configFileName)

outfile = {}
oname = {}
tfStr = {}
dhcpStr = {}
outfile_dhcp = {}
oname_def_dhcp = {}
oname_datafile = {}
vcn_dns_label = ''

global dhcp_data


# Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
datasource = env.get_template('data-source-template')
defaultdhcp = env.get_template('default-dhcp-template')


# Function to establish peering between LPGs
def establishPeering(peering_dict):
    for left_vcn, value in peering_dict.items():
        region = vcns.vcn_region[left_vcn]
        outfile = outdir + "/" + region + "/" + prefix + '-major-objs.tf'

        right_vcns = value.split(",")

        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            right_vcn = right_vcn.strip()
            right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)

            try:
                if (vcns.vcn_lpg_names[left_vcn][0].lower() == 'n' or vcns.vcn_lpg_names[right_vcn][0].lower() == 'n'):
                    print( "\nERROR!!! Cannot specify n for lpg_required field of VCN if it is part of VCN peering..Exiting!")
                    exit(1)
            except IndexError:

                print("\nERROR!!! Insufficient LPGs declared for either " + left_vcn + " or " + right_vcn + ". Check lpg_required column in VCNs tab..Exiting!")
                exit(1)
            searchString = """##peer_id for lpg """ + left_vcn + "_" + vcns.vcn_lpg_names[left_vcn][0] + "##"
            vcns.vcn_lpg_names[left_vcn].pop(0)
            lpg_name = vcns.vcn_lpg_names[right_vcn][0]
            lpg_tf_name = right_vcn + "_" + lpg_name
            lpg_tf_name = commonTools.check_tf_variable(lpg_tf_name)

            peerStr = """peer_id = oci_core_local_peering_gateway.""" + lpg_tf_name + """.id"""
            vcns.vcn_lpg_names[right_vcn].pop(0)

            # Update file contents
            with open(outfile) as f:
                data = f.read()
            f.close()
            updated_data = re.sub(searchString, peerStr, data)
            with open(outfile, 'w') as f:
                f.write(updated_data)
            f.close()
    # print("VCN Peering Done")


def processVCN(tempStr):
    igw = ''
    ngw = ''
    sgw = ''
    drg = ''
    rt_tf_name = ''
    rt_var = ''
    lpgdata = ''
    region = tempStr['region'].lower().strip()
    vcn_name = tempStr['vcn_name'].strip()
    vcn_tf_name = commonTools.check_tf_variable(vcn_name)
    # vcn_cidr = tempStr['vcn_cidr'].strip()
    vcn_drg = tempStr['drg_required'].strip()
    vcn_igw = tempStr['igw_required'].strip()
    vcn_ngw = tempStr['ngw_required'].strip()
    vcn_sgw = tempStr['sgw_required'].strip()
    vcn_lpg = tempStr['lpg_required'].strip()
    hub_spoke_none = tempStr['hub_spoke_peer_none'].strip()
    compartment_var_name = str(tempStr['compartment_name']).strip()

    # Added to check if compartment name is compatible with TF variable name syntax
    compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
    vcn_dns_label = tempStr['dns_label'].lower().strip()

    # Create TF object for default DHCP options
    dhcpname = vcn_name + "_Default DHCP Options for " + vcn_name
    dhcp_tf_name = commonTools.check_tf_variable(dhcpname)
    tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name, 'dhcp_tf_name': dhcp_tf_name,
                'server_type': 'VcnLocalPlusInternet'}

    tempStr.update(tempdict)

    dhcp_default = defaultdhcp.render(tempStr)

    vcn = env.get_template('major-objects-vcn-template')
    vcn = vcn.render(tempStr)
    # print(dhcp_default)

    if vcn_igw != "n":
        # use default name
        if (vcn_igw == "y"):
            igw_name = vcn_name + "_igw"
            tempStr['igw_name'] = igw_name


        # use name provided in input
        else:
            igw_name = vcn_igw
            tempStr['igw_name'] = igw_name

        igw_tf_name = vcn_name + "_" + igw_name
        igw_tf_name = commonTools.check_tf_variable(igw_tf_name)

        tempStr['igw_tf_name'] = igw_tf_name
        tempStr.update(tempdict)

        igw = env.get_template('major-objects-igw-template')
        igw = igw.render(tempStr)
    # print(igw)

    if vcn_drg != "n":
        # use default name
        if (vcn_drg == "y"):
            # drg_name = vcn_name + "_drg"
            drg_name = region + "_drg"

            # drg_display = vcn_name + "_drg"
            drg_display = region + "_drg"

        # use name provided in input
        else:
            drg_name = vcn_drg
            drg_display = vcn_drg

        drg_tf_name = commonTools.check_tf_variable(drg_name)

        drg_rt_name = ""
        if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
            with open(outdir + "/" + region + "/obj_names.safe") as f:
                for line in f:
                    if ("drginfo::::" + vcn_name + "::::" + drg_display in line):
                        drg_rt_name = line.split("::::")[3].strip()
                        tempStr['drg_tf_name'] = drg_tf_name
                        break
        if (drg_rt_name == ""):
            # rt_var = vcn_name+"_"+drg_name + "_rt"
            rt_var = vcn_name + "_Route Table associated with DRG-" + drg_name
        else:
            rt_var = vcn_name + "_" + drg_rt_name

        tempStr['rt_var'] = rt_var

        drg_attach_name = ""
        if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
            with open(outdir + "/" + region + "/obj_names.safe") as f:
                for line in f:
                    if ("drgattachinfo::::" + vcn_name + "::::" + drg_display in line):
                        drg_attach_name = line.split("::::")[3].strip()
                        tempStr['drg_attach_name'] = drg_attach_name
                        break
        if (drg_attach_name == ""):
            # rt_var = vcn_name+"_"+drg_name + "_rt"
            drg_attach_name = drg_name + "_attach"
            tempStr['drg_attach_name'] = drg_attach_name

        drg_attach_tf_name = vcn_name + "_" + drg_attach_name
        drg_attach_tf_name = commonTools.check_tf_variable(drg_attach_tf_name)
        rt_tf_name = commonTools.check_tf_variable(rt_var)

        tempStr['drg_attach_tf_name'] = drg_attach_tf_name
        tempStr['rt_tf_name'] = rt_tf_name
        tempStr['compartment_tf_name'] = compartment_var_name
        tempStr['drg_required'] = tempStr['drg_required'].lower().strip()
        tempStr['drg_name'] = drg_name
        tempStr['drg_display'] = drg_display
        tempStr['drg_tf_name'] = drg_tf_name

        # Create new DRG
        # if (drg_ocid == ''):
        drg = env.get_template('major-objects-drg-template')
        drg = drg.render(tempStr)

    if vcn_sgw != "n":
        # use default name
        if (vcn_sgw == "y"):
            sgw_name = vcn_name + "_sgw"
        # use name provided in input
        else:
            sgw_name = vcn_sgw
        sgw_tf_name = vcn_name + "_" + sgw_name
        sgw_tf_name = commonTools.check_tf_variable(sgw_tf_name)

        tempStr['sgw_tf_name'] = sgw_tf_name
        tempStr['sgw_name'] = sgw_name
        tempStr['sgw_required'] = tempStr['sgw_required'].lower().strip()

        sgw = env.get_template('major-objects-sgw-template')
        sgw = sgw.render(tempStr)

    if vcn_ngw != 'n':
        # use default name
        if (vcn_ngw == "y"):
            ngw_name = vcn_name + "_ngw"
        # use name provided in input
        else:
            ngw_name = vcn_ngw
        ngw_tf_name = vcn_name + "_" + ngw_name
        ngw_tf_name = commonTools.check_tf_variable(ngw_tf_name)

        tempStr['ngw_name'] = ngw_name
        tempStr['ngw_tf_name'] = ngw_tf_name
        tempStr['ngw_required'] = tempStr['ngw_required'].lower().strip()

        ngw = env.get_template('major-objects-ngw-template')
        ngw = ngw.render(tempStr)

    if (vcn_lpg != 'n'):
        count_lpg = 0

        if (hub_spoke_none == 'hub'):
            spoke_vcns = vcns.peering_dict[vcn_name].split(",")
            count_spokes = len(spoke_vcns)

        for lpg_name in vcns.vcn_lpg_names[vcn_name]:
            count_lpg = count_lpg + 1
            lpg_tf_name = vcn_name + "_" + lpg_name
            lpg_tf_name = commonTools.check_tf_variable(lpg_tf_name)

            tempStr['lpg_tf_name'] = lpg_tf_name
            tempStr['lpg_name'] = lpg_name
            tempStr['vcn_tf_name'] = vcn_tf_name
            tempStr['lpg_required'] = tempStr['lpg_required'].lower().strip()

            if (hub_spoke_none == 'hub'):
                lpg_rt_name = ""
                if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
                    with open(outdir + "/" + region + "/obj_names.safe") as f:
                        for line in f:
                            if ("lpginfo::::" + vcn_name + "::::" + lpg_name in line):
                                lpg_rt_name = line.split("::::")[3].strip()

                if (lpg_rt_name != ""):
                    rt_var = vcn_name + "_" + lpg_rt_name
                elif (count_lpg <= count_spokes):
                    rt_var = vcn_name + "_Route Table associated with LPG-" + lpg_name
                else:
                    rt_var = ""
                rt_tf_name = commonTools.check_tf_variable(rt_var)

            tempStr['rt_tf_name'] = rt_tf_name
            tempStr['rt_var'] = rt_var

            lpg = env.get_template('major-objects-lpg-template')
            lpg = lpg.render(tempStr)
            lpgdata = lpgdata + lpg

    tfStr[region] = tfStr[region] + igw + ngw + sgw + drg + lpgdata + vcn
    dhcpStr[region] = dhcpStr[reg] + dhcp_default


# If input is CD3 excel file
if ('.xls' in filename):
    # Get vcns object from commonTools
    vcns = parseVCNs(filename)

    for reg in ct.all_regions:
        tfStr[reg] = ''
        dhcpStr[reg] = ''

    # Read cd3 using pandas dataframe
    df = pd.read_excel(filename, sheet_name='VCNs', skiprows=1, dtype = object)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Process VCNs
    for i in df.index:
        region = str(df['Region'][i])
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'VCN Name']).lower() == 'nan' or
                str(df.loc[i, 'CIDR Block']).lower() == 'nan' or str(df.loc[i, 'DRG Required']).lower() == 'nan' or str(
                    df.loc[i, 'IGW Required']).lower() == 'nan' or
                str(df.loc[i, 'NGW Required']).lower() == 'nan' or str(
                    df.loc[i, 'SGW Required']).lower() == 'nan' or str(df.loc[i, 'LPG Required']).lower() == 'nan' or
                str(df.loc[i, 'Hub/Spoke/Peer/None']).lower() == 'nan'):
            print("\nColumn Values(except dns_label) or Rows cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            #Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == "DNS Label":
                # check if vcn_dns_label is not given by user in input use vcn name
                if str(columnvalue).lower() == 'nan' or str(columnvalue).lower() == '':
                    regex = re.compile('[^a-zA-Z0-9]')
                    vcn_dns = regex.sub('', df.loc[i, 'VCN Name'])
                    # truncate all digits from start of dns_label
                    index = 0
                    for c in vcn_dns:
                        if c.isdigit() == True:
                            index = index + 1
                            continue
                        else:
                            break
                    vcn_dns = vcn_dns[index:]
                    vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns
                    tempdict = {'dns_label': vcn_dns_label, 'vcn_dns': vcn_dns}
                else:
                    tempdict = {'dns_label': columnvalue.strip() }

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        processVCN(tempStr)

# If CD3 excel file is not given as input
elif ('.properties' in filename):
    vcns = parseVCNs(filename)
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

        processVCN(region, vcn_name, vcn_cidr, vcn_drg, vcn_igw, vcn_ngw, vcn_sgw, vcn_lpg, hub_spoke_peer_none,
                   compartment_var_name, vcn_dns_label, dhcp_data)

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

if (modify_network == 'true'):
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg

        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
        outfile_dhcp[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"

        x = datetime.datetime.now()
        date = x.strftime("%f").strip()

        if (os.path.exists(outfile[reg])):
            print("creating backup file " + outfile[reg] + "_backup" + date)
            shutil.copy(outfile[reg], outfile[reg] + "_backup" + date)
        if (os.path.exists(outfile_dhcp[reg])):
            print("creating backup file " + outfile_dhcp[reg] + "_backup" + date)
            shutil.copy(outfile_dhcp[reg], outfile_dhcp[reg] + "_backup" + date)

        oname[reg] = open(outfile[reg], "w")
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for major objects has been updated for region " + reg)

        oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w")
        oname_def_dhcp[reg].write(dhcpStr[reg])
        oname_def_dhcp[reg].close()
        print(outfile_dhcp[reg] + " containing TF for default DHCP options for VCNs has been updated for region " + reg)


elif (modify_network == 'false'):
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg

        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
        outfile_dhcp[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"

        oname_datafile[reg] = open(reg_out_dir + "/oci-data.tf", "w")
        datastr = datasource.render()
        oname_datafile[reg].write(datastr)
        print(reg_out_dir + "/oci-data.tf" + " containing TF for oci-data has been created for region " + reg)

        if (dhcpStr[reg] != ''):
            oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w")
            oname_def_dhcp[reg].write(dhcpStr[reg])
            oname_def_dhcp[reg].close()
            print(outfile_dhcp[reg] + " containing TF for default DHCP options for VCNs has been created for region " + reg)

        if (tfStr[reg] != ''):
            tfStr[reg] = tfStr[reg]
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for VCN major objects has been created for region " + reg)

establishPeering(vcns.peering_dict)


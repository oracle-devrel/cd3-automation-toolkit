#!/usr/bin/python3
##### Author : Suruchi ###
##### Oracle Consulting ####


######
# Required Files
# Properties File: vcn-info.properties"
# Code will read input subnet file name for each vcn from properties file
# Subnets file will contain info about each subnet. Seclists will be created based on the inputs in properties file
# Outfile
######

import sys
import argparse
import configparser
import re
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *


def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." + os.path.join(dir, f))
            os.remove(os.path.join(dir, f))


parser = argparse.ArgumentParser(description="Creates a terraform sec list resource with name for each subnet"
                                             "identified in the subnet input file.  This creates open egress (0.0.0.0/0) and "
                                             "All protocols within subnet ingress rules.  This also opens ping between peered VCNs"
                                             " and ping from On-Prem to hub VCN based on the input property add_ping_sec_rules_vcnpeering "
                                             "and add_ping_sec_rules_onprem respectively. Any other rules should be put in manually.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory")
parser.add_argument("--modify_network", help="modify: true or false", required=False)
parser.add_argument("--configFileName", help="Config file name", required=False)


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

filename = args.inputfile
outdir = args.outdir
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

fname = None
oname = None
secrulefiles = {}
ADS = ["AD1", "AD2", "AD3"]

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('seclist-template')
secrule = env.get_template('ingress-egress-template')

def processSubnet(tempStr):

    tempStr['region'].lower().strip()
    subnet_cidr = tempStr['cidr_block'].strip()

    # Seclist name specifiied as 'n' - dont create any seclist

    if tempStr['seclist_names'].lower() == 'n':
        return

    if (tempStr['availability_domain'].strip().lower() != 'regional'):
        AD = tempStr['availability_domain'].strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    vcn_name = tempStr['vcn_name']
    vcn_tf_name = commonTools.check_tf_variable(tempStr['vcn_name'])
    tempStr['vcn_tf_name'] = vcn_tf_name

    index = 0
    seclist_names = tempStr['sl_names']
    tempSecList = ''
    for sl_name in seclist_names:
        sl_name = sl_name.strip()

        # check if subnet cidr needs to be attached
        if (vcnInfo.subnet_name_attach_cidr == 'y'):
            if (str(ad_name) != ''):
                name1 = sl_name + "-ad" + str(ad_name)
            else:
                name1 = sl_name
            display_name = name1 + "-" + tempStr['cidr_block']
        else:
            display_name = sl_name
        tempStr['display_name'] = display_name

        sl_tf_name = vcn_name+ "_" + display_name
        sl_tf_name = commonTools.check_tf_variable(sl_tf_name)
        tempStr['seclist_tf_name'] = sl_tf_name


        if (sl_tf_name + "_seclist.tf" in secrulefiles[region]):
            secrulefiles[region].remove(sl_tf_name + "_seclist.tf")
        outfile = outdir + "/" + region + "/" + sl_tf_name + "_seclist.tf"

        # If Modify Network is set to true
        if (os.path.exists(outfile) and modify_network == 'true'):
            continue

        # If same seclist name is used for subsequent subnets
        if (index == 0 and os.path.exists(outfile) and modify_network == 'false'):
            tempStr['rule_type'] = "ingress"
            tempStr['source'] = subnet_cidr
            tempStr['protocol_code'] = 'all'
            tempStr['isstateless'] = "true"

            Str = secrule.render(tempStr)

            with open(outfile, 'r+') as file:
                filedata = file.read()
            file.close()

            # Replace the target string
            textToSearch = "####ADD_NEW_SEC_RULES####" + vcn_tf_name + "_" + sl_tf_name
            Str = Str + "\n" + textToSearch

            filedata = filedata.replace(textToSearch, Str)
            oname = open(outfile, "w")
            oname.write(filedata)
            oname.close()
            continue

        # New Seclist
        oname = open(outfile, "w")
        tempStr['index'] = index
        
        tempSecList = template.render(tempStr)
        if index != 0:
            tempSecList=tempSecList +"\n"
        elif (index == 0):
            secrule_data = ''
            rule_type = ['ingress','egress']
            for rule in rule_type:
                tempStr['destination'] = '0.0.0.0/0'
                tempStr['protocol_code'] = 'all'
                tempStr['source'] = subnet_cidr
                tempStr['rule_type'] = rule
                tempStr['isstateless'] = "true"
                secrule_data = secrule_data + secrule.render(tempStr)
            textToSearch = "####ADD_NEW_SEC_RULES####" + vcn_tf_name + "_" + sl_tf_name
            secrule_data = secrule_data + textToSearch
            tempSecList = tempSecList.replace(textToSearch,secrule_data)
        oname.write(tempSecList)
        oname.close()
        print(outfile + " containing TF for seclist has been created for region " + region)
        index = index + 1

# If input is CD3 excel file
if ('.xls' in filename):
    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Purge existing routetable files
    if (modify_network == 'false'):
        for reg in ct.all_regions:
            purge(outdir+"/"+reg, "_seclist.tf")
            secrulefiles.setdefault(reg, [])

    # Get existing list of secrule table files
    if (modify_network == 'true'):
        for reg in ct.all_regions:
            secrulefiles.setdefault(reg, [])
            lisoffiles = os.listdir(outdir + "/" + reg)
            for file in lisoffiles:
                if "_seclist.tf" in file:
                    secrulefiles[reg].append(file)

    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Start processing each subnet
    for i in df.index:
        region = df.loc[i, 'Region']
        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1, dictionary2, string  and list
        tempStr = {}
        tempdict = {}
        sl_names = []
        compartment_var_name = ''

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i,'VCN Name']).lower() == 'nan':
            print(" The values for Region, Compartment Name and VCN Name cannot be left empty in Subnets Tab. Please enter a value and try again !!")
            exit()

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            if columnvalue == '1.0' or  columnvalue == '0.0':
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

            if (columnvalue.lower() == 'nan'):
                columnvalue = ""

            if "::" in columnvalue:
                if columnname != 'Compartment Name':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue
            vcn_name = str(df.loc[i,'VCN Name'].strip())

            if (vcn_name.strip() not in vcns.vcn_names):
                print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
                exit(1)

            if columnname == 'Availability Domain\n(AD1|AD2|AD3|Regional)':
                columnname = 'availability_domain'
                columnvalue = columnvalue.strip()

            if columnname == 'Seclist Names':
                columnvalue = columnvalue.strip()
                if columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    sl_names = columnvalue.split(",")
                else:
                    sl_names.append(str(df.loc[i,'Subnet Name']).strip())
                compartment_var_name = compartment_var_name.strip()
                tempdict = {'compartment_tf_name' : compartment_var_name, 'sl_names' : sl_names}

            #Added to check if compartment name is compatible with TF variable name syntax
            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = columnvalue
            tempStr.update(tempdict)

        processSubnet(tempStr)

    # remove any extra sec list files (not part of latest cd3)
    for reg in ct.all_regions:
        if(len(secrulefiles[reg])!=0):
            print("\nATTENION!!! Below SecLists are not attached to any subnet; If you want to delete any of them, remove the TF file!!!")
        for remaining_sl_file in secrulefiles[reg]:
            print(outdir + "/" + reg + "/" + remaining_sl_file)

            # print("\nRemoving "+outdir + "/" + reg + "/"+remaining_sl_file)
            # os.remove(outdir + "/" + reg + "/"+remaining_sl_file)
            # secrulefiles[reg].remove(remaining_sl_file)

# If CD3 excel file is not given as input
elif ('.properties' in filename):
    # Get VCN Info from VCN_INFO section
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.inputfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    all_regions = config.get('Default', 'regions')
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    if (subnet_add == 'false'):
        for reg in all_regions:
            purge(outdir + "/" + reg, "_seclist.tf")
    subnet_name_attach_cidr = config.get('Default', 'subnet_name_attach_cidr')
    drg_destinations = config.get('Default', 'drg_subnet')
    if (drg_destinations == ''):
        print("\ndrg_subnet should not be left empty.. It will create empty route tables")
    else:
        drg_destinations = drg_destinations.split(",")

    vcns = config.options('VCN_INFO')
    for vcn_name in vcns:
        vcn_lpg_rules.setdefault(vcn_name, '')

    # Create sec rules as per Section VCN_PEERING
    peering_dict = dict(config.items('VCN_PEERING'))
    ocs_vcn_cidr = peering_dict['ocs_vcn_cidr']
    peering_dict.pop('ocs_vcn_lpg_ocid')
    add_ping_sec_rules_vcnpeering = peering_dict['add_ping_sec_rules_vcnpeering']
    add_ping_sec_rules_onprem = peering_dict['add_ping_sec_rules_onprem']
    peering_dict.pop('add_ping_sec_rules_vcnpeering')
    peering_dict.pop('add_ping_sec_rules_onprem')
    peering_dict.pop('ocs_vcn_cidr')

    if (add_ping_sec_rules_vcnpeering.strip().lower() == 'y'):
        createLPGSecRules(peering_dict)

    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        region = vcn_data[0].strip().lower()
        if region not in all_regions:
            print("Invalid Region")
            exit(1)
        vcn_drg = vcn_data[2].strip().lower()
        hub_spoke_none = vcn_data[6].strip().lower()
        vcn_subnet_file = vcn_data[7].strip().lower()
        if os.path.isfile(vcn_subnet_file) == False:
            print(
                "input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping SecList TF creation for this VCN.")
            continue
        sps = vcn_data[9].strip().lower()
        seclists_per_subnet = int(sps)

        fname = open(vcn_subnet_file, "r")

        # Read subnet file
        for line in fname:
            i = 0
            if not line.startswith('#') and line != '\n':
                [compartment_var_name, name, sub, AD, pubpvt, dhcp, rt_name, seclist_name, common_seclist_name, SGW,
                 NGW, IGW, dns_label] = line.split(',')
                linearr = line.split(",")
                compartment_var_name = linearr[0].strip()
                name = linearr[1].strip()
                subnet = linearr[2].strip()
                if (
                        vcn_name + "_" + common_seclist_name.strip().lower() != '' and common_seclist_name not in common_seclist_names):
                    common_seclist_names[region].append(vcn_name + "_" + common_seclist_name)
                    out_common_file = outdir + "/" + region + "/" + vcn_name + "_" + common_seclist_name + "_seclist.tf"
                    oname_common = open(out_common_file, "w")
                    data = """
                                                resource "oci_core_security_list" \"""" + vcn_name + "_" + common_seclist_name.strip() + "-1" """"{
                                                    compartment_id = "${var.""" + compartment_var_name + """}"
                                                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
                                                    display_name = \"""" + common_seclist_name.strip() + "-1" """"
                                                    ####ADD_NEW_SEC_RULES####1
                                                }
                                                """
                    oname_common.write(data)
                    print(
                        out_common_file + " containing TF for seclist has been created for region " + region)
                    oname_common.close()

                processSubnet(region, vcn_name, AD, seclists_per_subnet, name, seclist_name.strip(),
                              subnet_name_attach_cidr, compartment_var_name)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit(1)

if (fname != None):
    fname.close()

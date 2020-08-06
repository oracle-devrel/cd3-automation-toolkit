#!/usr/bin/python3
# Author: Suruchi
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import argparse
import configparser
import pandas as pd
import shutil
import datetime
import os

sys.path.append(os.getcwd() + "/../../..")
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Files
# input file is cd3 , A prefix for the tf files generated- ex: <prefix>_dhcp.tf
# A Config file
# Outdir
######


parser = argparse.ArgumentParser(description="Create DHCP options terraform file")
parser.add_argument("inputfile",
                    help="Full Path of input file. It could be CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--modify_network", help="Modify: true or false", required=False)
parser.add_argument("--configFileName", help="Config file name", required=False)

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
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName = ""

ct = commonTools()
ct.get_subscribedregions(configFileName)

outfile = {}
deffile = {}
oname = {}
defname = {}
tfStr = {}
defStr = {}

# Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('custom-dhcp-template')
defaultdhcp = env.get_template('default-dhcp-template')


def processDHCP(tempStr):
    compartment_var_name = tempStr['compartment_tf_name'].strip()
    region = tempStr['region'].lower().strip()
    vcn_name = tempStr['vcn_name'].strip()
    vcn_tf_name = commonTools.check_tf_variable(vcn_name)

    # Added to check if compartment name is compatible with TF variable name syntax
    compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

    server_type = tempStr['server_type'].strip()
    search_domain = tempStr['search_domain'].strip()
    dhcp_option_name = tempStr['dhcp_option_name'].strip()
    vcn_dhcp = vcn_name + "_" + dhcp_option_name
    vcn_dhcp_tf_name = commonTools.check_tf_variable(vcn_dhcp)

    tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name,
                'dhcp_tf_name': vcn_dhcp_tf_name, 'vcn_dhcp': vcn_dhcp,
                'vcn_name': vcn_name, 'search_domain': search_domain, 'dhcp_option_name': dhcp_option_name,
                'server_type': server_type}

    tempStr.update(tempdict)

    if ("Default DHCP Options for " in dhcp_option_name):
        data = defaultdhcp.render(tempStr)
    else:
        data = template.render(tempStr)

    tfStr[region] = tfStr[region] + data


if ('.xls' in args.inputfile):
    vcns = parseVCNs(filename)
    for reg in ct.all_regions:
        tfStr[reg] = ''
        defStr[reg] = ''

    df = pd.read_excel(args.inputfile, sheet_name='DHCP', skiprows=1, dtype = object)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break
        region = region.strip().lower()

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
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

            if columnname == "Compartment Name":
                compartment_var_name = columnvalue.strip()
                tempStr['compartment_tf_name'] = compartment_var_name

            if columnname == "VCN Name":
                vcn_name = columnvalue.strip()
                tempStr['vcn_name'] = vcn_name

                if (vcn_name.strip() not in vcns.vcn_names):
                    print(
                        "\nERROR!!! " + vcn_name + " specified in DHCP tab has not been declared in VCNs tab..Exiting!")
                    exit(1)

            if columnname == "Server Type(VcnLocalPlusInternet|CustomDnsServer)":
                columnname = 'server_type'
                columnvalue = columnvalue.strip()

            if columnname == 'Custom DNS Server':
                custom_dns_server = str(columnvalue).strip()
                if custom_dns_server != '':
                    custom_dns_server = custom_dns_server.replace(',', '","')
                    custom_dns_server = '"' + custom_dns_server + '"'
                    tempdict = {'custom_dns_server': custom_dns_server}
                tempStr.update(tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
        processDHCP(tempStr)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx")

if (modify_network == 'true'):
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + prefix + '-dhcp.tf'
        deffile[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"

        x = datetime.datetime.now()
        date = x.strftime("%f").strip()
        # if(tfStr[reg]!=''):
        if (os.path.exists(outfile[reg])):
            print("creating backup file " + outfile[reg] + "_backup" + date)
            shutil.copy(outfile[reg], outfile[reg] + "_backup" + date)
        oname[reg] = open(outfile[reg], "w")
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for DHCP Options has been updated for region " + reg)

        # Added this if condition again because modify network was showing tf destroying Default DHCP Options
        if (defStr[reg] != ''):
            if (os.path.exists(deffile[reg])):
                print("creating backup file " + deffile[reg] + "_backup" + date)
                shutil.copy(outfile[reg], deffile[reg] + "_backup" + date)
            defname[reg] = open(deffile[reg], "w")
            defname[reg].write(defStr[reg])
            defname[reg].close()
            print(deffile[reg] + " containing TF for Default DHCP Options has been updated for region " + reg)


elif (modify_network == 'false'):
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + prefix + '-dhcp.tf'
        deffile[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"

        if (tfStr[reg] != ''):
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for DHCP Options has been created for region " + reg)

        if (defStr[reg] != ''):
            defname[reg] = open(deffile[reg], "w")
            defname[reg].write(defStr[reg])
            defname[reg].close()
            print(deffile[reg] + " containing TF for Default DHCP Options has been created for region " + reg)

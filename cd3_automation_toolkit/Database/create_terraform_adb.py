#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Groups
#
# Author: Kartikey Rajput
# Oracle Consulting
# Modified (TF Upgrade): Divya Das
#

import sys
import argparse
import os
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Create ADB terraform file")
    parser.add_argument("inputfile", help="Full Path of input file. It could be CD3 excel file")
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


#If input is cd3 file
def create_terraform_adb(inputfile, outdir, prefix, config=DEFAULT_LOCATION):

    filename = inputfile
    configFileName = config
    sheetName = "ADB"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('adb-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    subnets = parseSubnets(filename)
    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region=region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'CPU Core Count']).lower() == 'nan' or \
                str(df.loc[i, 'Data Storage Size in TB']).lower() == 'nan' or \
                str(df.loc[i, 'DB Name']).lower() == 'nan':
            print("\nRegion, Compartment Name, CPU Core Count, Data Storage Size in TB and DB Name fields are mandatory. Please enter a value and try again !!")
            print("\n** Exiting **")
            exit()

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {columnname: columnvalue}

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "ADB Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == 'Database Workload':
                columnvalue = columnvalue.strip()
                autonomous_value = commonTools.check_tf_variable(columnvalue).lower()
                tempdict = {'autonomous_value': autonomous_value}

            if columnname == 'NSGs':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg_str = ""
                    nsg = ""
                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        if "ocid" in NSGs[k].strip():
                            nsg = "\"" + NSGs[k].strip() + "\""
                        else:
                            nsg = "\"" + commonTools.check_tf_variable(NSGs[k].strip()) + "\""

                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    tempdict = {'nsg_ids': nsg_str}
                    tempStr.update(tempdict)
                continue


            if columnname == "Subnet Name":
                if columnvalue != '':
                    subnet_tf_name = columnvalue.strip()
                    if ("ocid1.subnet.oc1" in subnet_tf_name):
                        network_compartment_id = ""
                        vcn_name = ""
                        subnet_id = subnet_tf_name
                    else:
                        try:
                            key = region, subnet_tf_name
                            network_compartment_id = commonTools.check_tf_variable(subnets.vcn_subnet_map[key][0])
                            vcn_name = subnets.vcn_subnet_map[key][1]
                            subnet_id = subnets.vcn_subnet_map[key][2]
                        except Exception as e:
                            print("Invalid Subnet Name specified for row " + str(
                                i + 3) + ". It Doesnt exist in Subnets sheet. Exiting!!!")
                            exit()
                else:
                    subnet_id = ""
                    vcn_name = ""
                    network_compartment_id = ""

                tempdict = {'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                            'subnet_id': subnet_id}

            if columnname == "License Model" and columnvalue.strip() == "LICENSE_INCLUDED":
                license_model = columnvalue.strip()
                database_edition = ""
                tempdict = {'license_model' : license_model, 'database_edition': database_edition}
                tempStr.update(tempdict)

            if columnname == 'Whitelisted IP Addresses':
                if columnvalue != '':
                    nsg_str = []
                    subnet_id = ""
                    vcn_name = ""
                    network_compartment_id = ""
                    WLs = columnvalue.split(",")
                    k=0
                    wl_str = ""
                    while k<len(WLs):
                        wl_str = wl_str + '"'+ str(WLs[k].strip())+'"'
                        if (k != len(WLs) - 1):
                            wl_str = wl_str + ","
                        k +=1
                else:
                    wl_str = ""
                tempdict = {'whitelisted_ips': wl_str,'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                            'subnet_id': subnet_id }
                tempStr.update(tempdict)


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region]=tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename


        if(tfStr[reg]!=''):
            src = "##Add New ADB for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg]=open(outfile[reg],'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for ADB has been created for region "+reg)
                        
if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_terraform_adb(args.inputfile, args.outdir, args.prefix, args.config)

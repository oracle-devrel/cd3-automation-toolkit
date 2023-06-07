#!/usr/bin/python3
# Copyright (c) 2019, 2023, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Users
#
# Author: Gaurav Goyal
# Oracle Consulting
#

import argparse
import os
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    parser = argparse.ArgumentParser(description="Create Users terraform file")
    parser.add_argument('inputfile', help='Full Path of input CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('service_dir', help='Structured out directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()

#If input is cd3 file
def create_terraform_users(inputfile, outdir, service_dir, prefix, config=DEFAULT_LOCATION):
    # Read the arguments
    filename = inputfile
    configFileName = config

    sheetName = 'Users'
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'
    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    users_template = env.get_template('users-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    tfStr[ct.home_region] = ''


    # Take backup of files
    srcdir = outdir + "/" + ct.home_region + "/" + service_dir + "/"
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
        if region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = { "count" : i }
        tempdict = {}
        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'User Name']).lower() == 'nan' :
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit()


        for columnname in dfcolumns:

            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df[columnname][i]).strip()

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)


            if columnname == 'User Name':
                columnvalue = columnvalue.strip()
                user_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'user_tf_name': user_tf_name}
                tempdict['name'] = columnvalue

            # If description field is empty; put name as description
            if columnname == 'User Description':
                columnvalue = commonTools.check_columnvalue(columnvalue)
                tempdict = {'description': columnvalue}

            if columnname == 'User email':
                columnvalue = commonTools.check_columnvalue(columnvalue)
                tempdict = {'email': columnvalue}

            if columnname == 'Group Names':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    group_str = ""
                    Groups = columnvalue.split(",")
                    k = 0
                    while k < len(Groups):
                        if Groups[k].strip()=="":
                            k += 1
                            continue
                        if "ocid" in Groups[k].strip():
                            group = "\"" + Groups[k].strip() + "\""
                        else:
                            group = "\"" + Groups[k].strip() + "\""

                        group_str = group_str + str(group)
                        if (k != len(Groups) - 1):
                            group_str = group_str + ","
                        k += 1
                    tempdict = {'groups_names': group_str}
                    tempStr.update(tempdict)
                continue


            if columnname == 'Disable Capabilities':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    capability_str = ""
                    capabilities = columnvalue.split(",")
                    k = 0
                    while k < len(capabilities):
                        if capabilities[k].strip()=="":
                            k += 1
                            continue
                        capability = "\"" + capabilities[k].strip() + "\""
                        capability_str = capability_str + str(capability)
                        if (k != len(capabilities) - 1):
                            capability_str = capability_str + ","
                        k += 1
                    tempdict = {'capabilities_to_disable': capability_str}
                    tempStr.update(tempdict)
                continue

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()


            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region]= tfStr[region][:-1] + users_template.render(tempStr)
    # Write TF string to the file in respective region directory
    reg=ct.home_region

    reg_out_dir = outdir + "/" + reg + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

    if(tfStr[reg]!=''):
        tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " for Users has been created for region "+reg)


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_users(args.inputfile, args.outdir, args.service_dir, args.prefix, config=args.config)
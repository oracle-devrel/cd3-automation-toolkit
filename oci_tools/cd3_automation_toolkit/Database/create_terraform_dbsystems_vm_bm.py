#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Database System Virtual Machine
#
# Author: Suruchi
# Oracle Consulting
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
    parser = argparse.ArgumentParser(description="Create DB VM and DB BM terraform file")
    parser.add_argument('inputfile', help='Full Path of input CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


#If input is cd3 file
def create_terraform_dbsystems_vm_bm(inputfile, outdir, prefix, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config

    sheetName = "DBSystems-VM-BM"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'
    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('module-DBSystems-VM-BM-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/"
        resource = sheetName.lower()
        #commonTools.backup_file(srcdir, resource, sheetName.lower()+".tf")
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    regions_done_count = []

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        #if region.lower() == 'nan':
        #    continue

        region=region.strip().lower()


        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region.lower() != 'nan' and region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        #Check if it is different DB home on same BM DB
        if str(df.loc[i, 'Region']).lower() == 'nan' and \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' and \
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' and \
                str(df.loc[i, 'DB System Display Name']).lower() == 'nan' and \
                str(df.loc[i, 'Subnet Name']).lower() == 'nan' and \
                str(df.loc[i, 'Shape']).lower() == 'nan' and \
                str(df.loc[i, 'Node Count']).lower() == 'nan' and \
                str(df.loc[i, 'CPU Core Count']).lower() == 'nan' and \
                str(df.loc[i, 'Database Edition']).lower() == 'nan' and \
                str(df.loc[i, 'Data Storage Size in GB']).lower() == 'nan' and \
                str(df.loc[i, 'Data Storage Percentage']).lower() == 'nan' and \
                str(df.loc[i, 'Disk Redundancy']).lower() == 'nan' and \
                str(df.loc[i, 'License Model']).lower() == 'nan' and \
                str(df.loc[i, 'Hostname Prefix']).lower() == 'nan' and \
                str(df.loc[i, 'DB Name']).lower() != 'nan':
            continue

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or \
                str(df.loc[i, 'SSH Key Var Name']).lower() == 'nan' or \
                str(df.loc[i, 'Subnet Name']).lower() == 'nan' or \
                str(df.loc[i, 'Hostname Prefix']).lower() == 'nan' or \
                str(df.loc[i, 'Shape']).lower() == 'nan' :
            print("\nRegion, Compartment Name, Availability Domain(AD1|AD2|AD3), SSH Key Var Name, Subnet Name, Hostname, Shape are mandatory fields. Please enter a value and try again.......Exiting!!")
            exit()
        if str(df.loc[i, 'DB Name']).lower() == 'nan' or \
                str(df.loc[i, 'DB Version']).lower() == 'nan' or \
                str(df.loc[i, 'Database Edition']).lower() == 'nan' or \
                str(df.loc[i, 'DB Admin Password']).lower() == 'nan':
            print("\nDB Name, DB Version, Database Edition, DB Admin Password are mandatory fields. Please enter a value and try again.......Exiting!!")
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

            if columnname == "SSH Key Var Name":
                if columnvalue.strip() != '' and  columnvalue.strip().lower() != 'nan':
                    if "ssh-rsa" in columnvalue.strip():
                        ssh_key_var_name = "\"" + columnvalue.strip() + "\""
                    else:
                        ssh_key_var_name = "var." + columnvalue.strip()
                    tempdict = {'ssh_key_var_name': ssh_key_var_name}

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "DB System Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == 'Subnet Name':
                columnvalue = commonTools.check_tf_variable(columnvalue)


            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain': columnvalue}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if (region not in regions_done_count):
            tempdict = {"count": 0}
            regions_done_count.append(region)
        else:
            tempdict = {"count": i}
        tempStr.update(tempdict)


        # Write all info to TF string
        tfStr[region]=tfStr[region] + template.render(tempStr)


    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        #outfile[reg] = reg_out_dir + "/" + prefix + "_"+sheetName.lower()+".tf"
        outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

        if(tfStr[reg]!=''):
            oname[reg]=open(outfile[reg],'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for DBSystems-VM-BM has been created for region "+reg)

        # Rename the modules file in outdir to .tf
        module_filename = outdir + "/" + reg + "/" + sheetName.lower() + ".txt"
        rename_module_filename = outdir + "/" + reg + "/" + sheetName.lower() + ".tf"

        if not os.path.isfile(rename_module_filename):
            if os.path.isfile(module_filename):
                os.rename(module_filename, rename_module_filename)


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_dbsystems_vm_bm(args.inputfile, args.outdir, args.prefix, args.config)

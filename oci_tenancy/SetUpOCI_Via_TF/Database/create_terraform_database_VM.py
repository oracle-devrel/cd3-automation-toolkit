#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Database System Virtual Machine
#
# Author: Kartikey Rajput
# Oracle Consulting
# Modified (TF Upgrade): Kartikey Rajput
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
    parser = argparse.ArgumentParser(description="Create DBVM terraform file")
    parser.add_argument("inputfile", help="Full Path of input file. It could be CD3 excel file")
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


#If input is cd3 file
def create_terraform_database_VM(inputfile, outdir, prefix, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('db-EXA-VM-BM-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "DB_System_VM")

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''

    uniquereg = df['Region'].unique()
    # Take backup of files
    for eachregion in uniquereg:
        eachregion = str(eachregion).strip().lower()
        reg_out_dir = outdir + "/" + eachregion
        if (eachregion in commonTools.endNames) or ('nan' in str(eachregion).lower() ):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = reg_out_dir + "/"
        resource = 'DBVM'
        commonTools.backup_file(srcdir, resource, "DBVM.tf")

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region.lower() == 'nan':
            continue

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
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or \
                str(df.loc[i, 'Oracle DB Software Edition']).lower() == 'nan' or \
                str(df.loc[i, 'DB Version']).lower() == 'nan' or \
                str(df.loc[i, 'Hostname Prefix']).lower() == 'nan' or \
                str(df.loc[i, 'Shape']).lower() == 'nan' :
            print("\nCompartment Name, Availability Domain(AD1|AD2|AD3), Oracle DB Software Edition, DB Version, Hostname Prefix, Shape are mandatory fields. Please enter a value and try again.......Exiting!!")
            exit()

        if str(df.loc[i, 'SSH Key']).lower() == 'nan' or \
                str(df.loc[i, 'Subnet Name']).lower() == 'nan' or \
                str(df.loc[i, 'DB Home']).lower() == 'nan' or \
                str(df.loc[i, 'DB Admin Password']).lower() == 'nan':
            print("\nSSH Key, Subnet Name, DB Home, DB Admin Password are mandatory fields. Please enter a value and try again.......Exiting!!")
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

            if columnname == "DB Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == "DB Size (GB)":
                tempdict = {'db_size': columnvalue.strip()}

            if columnname == 'Subnet Name':
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == "Recovery Windows (Days)":
                tempdict = {'recovery_windows': columnvalue.strip()}

            if columnname == 'DB Home':
                columnname = 'db_name'

            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain': columnvalue}

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
        outfile[reg] = reg_out_dir + "/DBVM.tf"

        if(tfStr[reg]!=''):
            oname[reg]=open(outfile[reg],'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for DBVM has been created for region "+reg)

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_database_VM(args.inputfile, args.outdir, args.prefix, args.config)

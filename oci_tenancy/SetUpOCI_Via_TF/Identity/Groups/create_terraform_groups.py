#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Groups
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

# import sys
import argparse
import os
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
# sys.path.append(os.getcwd()+"/../..")
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    parser = argparse.ArgumentParser(description="Create Groups terraform file")
    parser.add_argument("inputfile", help="Full Path of input file. It could be CD3 excel file")
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")

    # Declare variables
    args = parser.parse_args()


#If input is cd3 file
def create_terraform_groups(inputfile, outdir, prefix, config=DEFAULT_LOCATION):
    # Read the arguments
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('groups-template')
    dynamicgroup =  env.get_template('dynamic-groups-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Groups")

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

        if (eachregion in commonTools.endNames):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        srcdir = reg_out_dir + "/"
        resource = 'Groups'
        commonTools.backup_file(srcdir, resource, "-groups.tf")

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
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Name']).lower() == 'nan' :
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit()

        for columnname in dfcolumns:

            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Name':
                columnvalue = columnvalue.strip()
                group_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'group_tf_name': group_tf_name}

            # If description field is empty; put name as description
            if columnname == 'Description':
                if columnvalue == "" or columnvalue == 'nan':
                    columnvalue = df.loc[i,'Name']
                    tempdict = {'description': columnvalue}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
        # Write all info to TF string
        if str(df.loc[i, 'Matching Rule']).lower() == 'nan':
            tfStr[region]=tfStr[region] + template.render(tempStr)
        else:
            tfStr[region] = tfStr[region] + dynamicgroup.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/" + prefix + '-groups.tf'

        if(tfStr[reg]!=''):
            oname[reg]=open(outfile[reg],'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for groups has been created for region "+reg)

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_groups(args.inputfile, args.outdir, args.prefix, config=args.config)

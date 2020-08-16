#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Backup Policy - Block Volume
#
# Author: Shruthi Subramanian
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import os
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######

# If input in cd3 file
def main():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Attaches back up policy to Block Volumes")
    parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf file ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.file
    outdir = args.outdir

    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('block-backup-policy-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "BlockVols")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    reg = df['Region'].unique()

    # Take backup of files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()
        resource='BlockBackupPolicy'
        if (eachregion in commonTools.endNames or eachregion == 'nan'):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-backup-policy.tf")

    for i in df.index:
        region = df.loc[i,"Region"]
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        policy_data_file = outdir + "/"+region+"/oci-backup-policy-data.tf"
        datasource = env.get_template('datasource-template')

        fname=open(policy_data_file,"w+")

        # To add the 'data' resource - required for fetching the policy id
        fname.write(datasource.render())
        fname.close()

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        #Check if values are entered for mandatory fields
        if str(df.loc[i,"Region"]).lower() == 'nan' or str(df.loc[i, 'Block Name']).lower() == 'nan' or str(df.loc[i,'Backup Policy']).lower()  == 'nan':
            print( "The values for Region, Block Name and Backup Policy cannot be left empty. Please enter a value and try again !!")
            exit()

        # Fetch data ; loop through columns
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if (columnname == 'Block Name'):
                columnvalue = commonTools.check_tf_variable(columnvalue)
                blockname_tf = columnvalue
                tempdict = {'block_tf_name' : blockname_tf}

            if (columnname == 'Backup Policy'):
                columnname = 'backup_policy'
                columnvalue = columnvalue.lower()

            columnname = commonTools.check_column_headers(columnname)

            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        #Render template
        backuppolicy =  template.render(tempStr)

        #Write to output file
        file = outdir + "/" + region + "/" + blockname_tf + "-backup-policy.tf"
        oname = open(file, "w+")
        print("Writing " + file)
        oname.write(backuppolicy)
        oname.close()

if __name__ == '__main__':

    # Execution of the code begins here
    main()
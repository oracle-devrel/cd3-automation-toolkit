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
from oci.config import DEFAULT_LOCATION
from pathlib import Path
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description='Attaches back up policy to Block Volumes')
    parser.add_argument('file', help='Full Path of CD3 excel file. eg CD3-template.xlsx in example folder')
    parser.add_argument('outdir', help='directory path for output tf file ')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


# If input in cd3 file
def block_backups_policy(inputfile, outdir, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
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

        if (eachregion in commonTools.endNames):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        resource = 'BlockBackupPolicy'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_block-backup-policy.tf")
        commonTools.backup_file(srcdir,resource,"-block-backup-policy-data.tf")

    policy_done = []
    for i in df.index:
        region = df.loc[i,"Region"]
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        policy_data_file = outdir + "/"+region+"/oci-block-backup-policy-data.tf"
        datasource = env.get_template('backup-policy-data-source-template')
        oci_policy = ["gold","silver","bronze"]
        reg_policy = str(df.loc[i, 'Region']).lower()+"-"+str(df.loc[i, 'Backup Policy']).lower()

        if str(df.loc[i,'Backup Policy']).lower() in oci_policy and  reg_policy not in policy_done:
            if os.path.isfile(policy_data_file):
                with open(policy_data_file) as fname:
                    if "block_"+str(df.loc[i,'Backup Policy']).lower() not in fname.read():
                            policy_data_dict = {'block_tf_policy': str(df.loc[i, 'Backup Policy']).lower(),'policy_tf_compartment': commonTools.check_tf_variable(str(df.loc[i, 'Custom Policy Compartment Name']))}
                            fname=open(policy_data_file,"a+")
                            # To add the 'data' resource - required for fetching the policy id
                            fname.write(datasource.render(policy_data_dict))
                            fname.close()
            else:
                policy_data_dict = {'block_tf_policy': str(df.loc[i, 'Backup Policy']).lower(),'policy_tf_compartment': commonTools.check_tf_variable(str(df.loc[i, 'Custom Policy Compartment Name']))}

                fname = open(policy_data_file, "w+")
                # To add the 'data' resource - required for fetching the policy id
                fname.write(datasource.render(policy_data_dict))
                fname.close()
            policy_done.append(reg_policy)
        else:
            if str(df.loc[i, 'Backup Policy']).lower() not in oci_policy and reg_policy not in policy_done:
                if os.path.isfile(policy_data_file):
                    with open(policy_data_file) as fname:
                        if "block_"+str(df.loc[i, 'Backup Policy']).lower() not in fname.read():
                            policy_data_dict = {'block_tf_policy' : str(df.loc[i,'Backup Policy']).lower(),'policy_tf_compartment' : commonTools.check_tf_variable(str(df.loc[i,'Custom Policy Compartment Name']))}
                            fname = open(policy_data_file, "a+")
                            # To add the 'data' resource - required for fetching the policy id
                            fname.write(datasource.render(policy_data_dict))
                            fname.close()
                else:
                    policy_data_dict = {'block_tf_policy' : str(df.loc[i,'Backup Policy']).lower(),'policy_tf_compartment' : commonTools.check_tf_variable(str(df.loc[i,'Custom Policy Compartment Name']))}
                    fname = open(policy_data_file, "w+")
                    # To add the 'data' resource - required for fetching the policy id
                    fname.write(datasource.render(policy_data_dict))
                    fname.close()
                policy_done.append(reg_policy)


        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}
        policy = ''
        blockname_tf = ''
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
                columnvalue = str(columnvalue).strip()
                if columnvalue != '':
                    columnvalue = columnvalue.lower()
                    policy = commonTools.check_tf_variable(columnvalue)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        #Render template
        if policy != '':
            backuppolicy =  template.render(tempStr)

            #Write to output file
            file = outdir + "/" + region + "/" + blockname_tf + "_block-backup-policy.tf"
            oname = open(file, "w+")
            print("Writing to " + file)
            oname.write(backuppolicy)
            oname.close()

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    block_backups_policy(args.file, args.outdir, args.config)

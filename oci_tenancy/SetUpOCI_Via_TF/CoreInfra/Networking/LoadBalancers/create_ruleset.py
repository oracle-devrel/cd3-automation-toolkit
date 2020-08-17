#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create Rule Set
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import sys
import argparse
import os
import pandas as pd
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######

# If input file is CD3
def main():

    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates Rule Set TF files for LBR")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    rs = env.get_template('rule-set-template')


    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.inputfile
    outdir = args.outdir
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "LB-Listener")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    '''
    #DF with just the load balancer names and the Region details

    # fill the empty values with that in previous row.
    dffill = df[['Region','LBR Name']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','LBR Name']]
    dfdrop = df.drop(dfdrop, axis=1)

    #dfcert with required details
    df = pd.concat([dffill, dfdrop], axis=1)
    '''

    unique_region = df['Region'].unique()

    # Take backup of files
    for eachregion in unique_region:
        eachregion = str(eachregion).strip().lower()
        if (eachregion in commonTools.endNames):
            break
        if eachregion == 'nan':
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        resource='PathRouteSet-RuleSet'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_pathrouteset_lb.tf")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if region.lower() == 'nan':
            continue

        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the values mentioned in VCN Info tab...Exiting!!")
            exit()

        # temporary dictionaries
        tempStr= {}
        tempdict= {}
        lbr_hostname = ''
        rule_set_names = ''
        listener_tf_name = ''
        lbr_tf_name = ''

        #Check if mandatory field is empty
        if (str(df.loc[i,'Listener Name']).lower() == 'nan') or (str(df.loc[i,'Listener Protocol (HTTPS|HTTP|TCP)']).lower() == 'nan') or (str(df.loc[i,'Listener Port']).lower() == 'nan') or (str
            (df.loc[i,'Backend Set Name']).lower() == 'nan') :
            print("\nColumns Backend Set Name, Listener Name, Listerner Protocol and Listener Port cannot be left empty.....Exiting!")
            exit(1)

        # UseSSL cannot be'n', if the protocol is HTTPS
        if (str(df.loc[i,'Listener Protocol (HTTPS|HTTP|TCP)']).upper() == 'HTTPS'):
            if (str(df.loc[i,'UseSSL']).lower() != 'y'):
                print("\nUseSSL must be 'y' if the Listener Protocol is 'HTTPS'......Exiting!!")
                exit(1)

        # Fetch data; loop through columns
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

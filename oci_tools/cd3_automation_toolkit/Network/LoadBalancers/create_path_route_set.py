#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create Path Route Set
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import sys
import argparse
import os
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader


######
# Required Inputs-CD3 excel file, Config file AND outdir
######
def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates Path Route Set TF files for LBR")
    parser.add_argument("inputfile", help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


# If input file is CD3
def create_path_route_set(inputfile, outdir, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    prs = env.get_template('path-route-set-template')
    pathroutes = env.get_template('path-route-rules-template')
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "PathRouteSet")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    #DF with just the load balancer names and the Region details

    # fill the empty values with that in previous row.
    dffill = df[['Region','LBR Name','Path Route Set Name']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','LBR Name','Path Route Set Name']]
    dfdrop = df.drop(dfdrop, axis=1)

    #dfcert with required details
    df = pd.concat([dffill, dfdrop], axis=1)


    # Take backup of files
    for eachregion in ct.all_regions:
        resource = 'PathRouteSet'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_pathrouteset-lb.tf")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    path_route_set_list = []
    prs_str = ''
    srcStr = "#Add_Path_Routes_here"

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
        tempStr = {}
        tempdict = {}
        lbr_tf_name= ''
        path_route_set_tf_name = ''

        # Check if mandatory field is empty
        if (str(df.loc[i, 'Path']).lower() == 'nan') or (str(df.loc[i, 'Backend Set Name']).lower() == 'nan'):
            print("\nColumns Backend Set Name and Path cannot be left empty.....Exiting!")
            exit(1)

        # Fetch data; loop through columns
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "LBR Name":
                lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == "Path Route Set Name":
                path_route_set_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'path_route_set_tf_name': path_route_set_tf_name}

            if columnname == "Backend Set Name":
                backend_set_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'backend_set_tf_name': backend_set_tf_name}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        lbr_path_route_set_name = lbr_tf_name+"_"+path_route_set_tf_name
        if lbr_path_route_set_name != '':
            if lbr_path_route_set_name not in path_route_set_list:
                path_route_set_list.append(lbr_path_route_set_name)
                rule_str = pathroutes.render(tempStr)
                tempdict2 = {'path_routes': rule_str}
                tempStr.update(tempdict2)

                # Render Path Route Set Template
                prs_str = prs.render(tempStr)

                # Write to TF file
                outfile = outdir + "/" + region + "/" + lbr_tf_name + "_" + path_route_set_tf_name + "_pathrouteset-lb.tf"
                oname = open(outfile, "w+")
                print("Writing to " + outfile)
                oname.write(prs_str)
                oname.close()

            else:
                rule_str = pathroutes.render(tempStr)
                tempdict2 = {'path_routes': rule_str}
                tempStr.update(tempdict2)

                #Add the additional Path Routes to the existing Path Route Set
                prs_str = prs_str.replace(srcStr,rule_str)

                # Write to TF file - Update the Routes
                outfile = outdir + "/" + region + "/" + lbr_tf_name + "_" + path_route_set_tf_name + "_pathrouteset-lb.tf"
                oname = open(outfile, "w+")
                oname.write(prs_str)
                oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_path_route_set(args.inputfile, args.outdir, args.config)
#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create Path Route Set
#
# Author: Shruthi Subramanian
# Oracle Consulting
#
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader


######
# Required Inputs-CD3 excel file, Config file AND outdir
######
# Execution of the code begins here
def create_path_route_set(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    prs = env.get_template('path-route-set-template')
    pathrouterules = env.get_template('path-route-rules-template')
    filename = inputfile
    sheetName = "LB-PathRouteSet"
    lb_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

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
    prs_str = {}
    rule_str = {}
    path_route_set_list = {}

    # Take backup of files
    for reg in ct.all_regions:
        prs_str[reg] = ''
        rule_str[reg] = ''
        path_route_set_list[reg] = []
        resource = sheetName.lower()
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, lb_auto_tfvars_filename)

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
            if lbr_path_route_set_name not in path_route_set_list[region]:
                rule_str[region] = ''
                path_route_set_list[region].append(lbr_path_route_set_name)

                # Render Path Route Set Template
                prs_str[region] = prs_str[region] + prs.render(tempStr)

            srcStr = "#Add_Rules_for_" + lbr_path_route_set_name + "_here"
            replacestr = "#Path_routes_for_" + lbr_path_route_set_name + "_here"
            if lbr_path_route_set_name in path_route_set_list[region]:
                if srcStr in rule_str[region]:
                    # Create the remaining rules
                    rule_str[region] = rule_str[region].replace(srcStr, pathrouterules.render(tempStr))

                    if replacestr in prs_str[region]:
                        # Add the first rule to the final string
                        prs_str[region] = prs_str[region].replace(replacestr, rule_str[region])

                    else:
                        # Add the last rule to the final string
                        prs_str[region] = prs_str[region].replace(srcStr, pathrouterules.render(tempStr))

                else:
                    # Create the first rule
                    rule_str[region] = pathrouterules.render(tempStr)
                    prs_str[region] = prs_str[region].replace(replacestr, rule_str[region])


    # Take backup of files
    for reg in ct.all_regions:
        if prs_str[reg] != '':
            # Generate Final String
            src = "##Add New Path Route Sets for "+reg.lower()+" here##"
            prs_str[reg] = prs.render(skeleton=True, count=0, region=reg).replace(src,prs_str[reg]+"\n"+src)
            finalstring = "".join([s for s in prs_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            srcdir = outdir + "/" + reg + "/" + service_dir + "/"

            # Write to TF file
            outfile = srcdir + lb_auto_tfvars_filename
            oname = open(outfile, "w+")
            print("Writing to " + outfile)
            oname.write(finalstring)
            oname.close()


#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create LB Routing Policy
#
# Author: Ulaganathan N
# Oracle Consulting


import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from commonTools import *



def create_lb_routing_policy(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    lb_routing_policy_template = env.get_template('lb-routing-policy-template')
    filename = inputfile
    sheetName = "LB-RoutingPolicy"
    lb_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # DF with just the load balancer names and the Region details
    dffill = df[['Region', 'LBR Name', 'Routing Policy Name']]
    dffill = dffill.fillna(method='ffill')

    # Drop unnecessary columns
    dfdrop = df[['Region', 'LBR Name', 'Routing Policy Name']]
    dfdrop = df.drop(dfdrop, axis=1)

    # dfcert with required details
    df = pd.concat([dffill, dfdrop], axis=1)
    routing_policies = {}
    defined_tags = {}
    freeform_tags = {}

    # Take backup of files
    for reg in ct.all_regions:
        routing_policies[reg] = ''
        defined_tags[reg] = ''
        freeform_tags[reg] = ''
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
        lbr_tf_name = ''
        routing_policy_tf_name = ''

        # Check if mandatory field is empty
        if pd.isna(df.loc[i, 'Rules']):
            print("\nColumn Rules cannot be left empty.....Exiting!")
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
                tempdict = {'load_balancer_id': columnvalue, 'lbr_tf_name':  lbr_tf_name}

            if columnname == "Routing Policy Name":
                routing_policy_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'name': routing_policy_tf_name, 'routing_policy_tf_name': routing_policy_tf_name}

            if columnname == "Rules":
                # Split the string into lines and remove any trailing commas
                rules = [line.strip() for line in columnvalue.split('\n')]
                processed_rules = []

                for rule in rules:
                    parts = [part.strip() for part in rule.split('::')]

                    if len(parts) >= 2:
                        name = parts[0]
                        condition = parts[1]
                        backend_set_name = parts[2] if len(parts) > 2 else ""

                        processed_rules.append({
                            'name': name,
                            'condition': condition,
                            'backend_set_name': backend_set_name
                        })
                tempdict = {'rules': processed_rules}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        routing_policy_name = lbr_tf_name + "_" + routing_policy_tf_name

        if routing_policy_name != '':
            if routing_policy_name not in routing_policies[region]:
                routing_policies[region] = routing_policies[region] + lb_routing_policy_template.render(tempStr)


    # Take backup of files
    for reg in ct.all_regions:
        if routing_policies[reg] != '':
            # Generate Final String
            src = "##Add New Routing Policy for " + reg.lower() + " here##"
            routing_policies[reg] = lb_routing_policy_template.render(skeleton=True, count=0, region=reg).replace(src, routing_policies[reg] + "\n" + src)
            finalstring = "".join([s for s in routing_policies[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            srcdir = outdir + "/" + reg + "/" + service_dir + "/"

            # Write to TF file
            outfile = srcdir + lb_auto_tfvars_filename
            oname = open(outfile, "w+")
            print("Writing to " + outfile)
            oname.write(finalstring)
            oname.close()

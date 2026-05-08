#!/usr/bin/python3
# Copyright (c) 2016, 2024, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# Exadata Infrastructure @AWS
#
# Author: Oracle Consulting
#

import os
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
sys.path.append(os.getcwd()+"/..")
from common.python.commonTools import *
import awscloud.python.awsCommonTools as awsCommonTools


######
# Required Inputs- CD3 excel file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_exa_infra_aws(inputfile, outdir, prefix):

    filename = inputfile
    sheetName = "EXA-Infra-AWS"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'
    resource = sheetName.lower()

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('exa-infra-aws-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    tfStr = ''

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Iterate over rows
    for i in df.index:
        display_name = str(df.loc[i, 'Display Name']).strip()

        # Encountered <End>
        if (display_name in commonTools.endNames):
            break

        if display_name.lower() == 'nan':
            continue

        display_name = display_name.strip()

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Display Name']).lower() == 'nan' or \
                str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Availability Zone ID']).lower() == 'nan' or \
                str(df.loc[i, 'Shape']).lower() == 'nan' or \
                str(df.loc[i, 'Compute Count']).lower() == 'nan' or \
                str(df.loc[i, 'Storage Count']).lower() == 'nan' or \
                str(df.loc[i, 'Database Server Type']).lower() == 'nan' or \
                str(df.loc[i, 'Storage Server Type']).lower() == 'nan':
            print("\nAll fields except Maintenance Window, Customer Contacts and Common Tags are mandatory. Please enter a value and try again !!")
            exit(1)

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in awsCommonTools.awsCommonTools.tagColumns:
                tempdict = awsCommonTools.awsCommonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Display Name":
                display_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_name)
                tempdict = {'display_name': display_name, 'display_tf_name': display_tf_name}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr = tfStr + template.render(tempStr)

    # Write TF string to the file
    if (tfStr != ''):
        outfile = outdir + "/" + auto_tfvars_filename
        commonTools.backup_file(outdir, resource, auto_tfvars_filename)
        src = "##Add New Exa-Infra @AWS here##"
        tfStr = template.render(count=0).replace(src, tfStr + "\n" + src)
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname = open(outfile, 'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for Exa-Infra @AWS has been created")
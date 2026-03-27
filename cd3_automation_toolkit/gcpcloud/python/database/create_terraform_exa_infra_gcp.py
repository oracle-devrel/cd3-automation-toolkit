#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# Database EXA
#
# Author: Suruchi
# Oracle Consulting
#

import os
import re
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
sys.path.append(os.getcwd()+"/..")
from common.python.commonTools import *
import gcpcloud.python.gcpCommonTools as gcpCommonTools


######
# Required Inputs- CD3 excel file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_exa_infra_gcp(inputfile, outdir, prefix):

    filename = inputfile
    sheetName = "EXA-Infra-GCP"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'
    resource = sheetName.lower()

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('exa-infra-gcp-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    tfStr = ''

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Iterate over rows
    for i in df.index:
        location = str(df.loc[i, 'Location']).strip()

        # Encountered <End>
        if (location in commonTools.endNames):
            break

        if location.lower() == 'nan':
            continue

        location=location.strip().lower()

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Location']).lower() == 'nan' or \
                str(df.loc[i, 'GCP Oracle Zone']).lower() == 'nan' or \
                str(df.loc[i, 'Location']).lower() == 'nan' or \
                str(df.loc[i, 'Exadata Infra Display Name']).lower() == 'nan' or \
                str(df.loc[i, 'Shape']).lower() == 'nan':
            print("\nAll fields except Maintenane Window, Maintenance Contact and Labels are mandatory. Please enter a value and try again !!")

            exit(1)

        #tempdict = {'oracle_db_software_edition' : 'ENTERPRISE_EDITION_EXTREME_PERFORMANCE'}

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)


            # Process Defined and Freeform Tags
            if columnname.lower() in gcpCommonTools.tagColumns:
                tempdict = gcpCommonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Exadata Infra Display Name":
                display_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_name)
                cloud_exadata_infrastructure_id = re.sub(r'[^a-z0-9-]', '', display_name.lower())
                tempdict = {'display_name': display_name, 'display_tf_name': display_tf_name, 'cloud_exadata_infrastructure_id' : cloud_exadata_infrastructure_id}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)


        # Write all info to TF string
        tfStr = tfStr + template.render(tempStr)

    # Write TF string to the file
    if (tfStr != ''):
        outfile = outdir + "/" + auto_tfvars_filename
        commonTools.backup_file(outdir, resource, auto_tfvars_filename)
        src = "##Add New Exa-Infra @GCP here##"
        tfStr = template.render(count=0).replace(src, tfStr + "\n" + src)
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname = open(outfile, 'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for Exa-Infra @GCP has been created")
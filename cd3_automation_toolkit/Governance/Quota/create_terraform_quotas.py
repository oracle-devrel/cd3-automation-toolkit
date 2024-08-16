#!/usr/bin/python3
# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Quota
#
# Author: Bhanu P. Lohumi
# Oracle Consulting
#
import os
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_quotas(inputfile, outdir, service_dir, prefix, ct):

    filename = inputfile
    sheetName = "Quotas"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    # Temporary dictionaries
    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    quota_template = env.get_template('quota-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    tfStr[ct.home_region] = ''
    resource = sheetName.lower()
    reg = ct.home_region
    reg_out_dir = outdir + "/" + reg + "/" + service_dir
    commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, "Region"])
        quota_name = str(df.loc[i, "Name"])
        quota_desc = str(df.loc[i, "Description"])
        quota_desc = quota_desc.replace("\n", "\\n") if quota_desc != 'nan' else quota_name
        quota_policy = str(df.loc[i, "Quota Policy"])

        # Encountered <End>
        if region in commonTools.endNames:
            break

        region = region.strip().lower()
        # Exit if mandatory parameters are empty
        if region != 'nan' and region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)

        if quota_policy.strip().lower() == 'nan':
            exit_menu("\n Quota Policy cannot be left empty....Exiting!!")
        if quota_name.strip().lower() == 'nan' :
            exit_menu("\n Quota Name cannot be left empty....Exiting!!")

        # Temporary dictionaries
        tempStr = {}
        tempdict = {}

        # Loop through the columns; used to fetch newdly added columns and values
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df.loc[i, columnname]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Name':
                columnvalue = columnvalue.strip()
                quota_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'name': columnvalue,'quota_tf_name':quota_tf_name}

            if columnname == 'Description':
                tempdict = {'description': quota_desc }

            if columnname == 'Quota Policy':
                actual_quota_policy = []
                for statement in columnvalue.split("\n"):
                    if "\'" in statement:
                        statement = statement.replace("\'", "<single_quote>")
                    actual_quota_policy.append(statement)
                tempdict = {'quota_policy': actual_quota_policy }

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region] = tfStr[region] + quota_template.render(tempStr)

    # Write TF string to the file in respective region directory
    reg = ct.home_region
    reg_out_dir = outdir + "/" + reg + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

    if (tfStr[reg] != ''):
        # Generate Final String
        src = "##Add New quota-policy for "+reg.lower()+" here##"
        tfStr[reg] = quota_template.render(count=0, region=reg).replace(src, tfStr[reg])
        tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        oname[reg] = open(outfile[reg], 'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " for Quotas has been created for region " + reg)


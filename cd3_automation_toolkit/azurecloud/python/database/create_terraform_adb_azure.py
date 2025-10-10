#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# Autonomous Database @Azure
#
# Author: Suruchi
# Oracle Consulting
#
import os
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
sys.path.append(os.getcwd()+"/..")
from common.python.commonTools import *
import azurecloud.python.azrCommonTools as azrCommonTools


######
# Required Inputs- CD3 excel file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_adb_azure(inputfile, outdir, prefix):

    filename = inputfile
    sheetName = "ADB-Azure"
    resource=sheetName.lower()
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('adb-azure-template')

    tfStr=''


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        region=region.strip().lower()

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # All columns ar mandatory except customer contacts and tags
        if (str(df.loc[i, 'Region']).lower() == 'nan' or \
            str(df.loc[i, 'Resource Group Name']).lower() == 'nan' or \
            str(df.loc[i, 'Network Details']).lower() == 'nan' or \
            str(df.loc[i, 'DB Version']).lower() == 'nan'):
            print("\nAll fields except Customer Contacts and Common Tags are mandatory. Please enter a value and try again !!")
            print("\n** Exiting **")
            exit(1)


        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)


            # Process Defined and Freeform Tags
            if columnname.lower() in azrCommonTools.tagColumns:
                tempdict = azrCommonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "ADB Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == "Resource Group Name":
                container_id = columnvalue.strip()
                tempdict = {'container_id': container_id}


            if columnname == 'Database Workload':
                autonomous_value = columnvalue.strip().lower()
                tempdict = {'autonomous_value': autonomous_value}

            if columnname == "Network Details":
                if len(columnvalue.split("@")) == 2:
                    network_container_id = columnvalue.split("@")[0].strip()
                    vcn_subnet_name = columnvalue.split("@")[1].strip()
                else:
                    network_container_id = container_id
                    vcn_subnet_name = columnvalue

                if ("::" not in vcn_subnet_name):
                    print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                    exit(1)
                else:
                    vcn_name = vcn_subnet_name.split("::")[0].strip()
                    subnet_id = vcn_subnet_name.split("::")[1].strip()

                tempdict = {'network_container_id': network_container_id, 'vnet_name': vcn_name,'subnet_id': subnet_id}


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr=tfStr + template.render(tempStr)


    if(tfStr!=''):
        outfile = outdir + "/" + auto_tfvars_filename
        commonTools.backup_file(outdir, resource, auto_tfvars_filename)
        src = "##Add New ADB @Azure here##"
        tfStr= template.render(count=0).replace(src, tfStr + "\n" + src)
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname=open(outfile,'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for ADB @Azure has been created")

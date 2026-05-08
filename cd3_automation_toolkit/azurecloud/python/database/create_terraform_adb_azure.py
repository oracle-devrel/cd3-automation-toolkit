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
            str(df.loc[i, 'ODB Network Details']).lower() == 'nan' or \
            str(df.loc[i, 'ODB Network Subnet Details']).lower() == 'nan' or \
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

            if columnname == "ODB Network Details":
                values = columnvalue.split("::")
                if values[0].strip().upper()=="CREATE":
                    if len(values) !=5 :
                        print("Invalid Value for ODB Network Details. Exiting!!")
                        exit(1)
                    create_odb_network="true"
                    network_resource_group_name = values[1].strip()
                    vnet_name = values[2].strip()
                    vnet_cidr = values[4].strip()
                    network_az_region = values[3].strip()

                else:
                    create_odb_network = "false"
                    network_resource_group_name = values[0].strip()
                    vnet_name = values[1].strip()
                    vnet_cidr = ""
                    network_az_region=""

                tempdict = {'create_odb_network': create_odb_network, 'network_resource_group_name': network_resource_group_name,
                            'vnet_name': vnet_name, 'vnet_cidr': vnet_cidr,
                            'network_az_region': network_az_region}
            if columnname == "ODB Network Subnet Details":
                values = columnvalue.split("::")
                delegated_subnet_name = values[0].strip()
                if len(values)==2:
                    subnet_cidr = values[1].strip()
                else:
                    subnet_cidr=""


                tempdict = {'delegated_subnet_name': delegated_subnet_name, 'subnet_cidr': subnet_cidr}

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

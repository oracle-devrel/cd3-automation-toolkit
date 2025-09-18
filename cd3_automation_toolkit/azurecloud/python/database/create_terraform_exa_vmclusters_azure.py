#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# Database EXA
#
# Author: Kartikey Rajput
# Oracle Consulting
# Modified (TF Upgrade): Kartikey Rajput
#
import os
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
sys.path.append(os.getcwd()+"/..")
from common.python.commonTools import *
import azurecloud.python.azrCommonTools as azrCommonTools


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_exa_vmclusters_azure(inputfile, outdir, prefix):
    filename = inputfile

    sheetName = "EXA-VMClusters-Azure"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'
    resource = sheetName.lower()


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('exa-vmcluster-azure-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    tfStr = ''

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    #subnets = parseSubnets(filename)


    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region.lower() == 'nan':
            continue

        region = region.strip().lower()


        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}


        # Check if values are entered for mandatory fields
        '''
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'Exadata Infra Display Name']).lower() == 'nan' or \
                str(df.loc[i, 'VM Cluster Display Name']).lower() == 'nan' or \
                str(df.loc[i, 'Client Network Details']).lower() == 'nan' or \
                str(df.loc[i, 'Backup Network Details']).lower() == 'nan' or \
                str(df.loc[i, 'CPU Core Count']).lower() == 'nan' or \
                str(df.loc[i, 'SSH Key Var Name']).lower() == 'nan' or \
                str(df.loc[i, 'Hostname Prefix']).lower() == 'nan' or \
                str(df.loc[i, 'Oracle Grid Infrastructure Version']).lower() == 'nan':
                print("\nRegion, Compartment Name, Exadata Infra Display Name, VM Cluster Display Name, Network Details, CPU Core Count, Hostname Prefix, Oracle Grid Infrastructure Version, SSH Key Var Name are mandatory fields. Please enter a value and try again.......Exiting!!")
                exit(1)
        '''

        # tempdict = {'oracle_db_software_edition' : 'ENTERPRISE_EDITION_EXTREME_PERFORMANCE'}

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            if columnname == "Resource Group Name":
                container_id = columnvalue.strip()
                tempdict = {'container_id': container_id}

            if columnname == "VM Cluster Display Name":
                display_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_name)
                tempdict = {'display_tf_name': display_tf_name, 'display_name': display_name}

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


            # Process Defined and Freeform Tags
            if columnname.lower() in azrCommonTools.tagColumns:
                tempdict = azrCommonTools.split_tag_values(columnname, columnvalue, tempdict)


            if columnname == "Exadata Infra Display Name":
                exadata_infrastructure_name = columnvalue.strip()
                tempdict = {'exadata_infrastructure_name': exadata_infrastructure_name}


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)



        # Write all info to TF string
        tfStr = tfStr + template.render(tempStr)

    # Write TF string to the file
    if (tfStr != ''):
        outfile = outdir + "/" + auto_tfvars_filename
        commonTools.backup_file(outdir, resource, auto_tfvars_filename)
        src = "##Add New Exa-VMCluster @Azure here##"
        tfStr = template.render(count=0).replace(src, tfStr + "\n" + src)
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname = open(outfile, 'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for Exa-VMCluster @Azure has been created")
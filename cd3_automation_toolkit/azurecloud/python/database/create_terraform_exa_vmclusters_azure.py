#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# Database EXA VM Cluster @Azure
#
# Author: Suruchi
# Oracle Consulting

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
                str(df.loc[i, 'ODB Network Details']).lower() == 'nan' or \
                str(df.loc[i, 'ODB Network Subnet Details']).lower() == 'nan' or \
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

            if columnname == "ODB Network Details":
                values = columnvalue.split("::")
                if values[0].strip().upper() == "CREATE":
                    if len(values) != 5:
                        print("Invalid Value for ODB Network Details. Exiting!!")
                        exit(1)
                    create_odb_network = "true"
                    network_resource_group_name = values[1].strip()
                    vnet_name = values[2].strip()
                    vnet_cidr = values[4].strip()
                    network_az_region = values[3].strip()

                else:
                    create_odb_network = "false"
                    network_resource_group_name = values[0].strip()
                    vnet_name = values[1].strip()
                    vnet_cidr = ""
                    network_az_region = ""

                tempdict = {'create_odb_network': create_odb_network,
                            'network_resource_group_name': network_resource_group_name,
                            'vnet_name': vnet_name, 'vnet_cidr': vnet_cidr,
                            'network_az_region': network_az_region}
            if columnname == "ODB Network Subnet Details":
                values = columnvalue.split("::")
                delegated_subnet_name = values[0].strip()
                if len(values) == 2:
                    subnet_cidr = values[1].strip()
                else:
                    subnet_cidr = ""

                tempdict = {'delegated_subnet_name': delegated_subnet_name, 'subnet_cidr': subnet_cidr}

            # Process Defined and Freeform Tags
            if columnname.lower() in azrCommonTools.tagColumns:
                tempdict = azrCommonTools.split_tag_values(columnname, columnvalue, tempdict)


            if columnname == "Exadata Infra Display Name":
                exadata_infrastructure_name = columnvalue.strip()
                tempdict = {'exadata_infrastructure_name': exadata_infrastructure_name}

            if columnname == "File System Configurations":
                if columnvalue.lower()!="nan" and columnvalue.lower()!='':
                    values=columnvalue.split(";")
                    j = 0
                    file_system_configurations = {}
                    for value in values:
                        if value == "":
                            break
                        j=j+1

                        mount_point= value.split("::")[0].strip()
                        size_in_gb = value.split("::")[1].strip()
                        file_system_configurations["file" + str(j)] = [mount_point, size_in_gb]
                        tempdict = {'file_system_configurations': file_system_configurations}
                        tempStr.update(tempdict)


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
#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# Database EXA VM Cluster @GCP
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
def create_terraform_exa_vmclusters_gcp(inputfile, outdir, prefix):
    filename = inputfile

    sheetName = "EXA-VMClusters-GCP"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'
    resource = sheetName.lower()


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('exa-vmcluster-gcp-template')

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
        location = str(df.loc[i, 'Location']).strip()

        # Encountered <End>
        if (location in commonTools.endNames):
            break

        if location.lower() == 'nan':
            continue

        location = location.strip().lower()


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


            if columnname == "VM Cluster Display Name":
                display_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_name)
                cloud_vm_cluster_id = re.sub(r'[^a-z0-9-]', '', display_name.lower())
                tempdict = {'display_tf_name': display_tf_name, 'display_name': display_name,'cloud_vm_cluster_id':cloud_vm_cluster_id}

            if columnname == "Exadata Infra Display Name":
                display_name = columnvalue.strip()
                exa_project=str(df.loc[i, 'Project']).strip()
                exa_name=display_name

                if "@" in display_name:
                    names = display_name.split("@")
                    exa_project = names[0].strip()
                    exa_name = names[1].strip()

                cloud_exadata_infrastructure_id = re.sub(r'[^a-z0-9-]', '', exa_name.lower())
                tempdict = {'exadata_infrastructure_project': exa_project,'exadata_infrastructure_id_from_name' : cloud_exadata_infrastructure_id}


            if columnname == "ODB Network Details":
                values = columnvalue.split("::")
                if len(values)<3:
                    print("Invalid Value for ODB Network Details. Exiting!!")
                    exit(1)

                if values[0].strip().upper()=="CREATE":
                    if len(values) !=5 :
                        print("Invalid Value for ODB Network Details. Exiting!!")
                        exit(1)
                    create_odb_network="true"
                    odb_network_project = values[1].strip()
                    vpc_network_name = values[2].strip()
                    odb_network_id = values[3].strip()
                    odb_network_gcp_oracle_zone = values[4].strip()

                else:
                    create_odb_network = "false"
                    odb_network_project = values[0].strip()
                    vpc_network_name = values[1].strip()
                    odb_network_id = values[2].strip()
                    if (len(values) == 4):
                        odb_network_gcp_oracle_zone = values[3].strip()
                    else:
                        odb_network_gcp_oracle_zone=""

                tempdict = {'create_odb_network': create_odb_network, 'odb_network_project': odb_network_project,
                            'vpc_network_name': vpc_network_name, 'odb_network_id': odb_network_id,
                            'odb_network_gcp_oracle_zone': odb_network_gcp_oracle_zone}

            if columnname == "ODB Network Subnets Details":
                values = columnvalue.split("::")
                if len(values) < 4:
                    print("Invalid Value for ODB Network Subnets Details. Exiting!!")
                    exit(1)

                if values[0].strip().upper() == "CREATE":
                    if len(values) !=5 :
                        print("Invalid Value for ODB Network Subnets Details. Exiting!!")
                        exit(1)
                    create_odb_network_subnets = "true"
                    odb_client_subnet_id = values[1].strip()
                    client_subnet_cidr = values[2].strip()
                    odb_backup_subnet_id = values[3].strip()
                    backup_subnet_cidr = values[4].strip()

                else:
                    create_odb_network_subnets = "false"
                    odb_client_subnet_id = values[0].strip()
                    client_subnet_cidr = ""
                    odb_backup_subnet_id=values[2].strip()
                    backup_subnet_cidr=""

                tempdict = {'create_odb_network_subnets': create_odb_network_subnets,'odb_client_subnet_id':odb_client_subnet_id,'client_subnet_cidr':client_subnet_cidr,'odb_backup_subnet_id':odb_backup_subnet_id,'backup_subnet_cidr':backup_subnet_cidr}


            # Process Defined and Freeform Tags
            if columnname.lower() in gcpCommonTools.tagColumns:
                tempdict = gcpCommonTools.split_tag_values(columnname, columnvalue, tempdict)


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr = tfStr + template.render(tempStr)

    # Write TF string to the file
    if (tfStr != ''):
        outfile = outdir + "/" + auto_tfvars_filename
        commonTools.backup_file(outdir, resource, auto_tfvars_filename)
        src = "##Add New Exa-VMCluster @GCP here##"
        tfStr = template.render(count=0).replace(src, tfStr + "\n" + src)
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname = open(outfile, 'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for Exa-VMCluster @GCP has been created")
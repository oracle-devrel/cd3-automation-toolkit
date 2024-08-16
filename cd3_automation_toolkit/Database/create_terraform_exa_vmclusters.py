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
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_exa_vmclusters(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile

    sheetName = "EXA-VMClusters"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('exa-vmclusters-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    #subnets = parseSubnets(filename)

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    regions_done_count = []

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region.lower() == 'nan':
            continue

        region = region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}
        nsg_id = ''
        db_server_id = ''
        backup_nsg_id = ''

        # Check if values are entered for mandatory fields
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

        # tempdict = {'oracle_db_software_edition' : 'ENTERPRISE_EDITION_EXTREME_PERFORMANCE'}

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {columnname: columnvalue}

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "VM Cluster Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'vm_cluster_display_tf_name': display_tf_name}

            if columnname == "Exadata Infra Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'exadata_infra_display_tf_name': display_tf_name}

            subnet_id = ''
            network_compartment_id = ''
            vcn_name = ''
            if columnname == 'Client Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    network_compartment_id = "root"
                    vcn_name = ""
                    subnet_id = columnvalue
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(
                            str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                tempdict = {'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                            'client_subnet_name': subnet_id}

            subnet_id = ''
            network_compartment_id = ''
            vcn_name = ''
            if columnname == 'Backup Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    network_compartment_id = "root"
                    vcn_name = ""
                    subnet_id = columnvalue
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()

                tempdict = {'backup_subnet_name': subnet_id}

            if columnname == 'NSGs':
                if columnvalue != '':
                    db_nsgs = str(columnvalue).strip().split(",")
                    if len(db_nsgs) == 1:
                        for nsg in db_nsgs:
                            nsg_id = "\"" + nsg.strip() + "\""

                    elif len(db_nsgs) >= 2:
                        c = 1
                        for nsg in db_nsgs:
                            data = "\"" + nsg.strip() + "\""

                            if c == len(db_nsgs):
                                nsg_id = nsg_id + data
                            else:
                                nsg_id = nsg_id + data + ","
                            c += 1
                columnvalue = nsg_id

            if columnname == 'DB Servers':
                if columnvalue != '':
                    db_servers = str(columnvalue).strip().split(",")
                    if len(db_servers) == 1:
                        for db_server in db_servers:
                            db_server_id = "\"" + db_server.strip() + "\""

                    elif len(db_servers) >= 2:
                        c = 1
                        for db_server in db_servers:
                            data = "\"" + db_server.strip() + "\""

                            if c == len(db_servers):
                                db_server_id = db_server_id + data
                            else:
                                db_server_id = db_server_id + data + ","
                            c += 1
                columnvalue = db_server_id


            if columnname == 'Backup Network NSGs':
                if columnvalue != '':
                    backup_nsgs = str(columnvalue).strip().split(",")
                    if len(backup_nsgs) == 1:
                        for nsgs in backup_nsgs:
                            backup_nsg_id = "\"" + nsgs.strip() + "\""

                    elif len(backup_nsgs) >= 2:
                        c = 1
                        for nsgs in backup_nsgs:
                            data = "\"" + nsgs.strip() + "\""

                            if c == len(backup_nsgs):
                                backup_nsg_id = backup_nsg_id + data
                            else:
                                backup_nsg_id = backup_nsg_id + data + ","
                            c += 1
                columnvalue = backup_nsg_id

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if (region not in regions_done_count):
            tempdict = {"count": 0}
            regions_done_count.append(region)
        else:
            tempdict = {"count": i}
        tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region] = tfStr[region][:-1] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

        if (tfStr[reg] != ''):
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for EXA-VMClusters has been created for region " + reg)

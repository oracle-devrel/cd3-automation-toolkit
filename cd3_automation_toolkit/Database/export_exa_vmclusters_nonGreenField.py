#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI Database
# EXA VM Cluster
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import oci
import os
import json
import re
import subprocess as sp
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader

importCommands = {}
oci_obj_names = {}


def print_exa_vmcluster(region, vnc_client,exa_infra, exa_vmcluster, key_name,values_for_column, ntk_compartment_name, db_servers,state,ct):
    exa_infra_tf_name = commonTools.check_tf_variable(exa_infra.display_name)
    exa_vmcluster_tf_name = commonTools.check_tf_variable(exa_vmcluster.display_name)

    exa_vmcluster_client_subnet_id = exa_vmcluster.subnet_id
    client_subnet_info = vnc_client.get_subnet(exa_vmcluster_client_subnet_id)
    client_subnet_name = client_subnet_info.data.display_name  # Subnet-Name
    client_vcn_name = vnc_client.get_vcn(client_subnet_info.data.vcn_id).data.display_name  # vcn-Name
    ntk_compartment_id = vnc_client.get_vcn(client_subnet_info.data.vcn_id).data.compartment_id  # compartment-id
    network_compartment_name = ntk_compartment_name
    for comp_name, comp_id in ct.ntk_compartment_ids.items():
        if comp_id == ntk_compartment_id:
            network_compartment_name = comp_name
    client_network = network_compartment_name + "@" + client_vcn_name + "::" + client_subnet_name

    exa_vmcluster_backup_subnet_id = exa_vmcluster.backup_subnet_id
    backup_subnet_info = vnc_client.get_subnet(exa_vmcluster_backup_subnet_id)
    backup_subnet_name = backup_subnet_info.data.display_name  # Subnet-Name
    backup_vcn_name = vnc_client.get_vcn(backup_subnet_info.data.vcn_id).data.display_name  # vcn-Name
    ntk_compartment_id = vnc_client.get_vcn(backup_subnet_info.data.vcn_id).data.compartment_id  # compartment-id
    network_compartment_name = ntk_compartment_name
    for comp_name, comp_id in ct.ntk_compartment_ids.items():
        if comp_id == ntk_compartment_id:
            network_compartment_name = comp_name
    backup_network = network_compartment_name + "@" + backup_vcn_name + "::" + backup_subnet_name


    NSGs = exa_vmcluster.nsg_ids
    nsg_names = ""
    if (NSGs is not None and len(NSGs)):
        for j in NSGs:
            nsg_info = vnc_client.get_network_security_group(j)
            nsg_names = nsg_names + "," + nsg_info.data.display_name
        nsg_names = nsg_names[1:]

    Backup_NSGs = exa_vmcluster.backup_network_nsg_ids
    backup_nsg_names = ""
    if (Backup_NSGs is not None and len(Backup_NSGs)):
        for j in Backup_NSGs:
            nsg_info = vnc_client.get_network_security_group(j)
            backup_nsg_names = backup_nsg_names + "," + nsg_info.data.display_name
        backup_nsg_names = backup_nsg_names[1:]


    maintenance_window = exa_infra.maintenance_window
    tf_resource = f'module.exa-vmclusters[\\"{exa_vmcluster_tf_name}\\"].oci_database_cloud_vm_cluster.exa_vmcluster'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(exa_vmcluster.id)}'

    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'Exadata Infra Display Name':
            values_for_column[col_header].append(exa_infra.display_name)
        elif col_header == 'SSH Key Var Name':
            values_for_column[col_header].append(key_name)
        elif col_header == 'Client Network Details':
            values_for_column[col_header].append(client_network)
        elif col_header == 'Backup Network Details':
            values_for_column[col_header].append(backup_network)
        elif (col_header == "NSGs"):
            values_for_column[col_header].append(nsg_names)
        elif (col_header == "Backup Network NSGs"):
            values_for_column[col_header].append(backup_nsg_names)
        elif (col_header == "DB Servers"):
            values_for_column[col_header].append(db_servers)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(exa_vmcluster, col_header, values_for_column)
        else:
            oci_objs = [exa_vmcluster,exa_infra]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

# Execution of the code begins here


def export_exa_vmclusters(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[],export_regions=[],export_tags=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global cd3file
    global reg
    global values_for_column,tf_or_tofu

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]


    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = 'EXA-VMClusters'

    var_data ={}

    # Read CD3
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Exa-VMClusters  will be overwritten during export process!!!\n")

    # Load variables template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent.parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch Block Volume Details
    print("\nFetching details of Exadata VM Clusters...")

    for reg in export_regions:
        var_data[reg] = ""

        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        region = reg.capitalize()

        db_client = oci.database.DatabaseClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        vnc_client = oci.core.VirtualNetworkClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)

        db={}
        for ntk_compartment_name in export_compartments:
            exa_infras = oci.pagination.list_call_get_all_results(db_client.list_cloud_exadata_infrastructures,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="AVAILABLE")
            for exa_infra in exa_infras.data:
                # Tags filter
                defined_tags = exa_infra.defined_tags
                tags_list = []
                for tkey, tval in defined_tags.items():
                    for kk, vv in tval.items():
                        tag = tkey + "." + kk + "=" + vv
                        tags_list.append(tag)

                if export_tags == []:
                    check = True
                else:
                    check = any(e in tags_list for e in export_tags)
                # None of Tags from export_tags exist on this instance; Dont export this instance
                if check == False:
                    continue

                for ntk_compartment_name_again in export_compartments:
                    exa_vmclusters = oci.pagination.list_call_get_all_results(db_client.list_cloud_vm_clusters,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], cloud_exadata_infrastructure_id=exa_infra.id, lifecycle_state="AVAILABLE")
                    for exa_vmcluster in exa_vmclusters.data:
                        # Tags filter
                        defined_tags = exa_vmcluster.defined_tags
                        tags_list = []
                        for tkey, tval in defined_tags.items():
                            for kk, vv in tval.items():
                                tag = tkey + "." + kk + "=" + vv
                                tags_list.append(tag)

                        if export_tags == []:
                            check = True
                        else:
                            check = any(e in tags_list for e in export_tags)
                        # None of Tags from export_tags exist on this instance; Dont export this instance
                        if check == False:
                            continue

                        # Get ssh keys for exa vm cluster
                        key_name = commonTools.check_tf_variable(exa_vmcluster.display_name + "_" + exa_vmcluster.hostname)
                        db_ssh_keys = exa_vmcluster.ssh_public_keys
                        db_ssh_keys = json.dumps(db_ssh_keys)
                        db[key_name] = db_ssh_keys

                        db_serverids = exa_vmcluster.db_servers
                        db_servers = ''
                        if (db_serverids is not None and len(db_serverids)):
                            for db_server in db_serverids:
                                db_server_name = db_client.get_db_server(exa_infra.id, db_server).data.display_name
                                db_servers = db_server_name +","+db_servers
                            db_servers=db_servers.removesuffix(',')

                        print_exa_vmcluster(region, vnc_client, exa_infra,exa_vmcluster,key_name, values_for_column, ntk_compartment_name_again,db_servers,state,ct)

        file = f'{outdir}/{reg}/{service_dir}/variables_{reg}.tf'
        # Read variables file data
        with open(file, 'r') as f:
            var_data[reg] = f.read()

        tempStr = ""
        for k, v in db.items():
            tempStr = "\t"+k +" = " + v +"\n" +tempStr

        tempStr = "\n"+tempStr
        tempStr = "#START_exacs_ssh_keys#" + tempStr + "\t#exacs_ssh_keys_END#"
        var_data[reg] = re.sub('#START_exacs_ssh_keys#.*?#exacs_ssh_keys_END#', tempStr, var_data[reg],
                               flags=re.DOTALL)

        # Write variables file data
        with open(file, "w") as f:
            f.write(var_data[reg])

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} Exadata VM Clusters exported into CD3.\n".format(len(values_for_column["Region"])))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for Exadata VM Clusters #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])


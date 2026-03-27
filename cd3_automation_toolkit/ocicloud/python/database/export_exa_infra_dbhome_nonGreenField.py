#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI Database
# EXA Infra DBHome
#
# Author: Praseed M C
# Oracle Consulting
#

import oci
import os, sys
import subprocess as sp
sys.path.append(os.getcwd() + "../")
from common.python.commonTools import *
import ocicloud.python.ociCommonTools as ociCommonTools

importCommands = {}
oci_obj_names = {}


def print_exa_dbhome(region, exa_dbhome,vm_cluster,exadata_infrastructure,exa_infra_compartment_name,values_for_column, ntk_compartment_name,state):
    exa_dbhome_tf_name = commonTools.check_tf_variable(exa_dbhome.display_name)
    tf_resource = f'module.db-homes[\\"{vm_cluster.data.display_name}_{exa_dbhome_tf_name}\\"].oci_database_db_home.database_db_home'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(exa_dbhome.id)}'
    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'Exadata Infra Display Name':
            exa_infra_name = f"{exa_infra_compartment_name}@{exadata_infrastructure.data.display_name}"
            values_for_column[col_header].append(exa_infra_name)
        elif col_header == 'VM Cluster Display Name':
            exa_vlcluster_name = vm_cluster.data.display_name
            values_for_column[col_header].append(exa_vlcluster_name)
        elif col_header == 'DB Home Name':
            db_home_name = exa_dbhome.display_name
            values_for_column[col_header].append(db_home_name)
        elif col_header == 'DB Version':
            db_version = exa_dbhome.db_version
            values_for_column[col_header].append(db_version)
        elif col_header.lower() in ociCommonTools.tagColumns:
            values_for_column = ociCommonTools.export_tags(exa_dbhome, col_header, values_for_column)

# Execution of the code begins here


def export_exa_dbhome(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[],export_tags=[]):
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

    sheetName = 'EXA-DBHomes'
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- EXA-DBHomes  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch Block Volume Details
    print("\nFetching details of Exadata Infra DB Homes...")

    for reg in export_regions:
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

        for ntk_compartment_name in export_compartments:
            exa_dbhomes = oci.pagination.list_call_get_all_results(db_client.list_db_homes,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="AVAILABLE")
            for exa_dbhome in exa_dbhomes.data:
                if exa_dbhome.vm_cluster_id:
                    vm_cluster = db_client.get_cloud_vm_cluster(cloud_vm_cluster_id=exa_dbhome.vm_cluster_id)
                    exadata_infrastructure = db_client.get_cloud_exadata_infrastructure(cloud_exadata_infrastructure_id=vm_cluster.data.cloud_exadata_infrastructure_id)
                    #print("exa_data",exadata_infrastructure.data)
                    #print("comp_data",ct.ntk_compartment_ids)
                    exa_infra_compartment_name = next((name for name, ocid in ct.ntk_compartment_ids.items() if ocid == exadata_infrastructure.data.compartment_id), None)

                    # Tags filter
                    defined_tags = exa_dbhome.defined_tags
                    tags_list = []
                    if defined_tags:
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

                    print_exa_dbhome(region, exa_dbhome,vm_cluster,exadata_infrastructure,exa_infra_compartment_name,values_for_column, ntk_compartment_name,state)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} Exadata DB Homes exported into CD3.\n".format(len(values_for_column["Region"])))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for Exadata Infra DBHomes #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])



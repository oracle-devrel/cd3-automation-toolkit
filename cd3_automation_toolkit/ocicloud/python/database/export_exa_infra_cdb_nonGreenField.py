#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI Database
# EXA Infra CDB
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


def print_exa_cdb(region,exadata_infrastructure,exa_infra_compartment_name,vm_cluster,exa_dbhome, exa_cdb,values_for_column, ntk_compartment_name,state):
    exa_cdb_tf_name = commonTools.check_tf_variable(exa_cdb.db_name)
    exa_dbhome_tf_name = commonTools.check_tf_variable(exa_dbhome.display_name)
    tf_resource = f'module.databases[\\"{exa_dbhome_tf_name}_{exa_cdb_tf_name}\\"].oci_database_database.database_database'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(exa_cdb.id)}'

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
        #elif col_header == 'DB Version':
            #db_version = exa_dbhome.db_version
            #values_for_column[col_header].append(db_version)
        elif col_header == 'CDB Name':
            cdb_name = exa_cdb.db_name
            values_for_column[col_header].append(cdb_name)
        elif col_header == 'DB Unique Name':
            db_unique_name = exa_cdb.db_unique_name
            values_for_column[col_header].append(db_unique_name)
        elif col_header == 'Default PDB Name':
            default_pdb_name = exa_cdb.pdb_name
            values_for_column[col_header].append(default_pdb_name)
        elif col_header == 'SID Prefix':
            sid_prefix = exa_cdb.sid_prefix
            values_for_column[col_header].append(sid_prefix)
        elif col_header == 'Character Set':
            character_set = exa_cdb.character_set
            values_for_column[col_header].append(character_set)
        elif col_header == 'Ncharacter Set':
            ncharacter_set = exa_cdb.ncharacter_set
            values_for_column[col_header].append(ncharacter_set)

        elif col_header in ('Admin Password', 'TDE Wallet Password'):
            values_for_column[col_header].append("")

        if exa_cdb.db_backup_config:
            if col_header == 'Auto Backup Enabled':
                    auto_backup_enabled = exa_cdb.db_backup_config.auto_backup_enabled
                    values_for_column[col_header].append(auto_backup_enabled)

            if col_header == 'Backup Dest Type':
                if exa_cdb.db_backup_config.backup_destination_details:
                    backup_destination_details = exa_cdb.db_backup_config.backup_destination_details[0].type
                    values_for_column[col_header].append(backup_destination_details)
                else:
                    backup_destination_details = ""
                    values_for_column[col_header].append(backup_destination_details)
            if col_header == 'DBRS policy ID':
                if exa_cdb.db_backup_config.backup_destination_details:
                    dbrs_policy_id = exa_cdb.db_backup_config.backup_destination_details[0].dbrs_policy_id
                    values_for_column[col_header].append(dbrs_policy_id)
                else:
                    backup_destination_details = ""
                    values_for_column[col_header].append(backup_destination_details)

            if col_header == 'Recovery Window in Days':
                recovery_window_in_days = exa_cdb.db_backup_config.recovery_window_in_days
                values_for_column[col_header].append(recovery_window_in_days)

            if col_header == 'Auto Full Backup Day':
                auto_full_backup_day = exa_cdb.db_backup_config.auto_full_backup_day
                values_for_column[col_header].append(auto_full_backup_day)

            if col_header == 'Auto Full Backup Window':
                auto_full_backup_window = exa_cdb.db_backup_config.auto_full_backup_window
                values_for_column[col_header].append(auto_full_backup_window)

            if col_header == 'Auto Backup Window':
                auto_backup_window = exa_cdb.db_backup_config.auto_backup_window
                values_for_column[col_header].append(auto_backup_window)

            if col_header == 'Backup Deletion Policy':
                backup_deletion_policy = exa_cdb.db_backup_config.backup_deletion_policy
                values_for_column[col_header].append(backup_deletion_policy)

            if col_header == 'Run Immediate Full Backup':
                run_immediate_full_backup = exa_cdb.db_backup_config.run_immediate_full_backup

                if run_immediate_full_backup == "":
                    run_immediate_full_backup = "false"

                values_for_column[col_header].append(run_immediate_full_backup)

        else:
            if col_header == 'Auto Backup Enabled':
                auto_backup_enabled = False
                values_for_column[col_header].append(auto_backup_enabled)

            if col_header == 'Backup Dest Type':
                backup_destination_details = ""
                values_for_column[col_header].append(backup_destination_details)
            if col_header == 'DBRS policy ID':
                backup_destination_details = ""
                values_for_column[col_header].append(backup_destination_details)

            if col_header == 'Recovery Window in Days':
                recovery_window_in_days = ""
                values_for_column[col_header].append(recovery_window_in_days)
            if col_header == 'Auto Full Backup Day':
                auto_full_backup_day = ""
                values_for_column[col_header].append(auto_full_backup_day)

            if col_header == 'Auto Full Backup Window':
                auto_full_backup_window = ""
                values_for_column[col_header].append(auto_full_backup_window)

            if col_header == 'Auto Backup Window':
                auto_backup_window = ""
                values_for_column[col_header].append(auto_backup_window)

            if col_header == 'Backup Deletion Policy':
                backup_deletion_policy = ""
                values_for_column[col_header].append(backup_deletion_policy)

            if col_header == 'Run Immediate Full Backup':
                run_immediate_full_backup = False
                values_for_column[col_header].append(run_immediate_full_backup)

        if col_header.lower() in ociCommonTools.tagColumns:
            values_for_column = ociCommonTools.export_tags(exa_cdb, col_header, values_for_column)

# Execution of the code begins here


def export_exa_cdb(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[],export_tags=[]):
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

    sheetName = 'EXA-CDBs'
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- EXA-CDBs  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch Block Volume Details
    print("\nFetching details of Exadata Infra CDBs...")

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
                    exa_cdbs = oci.pagination.list_call_get_all_results(db_client.list_databases,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],db_home_id=exa_dbhome.id, lifecycle_state="AVAILABLE")
                    for exa_cdb in exa_cdbs.data:
                        vm_cluster = db_client.get_cloud_vm_cluster(cloud_vm_cluster_id=exa_cdb.vm_cluster_id)
                        exadata_infrastructure = db_client.get_cloud_exadata_infrastructure(cloud_exadata_infrastructure_id=vm_cluster.data.cloud_exadata_infrastructure_id)
                        exa_infra_compartment_name = next((name for name, ocid in ct.ntk_compartment_ids.items() if
                                                           ocid == exadata_infrastructure.data.compartment_id), None)
                        # Tags filter
                        defined_tags = exa_cdb.defined_tags
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

                        print_exa_cdb(region,exadata_infrastructure,exa_infra_compartment_name,vm_cluster,exa_dbhome, exa_cdb,values_for_column, ntk_compartment_name,state)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} Exadata CDBs exported into CD3.\n".format(len(values_for_column["Region"])))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for Exadata CDBs #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])



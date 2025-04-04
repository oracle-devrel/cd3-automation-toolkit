#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export KMS Objects from OCI
# Keys & Vaults

# Author: Lasya Vadavalli
# Oracle Consulting
#
import sys
import oci
from oci.key_management import KmsVaultClient
import os
import subprocess as sp
sys.path.append(os.getcwd() + "/..")
from commonTools import *
from oci.exceptions import TransientServiceError

# Execution of the code begins here
def export_keyvaults(inputfile, outdir, service_dir, config, signer, ct, export_regions=[], export_compartments=[],export_tags=[]):
    global values_for_column_kms
    global cd3file,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    comp_id_list = list(ct.ntk_compartment_ids.values())
    comp_name_list = list(ct.ntk_compartment_ids.keys())


    cd3file = inputfile

    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "KMS"

    # Read CD3 KMS Sheets
    df, values_for_column_kms = commonTools.read_cd3(cd3file, sheetName)
    sheet_dict_kms = ct.sheet_dict[sheetName]


    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- KMS would be overwritten during export process!!!\n")

    total_vaults = 0
    total_keys = 0

    print("\nFetching KMS Vaults and Keys...")
    for reg in export_regions:
        importCommands = ""
        region = reg.lower()
        script_file = f'{outdir}/{region}/{service_dir}/import_commands_kms.sh'
        # create backups
        if os.path.exists(script_file):
            commonTools.backup_file(os.path.dirname(script_file), "tf_import_kms", os.path.basename(script_file))

        config["region"] = ct.region_dict[reg]
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        kms_vault_client = KmsVaultClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        for ntk_compartment_name in export_compartments:

            vaults = oci.pagination.list_call_get_all_results(kms_vault_client.list_vaults,
                                                              compartment_id=ct.ntk_compartment_ids[
                                                                  ntk_compartment_name])

            for vault in vaults.data:
                get_vault_data = kms_vault_client.get_vault(vault_id=vault.id).data
                key_count = 0
                if vault.lifecycle_state not in ["DELETED", "PENDING_DELETION", "SCHEDULING_DELETION"]:
                    # Tags filter
                    defined_tags = get_vault_data.defined_tags
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

                    try:
                        replicas = kms_vault_client.list_vault_replicas(vault_id=vault.id).data
                        for replica in replicas:
                            region_name = None
                            for region, region_identifier in ct.region_dict.items():
                                if region_identifier == replica.region:
                                    region_name = region
                                    break
                        kms_key_client = oci.key_management.KmsManagementClient(config,service_endpoint=vault.management_endpoint,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
                        keys = oci.pagination.list_call_get_all_results(kms_key_client.list_keys, compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name])
                        total_vaults += 1
                        vault_tf_name = commonTools.check_tf_variable(vault.display_name)
                        tf_resource = f'module.vaults[\\"{vault_tf_name}\\"].oci_kms_vault.vault'
                        if tf_resource not in state["resources"]:
                            importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {vault.id}'


                        if keys.data != []:
                            for key in keys.data:
                                first_key = False
                                if key.lifecycle_state not in ["DELETED", "PENDING_DELETION", "SCHEDULING_DELETION"]:

                                    # Tags filter
                                    defined_tags = key.defined_tags
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

                                    key_count += 1
                                    total_keys += 1
                                    key_tf_name = commonTools.check_tf_variable(key.display_name)
                                    tf_resource = f'module.keys[\\"{key_tf_name}\\"].oci_kms_key.key'
                                    if tf_resource not in state["resources"]:
                                        importCommands += f'\n{tf_or_tofu} import "{tf_resource}" managementEndpoint/{vault.management_endpoint}/keys/{key.id}'
                                    get_key_data = kms_key_client.get_key(key_id=key.id).data
                                    if get_key_data.vault_id == vault.id and get_key_data.lifecycle_state != "PENDING_DELETION":
                                        if key_count == 1:
                                            first_key = True

                                        if first_key == True:
                                            for col_header in values_for_column_kms.keys():
                                                if col_header == 'Region':
                                                    values_for_column_kms[col_header].append(reg)
                                                elif col_header == 'Vault Compartment Name':
                                                    values_for_column_kms[col_header].append(ntk_compartment_name)
                                                elif col_header == 'Vault Display Name':
                                                    values_for_column_kms[col_header].append(vault.display_name)
                                                elif col_header == 'Vault type':
                                                    values_for_column_kms[col_header].append(vault.vault_type)

                                                elif col_header == 'Replica Region':
                                                    if not replicas:
                                                        values_for_column_kms[col_header].append('')
                                                    else:
                                                        if region_name:
                                                            values_for_column_kms[col_header].append(region_name)
                                                        else:
                                                            values_for_column_kms[col_header].append('')
                                                elif str(col_header).lower() in ["vault defined tags", "vault freeform tags"]:
                                                    values_for_column_kms = commonTools.export_tags(vault, col_header,
                                                                                                    values_for_column_kms)

                                                elif col_header == 'Key Compartment Name':
                                                    comp_name = comp_name_list[comp_id_list.index(get_key_data.compartment_id)]
                                                    values_for_column_kms[col_header].append(comp_name)
                                                elif col_header == 'Key Display Name':
                                                    values_for_column_kms[col_header].append(get_key_data.display_name)
                                                elif col_header == 'Protection mode':
                                                    values_for_column_kms[col_header].append(get_key_data.protection_mode)
                                                elif col_header == 'Algorithm':
                                                    values_for_column_kms[col_header].append(get_key_data.key_shape.algorithm)
                                                elif col_header == 'Length in bits':
                                                    values_for_column_kms[col_header].append((get_key_data.key_shape.length)*8)
                                                elif col_header == 'Curve Id':
                                                    values_for_column_kms[col_header].append(get_key_data.key_shape.curve_id if get_key_data.key_shape.algorithm == 'ECDSA' else '')
                                                elif col_header == 'Auto rotation':
                                                    values_for_column_kms[col_header].append("TRUE" if get_key_data.is_auto_rotation_enabled==True else "FALSE")
                                                elif col_header == 'Rotation interval in days':
                                                    values_for_column_kms[col_header].append(get_key_data.auto_key_rotation_details.rotation_interval_in_days if hasattr(get_key_data.auto_key_rotation_details, 'rotation_interval_in_days') else '')
                                                elif str(col_header).lower() in ["key defined tags" , "key freeform tags"]:
                                                    if len(key.defined_tags) != 0:
                                                        values_for_column_kms = commonTools.export_tags(key, col_header, values_for_column_kms)
                                                    else:
                                                        values_for_column_kms[col_header].append('')
                                                else:
                                                    oci_objs = [vault, key, get_key_data, get_vault_data, get_vault_data.replica_details]
                                                    values_for_column_kms = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                                             sheet_dict_kms,
                                                                                                             values_for_column_kms)
                                        else:
                                            for col_header in values_for_column_kms.keys():
                                                if col_header == 'Key Compartment Name':
                                                    comp_name = comp_name_list[comp_id_list.index(get_key_data.compartment_id)]
                                                    values_for_column_kms[col_header].append(comp_name)
                                                elif col_header == 'Key Display Name':
                                                    values_for_column_kms[col_header].append(get_key_data.display_name)
                                                elif col_header == 'Protection mode':
                                                    values_for_column_kms[col_header].append(get_key_data.protection_mode)
                                                elif col_header == 'Algorithm':
                                                    values_for_column_kms[col_header].append(get_key_data.key_shape.algorithm)
                                                elif col_header == 'Length in bits':
                                                    values_for_column_kms[col_header].append((get_key_data.key_shape.length) * 8)
                                                elif col_header == 'Curve Id':
                                                    values_for_column_kms[col_header].append(
                                                        get_key_data.key_shape.curve_id if get_key_data.key_shape.algorithm == 'ECDSA' else '')
                                                elif col_header == 'Auto rotation':
                                                    values_for_column_kms[col_header].append("TRUE" if get_key_data.is_auto_rotation_enabled==True else "FALSE")
                                                elif col_header == 'Rotation interval in days':
                                                    values_for_column_kms[col_header].append(get_key_data.auto_key_rotation_details.rotation_interval_in_days if hasattr(get_key_data.auto_key_rotation_details,'rotation_interval_in_days') else '')
                                                elif str(col_header).lower() in ["key defined tags", "key freeform tags"]:
                                                    if len(key.defined_tags) != 0:
                                                        values_for_column_kms = commonTools.export_tags(key, col_header,
                                                                                                        values_for_column_kms)
                                                    else:
                                                        values_for_column_kms[col_header].append('')
                                                else:
                                                    oci_objs = [key, get_key_data]
                                                    values_for_column_kms = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                                             sheet_dict_kms,
                                                                                                             values_for_column_kms)
                                                    pass
                        else:
                            for col_header in values_for_column_kms.keys():
                                if col_header == 'Region':
                                    values_for_column_kms[col_header].append(reg)
                                elif col_header == 'Vault Compartment Name':
                                    values_for_column_kms[col_header].append(ntk_compartment_name)
                                elif col_header == 'Vault Display Name':
                                    values_for_column_kms[col_header].append(vault.display_name)
                                elif col_header == 'Vault type':
                                    values_for_column_kms[col_header].append(vault.vault_type)
                                elif col_header == 'Replica Region':
                                    if not replicas:
                                        values_for_column_kms[col_header].append('')
                                    else:
                                        if region_name:
                                            values_for_column_kms[col_header].append(region_name)
                                        else:
                                            values_for_column_kms[col_header].append('')
                                elif str(col_header).lower() in ["vault defined tags", "vault freeform tags"]:
                                    values_for_column_kms = commonTools.export_tags(vault, col_header,
                                                                                    values_for_column_kms)
                                else:
                                    oci_objs = [vault, get_vault_data, get_vault_data.replica_details]
                                    values_for_column_kms = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                             sheet_dict_kms,
                                                                                             values_for_column_kms)

                    except TransientServiceError as e:
                        continue

        #Write Import Commands to script file
        init_commands = f'\n######### Writing import for OCI Vaults #########\n\n#!/bin/bash\n{tf_or_tofu} init'

        if importCommands != "":
            importCommands += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands)

    #Write resource data to input Excel sheet
    commonTools.write_to_cd3(values_for_column_kms, cd3file, sheetName)
    print(f"{total_vaults} Vaults and {total_keys} Keys Details are exported into CD3.\n")







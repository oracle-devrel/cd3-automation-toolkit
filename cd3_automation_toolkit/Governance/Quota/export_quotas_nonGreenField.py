#!/usr/bin/python3
# Copyright (c) 2024 Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export quotas
#
#Author: Bhanu P. Lohumi
#Oracle Consulting
#
import sys
import oci
import os
import subprocess as sp
from commonTools import *

sys.path.append(os.getcwd()+"/..")

compartment_ids={}
importCommands={}
tf_name_namespace_list = []

def print_quotas(values_for_columns,region, quota,quota_policy):
    for col_header in values_for_columns.keys():
        if (col_header == "Region"):
             values_for_columns[col_header].append(region.capitalize())
        elif (col_header == "Name"):
            values_for_columns[col_header].append(quota.name)
        elif (col_header == "Description"):
            values_for_columns[col_header].append(quota.description)
        elif (col_header == "Quota Policy"):
            values_for_columns[col_header].append(quota_policy)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_columns = commonTools.export_tags(quota, col_header, values_for_columns)

# Execution of the code begins here
def export_quotas_nongreenfield(inputfile, outdir, service_dir, config, signer, ct,export_tags):
    global tf_import_cmd
    global values_for_column_quotas
    global sheet_dict_quotas
    global importCommands,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    sheet_name = 'Quotas'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/import_commands_'+sheet_name.lower()+'.sh'
    cd3file = inputfile
    importCommands = ""
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_quotas = commonTools.read_cd3(cd3file, sheet_name)

    # Get dict for columns from Excel_Columns
    sheet_dict_quotas = ct.sheet_dict[sheet_name]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Quotas would be overwritten during export process!!!\n")

    # Create backups
    if os.path.exists(script_file):
        commonTools.backup_file(os.path.dirname(script_file), "import_"+sheet_name.lower(), os.path.basename(script_file))

    # Fetch quotas
    print("\nFetching quotas...")
    reg = (ct.home_region).lower()
    config.__setitem__("region", ct.region_dict[reg])
    state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
    try:
        byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
        output = byteOutput.decode('UTF-8').rstrip()
        for item in output.split('\n'):
            state["resources"].append(item.replace("\"", "\\\""))
    except Exception as e:
        pass
    tenancy_id = config["tenancy"]
    quotas_client = oci.limits.QuotasClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    region = ct.home_region.lower()

    quotas_list = oci.pagination.list_call_get_all_results(quotas_client.list_quotas,compartment_id=tenancy_id,lifecycle_state="ACTIVE")
    if quotas_list.data != []:
        for quota_info in quotas_list.data:
            quota_policy = ""
            quota = quotas_client.get_quota(quota_id=quota_info.id).data

            # Tags filter
            defined_tags = quota.defined_tags
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

            for statement in quota.statements:
                quota_policy +="\n"+str(statement)

            print_quotas(values_for_column_quotas, region, quota,quota_policy[1:])
            quota_tf_name = commonTools.check_tf_variable(quota_info.name)
            tf_resource = f'module.quota_policies[\\"{quota_tf_name}\\"].oci_limits_quota.quota'
            if tf_resource not in state["resources"]:
                importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {str(quota_info.id)}'


    commonTools.write_to_cd3(values_for_column_quotas, cd3file, sheet_name)
    print("{0} quotas exported into CD3.\n".format(len(values_for_column_quotas["Region"])))

    init_commands = f'\n######### Writing import for Quota #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    if importCommands != "":
        importCommands += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands)


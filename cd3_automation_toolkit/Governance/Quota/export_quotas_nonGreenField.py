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
def export_quotas_nongreenfield(inputfile, outdir, service_dir, config, signer, ct):
    global tf_import_cmd
    global values_for_column_quotas
    global sheet_dict_quotas
    global importCommands
    sheet_name = 'Quotas'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/tf_import_commands_'+sheet_name.lower()+'_nonGF.sh'
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
        commonTools.backup_file(os.path.dirname(script_file), "tf_import_"+sheet_name.lower(), os.path.basename(script_file))

    # Fetch quotas
    print("\nFetching quotas...")
    config.__setitem__("region", ct.region_dict[ct.home_region])
    tenancy_id = config["tenancy"]
    quotas_client = oci.limits.QuotasClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    region = ct.home_region.lower()

    quotas_list = oci.pagination.list_call_get_all_results(quotas_client.list_quotas,compartment_id=tenancy_id,lifecycle_state="ACTIVE")
    if quotas_list.data != []:
        importCommands += "\n######### Writing import for quotas #########\n\n"
        importCommands += "#!/bin/bash"
        importCommands += "\n"
        importCommands += "terraform init"
        for quota_info in quotas_list.data:
            quota_policy = ""
            quota = quotas_client.get_quota(quota_id=quota_info.id).data
            for statement in quota.statements:
                quota_policy +="\n"+str(statement)

            print_quotas(values_for_column_quotas, region, quota,quota_policy[1:])
            quota_tf_name = commonTools.check_tf_variable(quota_info.name)
            importCommands += "\nterraform import \"module.quota_policies[\\\"" + quota_tf_name+ "\\\"].oci_limits_quota.quota\" " + str(quota_info.id)

        importCommands += "\nterraform plan"

    commonTools.write_to_cd3(values_for_column_quotas, cd3file, sheet_name)
    print("{0} quotas exported into CD3.\n".format(len(values_for_column_quotas["Region"])))

    if importCommands != "":
        with open(script_file, 'a') as importCommandsfile:
            importCommandsfile.write(importCommands)


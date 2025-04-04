#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI Database
# EXA Infra
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import oci
import os
import subprocess as sp
from commonTools import *

importCommands = {}
oci_obj_names = {}


def print_exa_infra(region, exa_infra, values_for_column, ntk_compartment_name,state):
    exa_infra_tf_name = commonTools.check_tf_variable(exa_infra.display_name)
    maintenance_window = exa_infra.maintenance_window
    tf_resource = f'module.exa-infra[\\"{exa_infra_tf_name}\\"].oci_database_cloud_exadata_infrastructure.exa_infra'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(exa_infra.id)}'

    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif ("Availability Domain" in col_header):
            value = exa_infra.__getattribute__(sheet_dict[col_header])
            ad = ""
            if ("AD-1" in value or "ad-1" in value):
                ad = "AD1"
            elif ("AD-2" in value or "ad-2" in value):
                ad = "AD2"
            elif ("AD-3" in value or "ad-3" in value):
                ad = "AD3"
            values_for_column[col_header].append(ad)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(exa_infra, col_header, values_for_column)
        else:
            oci_objs = [exa_infra,maintenance_window]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

# Execution of the code begins here


def export_exa_infra(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[],export_tags=[]):
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


    sheetName = "EXA-Infra"
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- EXA-Infra  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch Block Volume Details
    print("\nFetching details of Exadata Infra...")

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

                print_exa_infra(region, exa_infra,values_for_column, ntk_compartment_name,state)


    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} Exadata Infra exported into CD3.\n".format(len(values_for_column["Region"])))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for Exadata Infra #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])



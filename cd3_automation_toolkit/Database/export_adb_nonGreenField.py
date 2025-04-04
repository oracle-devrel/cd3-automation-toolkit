#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export Autonomous Databases
#
# Author: Bhanu P. Lohumi
# Oracle Consulting
#
import oci
import os
import subprocess as sp
from commonTools import *
from oci.config import DEFAULT_LOCATION

importCommands = {}
oci_obj_names = {}


def print_adbs(region, vnc_client, adb, values_for_column, ntk_compartment_name,state,ct):
    adb_tf_name = commonTools.check_tf_variable(adb.display_name)
    customer_emails = ""
    if hasattr(adb,"customer_contacts") and adb.customer_contacts:
        for item in adb.customer_contacts:
            customer_emails += ","+item.email
    adb_subnet_id = adb.subnet_id

    if (adb_subnet_id is not None):
        adb_subnet_info = vnc_client.get_subnet(adb_subnet_id)
        adb_subnet_name = adb_subnet_info.data.display_name  # Subnet-Name
        adb_vcn_name = vnc_client.get_vcn(adb_subnet_info.data.vcn_id).data.display_name

        ntk_compartment_id = vnc_client.get_vcn(adb_subnet_info.data.vcn_id).data.compartment_id  # compartment-id
        network_compartment_name = ntk_compartment_name
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if comp_id == ntk_compartment_id:
                network_compartment_name = comp_name

        vs = network_compartment_name + "@" + adb_vcn_name + "::" + adb_subnet_name


    # Fetch NSGs
    NSGs = adb.nsg_ids
    nsg_names = ""
    if (NSGs is not None and len(NSGs)):
        for j in NSGs:
            nsg_info = vnc_client.get_network_security_group(j)
            nsg_names = nsg_names + "," + nsg_info.data.display_name
        nsg_names = nsg_names[1:]

    # Fetch Whitelisted IP Addresses
    whitelisted_ips = ""
    if adb.whitelisted_ips:
        for ip in adb.whitelisted_ips:
            whitelisted_ips = whitelisted_ips + "," + ip

        whitelisted_ips = whitelisted_ips[1:]
    tf_resource = f'module.adb[\\"{adb_tf_name}\\"].oci_database_autonomous_database.autonomous_database'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(adb.id)}'

    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'ADB Display Name':
            values_for_column[col_header].append(adb.display_name)
        elif col_header == 'Network Details':
            if (adb_subnet_id is not None):
                values_for_column[col_header].append(vs)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'Whitelisted IP Addresses':
            values_for_column[col_header].append(whitelisted_ips)
        elif col_header == 'DB Name':
            values_for_column[col_header].append(adb.db_name)
        elif col_header == 'Database Edition':
            if hasattr(adb, 'database_edition'):
                values_for_column[col_header].append(adb.database_edition)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'CPU Core Count':
            values_for_column[col_header].append(adb.cpu_core_count)
        elif col_header == 'Data Storage Size in TB':
            values_for_column[col_header].append(adb.data_storage_size_in_tbs)
        elif col_header == 'Database Workload':
            val= adb.db_workload
            if adb.db_workload == "DW":
                val="adw"
            elif adb.db_workload == "AJD":
                val="json"
            elif adb.db_workload == "OLTP":
                val="atp"
            elif adb.db_workload == "APEX":
                val="apex"
            values_for_column[col_header].append(val)
        elif col_header == 'License Model':
            values_for_column[col_header].append(adb.license_model)
        elif col_header == 'Character Set':
            if hasattr(adb, 'character_set'):
                values_for_column[col_header].append(adb.character_set)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'nCharacter Set':
            if hasattr(adb, 'ncharacter_set'):
                values_for_column[col_header].append(adb.ncharacter_set)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'Customer Contacts':
            values_for_column[col_header].append(customer_emails.lstrip(','))
        elif col_header == "NSGs":
            values_for_column[col_header].append(nsg_names)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(adb, col_header, values_for_column)
        else:
            oci_objs = [adb]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

# Execution of the code begins here
def export_adbs(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[],export_regions=[],export_tags=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global cd3file
    global reg
    global values_for_column,tf_or_tofu

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile  # input file
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "ADB"

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- ADB  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch ADB details
    print("\nFetching details of ADBs...")
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

        adb_client = oci.database.DatabaseClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        vnc_client = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        #adbs = {}

        for ntk_compartment_name in export_compartments:
            adbs = oci.pagination.list_call_get_all_results(adb_client.list_autonomous_databases,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
            for adb in adbs.data:
                adb = adb_client.get_autonomous_database(adb.id).data

                # Tags filter
                defined_tags = adb.defined_tags
                tags_list = []
                for tkey, tval in defined_tags.items():
                    for kk, vv in tval.items():
                        tag = tkey + "." + kk + "=" + vv
                        tags_list.append(tag)

                if export_tags==[]:
                    check=True
                else:
                    check = any(e in tags_list for e in export_tags )

                # None of Tags from export_tags exist on this instance; Dont export this instance
                if check == False:
                    continue

                print_adbs(region, vnc_client, adb, values_for_column, ntk_compartment_name,state,ct)


    commonTools.write_to_cd3(values_for_column, cd3file, "ADB")
    print("{0} ADBs exported into CD3.\n".format(len(values_for_column["Region"])))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for ADBs #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])

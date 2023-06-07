#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export Autonomous Databases
#
# Author: Bhanu P. Lohumi
# Oracle Consulting
#

import argparse
import sys
import oci
import os
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader
import json
import re

from oci.config import DEFAULT_LOCATION

importCommands = {}
oci_obj_names = {}


def print_adbs(region, vnc_client, adb, values_for_column, ntk_compartment_name):
    adb_tf_name = commonTools.check_tf_variable(adb.display_name)

    adb_subnet_id = adb.subnet_id

    if (adb_subnet_id is not None):
        adb_subnet_info = vnc_client.get_subnet(adb_subnet_id)
        adb_subnet_name = adb_subnet_info.data.display_name  # Subnet-Name
        adb_vcn_name = vnc_client.get_vcn(adb_subnet_info.data.vcn_id).data.display_name

    else:
        adb_subnet_name = ""
        adb_vcn_name = ""


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
    importCommands[region.lower()].write(
        "\nterraform import \"module.adb[\\\"" + adb_tf_name + "\\\"].oci_database_autonomous_database.autonomous_database\" " + str(adb.id))

    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'ADB Display Name':
            values_for_column[col_header].append(adb.display_name)
        elif col_header == 'Subnet Name':
            if (adb_subnet_id is not None):
                values_for_column[col_header].append(adb_vcn_name + "_" + adb_subnet_name)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'Whitelisted IP Addresses':
            values_for_column[col_header].append(whitelisted_ips)
        elif col_header == 'DB Name':
            values_for_column[col_header].append(adb.db_name)
        elif col_header == 'Database Edition':
            values_for_column[col_header].append(adb.database_edition)
        elif col_header == 'CPU Core Count':
            values_for_column[col_header].append(adb.cpu_core_count)
        elif col_header == 'Data Storage Size in TB':
            values_for_column[col_header].append(adb.data_storage_size_in_tbs)
        elif col_header == 'Database Workload':
            values_for_column[col_header].append(adb.db_workload)
        elif col_header == 'License Model':
            values_for_column[col_header].append(adb.license_model)
        elif col_header == 'Character Set':
            values_for_column[col_header].append(adb.character_set)
        elif col_header == 'nCharacter Set':
            values_for_column[col_header].append(adb.ncharacter_set)
        elif col_header == "NSGs":
            values_for_column[col_header].append(nsg_names)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(adb, col_header, values_for_column)
        else:
            oci_objs = [adb]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export ADB on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export ADB objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("service_dir", help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--export-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export ADBs")
    parser.add_argument("--export-regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                        required=False)
    return parser.parse_args()


def export_adbs(inputfile, _outdir, service_dir, ct, _config=DEFAULT_LOCATION, export_compartments=[],export_regions=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global cd3file
    global reg
    global outdir
    global values_for_column

    cd3file = inputfile  # input file
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    outdir = _outdir
    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    sheetName = "ADB"
    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- ADB  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch ADB details
    print("\nFetching details of ADBs...")


    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for ADBs #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()

        adb_client = oci.database.DatabaseClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        vnc_client = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        #adbs = {}

        for ntk_compartment_name in export_compartments:
            adbs = oci.pagination.list_call_get_all_results(adb_client.list_autonomous_databases,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")

            for adb in adbs.data:
                adb = adb_client.get_autonomous_database(adb.id).data
                print_adbs(region, vnc_client, adb, values_for_column, ntk_compartment_name)

    commonTools.write_to_cd3(values_for_column, cd3file, "ADB")

    print("ADBs exported to CD3\n")

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_adbs(args.inputfile, args.outdir, args.service_dir, args.config, args.export_compartments,args.export_regions)

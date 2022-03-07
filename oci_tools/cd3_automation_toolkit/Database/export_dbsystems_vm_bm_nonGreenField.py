#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export Block Volume Components
#
# Author: Shruthi Subramanian
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

from oci.config import DEFAULT_LOCATION

importCommands = {}
oci_obj_names = {}


def print_dbsystem_vm_bm(region, db_system_vm_bm, count,db_home, database ,vnc_client, key_name, values_for_column, ntk_compartment_name):
    db_system_vm_bm_tf_name = commonTools.check_tf_variable(db_system_vm_bm.display_name)

    db_system_subnet_id = db_system_vm_bm.subnet_id
    subnet_info = vnc_client.get_subnet(db_system_subnet_id)
    sub_name = subnet_info.data.display_name  # Subnet-Name
    vcn_name = vnc_client.get_vcn(subnet_info.data.vcn_id).data.display_name  # vcn-Name

    db_system_options = db_system_vm_bm.db_system_options
    maintenance_window = db_system_vm_bm.maintenance_window
    db_backup_config = database.db_backup_config
    connection_strings = database.connection_strings
    database_management_config = database.database_management_config

    if (count ==1):
        #importCommands[region.lower()].write("\nterraform import oci_database_db_system." + db_system_vm_bm_tf_name + " " + str(db_system_vm_bm.id))
        importCommands[region.lower()].write("\nterraform import \"module.dbsystems-vm-bm[\\\"" + db_system_vm_bm_tf_name + "\\\"].oci_database_db_system.database_db_system\" " + str(db_system_vm_bm.id))

    if(count!=1):
        for col_header in values_for_column:
            if col_header == 'Region' or col_header == 'Compartment Name' or col_header == 'Subnet Name' or "Availability Domain" in col_header or \
                col_header == 'Shape' or col_header == 'DB System Display Name' or col_header == 'Node Count' or col_header == 'CPU Core Count' or col_header == "Database Edition" or \
                col_header == 'Data Storage in GB' or col_header == 'Data Storage Percentage' or col_header == 'Disk Redundancy' or col_header == 'License Model' or \
                col_header == 'Hostname Prefix' or col_header == 'SSH Key Var Name' or col_header == 'Time Zone':

                values_for_column[col_header].append("")
            elif col_header == 'DB Admin Password':
                values_for_column[col_header].append('nullval')

            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(db_system_vm_bm, col_header, values_for_column)
            else:
                oci_objs = [db_home,database,db_backup_config,connection_strings,database_management_config]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

    #count = 1
    else:
        for col_header in values_for_column:
            if col_header == 'Region':
                values_for_column[col_header].append(region)
            elif col_header == 'Compartment Name':
                values_for_column[col_header].append(ntk_compartment_name)
            elif col_header == 'Subnet Name':
                values_for_column[col_header].append(commonTools.check_tf_variable(vcn_name + "_" + sub_name))
            elif col_header == 'DB Admin Password':
                values_for_column[col_header].append('nullval')
            elif col_header == 'SSH Key Var Name':
                values_for_column[col_header].append(key_name)
            elif ("Availability Domain" in col_header):
                value = db_system_vm_bm.__getattribute__(sheet_dict[col_header])
                ad = ""
                if ("AD-1" in value or "ad-1" in value):
                    ad = "AD1"
                elif ("AD-2" in value or "ad-2" in value):
                    ad = "AD2"
                elif ("AD-3" in value or "ad-3" in value):
                    ad = "AD3"
                values_for_column[col_header].append(ad)

            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(db_system_vm_bm, col_header, values_for_column)
            else:
                oci_objs = [db_system_vm_bm,db_system_options,maintenance_window,db_home,database,db_backup_config,connection_strings,database_management_config]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export Block Volumes on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export Block Volume objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export Block Volume Objects")
    return parser.parse_args()


def export_dbsystems_vm_bm(inputfile, _outdir, _config, network_compartments=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global cd3file
    global reg
    global outdir
    global values_for_column


    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()


    outdir = _outdir
    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    sheetName = 'DBSystems-VM-BM'
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Read CD3
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    # Check Compartments
    global comp_list_fetch
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments, ct.ntk_compartment_ids)

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- DBSystems-VM-BM  will be overwritten during export process!!!\n")

    # Load variables template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent.parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    variable_template = env.get_template('module-variables-template')

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'

    for reg in ct.all_regions:
        script_file = f'{outdir}/{reg}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Block Volume Details
    print("\nFetching details of VM and BM DB Systems...")

    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for DB System VM and DB System BM #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()

        db_client = oci.database.DatabaseClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        vnc_client = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        for ntk_compartment_name in comp_list_fetch:
            db_systems = oci.pagination.list_call_get_all_results(db_client.list_db_systems,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="AVAILABLE")

            db={}
            for db_system in db_systems.data:

                # Get ssh keys for db system
                key_name = commonTools.check_tf_variable(db_system.display_name+"-"+db_system.hostname)
                db_ssh_keys= db_system.ssh_public_keys
                db_ssh_keys=json.dumps(db_ssh_keys)
                db[key_name]=db_ssh_keys

                db_homes = oci.pagination.list_call_get_all_results(db_client.list_db_homes,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],db_system_id=db_system.id,lifecycle_state="AVAILABLE", sort_by="TIMECREATED", sort_order="ASC")
                count=0
                for db_home in db_homes.data:
                    count=count+1
                    databases = oci.pagination.list_call_get_all_results(db_client.list_databases,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],db_home_id=db_home.id,system_id=db_system.id,lifecycle_state="AVAILABLE")
                    for database in databases.data:
                        print_dbsystem_vm_bm(region, db_system, count,db_home, database, vnc_client, key_name,values_for_column, ntk_compartment_name)

        f = open(outdir + "/" + reg + "/ssh_metadata_vm_bm_db.tf", "w")

        for k, v in db.items():
            tempstr = {"var_tf_name": k, "values": v,"db_export":"true"}
            var_name = variable_template.render(tempstr)
            f.write(var_name)
        f.close()

        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')
        if "linux" in sys.platform:
            os.chmod(script_file, 0o755)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("Virtual Machine and Bare Metal DB Systems exported to CD3\n")


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_dbsystems_vm_bm(args.inputfile, args.outdir, args.config, args.network_compartments)

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
import oci
import os
import json
import re

from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader

importCommands = {}
oci_obj_names = {}


def print_exa_vmcluster(region, vnc_client,exa_infra, exa_vmcluster, key_name,values_for_column, ntk_compartment_name):
    exa_infra_tf_name = commonTools.check_tf_variable(exa_infra.display_name)
    exa_vmcluster_tf_name = commonTools.check_tf_variable(exa_vmcluster.display_name)

    exa_vmcluster_client_subnet_id = exa_vmcluster.subnet_id
    client_subnet_info = vnc_client.get_subnet(exa_vmcluster_client_subnet_id)
    client_subnet_name = client_subnet_info.data.display_name  # Subnet-Name
    client_vcn_name = vnc_client.get_vcn(client_subnet_info.data.vcn_id).data.display_name  # vcn-Name

    exa_vmcluster_backup_subnet_id = exa_vmcluster.backup_subnet_id
    backup_subnet_info = vnc_client.get_subnet(exa_vmcluster_backup_subnet_id)
    backup_subnet_name = backup_subnet_info.data.display_name  # Subnet-Name
    backup_vcn_name = vnc_client.get_vcn(backup_subnet_info.data.vcn_id).data.display_name  # vcn-Name


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

    importCommands[region.lower()].write("\nterraform import \"module.exa-vmclusters[\\\"" + exa_vmcluster_tf_name + "\\\"].oci_database_cloud_vm_cluster.exa_vmcluster\" " + str(exa_vmcluster.id))

    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'Exadata Infra Display Name':
            values_for_column[col_header].append(exa_infra.display_name)
        elif col_header == 'SSH Key Var Name':
            values_for_column[col_header].append(key_name)
        elif col_header == 'Client Subnet Name':
            values_for_column[col_header].append(client_vcn_name+"_"+client_subnet_name)
        elif col_header == 'Backup Subnet Name':
            values_for_column[col_header].append(backup_vcn_name + "_" + backup_subnet_name)
        elif (col_header == "NSGs"):
            values_for_column[col_header].append(nsg_names)
        elif (col_header == "Backup Network NSGs"):
            values_for_column[col_header].append(backup_nsg_names)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(exa_vmcluster, col_header, values_for_column)
        else:
            oci_objs = [exa_vmcluster,exa_infra]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export Block Volumes on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export Block Volume objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("service_dir", help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--export-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export Block Volume Objects")
    parser.add_argument("--export-regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                        required=False)
    return parser.parse_args()


def export_exa_vmclusters(inputfile, _outdir, service_dir, _config, ct, export_compartments=[],export_regions=[]):
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

    sheetName = 'EXA-VMClusters'
    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)
    
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

    # Fetch Block Volume Details
    print("\nFetching details of Exadata VM Clusters...")

    for reg in export_regions:
        var_data[reg] = ""

        importCommands[reg].write("\n\n######### Writing import for Exadata VM Clusters #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()

        db_client = oci.database.DatabaseClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        vnc_client = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        db={}
        for ntk_compartment_name in export_compartments:
            exa_infras = oci.pagination.list_call_get_all_results(db_client.list_cloud_exadata_infrastructures,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="AVAILABLE")
            for exa_infra in exa_infras.data:
                for ntk_compartment_name_again in export_compartments:
                    exa_vmclusters = oci.pagination.list_call_get_all_results(db_client.list_cloud_vm_clusters,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], cloud_exadata_infrastructure_id=exa_infra.id, lifecycle_state="AVAILABLE")
                    for exa_vmcluster in exa_vmclusters.data:
                        # Get ssh keys for exa vm cluster
                        key_name = commonTools.check_tf_variable(exa_vmcluster.display_name + "_" + exa_vmcluster.hostname)
                        db_ssh_keys = exa_vmcluster.ssh_public_keys
                        db_ssh_keys = json.dumps(db_ssh_keys)
                        db[key_name] = db_ssh_keys

                        print_exa_vmcluster(region, vnc_client, exa_infra,exa_vmcluster,key_name, values_for_column, ntk_compartment_name_again)

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


        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)

    print("Exadata VM Clusters exported to CD3\n")


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_exa_vmclusters(args.inputfile, args.outdir, args.service_dir, args.config, args.export_compartments,args.export_regions)

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
from oci.core.blockstorage_client import BlockstorageClient
from oci.core.compute_client import ComputeClient
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}

def policy_info(bvol,volume_id):
    asset_policy_id=''
    asset_policy_name = ''
    bvol_info = bvol.list_volume_backup_policies()
    blockvol_policy = bvol.get_volume_backup_policy_asset_assignment(asset_id=volume_id)
    for assets in blockvol_policy.data:
        asset_policy_id = assets.policy_id
    for policies in bvol_info.data:
        policy_id = policies.id
        policy_name = policies.display_name
        if asset_policy_id == policy_id:
            asset_policy_name = policy_name
    return asset_policy_id, asset_policy_name

def volume_attachment_info(compute,ntk_compartment_name,ct,volume_id):
    instance_id = ''
    attachment_type=''
    instance_name = ''
    attachment_id = ''
    attach_info = compute.list_volume_attachments(compartment_id = ct.ntk_compartment_ids[ntk_compartment_name], volume_id = volume_id)
    for attachments in attach_info.data:
        instance_id = attachments.instance_id
        attachment_type = attachments.attachment_type
        attachment_id = attachments.id
    compute_info = compute.list_instances(ct.ntk_compartment_ids[ntk_compartment_name])
    for instance in compute_info.data:
        if instance_id == instance.id:
           instance_name = instance.display_name
    return attachment_id, instance_name, attachment_type

def print_blockvolumes(region, BVOLS, bvol, compute, ct, values_for_column, ntk_compartment_name):
    for blockvols in BVOLS.data:
        volume_id = blockvols.id
        attachment_id, instance_name, attachment_type = volume_attachment_info(compute, ntk_compartment_name, ct,volume_id)
        asset_policy_id, asset_policy_name = policy_info(bvol, volume_id)
        block_tf_name = commonTools.check_tf_variable(blockvols.display_name)

        importCommands[region.lower()].write("\nterraform import oci_core_volume." + block_tf_name + " " + str(blockvols.id))
        if attachment_id != '':
            importCommands[region.lower()].write("\nterraform import oci_core_volume_attachment." + block_tf_name +"_volume_attachment " + str(attachment_id))
        if asset_policy_id != '':
            importCommands[region.lower()].write("\nterraform import oci_core_volume_backup_policy_assignment." + block_tf_name +"_bkupPolicy " + str(asset_policy_id))

        for col_header in values_for_column:
            if col_header == 'Region':
                values_for_column[col_header].append(region)
            elif col_header == 'Compartment Name':
                values_for_column[col_header].append(ntk_compartment_name)
            elif ("Availability Domain" in col_header):
                value = blockvols.__getattribute__(sheet_dict[col_header])
                ad = ""
                if ("AD-1" in value):
                    ad = "AD1"
                elif ("AD-2" in value):
                    ad = "AD2"
                elif ("AD-3" in value):
                    ad = "AD3"
                values_for_column[col_header].append(ad)
            elif col_header == 'Attach Type(iscsi|paravirtualized)':
                values_for_column[col_header].append(attachment_type)
            elif col_header == 'Attached To Instance':
                values_for_column[col_header].append(instance_name)
            elif col_header == 'Backup Policy':
                values_for_column[col_header].append(asset_policy_name)
            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(blockvols, col_header, values_for_column)
            else:
                oci_objs = [blockvols]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def main():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Export Block Volumes on OCI to CD3")
    parser.add_argument("cd3file", help="path of CD3 excel file to export network objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Block Volume Objects", required=False)
    parser.add_argument("--configFileName", help="Config file name" , required=False)

    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global values_for_vcninfo
    global cd3file
    global reg
    global outdir
    global values_for_column

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    cd3file = args.cd3file
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    input_config_file = args.configFileName
    input_compartment_list = args.networkCompartment
    if (input_compartment_list is not None):
        input_compartment_names = input_compartment_list.split(",")
        input_compartment_names = [x.strip() for x in input_compartment_names]
    else:
        input_compartment_names = None

    outdir = args.outdir

    if args.configFileName is not None:
        configFileName = args.configFileName
        config = oci.config.from_file(file_location=configFileName)
    else:
        configFileName=""
        config = oci.config.from_file()

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Read CD3
    df, values_for_column= commonTools.read_cd3(cd3file,"BlockVols")

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict["BlockVols"]

    # Check Compartments
    remove_comps = []
    if (input_compartment_names is not None):
        for x in range(0, len(input_compartment_names)):
            if (input_compartment_names[x] not in ct.ntk_compartment_ids.keys()):
                print("Input compartment: " + input_compartment_names[x] + " doesn't exist in OCI")
                remove_comps.append(input_compartment_names[x])

        input_compartment_names = [x for x in input_compartment_names if x not in remove_comps]
        if (len(input_compartment_names) == 0):
            print("None of the input compartments specified exist in OCI..Exiting!!!")
            exit(1)
        else:
            print("Fetching for Compartments... " + str(input_compartment_names))
    else:
        print("Fetching for all Compartments...")
    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- BlockVols  will be overwritten during export process!!!\n")

    # Create backups
    for reg in ct.all_regions:
        resource='tf_import_blockvol'
        if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_blockvol_nonGF.sh")):
            commonTools.backup_file(outdir + "/" + reg, resource, "tf_import_commands_blockvol_nonGF.sh")
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_blockvol_nonGF.sh", "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Block Volume Details
    print("\nFetching details of Block Volumes...")

    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for Block Volumes #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()
        comp_ocid_done = []
        compute = ComputeClient(config)
        bvol = BlockstorageClient(config)

        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])

                BVOLS = oci.pagination.list_call_get_all_results(bvol.list_volumes,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                print_blockvolumes(region, BVOLS, bvol, compute, ct, values_for_column, ntk_compartment_name)

        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_blockvol_nonGF.sh", "a")
        importCommands[reg].write("\n\nterraform plan")
        importCommands[reg].write("\n")
        importCommands[reg].close()
        if ("linux" in sys.platform):
            dir = os.getcwd()
            os.chdir(outdir + "/" + reg)
            os.system("chmod +x tf_import_commands_blockvol_nonGF.sh")
            os.chdir(dir)

    commonTools.write_to_cd3(values_for_column, cd3file, "BlockVols")

    print("Block Volumes exported to CD3\n")

if __name__ == '__main__':

    # Execution of the code begins here
    main()
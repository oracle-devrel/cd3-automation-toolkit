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
from oci.core.blockstorage_client import BlockstorageClient
from oci.core.compute_client import ComputeClient
from oci.config import DEFAULT_LOCATION
from commonTools import *

importCommands = {}
oci_obj_names = {}


def policy_info(bvol,volume_id,ct):
    asset_policy_name = ''
    asset_assignment_id = ''
    policy_comp_name = ''
    blockvol_policy = bvol.get_volume_backup_policy_asset_assignment(asset_id=volume_id)
    for assets in blockvol_policy.data:
        asset_assignment_id = assets.id
        asset_policy_id = assets.policy_id
        bvol_info = bvol.get_volume_backup_policy(policy_id=asset_policy_id)
        asset_policy_name = bvol_info.data.display_name
        policy_comp_id = bvol_info.data.compartment_id
        if str(policy_comp_id).lower() != 'none':
            comp_done_ids = []
            for comp_name,comp_ocids in ct.ntk_compartment_ids.items():
                if policy_comp_id == comp_ocids and policy_comp_id not in comp_done_ids:
                    policy_comp_name = comp_name
                    comp_done_ids.append(policy_comp_id)
    return asset_assignment_id, asset_policy_name, policy_comp_name


def volume_attachment_info(compute,ct,volume_id):
    instance_id = ''
    attachment_type=''
    instance_name = ''
    attachment_id = ''
    attachments=None
    for ntk_compartment_name in comp_list_fetch:
        attach_info = compute.list_volume_attachments(compartment_id = ct.ntk_compartment_ids[ntk_compartment_name], volume_id = volume_id)
        for attachments in attach_info.data:
            lifecycle_state = attachments.lifecycle_state
            if lifecycle_state == 'ATTACHED':
                instance_id = attachments.instance_id
                attachment_type = attachments.attachment_type
                attachment_id = attachments.id
            #compute_info = compute.list_instances(ct.ntk_compartment_ids[ntk_compartment_name])
            compute_info = compute.get_instance(instance_id=instance_id)#,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
            #for instance in compute_info.data:
            #if instance_id == compute_info.data.id:
            instance_name = compute_info.data.display_name
            return attachments,attachment_id, instance_name, attachment_type

    #retun empty values if not attached to any instance
    return attachments,attachment_id, instance_name, attachment_type


def print_blockvolumes(region, BVOLS, bvol, compute, ct, values_for_column, ntk_compartment_name, ad_names, display_names):
    volume_comp = ''
    for blockvols in BVOLS.data:
        volume_id = blockvols.id
        volume_compartment_id = blockvols.compartment_id
        AD_name = blockvols.availability_domain
        d_name = blockvols.display_name
        if (ad_names is not None):
            if (not any(e in AD_name for e in ad_names)):
                continue
        if (display_names is not None):
            if (not any(e in d_name for e in display_names)):
                continue
        attachments, attachment_id, instance_name, attachment_type = volume_attachment_info(compute, ct,volume_id)
        asset_assignment_id, asset_policy_name, policy_comp_name = policy_info(bvol, volume_id,ct)
        block_tf_name = commonTools.check_tf_variable(blockvols.display_name)

        comp_done_ids = []
        for comp_name,comp_id in ct.ntk_compartment_ids.items():
            if volume_compartment_id == comp_id and volume_compartment_id not in comp_done_ids:
                volume_comp = comp_name
                comp_done_ids.append(volume_compartment_id)

        importCommands[region.lower()].write("\nterraform import \"module.blockvolume[\\\"" + block_tf_name + "\\\"].oci_core_volume.block_volume\" " + str(blockvols.id))
        if attachment_id != '':
            importCommands[region.lower()].write("\nterraform import \"module.blockvolume[\\\"" + block_tf_name + "\\\"].oci_core_volume_attachment.block_vol_instance_attachment[0]\" " + str(attachment_id))

        if asset_assignment_id != '':
            importCommands[region.lower()].write("\nterraform import \"module.blockvolume[\\\"" + block_tf_name + "\\\"].oci_core_volume_backup_policy_assignment.volume_backup_policy_assignment[0]\" " + str(asset_assignment_id))
            pass
        for col_header in values_for_column:
            if col_header == 'Region':
                values_for_column[col_header].append(region)
            elif col_header == 'Compartment Name':
                values_for_column[col_header].append(volume_comp)
            elif ("Availability Domain" in col_header):
                value = blockvols.__getattribute__(sheet_dict[col_header])
                ad = ""
                if ("AD-1" in value or "ad-1" in value):
                    ad = "AD1"
                elif ("AD-2" in value or "ad-2" in value):
                    ad = "AD2"
                elif ("AD-3" in value or "ad-3" in value):
                    ad = "AD3"
                values_for_column[col_header].append(ad)
            elif col_header == 'Attach Type(iscsi|paravirtualized)':
                values_for_column[col_header].append(attachment_type)
            elif col_header == 'Attached To Instance':
                values_for_column[col_header].append(instance_name)
            elif col_header == 'Backup Policy':
                values_for_column[col_header].append(asset_policy_name)
            elif col_header == 'Custom Policy Compartment Name':
                values_for_column[col_header].append(policy_comp_name)
            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(blockvols, col_header, values_for_column)
            else:
                oci_objs = [blockvols,attachments]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export Block Volumes on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export Block Volume objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export Block Volume Objects")
    return parser.parse_args()


def export_blockvolumes(inputfile, _outdir, _config, network_compartments=[], display_names = [], ad_names = []):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global values_for_vcninfo
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

    sheetName = "BlockVolumes"
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
    print("Tabs- BlockVolumes  will be overwritten during export process!!!\n")

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
    print("\nFetching details of Block Volumes...")

    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for Block Volumes #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()
        compute = ComputeClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        bvol = BlockstorageClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        for ntk_compartment_name in comp_list_fetch:
                BVOLS = oci.pagination.list_call_get_all_results(bvol.list_volumes,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                print_blockvolumes(region, BVOLS, bvol, compute, ct, values_for_column, ntk_compartment_name, ad_names, display_names)

        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')
        if "linux" in sys.platform:
            os.chmod(script_file, 0o755)


    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)

    print("Block Volumes exported to CD3\n")


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_blockvolumes(args.inputfile, args.outdir, args.config, args.network_compartments)

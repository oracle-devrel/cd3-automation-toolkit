#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export Block Volume Components
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import re
import oci
import os
from oci.core.blockstorage_client import BlockstorageClient
from oci.core.compute_client import ComputeClient
from commonTools import *
import subprocess as sp

importCommands = {}
oci_obj_names = {}
source_ocids = {}

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


def volume_attachment_info(compute,ct,volume_id,export_compartments):
    instance_id = ''
    attachment_type=''
    instance_name = ''
    attachment_id = ''
    attachments=None
    for ntk_compartment_name in export_compartments:
        attach_info = compute.list_volume_attachments(compartment_id = ct.ntk_compartment_ids[ntk_compartment_name], volume_id = volume_id)
        for attachments in attach_info.data:
            lifecycle_state = attachments.lifecycle_state
            if lifecycle_state == 'ATTACHED':
                instance_id = attachments.instance_id
                attachment_type = attachments.attachment_type
                attachment_id = attachments.id
                compute_info = compute.get_instance(instance_id=instance_id)#,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
                instance_name = compute_info.data.display_name
                return attachments,attachment_id, instance_name, attachment_type

    #retun empty values if not attached to any instance
    return attachments,attachment_id, instance_name, attachment_type


def print_blockvolumes(region, BVOLS, bvol, compute, ct, values_for_column, ntk_compartment_name, display_names, ad_names,export_compartments,export_tags, state):
    volume_comp = ''
    for blockvols in BVOLS.data:
        # Tags filter
        defined_tags = blockvols.defined_tags
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

        volume_id = blockvols.id
        volume_compartment_id = blockvols.compartment_id
        AD_name = blockvols.availability_domain
        d_name = blockvols.display_name
        bv_defined_tags = blockvols.defined_tags
        if 'Oracle-Tags' in bv_defined_tags.keys():
            if 'CreatedBy' in bv_defined_tags['Oracle-Tags'].keys():
                created_by = bv_defined_tags['Oracle-Tags']['CreatedBy']
                if "ocid1.cluster" in created_by:
                    print("Skipping " + str(d_name) + " as it is created by oke cluster : " + str(created_by))
                    continue
        if ("AD-1" in AD_name or "ad-1" in AD_name):
            AD_name = "AD1"
        elif ("AD-2" in AD_name or "ad-2" in AD_name):
            AD_name = "AD2"
        elif ("AD-3" in AD_name or "ad-3" in AD_name):
            AD_name = "AD3"

        if (ad_names is not None):
            if (not any(e in AD_name for e in ad_names)):
                continue
        if (display_names is not None):
            if (not any(e in d_name for e in display_names)):
                continue
        if blockvols.block_volume_replicas is None:
            block_volume_replicas = ''
            cross_region_replication = ''
        else:
            cross_region_replication = 'On'
            block_volume_replicas = blockvols.block_volume_replicas
            bv_rep_ads = block_volume_replicas[0].availability_domain.strip()
            bv_rep_name = block_volume_replicas[0].display_name.strip()
            bv_rep_ads = bv_rep_ads.split(':')[1]
            if 'PHX' in bv_rep_ads:
                bv_rep_ad_region = 'Phoenix'
                bv_rep_ad = bv_rep_ads.split('-')[1] + bv_rep_ads.split('-')[2]
                block_volume_replicas = bv_rep_ad_region + '::' + bv_rep_ad + '::' + bv_rep_name
            elif 'ASHBURN' in bv_rep_ads:
                bv_rep_ad_region = bv_rep_ads.split('-')[1]
                bv_rep_ad = bv_rep_ads.split('-')[2] + bv_rep_ads.split('-')[3]
                bv_rep_ad_region = bv_rep_ad_region.lower().capitalize()
                block_volume_replicas = bv_rep_ad_region + '::' + bv_rep_ad + '::' + bv_rep_name
            else:
                bv_rep_ad_region = bv_rep_ads.split('-')[1]
                bv_rep_ad = bv_rep_ads.split('-')[3] + bv_rep_ads.split('-')[4]
                bv_rep_ad_region = bv_rep_ad_region.lower().capitalize()
                block_volume_replicas = bv_rep_ad_region + '::' + bv_rep_ad + '::' + bv_rep_name
        source_details = ''
        if blockvols.source_details is None:
            source_details = ''
        else:
            source_id = blockvols.source_details.id
            source_details = blockvols.source_details.type.strip() + "::" + commonTools.check_tf_variable(blockvols.display_name.strip())
            tmp_key = region + "--" + source_id
            #source_ocids[tmp_key] = commonTools.check_tf_variable(blockvols.display_name.strip())
            source_ocids[commonTools.check_tf_variable(blockvols.display_name.strip())] = tmp_key
        autotune_type = ''
        max_vpus_per_gb = ''
        if blockvols.autotune_policies == None:
            autotune_type = ''
            max_vpus_per_gb = ''
        elif len(blockvols.autotune_policies) == 1:
            autotune_type = blockvols.autotune_policies[0].autotune_type
            if autotune_type == 'PERFORMANCE_BASED':
                max_vpus_per_gb = blockvols.autotune_policies[0].max_vpus_per_gb
            else:
                max_vpus_per_gb = ''
        elif len(blockvols.autotune_policies) == 2:
            autotune_type = "BOTH"
            for autotune_policy in blockvols.autotune_policies:
                if autotune_policy.autotune_type == 'PERFORMANCE_BASED':
                    max_vpus_per_gb = autotune_policy.max_vpus_per_gb
        attachments, attachment_id, instance_name, attachment_type = volume_attachment_info(compute, ct,volume_id,export_compartments)
        asset_assignment_id, asset_policy_name, policy_comp_name = policy_info(bvol, volume_id,ct)
        block_tf_name = commonTools.check_tf_variable(blockvols.display_name)

        comp_done_ids = []
        for comp_name,comp_id in ct.ntk_compartment_ids.items():
            if volume_compartment_id == comp_id and volume_compartment_id not in comp_done_ids:
                volume_comp = comp_name
                comp_done_ids.append(volume_compartment_id)
        tf_resource = f'module.block-volumes[\\"{block_tf_name}\\"].oci_core_volume.block_volume'
        if tf_resource not in state["resources"]:
            importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(blockvols.id)}'

        tf_resource = f'module.block-volumes[\\"{block_tf_name}\\"].oci_core_volume_attachment.block_vol_instance_attachment[0]'
        if attachment_id != '' and tf_resource not in state["resources"]:
            importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(attachment_id)}'

        tf_resource = f'module.block-volumes[\\"{block_tf_name}\\"].oci_core_volume_backup_policy_assignment.volume_backup_policy_assignment[0]'
        if asset_assignment_id != '' and tf_resource not in state["resources"]:
            importCommands[region.lower()]+= f'\n{tf_or_tofu} import "{tf_resource}" {str(asset_assignment_id)}'
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
            elif col_header == 'Block Volume Replica (Region::AD::Name)':
                values_for_column[col_header].append(block_volume_replicas)
            elif col_header == 'Cross Region Replication':
                values_for_column[col_header].append(cross_region_replication)
            elif col_header == 'Source Details':
                values_for_column[col_header].append(source_details)
            elif col_header == 'Autotune Type':
                values_for_column[col_header].append(autotune_type)
            elif col_header == 'Max VPUS Per GB':
                values_for_column[col_header].append(max_vpus_per_gb)
            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(blockvols, col_header, values_for_column)
            else:
                oci_objs = [blockvols,attachments]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

# Execution of the code begins here
def export_blockvolumes(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[], export_tags=[],display_names = [], ad_names = []):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global values_for_column,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "BlockVolumes"
    # Read CD3
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- BlockVolumes  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch Block Volume Details
    print("\nFetching details of Block Volumes...")

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
        compute = ComputeClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        bvol = BlockstorageClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        for ntk_compartment_name in export_compartments:
                BVOLS = oci.pagination.list_call_get_all_results(bvol.list_volumes,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                print_blockvolumes(region, BVOLS, bvol, compute, ct, values_for_column, ntk_compartment_name, display_names, ad_names, export_compartments,export_tags, state)

        # writing volume source into variables file
        var_data = {}
        for reg in export_regions:
            file = f'{outdir}/{reg}/{service_dir}/variables_{reg}.tf'
            # Read variables file data
            with open(file, 'r') as f:
                var_data[reg] = f.read()

            tempStrOcids = ""
            for k, v in source_ocids.items():
                if v.split("--")[0].lower() == reg:
                    v = "\"" + v.split("--")[1] + "\""
                    tempStrOcids = "\t" + k + " = " + v + "\n" + tempStrOcids
            tempStrOcids = "\n" + tempStrOcids
            tempStrOcids = "#START_blockvolume_source_ocids#" + tempStrOcids + "\t#blockvolume_source_ocids_END#"
            var_data[reg] = re.sub('#START_blockvolume_source_ocids#.*?#blockvolume_source_ocids_END#', tempStrOcids,
                                   var_data[reg],
                                   flags=re.DOTALL)
            # Write variables file data
            with open(file, "w") as f:
                f.write(var_data[reg])
            f.close()

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} Block Volumes exported into CD3.\n".format(len(values_for_column["Region"])))

    # writing data
    init_commands = f'\n#!/bin/bash\n{tf_or_tofu} init\n######### Writing import for Block Volumes #########\n'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])


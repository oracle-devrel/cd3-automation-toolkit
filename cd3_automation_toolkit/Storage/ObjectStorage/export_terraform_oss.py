#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Buckets from OCI

#Author: Ranjini Rajendran
#Oracle Consulting

import sys
import oci
import re
from oci.identity import IdentityClient
from oci.config import DEFAULT_LOCATION
from oci.object_storage import ObjectStorageClient
import os
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd()+"/..")
from commonTools import *
from dateutil import parser
import subprocess as sp


importCommands = {}
oci_obj_names = {}

def print_buckets(region, outdir, service_dir,state, bucket_data, values_for_column, ntk_compartment_name,namespace_name, rp_id, retention_rule_data, rp_details, rp_name,lf_name_list,lf_name,lf_mapping,lf_excl,lf_incl,lf_prefix,ta_map,tgt_map):

    buckets_tf_name = commonTools.check_tf_variable(bucket_data.name)
    tf_resource = f'module.oss-buckets[\\"{buckets_tf_name}\\"].oci_objectstorage_bucket.bucket'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()]+=f'\n{tf_or_tofu} import "{tf_resource}" n/{namespace_name}/b/{bucket_data.name}'

    tf_resource = f'module.oss-buckets[\\"{buckets_tf_name}\\"].oci_objectstorage_replication_policy.replication_policy[0]'
    if rp_name and tf_resource not in state["resources"]:
        importCommands[region.lower()]+=f'\n{tf_or_tofu} import "{tf_resource}" n/{namespace_name}/b/{bucket_data.name}/replicationPolicies/{rp_id}'

    tf_resource = f'module.oss-buckets[\\"{buckets_tf_name}\\"].oci_objectstorage_object_lifecycle_policy.lifecycle_policy[0]'
    if bucket_data.object_lifecycle_policy_etag != None and tf_resource not in state["resources"]:
        importCommands[region.lower()]+=f'\n{tf_or_tofu} import "{tf_resource}" n/{namespace_name}/b/{bucket_data.name}/l'

    lf_names = lf_name_list if lf_name_list else ['']
    for lf_name in lf_names:
     if lf_name in lf_mapping and lf_name in lf_excl and lf_name in lf_incl and lf_name in lf_prefix and lf_name in ta_map and lf_name in tgt_map:
        for col_header in values_for_column:
            if col_header == 'Region':
                values_for_column[col_header].append(region)
            elif col_header == 'Compartment Name':
                values_for_column[col_header].append(ntk_compartment_name)
            elif col_header == 'Bucket Name':
                values_for_column[col_header].append(bucket_data.name)
            elif col_header == 'Storage Tier':
                values_for_column[col_header].append(bucket_data.storage_tier)
            elif col_header == 'Auto Tiering':
                if bucket_data.auto_tiering == 'InfrequentAccess':
                    values_for_column[col_header].append('Enabled')
                else:
                    values_for_column[col_header].append('Disabled')
            elif col_header == 'Object Versioning':
                values_for_column[col_header].append(bucket_data.versioning)
            elif col_header == 'Emit Object Events':
                if bucket_data.object_events_enabled == True:
                    values_for_column[col_header].append('Enabled')
                else:
                    values_for_column[col_header].append('Disabled')
            elif col_header == 'Visibility':
                if bucket_data.public_access_type == 'NoPublicAccess':
                    values_for_column[col_header].append('Private')
                else:
                    values_for_column[col_header].append('Public')
            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(bucket_data, col_header, values_for_column)
            elif col_header == 'Retention Rules':
                values_for_column[col_header].append(retention_rule_data)
            elif col_header == 'Replication Policy':
                values_for_column[col_header].append(rp_details)
            elif col_header == 'Lifecycle Policy Name':
                values_for_column[col_header].append(lf_name)
            elif col_header == 'Lifecycle Rule Period':
                values_for_column[col_header].append(str(ta_map[lf_name]).strip("[]'"))
            elif col_header == 'Lifecycle Target and Action':
                values_for_column[col_header].append(str(tgt_map[lf_name]).strip("[]'"))
            elif col_header == 'Lifecycle Policy Enabled':
                values_for_column[col_header].append(str(lf_mapping[lf_name])[1:-1])
            elif col_header == 'Lifecyle Exclusion Patterns':
                if lf_excl[lf_name] == ['None']:
                    values_for_column[col_header].append('')
                else:
                    exclusion_patterns = lf_excl[lf_name]
                    modified_exclusion_pattern = exclusion_patterns[0][2:-2]
                    modified_exclusion_pattern = modified_exclusion_pattern.replace("'", "")
                    values_for_column[col_header].append(str(modified_exclusion_pattern))

            elif col_header == 'Lifecyle Inclusion Patterns':
                if lf_incl[lf_name] == ['None']:
                    values_for_column[col_header].append('')
                else:
                    inclusion_patterns = lf_incl[lf_name]
                    modified_inclusion_patterns = inclusion_patterns[0][2:-2]
                    modified_inclusion_patterns = modified_inclusion_patterns.replace("'", "")
                    values_for_column[col_header].append(str(modified_inclusion_patterns))

            elif col_header == 'Lifecyle Inclusion Prefixes':
                if lf_prefix[lf_name] == ['None']:
                    values_for_column[col_header].append('')
                else:
                    inclusion_prefixes = lf_prefix[lf_name]
                    modified_inclusion_prefixes = inclusion_prefixes[0][2:-2]
                    modified_inclusion_prefixes = modified_inclusion_prefixes.replace("'", "")
                    values_for_column[col_header].append(str(modified_inclusion_prefixes))

            else:
                oci_objs = [bucket_data]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)
     else:
         for col_header in values_for_column:
             if col_header == 'Region':
                 values_for_column[col_header].append(region)
             elif col_header == 'Compartment Name':
                 values_for_column[col_header].append(ntk_compartment_name)
             elif col_header == 'Bucket Name':
                 values_for_column[col_header].append(bucket_data.name)
             elif col_header == 'Storage Tier':
                 values_for_column[col_header].append(bucket_data.storage_tier)
             elif col_header == 'Auto Tiering':
                 if bucket_data.auto_tiering == 'InfrequentAccess':
                     values_for_column[col_header].append('Enabled')
                 else:
                     values_for_column[col_header].append('Disabled')
             elif col_header == 'Object Versioning':
                 values_for_column[col_header].append(bucket_data.versioning)
             elif col_header == 'Emit Object Events':
                 if bucket_data.object_events_enabled == True:
                     values_for_column[col_header].append('Enabled')
                 else:
                     values_for_column[col_header].append('Disabled')
             elif col_header == 'Visibility':
                 if bucket_data.public_access_type == 'NoPublicAccess':
                     values_for_column[col_header].append('Private')
                 else:
                     values_for_column[col_header].append('Public')
             elif col_header.lower() in commonTools.tagColumns:
                 values_for_column = commonTools.export_tags(bucket_data, col_header, values_for_column)
             elif col_header == 'Retention Rules':
                 values_for_column[col_header].append(retention_rule_data)
             elif col_header == 'Replication Policy':
                 values_for_column[col_header].append(rp_details)
             else:
                 oci_objs = [bucket_data]
                 values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict,values_for_column)

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def export_buckets(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[],export_regions=[],export_tags=[]):
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

    # Declare variables
    sheetName = "Buckets"

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Buckets  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

        # Fetch Bucket Details
    print("\nFetching details of Buckets...")

    lifecycle_map = {}
    total_resources=0
    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()
        buckets_client = ObjectStorageClient(config=config, retry_strategy = oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        namespace = buckets_client.get_namespace().data
        namespace_name = namespace
        state = {'path':f'{outdir}/{reg}/{service_dir}','resources':[]}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"],stderr=sp.DEVNULL )
            output =  byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"","\\\""))
        except Exception as e:
            pass

        for ntk_compartment_name in export_compartments:
            ossbuckets = oci.pagination.list_call_get_all_results(buckets_client.list_buckets,namespace,compartment_id = ct.ntk_compartment_ids[ntk_compartment_name])
            for bucket in ossbuckets.data:

                bucket_name = bucket.name
                ##buckets info##
                try:
                    bucket_data = buckets_client.get_bucket(namespace_name, bucket_name, fields=['autoTiering']).data
                    # Tags filter
                    defined_tags = bucket_data.defined_tags
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
                except Exception as e:
                    print("Skipping Bucket "+bucket_name +" because of some issue. Check OCI console for details")
                    bucket_data=None
                    continue

                total_resources+=1
                #Get Retention Policies for bucket
                retention_policies = buckets_client.list_retention_rules(namespace_name, bucket_name).data
                retention_rule_data_list = []
                for retention_policy in retention_policies.items:
                    rt_name = str(retention_policy.display_name)
                    if(retention_policy.duration != None):
                        rt_time_amount = str(retention_policy.duration.time_amount)
                        rt_time_unit = str(retention_policy.duration.time_unit)
                        rt_time_rule_locked = str(retention_policy.time_rule_locked)
                        if rt_time_rule_locked != 'None' and rt_time_rule_locked != '':
                            date_obj = parser.parse(rt_time_rule_locked)
                            # rt_time_rule_locked = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                            rt_time_rule_locked = (date_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]).rstrip("0") + "Z"
                            rt_data = rt_name + "::" + rt_time_amount + "::" + rt_time_unit + "::" + rt_time_rule_locked
                        else:
                            rt_data = rt_name + "::" + rt_time_amount + "::" + rt_time_unit
                    else:
                        rt_data=rt_name + "::indefinite"
                    retention_rule_data_list.append(rt_data)

                retention_rule_data = "\n".join(retention_rule_data_list)

                # Get Replication Policies for bucket
                rp_name = None
                rp_destination_region_name = None
                rp_destination_bucket_name = None
                rp_id = None
                if bucket_data.replication_enabled != "false":
                    replication_policy = buckets_client.list_replication_policies(namespace_name, bucket_name).data
                    rp_data = {"items": replication_policy}
                    if rp_data and rp_data['items']:
                        for item in rp_data['items']:
                            rp_name = str(item.name)
                            rp_id = str(item.id)
                            rp_destination_bucket_name = str(item.destination_bucket_name)
                            rp_destination_region_name = str(item.destination_region_name)
                            region_parts = rp_destination_region_name.split("-")
                            rp_destination_region_name = region_parts[-2]
                            rp_data = rp_name + "::" + rp_destination_region_name + "::" + rp_destination_bucket_name
                    else:
                        rp_data = None

                rp_details = rp_data

                # Get lifecycle rules for the bucket
                lf_name_list = []
                lf_mapping = {}
                lf_excl = {}
                lf_incl = {}
                lf_prefix = {}
                ta_map = {}
                tgt_map = {}
                lf_exclusion_patterns = ""
                lf_inclusion_patterns = ""
                lf_inclusion_prefixes = ""
                lf_name = ""
                if bucket_data.object_lifecycle_policy_etag != None:
                    lifecycle_policy = buckets_client.get_object_lifecycle_policy(namespace_name, bucket_name).data
                    for rule in lifecycle_policy.items:
                        lf_name = str(rule.name)
                        lf_isenabled = rule.is_enabled
                        lf_tgt_map = str(rule.target) + "::" + str(rule.action)
                        lf_ta_map = str(rule.time_amount) + "::" + str(rule.time_unit)
                        if rule.object_name_filter is not None:
                            lf_exclusion_patterns = str(rule.object_name_filter.exclusion_patterns)
                            lf_inclusion_patterns = str(rule.object_name_filter.inclusion_patterns)
                            lf_inclusion_prefixes = str(rule.object_name_filter.inclusion_prefixes)
                        lf_name_list.append(lf_name)

                        # Add Rule Period value to the dictionary for the current rule name
                        if lf_name in ta_map:
                            ta_map[lf_name].append(lf_ta_map)
                        else:
                            ta_map[lf_name] = [lf_ta_map]

                        # Add Target Action Mapping value to the dictionary for the current rule name
                        if lf_name in tgt_map:
                            tgt_map[lf_name].append(lf_tgt_map)
                        else:
                            tgt_map[lf_name] = [lf_tgt_map]

                        # Add is_enabled value to the dictionary for the current rule name
                        if lf_name in lf_mapping:
                            lf_mapping[lf_name].append(lf_isenabled)
                        else:
                            lf_mapping[lf_name] = [lf_isenabled]

                        # Add exclusion patterns value to the dictionary for the current rule name
                        if lf_name in lf_excl:
                            lf_excl[lf_name].append(lf_exclusion_patterns)
                        else:
                            lf_excl[lf_name] = [lf_exclusion_patterns]

                        # Add inclusion patterns value to the dictionary for the current rule name
                        if lf_name in lf_incl:
                            lf_incl[lf_name].append(lf_inclusion_patterns)
                        else:
                            lf_incl[lf_name] = [lf_inclusion_patterns]

                        # Add inclusion prefixes value to the dictionary for the current rule name
                        if lf_name in lf_prefix:
                            lf_prefix[lf_name].append(lf_inclusion_prefixes)
                        else:
                            lf_prefix[lf_name] = [lf_inclusion_prefixes]

                print_buckets(region, outdir, service_dir,state,bucket_data, values_for_column, ntk_compartment_name, namespace_name,rp_id,retention_rule_data,rp_details,rp_name,lf_name_list,lf_name,lf_mapping,lf_excl,lf_incl,lf_prefix,ta_map,tgt_map)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} Buckets exported into CD3.\n".format(total_resources))


    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for Buckets #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands+importCommands[reg])
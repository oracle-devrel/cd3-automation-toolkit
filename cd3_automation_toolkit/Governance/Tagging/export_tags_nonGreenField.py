#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export Tags
#
#Author: Shravanthi Lingam
#Oracle Consulting
#
import argparse
import sys
import oci
from oci.identity import IdentityClient
import os
import subprocess as sp
from commonTools import *

sys.path.append(os.getcwd()+"/..")

compartment_ids={}
tf_name_namespace_list = []

def add_values_in_dict(sample_dict, key, list_of_values):
    ''' Append multiple values to a key in
        the given dictionary '''
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict

def  print_tags(values_for_column_tags,region, ntk_compartment_name, tag, tag_key, tag_default_value,reg,state):
    validator = ''
    tag_key_name = ''
    tag_key_description = ''
    tag_key_is_cost_tracking = ''
    if ( str(tag_key) != "Nan"  ):
         tag_key_name = tag_key.name
         tag_key_description = tag_key.description
         tag_key_is_cost_tracking = tag_key.is_cost_tracking
         validator = tag_key.validator
         if ( validator is not None ):
          validator = str(validator)
          validator = validator.replace("\n","")
          validator = validator.split("{  \"validator_type\": \"ENUM\",  \"values\": [    ")
          validator = validator[1].split("  ]}")
          validator = "ENUM::" + validator[0].replace("    ","")

    for col_header in values_for_column_tags.keys():
        if (col_header == "Region"):
             values_for_column_tags[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_tags[col_header].append(ntk_compartment_name)
        elif (col_header == "Tag Namespace"):
            tagname = tag.name
            values_for_column_tags[col_header].append(tagname)
            tagname = commonTools.check_columnvalue(tagname)
        elif (col_header == "Namespace Description"):
            values_for_column_tags[col_header].append(tag.description)
        elif (col_header == "Tag Keys"):
            values_for_column_tags[col_header].append(tag_key_name)
            tag_key_name = commonTools.check_columnvalue(tag_key_name)
        elif (col_header == "Tag Description"):
            values_for_column_tags[col_header].append(tag_key_description)
        elif (col_header == "Cost Tracking"):
            values_for_column_tags[col_header].append(tag_key_is_cost_tracking)
        elif (col_header == "Validator"):
            values_for_column_tags[col_header].append(validator)
        elif (col_header == "Default Tag Compartment=Default Tag Value"):
            if tag_default_value:
                default_value = ''
                if len(tag_default_value) != 0:
                    for value in tag_default_value:
                        default_value = default_value +";"+ value
                    values_for_column_tags[col_header].append(str(default_value).lstrip(';'))
                else:
                    values_for_column_tags[col_header].append('')
            else:
                values_for_column_tags[col_header].append('')

        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_tags = commonTools.export_tags(tag, col_header, values_for_column_tags)
        else:
            oci_objs = [tag,tag_key]#,tag_default]
            values_for_column_tags = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_tags,values_for_column_tags)

    tf_name_namespace = commonTools.check_tf_variable(tagname)
    tf_name_key = commonTools.check_tf_variable(tag_key_name)
    tf_resource = f'module.tag-namespaces[\\"{tf_name_namespace}\\"].oci_identity_tag_namespace.tag_namespace'
    if tag.id not in tf_name_namespace_list and tf_resource not in state["resources"]:
        importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {str(tag.id)}'
        tf_name_namespace_list.append(tag.id)
    tf_resource = f'module.tag-keys[\\"{tf_name_namespace}_{tf_name_key}\\"].oci_identity_tag.tag'
    if str(tag_key) != "Nan" and tf_resource not in state["resources"]:
        importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" tagNamespaces/{str(tag.id)}/tags/{str(tag_key_name)}'
    if tag_default_value != []:
        if len(tag_default_value) != 0:
            for value in tag_default_value:
                tf_resource = f'module.tag-defaults[\\"{tf_name_namespace}_{tf_name_key}_{commonTools.check_tf_variable(value.split("=")[0]).strip()}-default\\"].oci_identity_tag_default.tag_default'
                if tf_resource not in state["resources"]:
                    importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {str(defaultcomp_to_tagid_map[tf_name_key+"-"+commonTools.check_tf_variable(value.split("=")[0])])}'


# Execution of the code begins here
def export_tags_nongreenfield(inputfile, outdir, service_dir, config, signer, ct, export_compartments):
    global tf_import_cmd
    global values_for_column_tags
    global sheet_dict_tags
    global importCommands
    global tag_default_comps_map
    global defaultcomp_to_tagid_map,tf_or_tofu
    importCommands = {}
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile
    sheetName="Tags"

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_tags = commonTools.read_cd3(cd3file, sheetName)

    tag_default_comps_map = {}
    tag_name_id_map = {}
    defaultcomp_to_tagid_map = {}

    # Get dict for columns from Excel_Columns
    sheet_dict_tags = ct.sheet_dict[sheetName]


    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Tags would be overwritten during export process!!!\n")

    # Create backup
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
    if (os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)

    importCommands[ct.home_region] = ''
    # Fetch Tags
    print("\nFetching Tags...")
    config.__setitem__("region", ct.region_dict[ct.home_region])
    state = {'path': f'{outdir}/{ct.home_region}/{service_dir}', 'resources': []}
    try:
        byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
        output = byteOutput.decode('UTF-8').rstrip()
        for item in output.split('\n'):
            state["resources"].append(item.replace("\"", "\\\""))
    except Exception as e:
        pass
    identity = IdentityClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    region = ct.home_region.lower()
    comp_ocid_done = []

    for ntk_compartment_name in export_compartments:
        if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
            tag_defaults = oci.pagination.list_call_get_all_results(identity.list_tag_defaults,
                                                                            compartment_id=ct.ntk_compartment_ids[
                                                                                ntk_compartment_name],
                                                                            lifecycle_state="ACTIVE")
            if tag_defaults.data != []:
                for tag_default in tag_defaults.data:
                    if tag_default.tag_definition_name != '(deleted tag definition)':
                        my_val=tag_default.value
                        if tag_default.is_required==True:
                            my_val=""
                        add_values_in_dict(tag_default_comps_map, tag_default.tag_definition_id+"="+tag_default.tag_definition_name, [ntk_compartment_name+"="+my_val])
                    defaultcomp_to_tagid_map.update({ commonTools.check_tf_variable(str(tag_default.tag_definition_name).replace('\\','\\\\'))+"-"+commonTools.check_tf_variable(ntk_compartment_name) : tag_default.id })

    comp_ocid_done = []
    for ntk_compartment_name in export_compartments:
        if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
            tags = oci.pagination.list_call_get_all_results(identity.list_tag_namespaces,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],lifecycle_state="ACTIVE")

            tag_namespace_check = []
            tag_list = []
            for tag in tags.data:
                tag_list.append(str(tag.id))
                tag_keys = oci.pagination.list_call_get_all_results(identity.list_tags, tag_namespace_id=tag.id,
                                                                            lifecycle_state="ACTIVE")
                tag_key_check = []
                tag_default_check = []
                for tag_key in tag_keys.data:
                    tag_key = identity.get_tag(tag.id, tag_key.name)
                    tag_key = tag_key.data
                    tag_key_id = str(tag_key.id)
                    tag_key_check.append(tag_key_id)
                    tag_name_id_map.update({ tag_key.id : tag_key.name })
                    if (tag_key.id+"="+tag_key.name in tag_default_comps_map):
                        tag_default_check.append(str(tag_key.id))
                        tag_default_value = tag_default_comps_map[tag_key.id+"="+tag_key.name]
                        tag_namespace_check.append(str(tag.id))
                        print_tags(values_for_column_tags, region, ntk_compartment_name, tag, tag_key,tag_default_value,ct.home_region,state)
                check_non_default_tags = [i for i in tag_key_check + tag_default_check if i not in tag_key_check or i not in tag_default_check]
                for tag_check in check_non_default_tags:
                    for tag_key in tag_keys.data:
                        if (tag_check in tag_key.id):
                            tag_key = identity.get_tag(tag.id, tag_key.name)
                            tag_key = tag_key.data
                            tag_default_value = ''
                            tag_namespace_check.append(str(tag.id))
                            print_tags(values_for_column_tags, region, ntk_compartment_name, tag, tag_key,tag_default_value,ct.home_region,state)
            tag_namespace_check = list(dict.fromkeys(tag_namespace_check))
            check_non_key_tags = [i for i in tag_list + tag_namespace_check if i not in tag_list or i not in tag_namespace_check]
            for tag_check in check_non_key_tags:
                tag_key = "Nan"
                tag_default_value = ''
                for tag in tags.data:
                    if (tag_check in tag.id):
                        tag = identity.get_tag_namespace(tag.id).data
                        print_tags(values_for_column_tags, region, ntk_compartment_name, tag, tag_key,tag_default_value,ct.home_region,state)

    commonTools.write_to_cd3(values_for_column_tags, cd3file, "Tags")
    print("{0} rows exported into CD3 for Tagging Resources.\n".format(len(values_for_column_tags["Region"])))

    init_commands = f'\n######### Writing import for Tagging #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    if importCommands[ct.home_region] != "":
        importCommands[ct.home_region] += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands[ct.home_region])


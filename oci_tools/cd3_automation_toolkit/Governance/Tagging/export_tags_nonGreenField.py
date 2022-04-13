#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI solutions components
# Notifications & Subscriptions
#
#Author: Shravanthi Lingam
#Oracle Consulting
#
import argparse
import sys
import oci
from oci.identity import IdentityClient
from oci.config import DEFAULT_LOCATION
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *

compartment_ids={}
importCommands={}
tf_name_namespace_list = []

def add_values_in_dict(sample_dict, key, list_of_values):
    ''' Append multiple values to a key in
        the given dictionary '''
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict

def  print_tags(values_for_column_tags,region, ntk_compartment_name, tag, tag_key, tag_default_value, tag_default, tag_default_comp):
    if ( tag_default_value == '' ) :
     tag_default_comp = ""
     tag_default_id = ''
    else:
     tag_default_id = tag_default.id
     if (tag_default.is_required is True):
        tag_default_value = ""
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
        elif (col_header == "Default Tag Compartment"):
            if "ocid1.tagdefinition.oc1" in str(tag_default_comp):
                values_for_column_tags[col_header].append(','.join([str(item) for item in tag_default_comps_map[tag_default_comp]]))
            else:
                values_for_column_tags[col_header].append(tag_default_comp)
        elif (col_header == "Default Tag Value"):
            values_for_column_tags[col_header].append(tag_default_value)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_tags = commonTools.export_tags(tag, col_header, values_for_column_tags)
        else:
            oci_objs = [tag,tag_key,tag_default]
            values_for_column_tags = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_tags,values_for_column_tags)

    tf_name_namespace = commonTools.check_tf_variable(tagname)
    tf_name_key = commonTools.check_tf_variable(tag_key_name)
    if (tag.id not in tf_name_namespace_list):
        importCommands[region].write("\nterraform import \"module.tag-namespaces[\\\"" + tf_name_namespace + "\\\"].oci_identity_tag_namespace.tag_namespace\" " + str(tag.id))
        tf_name_namespace_list.append(tag.id)
    if ( str(tag_key) != "Nan" ):
      importCommands[region].write("\nterraform import \"module.tag-keys[\\\""+tf_name_namespace + '-' + tf_name_key + '\\\"].oci_identity_tag.tag\" ' + "tagNamespaces/"+ str(tag.id) +"/tags/\"" + str(tag_key_name) + "\"")
    if ( tag_default_comp != ''):
        for comp in tag_default_comps_map[tag_default_comp]:
            importCommands[region].write("\nterraform import \"module.tag-defaults[\\\""+ tf_name_namespace+'-' +tf_name_key + '-' +commonTools.check_tf_variable(comp)+ '-default'+ '\\\"].oci_identity_tag_default.tag_default\" ' + str(tag_default_id))


def parse_args():
    parser = argparse.ArgumentParser(description="Export Tags on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export tag objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", default=[], nargs='*', help="comma seperated Compartments for which to export Identity Objects", required=False)
    return parser.parse_args()


def export_tags_nongreenfield(inputfile, outdir, _config, network_compartments):
    global tf_import_cmd
    global values_for_column_tags
    global sheet_dict_tags
    global importCommands
    global config
    global tag_default_comps_map

    cd3file = inputfile
    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_tags = commonTools.read_cd3(cd3file, "Tags")

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)
    tag_default_comps_map = {}
    tag_name_id_map = {}

    # Get dict for columns from Excel_Columns
    sheet_dict_tags = ct.sheet_dict["Tags"]


    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Tags would be overwritten during export process!!!\n")

    # Create backups
    if (os.path.exists(outdir + "/" + ct.home_region + "/tf_import_commands_tags_nonGF.sh")):
               commonTools.backup_file(outdir + "/" + ct.home_region, "tf_import_tags", "tf_import_commands_tags_nonGF.sh")
    importCommands[ct.home_region] = open(outdir + "/" + ct.home_region + "/tf_import_commands_tags_nonGF.sh", "w")
    importCommands[ct.home_region].write("#!/bin/bash")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].write("terraform init")

    # Fetch Tags
    print("\nFetching Tags...")
    importCommands[ct.home_region].write("\n\n######### Writing import for Tags #########\n\n")
    config.__setitem__("region", ct.region_dict[ct.home_region])
    identity = IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    region = ct.home_region.lower()
    comp_ocid_done = []

    for ntk_compartment_name in ct.ntk_compartment_ids:
        if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
            tag_defaults = oci.pagination.list_call_get_all_results(identity.list_tag_defaults,
                                                                            compartment_id=ct.ntk_compartment_ids[
                                                                                ntk_compartment_name],
                                                                            lifecycle_state="ACTIVE")
            if tag_defaults.data != []:
                for tag_default in tag_defaults.data:
                    add_values_in_dict(tag_default_comps_map, tag_default.tag_definition_id, [ntk_compartment_name])

    comp_ocid_done = []
    for ntk_compartment_name in ct.ntk_compartment_ids:
        if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
            tags = oci.pagination.list_call_get_all_results(identity.list_tag_namespaces,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],lifecycle_state="ACTIVE")
            tag_defaults = oci.pagination.list_call_get_all_results(identity.list_tag_defaults,
                                                                            compartment_id=ct.ntk_compartment_ids[
                                                                                ntk_compartment_name],
                                                                            lifecycle_state="ACTIVE")

            tag_namespace_check = []
            tag_list = []
            tag_default_comp = ''
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
                    for tag_default in tag_defaults.data:
                        if (ct.ntk_compartment_ids[ntk_compartment_name] == tag_default.compartment_id):
                            tag_default_comp = ntk_compartment_name
                            if ("::" in ntk_compartment_name):
                                tag_default_comp = ntk_compartment_name
                        if (tag_key.id == tag_default.tag_definition_id):
                            tag_key_id = str(tag_key.id)
                            tag_default_check.append(tag_key_id)
                            tag_default_value = tag_default.value
                            tag_namespace_check.append( str(tag.id))
                            print_tags(values_for_column_tags, region, ntk_compartment_name, tag, tag_key,
                                               tag_default_value, tag_default, tag_key_id)
                check_non_default_tags = [i for i in tag_key_check + tag_default_check if
                                                  i not in tag_key_check or i not in tag_default_check]
                for tag_check in check_non_default_tags:
                    for tag_key in tag_keys.data:
                        if (tag_check in tag_key.id):
                            tag_key = identity.get_tag(tag.id, tag_key.name)
                            tag_key = tag_key.data
                            tag_default_value = ''
                            tag_default = ''
                            tag_namespace_check.append( str(tag.id))
                            print_tags(values_for_column_tags, region, ntk_compartment_name, tag, tag_key,
                                               tag_default_value, tag_default, tag_default_comp)

            tag_namespace_check = list(dict.fromkeys(tag_namespace_check))
            check_non_key_tags = [i for i in tag_list + tag_namespace_check if i not in tag_list or i not in tag_namespace_check]
            for tag_check in check_non_key_tags:
                tag_key = str(tag_key)
                tag_key = "Nan"
                tag_default_value = ''
                tag_default = ''
                tag_default_comp = ''
                for tag in tags.data:
                    if (tag_check in tag.id):
                        tag = identity.get_tag_namespace(tag.id).data
                        print_tags(values_for_column_tags, region, ntk_compartment_name, tag, tag_key,
                                       tag_default_value, tag_default, tag_default_comp)

    commonTools.write_to_cd3(values_for_column_tags, cd3file, "Tags")
    print("Tags exported to CD3\n")

    script_file = f'{outdir}/{ct.home_region}/tf_import_commands_tags_nonGF.sh'
    with open(script_file, 'a') as importCommands[ct.home_region]:
        importCommands[ct.home_region].write('\n\nterraform plan\n')
    if "linux" in sys.platform:
        os.chmod(script_file, 0o755)

if __name__=="__main__":
    args = parse_args()
    export_tags_nongreenfield(args.inputfile, args.outdir, args.config, args.network_compartments)

#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
#put them into CD3 Excel and create TF files

#Author: Suruchi
#Oracle Consulting
#

import argparse
import sys
import oci
import re
from oci.identity import IdentityClient
from oci.config import DEFAULT_LOCATION
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *


def parse_args():
    parser = argparse.ArgumentParser(description="Export Identity Objects in OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export identity objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", required=False, nargs='*', help="comma seperated Compartments for which to export Identity Objects")
    return parser.parse_args()


def export_identity(inputfile, outdir, _config, network_compartments=[]):
    global values_for_column_comps
    global values_for_column_groups
    global values_for_column_policies
    global sheet_dict_comps
    global sheet_dict_groups
    global sheet_dict_policies
    global config
    global cd3file

    cd3file = inputfile
    input_compartment_list = network_compartments

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()


    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)
    #config = oci.config.from_file()

    importCommands={}

    sheetName_comps = "Compartments"
    sheetName_groups = "Groups"
    sheetName_policies = "Policies"

    # Read CD3 Identity Sheets
    df, values_for_column_comps = commonTools.read_cd3(cd3file, sheetName_comps)
    df, values_for_column_groups = commonTools.read_cd3(cd3file, sheetName_groups)
    df, values_for_column_policies = commonTools.read_cd3(cd3file, sheetName_policies)

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Get dict for columns from Excel_Columns
    sheet_dict_comps = ct.sheet_dict[sheetName_comps]
    sheet_dict_groups = ct.sheet_dict[sheetName_groups]
    sheet_dict_policies = ct.sheet_dict[sheetName_policies]

    print("Fetching for all Compartments...")
    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Compartments, Groups, Policies would be overwritten during export process!!!\n")

    # Create backup
    resource = 'tf_import_identity'
    file_name='tf_import_commands_identity_nonGF.sh'
    script_file = f'{outdir}/{ct.home_region}/'+file_name
    if(os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region,resource,file_name)
    importCommands[ct.home_region] = open(script_file, "w")
    importCommands[ct.home_region].write("#!/bin/bash")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].write("terraform init")

    config.__setitem__("region", ct.region_dict[ct.home_region])
    idc=IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

    #Fetch Compartments
    print("\nFetching Compartments...")
    importCommands[ct.home_region].write("\n######### Writing import for Compartments #########\n")

    comp_ocids_done=[]
    root_index = 0
    sub_comp_l1_index = 0
    sub_comp_l2_index = 0
    sub_comp_l3_index = 0
    sub_comp_l4_index = 0
    sub_comp_l5_index = 0

    for c_name, c_id in ct.ntk_compartment_ids.items():
        c_details=idc.get_compartment(c_id).data

        #write child comps info
        if("::" in c_name):
            c_names=c_name.rsplit("::", 1)
            comp_display_name = c_names[1]
            comp_parent_name = c_names[0]
            tf_name = commonTools.check_tf_variable(c_name)
            if len(c_name.split("::")) == 2:
                importCommands[ct.home_region].write("\nterraform import \"module.sub-compartments-level1[\\\""+str(tf_name)+"\\\"].oci_identity_compartment.compartment\" " + c_id)
                sub_comp_l1_index = sub_comp_l1_index + 1
            if len(c_name.split("::")) == 3:
                importCommands[ct.home_region].write("\nterraform import \"module.sub-compartments-level2[\\\""+str(tf_name)+"\\\"].oci_identity_compartment.compartment\" " + c_id)
                sub_comp_l2_index = sub_comp_l2_index + 1
            if len(c_name.split("::")) == 4:
                importCommands[ct.home_region].write("\nterraform import \"module.sub-compartments-level3[\\\""+str(tf_name)+"\\\"].oci_identity_compartment.compartment\" " + c_id)
                sub_comp_l3_index = sub_comp_l3_index + 1
            if len(c_name.split("::")) == 5:
                importCommands[ct.home_region].write("\nterraform import \"module.sub-compartments-level4[\\\""+str(tf_name)+"\\\"].oci_identity_compartment.compartment\" " + c_id)
                sub_comp_l4_index = sub_comp_l4_index + 1
            if len(c_name.split("::")) == 6:
                importCommands[ct.home_region].write("\nterraform import \"module.sub-compartments-level5[\\\""+str(tf_name)+"\\\"].oci_identity_compartment.compartment\" " + c_id)
                sub_comp_l5_index = sub_comp_l5_index + 1

        #write parent comp info(at root)
        else:
            parent_c_id = c_details.compartment_id
            # if it root compartment
            if(parent_c_id==ct.ntk_compartment_ids["root"]):
                comp_display_name=c_name
                comp_parent_name = "root"
                tf_name = commonTools.check_tf_variable(c_name)
                importCommands[ct.home_region].write("\nterraform import \"module.iam-compartments[\\\""+str(tf_name)+"\\\"].oci_identity_compartment.compartment\" " + c_id)
                root_index = root_index + 1
            else:
                continue
        if(c_id not in comp_ocids_done):
            comp_ocids_done.append(c_id)
            for col_header in values_for_column_comps.keys():
                if(col_header == "Region"):
                    values_for_column_comps[col_header].append(ct.home_region.capitalize())
                elif(col_header == "Name"):
                    values_for_column_comps[col_header].append(comp_display_name)
                elif(col_header == "Parent Compartment"):
                    values_for_column_comps[col_header].append(comp_parent_name)
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_comps = commonTools.export_tags(c_details, col_header, values_for_column_comps)
                else:
                    oci_objs=[c_details]
                    values_for_column_comps=commonTools.export_extra_columns(oci_objs,col_header,sheet_dict_comps,values_for_column_comps)

    commonTools.write_to_cd3(values_for_column_comps,cd3file,sheetName_comps)
    print("Compartments exported to CD3\n")

    #Fetch Groups
    print("\nFetching Groups...")
    importCommands[ct.home_region].write("\n######### Writing import for Groups #########\n")
    groups = oci.pagination.list_call_get_all_results(idc.list_groups,compartment_id=config['tenancy'])
    dyngroups=oci.pagination.list_call_get_all_results(idc.list_dynamic_groups,compartment_id=config['tenancy'])
    index = 0
    for group in groups.data:
        grp_info=group
        if(grp_info.lifecycle_state == "ACTIVE"):
            grp_display_name=grp_info.name
            tf_name=commonTools.check_tf_variable(grp_display_name)
            importCommands[ct.home_region].write("\nterraform import \"module.iam-groups[\\\""+str(tf_name)+"\\\"].oci_identity_group.group[0]\" "+grp_info.id)
            index = index + 1
            for col_header in values_for_column_groups.keys():
                if (col_header == "Region"):
                    values_for_column_groups[col_header].append(ct.home_region.capitalize())
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_groups = commonTools.export_tags(grp_info, col_header, values_for_column_groups)
                else:
                    oci_objs=[grp_info]
                    values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_groups,values_for_column_groups)

    for group in dyngroups.data:
        grp_info=group
        if(grp_info.lifecycle_state == "ACTIVE"):
            grp_display_name=grp_info.name
            tf_name=commonTools.check_tf_variable(grp_display_name)
            importCommands[ct.home_region].write("\nterraform import \"module.iam-groups[\\\""+str(tf_name)+"\\\"].oci_identity_dynamic_group.dynamic_group[0]\" "+grp_info.id)
            index = index + 1
            for col_header in values_for_column_groups.keys():
                if (col_header == "Region"):
                    values_for_column_groups[col_header].append(ct.home_region.capitalize())
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_groups = commonTools.export_tags(grp_info, col_header, values_for_column_groups)
                else:
                    oci_objs=[grp_info]
                    values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_groups,values_for_column_groups)


    commonTools.write_to_cd3(values_for_column_groups,cd3file,sheetName_groups)
    print("Groups exported to CD3\n")

    # Fetch Policies
    print("\nFetching Policies...")
    importCommands[ct.home_region].write("\n\n######### Writing import for Policies #########\n\n")
    comp_ocid_done = []
    index = 0
    for ntk_compartment_name in ct.ntk_compartment_ids:
        if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
            policies = oci.pagination.list_call_get_all_results(idc.list_policies, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
            for policy in policies.data:
                policy_name=policy.name
                policy_comp_id=policy.compartment_id
                if (policy_comp_id == config['tenancy']):
                    policy_comp = 'root'
                else:
                    keys = []
                    for k, v in ct.ntk_compartment_ids.items():
                        if (v == policy_comp_id):
                            keys.append(k)

                    if (len(keys) > 1):
                        for key in keys:
                            if ("::" in key):
                                policy_comp = key
                    else:
                        policy_comp = keys[0]

                if (policy_comp != "root"):
                    tf_name = policy_comp+"_"+policy_name
                else:
                    tf_name = policy_name


                tf_name = commonTools.check_tf_variable(tf_name)
                importCommands[ct.home_region].write("\nterraform import \"module.iam-policies[\\\""+str(tf_name)+"\\\"].oci_identity_policy.policy\" " + policy.id)
                index = index + 1
                count=1
                policy_statements = policy.statements
                for stmt in policy_statements:
                    #Commented as statement case was changing
                    """if(" compartment " in stmt.lower()):
                        policy_compartment_name=stmt.lower().split(" compartment ")[1].split()[0]
                        stmt=re.sub(r'%s([\s]|$)'%policy_compartment_name, r'* ', stmt.lower())
                    elif(" tenancy" in stmt.lower()):
                        policy_compartment_name=''
        
                    if(" group " in stmt.lower()):
                        policy_grp_name=stmt.lower().split(" group ")[1].split()[0]
                        stmt=re.sub(r'%s([\s]|$)'%policy_grp_name, r'$ ', stmt.lower())
                    else:
                        policy_grp_name=""
                    """
                    if(count==1):
                        for col_header in values_for_column_policies.keys():
                            if (col_header == "Region"):
                                values_for_column_policies[col_header].append(ct.home_region.capitalize())
                            elif (col_header == "Compartment Name"):
                                values_for_column_policies[col_header].append(policy_comp)
                            elif (col_header == "Policy Statement Compartment"):
                                values_for_column_policies[col_header].append("")
                            elif (col_header == "Policy Statement Groups"):
                                values_for_column_policies[col_header].append("")
                            elif(col_header == "Policy Statements"):
                                values_for_column_policies[col_header].append(stmt)
                            elif col_header.lower() in commonTools.tagColumns:
                                values_for_column_policies = commonTools.export_tags(policy, col_header,values_for_column_policies)
                            else:
                                oci_objs=[policy]
                                values_for_column_policies = commonTools.export_extra_columns(oci_objs, col_header,sheet_dict_policies,values_for_column_policies)
                    else:
                        for col_header in values_for_column_policies.keys():
                            if (col_header == "Policy Statements"):
                                values_for_column_policies[col_header].append(stmt)
                            else:
                                values_for_column_policies[col_header].append("")

                    count=count+1

    commonTools.write_to_cd3(values_for_column_policies,cd3file,sheetName_policies)
    print("Policies exported to CD3\n")

    with open(script_file, 'a') as importCommands[ct.home_region]:
        importCommands[ct.home_region].write('\n\nterraform plan\n')

if __name__=="__main__":
    args = parse_args()
    export_identity(args.inputfile, args.outdir, args.config, args.network_compartments)

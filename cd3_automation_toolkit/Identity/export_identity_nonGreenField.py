#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
# Compartments, Groups, Policies

# Author: Suruchi
# Updated by Ranjini Rajendran
# Users export code updated by Gaurav Goyal
# Oracle Consulting
#

import sys
import oci
from oci.identity import IdentityClient
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *

# Execution of the code begins here
def export_identity(inputfile, outdir, service_dir,resource, config, signer, ct, export_compartments=[],export_domains={}):
    global values_for_column_comps
    global values_for_column_groups
    global values_for_column_policies
    global sheet_dict_comps
    global sheet_dict_groups
    global sheet_dict_policies
    global cd3file
    global importCommands


    cd3file = inputfile

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    importCommands={}
    config.__setitem__("region", ct.region_dict[ct.home_region])
    idc = IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)

    if resource == "Compartments":
        importCommands = ""
        sheetName_comps = "Compartments"
        # Read CD3 Identity Sheets
        df, values_for_column_comps = commonTools.read_cd3(cd3file, sheetName_comps)
        # Get dict for columns from Excel_Columns
        sheet_dict_comps = ct.sheet_dict[sheetName_comps]
        print("Tabs- Compartments would be overwritten during export process!!!\n")
        # Create backup
        resource = 'tf_import_' + sheetName_comps.lower()
        file_name = 'tf_import_commands_' + sheetName_comps.lower() + '_nonGF.sh'
        script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)
        importCommands += "#!/bin/bash\n"
        importCommands += "terraform init\n"
        importCommands += "\n######### Writing import for Compartments #########\n\n"

        # Fetch Compartments
        print("\nFetching Compartments...")

        comp_ocids_done = []
        root_index = 0
        sub_comp_l1_index = 0
        sub_comp_l2_index = 0
        sub_comp_l3_index = 0
        sub_comp_l4_index = 0
        sub_comp_l5_index = 0

        if ct.ntk_compartment_ids:
            compartments = ct.ntk_compartment_ids.items()
        else:
            ct.get_network_compartment_ids(config['tenancy'], "root", config, signer)
            compartments = ct.ntk_compartment_ids.items()

        for c_name, c_id in compartments:
            c_details = idc.get_compartment(c_id).data

            # write child comps info
            if ("::" in c_name):
                c_names = c_name.rsplit("::", 1)
                comp_display_name = c_names[1]
                comp_parent_name = c_names[0]
                tf_name = commonTools.check_tf_variable(c_name)
                if len(c_name.split("::")) == 2:
                    importCommands += "\nterraform import \"module.sub-compartments-level1[\\\"" + str(tf_name
                                                                                         ) + "\\\"].oci_identity_compartment.compartment\" " + c_id

                    sub_comp_l1_index = sub_comp_l1_index + 1
                if len(c_name.split("::")) == 3:
                    importCommands += "\nterraform import \"module.sub-compartments-level2[\\\"" + str(tf_name
                                                                                         ) + "\\\"].oci_identity_compartment.compartment\" " + c_id

                    sub_comp_l2_index = sub_comp_l2_index + 1
                if len(c_name.split("::")) == 4:
                    importCommands += "\nterraform import \"module.sub-compartments-level3[\\\"" + str(tf_name
                                                                                         ) + "\\\"].oci_identity_compartment.compartment\" " + c_id

                    sub_comp_l3_index = sub_comp_l3_index + 1
                if len(c_name.split("::")) == 5:
                    importCommands += "\nterraform import \"module.sub-compartments-level4[\\\"" + str(tf_name
                                                                                         ) + "\\\"].oci_identity_compartment.compartment\" " + c_id

                    sub_comp_l4_index = sub_comp_l4_index + 1
                if len(c_name.split("::")) == 6:
                    importCommands += "\nterraform import \"module.sub-compartments-level5[\\\"" + str(tf_name
                                                                                         ) + "\\\"].oci_identity_compartment.compartment\" " + c_id

                    sub_comp_l5_index = sub_comp_l5_index + 1

            # write parent comp info(at root)
            else:
                parent_c_id = c_details.compartment_id
                # if it root compartment
                if (parent_c_id == ct.ntk_compartment_ids["root"]):
                    comp_display_name = c_name
                    comp_parent_name = "root"
                    tf_name = commonTools.check_tf_variable(c_name)
                    importCommands += "\nterraform import \"module.iam-compartments[\\\"" + str(
                        tf_name
                        ) + "\\\"].oci_identity_compartment.compartment\" " + c_id

                    root_index = root_index + 1
                else:
                    continue
            if (c_id not in comp_ocids_done):
                comp_ocids_done.append(c_id)
                for col_header in values_for_column_comps.keys():
                    if (col_header == "Region"):
                        values_for_column_comps[col_header].append(ct.home_region.capitalize())
                    elif (col_header == "Name"):
                        values_for_column_comps[col_header].append(comp_display_name)
                    elif (col_header == "Parent Compartment"):
                        values_for_column_comps[col_header].append(comp_parent_name)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_comps = commonTools.export_tags(c_details, col_header,
                                                                          values_for_column_comps
                                                                          )
                    else:
                        oci_objs = [c_details]
                        values_for_column_comps = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                   sheet_dict_comps,
                                                                                   values_for_column_comps
                                                                                   )
        importCommands += "\nterraform plan"
        if importCommands != "":
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(importCommands)
        commonTools.write_to_cd3(values_for_column_comps, cd3file, sheetName_comps)
        print("{0} Compartments exported into CD3.\n".format(len(values_for_column_comps["Region"])))

    elif resource == "IAM Policies":
        importCommands = ""
        sheetName_policies = "Policies"
        df, values_for_column_policies = commonTools.read_cd3(cd3file, sheetName_policies)
        sheet_dict_policies = ct.sheet_dict[sheetName_policies]
        print("Tabs- Policies would be overwritten during export process!!!\n")
        # Create backup
        resource = 'tf_import_' + sheetName_policies.lower()
        file_name = 'tf_import_commands_' + sheetName_policies.lower() + '_nonGF.sh'
        script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)
        importCommands += "#!/bin/bash\n"
        importCommands += "terraform init\n"
        importCommands += "\n######### Writing import for Policies #########\n\n"
        # Fetch Policies
        print("\nFetching Policies...")
        comp_ocid_done = []
        index = 0
        for ntk_compartment_name in export_compartments:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                policies = oci.pagination.list_call_get_all_results(idc.list_policies,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name]
                                                                    )
                for policy in policies.data:
                    policy_name = policy.name
                    policy_comp_id = policy.compartment_id
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
                        tf_name = policy_comp + "_" + policy_name
                    else:
                        tf_name = policy_name

                    tf_name = commonTools.check_tf_variable(tf_name)
                    importCommands += "\nterraform import \"module.iam-policies[\\\"" + str(tf_name
                                                                                                               ) + "\\\"].oci_identity_policy.policy\" " + policy.id

                    index = index + 1
                    count = 1
                    policy_statements = policy.statements
                    for stmt in policy_statements:
                        # Commented as statement case was changing
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
                        if (count == 1):
                            for col_header in values_for_column_policies.keys():
                                if (col_header == "Region"):
                                    values_for_column_policies[col_header].append(ct.home_region.capitalize())
                                elif (col_header == "Compartment Name"):
                                    values_for_column_policies[col_header].append(policy_comp)
                                elif (col_header == "Policy Statement Compartment"):
                                    values_for_column_policies[col_header].append("")
                                elif (col_header == "Policy Statement Groups"):
                                    values_for_column_policies[col_header].append("")
                                elif (col_header == "Policy Statements"):
                                    values_for_column_policies[col_header].append(stmt)
                                elif col_header.lower() in commonTools.tagColumns:
                                    values_for_column_policies = commonTools.export_tags(policy, col_header,
                                                                                         values_for_column_policies
                                                                                         )
                                else:
                                    oci_objs = [policy]
                                    values_for_column_policies = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                                  sheet_dict_policies,
                                                                                                  values_for_column_policies
                                                                                                  )
                        else:
                            for col_header in values_for_column_policies.keys():
                                if (col_header == "Policy Statements"):
                                    values_for_column_policies[col_header].append(stmt)
                                else:
                                    values_for_column_policies[col_header].append("")

                        count = count + 1
        importCommands += "\nterraform plan"
        if importCommands != "":
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(importCommands)
        commonTools.write_to_cd3(values_for_column_policies, cd3file, sheetName_policies)
        print("{0} Policies exported into CD3.\n".format(len(values_for_column_policies["Region"])))

    elif resource == "IAM Groups":
        importCommands = ""
        sheetName_groups = "Groups"
        df, values_for_column_groups = commonTools.read_cd3(cd3file, sheetName_groups)
        sheet_dict_groups = ct.sheet_dict[sheetName_groups]
        print("Tabs- Groups would be overwritten during export process!!!\n")

        config.__setitem__("region", ct.region_dict[ct.home_region])
        idc = IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)

        # Create backup
        resource = 'tf_import_'+ sheetName_groups.lower()
        file_name = 'tf_import_commands_' + sheetName_groups.lower() + '_nonGF.sh'
        script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)
        importCommands += "#!/bin/bash\n"
        importCommands += "terraform init\n"
        importCommands += "\n######### Writing import for Groups #########\n\n"
        # Fetch Groups
        print("\nFetching Groups...")

        groups = oci.pagination.list_call_get_all_results(idc.list_groups,compartment_id=config['tenancy'])
        dyngroups=oci.pagination.list_call_get_all_results(idc.list_dynamic_groups,compartment_id=config['tenancy'])
        index = 0
        groupsDict = {}

        for group in groups.data:
            grp_info=group
            if(grp_info.lifecycle_state == "ACTIVE"):
                groupsDict[grp_info.id] = grp_info.name
                grp_display_name=grp_info.name
                tf_name=commonTools.check_tf_variable(grp_display_name)
                importCommands += "\nterraform import \"module.iam-groups[\\\""+str(tf_name)+"\\\"].oci_identity_group.group[0]\" "+grp_info.id
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
                groupsDict[grp_info.id] = grp_info.name
                grp_display_name=grp_info.name
                tf_name=commonTools.check_tf_variable(grp_display_name)
                importCommands += "\nterraform import \"module.iam-groups[\\\""+str(tf_name)+"\\\"].oci_identity_dynamic_group.dynamic_group[0]\" "+grp_info.id
                index = index + 1
                for col_header in values_for_column_groups.keys():
                    if (col_header == "Region"):
                        values_for_column_groups[col_header].append(ct.home_region.capitalize())
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_groups = commonTools.export_tags(grp_info, col_header, values_for_column_groups)
                    else:
                        oci_objs=[grp_info]
                        values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_groups,values_for_column_groups)

        importCommands += "\nterraform plan"
        if importCommands != "":
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(importCommands)
        commonTools.write_to_cd3(values_for_column_groups,cd3file,sheetName_groups)
        print("{0} Groups exported into CD3.\n".format(len(values_for_column_groups["Region"])))

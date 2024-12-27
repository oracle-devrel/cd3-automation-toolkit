#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
# Compartments, Groups, Policies

# Author: Suruchi
# Updated by Ranjini Rajendran
# Users export code updated by Gaurav Goyal
# Oracle Consulting

import sys
import oci
from oci.identity import IdentityClient
import os
import subprocess as sp
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
    global importCommands,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]


    cd3file = inputfile

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    config.__setitem__("region", ct.region_dict[ct.home_region])
    state = {'path': f'{outdir}/{ct.home_region}/{service_dir}', 'resources': []}
    try:
        byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
        output = byteOutput.decode('UTF-8').rstrip()
        for item in output.split('\n'):
            state["resources"].append(item.replace("\"", "\\\""))
    except Exception as e:
        pass
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
        resource = 'import_' + sheetName_comps.lower()
        file_name = 'import_commands_' + sheetName_comps.lower()+".sh"
        script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)

        # Fetch Compartments
        print("\nFetching Compartments...")

        comp_ocids_done = []
        root_index = 0
        sub_comp_l1_index = 0
        sub_comp_l2_index = 0
        sub_comp_l3_index = 0
        sub_comp_l4_index = 0
        sub_comp_l5_index = 0

        compartments={}

        if ct.ntk_compartment_ids:
            compartments = ct.ntk_compartment_ids.items()
        else:
            ct.get_network_compartment_ids(config['tenancy'], "root", config, signer)
            compartments = ct.ntk_compartment_ids.items()

        total_c = 0
        for c_name, c_id in compartments:
            total_c = total_c+1
            c_details = idc.get_compartment(c_id).data
            tf_resource = ""
            # write child comps info
            if ("::" in c_name):
                c_names = c_name.rsplit("::", 1)
                comp_display_name = c_names[1]
                comp_parent_name = c_names[0]
                tf_name = commonTools.check_tf_variable(c_name)
                if len(c_name.split("::")) == 2:
                    tf_resource = f'module.sub-compartments-level1[\\"{tf_name}\\"].oci_identity_compartment.compartment'
                    sub_comp_l1_index = sub_comp_l1_index + 1
                elif len(c_name.split("::")) == 3:
                    tf_resource = f'module.sub-compartments-level2[\\"{tf_name}\\"].oci_identity_compartment.compartment'
                    sub_comp_l2_index = sub_comp_l2_index + 1
                elif len(c_name.split("::")) == 4:
                    tf_resource = f'module.sub-compartments-level3[\\"{tf_name}\\"].oci_identity_compartment.compartment'
                    sub_comp_l3_index = sub_comp_l3_index + 1
                elif len(c_name.split("::")) == 5:
                    tf_resource = f'module.sub-compartments-level4[\\"{tf_name}\\"].oci_identity_compartment.compartment'
                    sub_comp_l4_index = sub_comp_l4_index + 1
                elif len(c_name.split("::")) == 6:
                    tf_resource = f'module.sub-compartments-level5[\\"{tf_name}\\"].oci_identity_compartment.compartment'
                    sub_comp_l5_index = sub_comp_l5_index + 1

            # write parent comp info(at root)
            else:
                parent_c_id = c_details.compartment_id
                # if it root compartment
                if (parent_c_id == ct.ntk_compartment_ids["root"]):
                    comp_display_name = c_name
                    comp_parent_name = "root"
                    tf_name = commonTools.check_tf_variable(c_name)
                    tf_resource = f'module.iam-compartments[\\"{tf_name}\\"].oci_identity_compartment.compartment'
                    root_index = root_index + 1
                else:
                    continue
            if tf_resource not in state["resources"]:
                importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {c_id}'
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

        init_commands = f'\n######### Writing import for Compartments #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands != "":
            importCommands += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands)
        commonTools.write_to_cd3(values_for_column_comps, cd3file, sheetName_comps)
        print("{0} Compartments exported into CD3.\n".format(total_c))

    elif resource == "IAM Policies":
        importCommands = ""
        sheetName_policies = "Policies"
        df, values_for_column_policies = commonTools.read_cd3(cd3file, sheetName_policies)
        sheet_dict_policies = ct.sheet_dict[sheetName_policies]
        print("Tabs- Policies would be overwritten during export process!!!\n")
        # Create backup
        resource = 'import_' + sheetName_policies.lower()
        file_name = 'import_commands_' + sheetName_policies.lower() + '.sh'
        script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)
        # Fetch Policies
        print("\nFetching Policies...")
        comp_ocid_done = []
        index = 0
        total_p = 0
        for ntk_compartment_name in export_compartments:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                policies = oci.pagination.list_call_get_all_results(idc.list_policies,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name]
                                                                    )
                for policy in policies.data:
                    total_p = total_p+1
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
                    tf_resource = f'module.iam-policies[\\"{str(tf_name)}\\"].oci_identity_policy.policy'
                    if tf_resource not in state["resources"]:
                        importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {policy.id}'

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
        init_commands = f'\n######### Writing import for Policies #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands != "":
            importCommands += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands)
        commonTools.write_to_cd3(values_for_column_policies, cd3file, sheetName_policies)
        print("{0} Policies exported into CD3.\n".format(total_p))

    elif resource == "IAM Groups":
        importCommands = ""
        sheetName_groups = "Groups"
        df, values_for_column_groups = commonTools.read_cd3(cd3file, sheetName_groups)
        sheet_dict_groups = ct.sheet_dict[sheetName_groups]
        print("Tabs- Groups would be overwritten during export process!!!\n")

        # Create backup
        resource = 'import_'+ sheetName_groups.lower()
        file_name = 'import_commands_' + sheetName_groups.lower() + '.sh'
        script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)
        # Fetch Groups
        print("\nFetching Groups...")
        total_g = 0
        def process_group(grp_info, members_list,membership_id_list, domain_name, is_dynamic=False, importCommands="", values_for_column_groups={}, non_domain=False):
            group_description = ""
            user_can_request_access = ""
            if non_domain:
                group_name = grp_info.name
                group_description = grp_info.description
                tf_name = commonTools.check_tf_variable(group_name)
                resource_id = grp_info.id
                if is_dynamic:
                    tf_resource = f'module.iam-groups[\\"{str(tf_name)}\\"].oci_identity_dynamic_group.dynamic_group[0]'
                else:
                    tf_resource = f'module.iam-groups[\\"{str(tf_name)}\\"].oci_identity_group.group[0]'
                count = 0
                for id in membership_id_list:
                    user_name = members_list[membership_id_list.index(id)]
                    membership_resource = f'module.iam-groups[\\"{str(tf_name)}\\"].oci_identity_user_group_membership.user_group_membership[\\"{user_name}\\"]'
                    if membership_resource not in state["resources"]:
                        importCommands += f'\n{tf_or_tofu} import "{membership_resource}" {id}'
                    count = count + 1
            else:
                group_name = grp_info.display_name
                tf_name = commonTools.check_tf_variable(group_name)
                domain_name = domain_name.upper() if domain_name.lower() == "default" else domain_name
                tf_name = domain_name + "_" + tf_name
                if is_dynamic:
                    group_description = grp_info.description
                    resource_id = f"idcsEndpoint/{idcs_endpoint}/dynamicResourceGroups/{grp_info.id}"
                    tf_resource = f'module.groups[\\"{str(tf_name)}\\"].oci_identity_domains_dynamic_resource_group.dynamic_group[0]'
                else:
                    requestable_group = grp_info
                    requestable = getattr(requestable_group,
                                          'urn_ietf_params_scim_schemas_oracle_idcs_extension_requestable_group', None)
                    user_can_request_access = "" if requestable is None else requestable.requestable
                    if hasattr(grp_info, 'urn_ietf_params_scim_schemas_oracle_idcs_extension_group_group'):
                        group_description = getattr(grp_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_group_group,
                                              'description', "")
                    resource_id = f"idcsEndpoint/{idcs_endpoint}/groups/{grp_info.id}"
                    tf_resource = f'module.groups[\\"{str(tf_name)}\\"].oci_identity_domains_group.group[0]'

            if tf_resource not in state["resources"]:
                importCommands += f'\n{tf_or_tofu} import "{tf_resource}" "{resource_id}"'

            for col_header in values_for_column_groups.keys():
                if col_header == "Region":
                    values_for_column_groups[col_header].append(ct.home_region.capitalize())
                elif col_header == "Name":
                    values_for_column_groups[col_header].append(group_name)
                elif col_header == "Members":
                    members_string = ','.join(members_list)
                    values_for_column_groups[col_header].append(members_string)
                elif col_header == "Description":
                    values_for_column_groups[col_header].append(group_description)
                elif col_header == "Domain Name" and not non_domain:
                    values_for_column_groups[col_header].append(domain_key)
                elif col_header == "Matching Rule":
                    values_for_column_groups[col_header].append(grp_info.matching_rule if is_dynamic else "")
                elif col_header == "User Can Request Access":
                    values_for_column_groups[col_header].append(str(user_can_request_access))
                elif col_header == "Defined Tags" and not non_domain:
                    defined_tags_info = grp_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_oci_tags
                    grp_defined_tags = []
                    if defined_tags_info is not None:
                        defined_tags = defined_tags_info.defined_tags
                        for tag in defined_tags:
                            namespace = tag.namespace
                            key = tag.key
                            value = tag.value
                            if namespace is not None and key is not None and value is not None:
                                grp_defined_tags.append(f"{namespace}.{key}={value}")
                        grp_defined_tags = ";".join(grp_defined_tags)
                    values_for_column_groups[col_header].append(grp_defined_tags if grp_defined_tags else "")
                elif col_header == "Defined Tags" and non_domain:
                    values_for_column_groups = commonTools.export_tags(grp_info, col_header, values_for_column_groups)
                else:
                    oci_objs = [grp_info]
                    values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_groups, values_for_column_groups)

            return importCommands, values_for_column_groups

        if ct.identity_domain_enabled:
            for domain_key, idcs_endpoint in export_domains.items():
                domain_name = domain_key.split("@")[1]
                domain_client = oci.identity_domains.IdentityDomainsClient(config=config, signer=signer,
                                                                           service_endpoint=idcs_endpoint)
                list_groups_response = domain_client.list_groups(attributes=['members'], attribute_sets=['all'])
                groups = list_groups_response.data.resources
                while list_groups_response.has_next_page:
                    list_groups_response = domain_client.list_groups(attributes=['members'], attribute_sets=['all'],page=list_groups_response.next_page)
                    groups.extend(list_groups_response.data.resources)

                for grp_info in groups:
                    if grp_info.display_name in ["Domain_Administrators", "All Domain Users", "Administrators"]:
                        continue
                    total_g +=1
                    members_list = [section.name for section in grp_info.members if section and section.name] if grp_info.members else []
                    importCommands, values_for_column_groups = process_group(grp_info, members_list,[], domain_name, is_dynamic=False, importCommands=importCommands, values_for_column_groups=values_for_column_groups)

                dyngroups_response = domain_client.list_dynamic_resource_groups(attributes=['matching_rule'],
                                                                                attribute_sets=['all']
                                                                                )
                dyngroups = dyngroups_response.data.resources
                while dyngroups_response.has_next_page:
                    dyngroups_response = domain_client.list_dynamic_resource_groups(attributes=['matching_rule'],
                                                                                    attribute_sets=['all'],
                                                                                    page=dyngroups_response.next_page
                                                                                    )
                    dyngroups.extend(dyngroups_response.data.resources)

                for dg in dyngroups:
                    total_g += 1
                    importCommands, values_for_column_groups = process_group(dg, [],[], domain_name, is_dynamic=True, importCommands=importCommands, values_for_column_groups=values_for_column_groups)
        else:
            groups = oci.pagination.list_call_get_all_results(idc.list_groups, compartment_id=config['tenancy'])
            dyngroups = oci.pagination.list_call_get_all_results(idc.list_dynamic_groups, compartment_id=config['tenancy'])

            for group in groups.data:
                total_g += 1
                if group.lifecycle_state == "ACTIVE":
                    group_membership = oci.pagination.list_call_get_all_results(idc.list_user_group_memberships, compartment_id=config['tenancy'], group_id=group.id)
                    members_list = [str(idc.get_user(membership.user_id).data.name).strip() for membership in group_membership.data]
                    membership_id_list = [str(membership.id) for membership in group_membership.data]
                    importCommands, values_for_column_groups = process_group(group, members_list,membership_id_list, domain_name="", is_dynamic=False, importCommands=importCommands, values_for_column_groups=values_for_column_groups, non_domain=True)

            for group in dyngroups.data:
                total_g += 1
                if group.lifecycle_state == "ACTIVE":
                    importCommands, values_for_column_groups = process_group(group, [],[], domain_name="", is_dynamic=True, importCommands=importCommands, values_for_column_groups=values_for_column_groups, non_domain=True)

        max_list_length = max(len(lst) for lst in values_for_column_groups.values())
        for col_name in values_for_column_groups:
            lst = values_for_column_groups[col_name]
            lst.extend([""] * (max_list_length - len(lst)))

        commonTools.write_to_cd3(values_for_column_groups, cd3file, sheetName_groups)

        init_commands = f'\n######### Writing import for Identity Groups #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands != "":
            importCommands += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands)
        print("{0} rows exported into CD3 for Groups and Dynamic Groups.\n".format(total_g))

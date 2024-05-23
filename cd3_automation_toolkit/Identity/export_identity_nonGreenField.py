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
def export_identity(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[]):
    global values_for_column_comps
    global values_for_column_groups
    global values_for_column_policies
    global sheet_dict_comps
    global sheet_dict_groups
    global sheet_dict_policies
    global cd3file

    cd3file = inputfile

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    importCommands={}

    sheetName_comps = "Compartments"
    sheetName_groups = "Groups"
    sheetName_policies = "Policies"

    # Read CD3 Identity Sheets
    df, values_for_column_comps = commonTools.read_cd3(cd3file, sheetName_comps)
    df, values_for_column_groups = commonTools.read_cd3(cd3file, sheetName_groups)
    df, values_for_column_policies = commonTools.read_cd3(cd3file, sheetName_policies)

    # Get dict for columns from Excel_Columns
    sheet_dict_comps = ct.sheet_dict[sheetName_comps]
    sheet_dict_groups = ct.sheet_dict[sheetName_groups]
    sheet_dict_policies = ct.sheet_dict[sheetName_policies]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Compartments, Groups, Policies would be overwritten during export process!!!\n")

    # Create backup
    resource = 'tf_import_identity'
    file_name='tf_import_commands_identity_nonGF.sh'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/'+file_name
    if(os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir,resource,file_name)
    importCommands[ct.home_region] = open(script_file, "w")
    importCommands[ct.home_region].write("#!/bin/bash")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].write("terraform init")

    config.__setitem__("region", ct.region_dict[ct.home_region])
    idc=IdentityClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

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
    print("{0} Compartments exported into CD3.\n".format(len(values_for_column_comps["Region"])))


    #Fetch Groups
    print("\nFetching Groups...")
    importCommands[ct.home_region].write("\n######### Writing import for Groups #########\n")
    default_domain_url = None
    try:
        domain = idc.list_domains(config["tenancy"])
        domain = domain.data
        default_domain_url = None
        domain_name_to_url = {}  # A dictionary to map domain display names to URLs
        src_domain_data = {}

        for d in domain:
            if d.type == "DEFAULT":
                default_domain_url = d.url
            src_domain_data[d.display_name] = d.url

    except oci.exceptions.ServiceError as e:
        pass

    if default_domain_url is not None:
        # Get the idcs_endpoint from user input
        domain_display_name = input("Enter the ',' separated Domain names to export the groups OR Enter 'all' to export from all domains OR leave it Blank to export from default domain : ")
        if domain_display_name.lower() == 'all':
            domain_name_to_url = src_domain_data
        elif not domain_display_name:
            domain_name_to_url = {'Default': default_domain_url}
        else:
            input_domains = {}
            try:
                for item in domain_display_name.split(','):
                    domain_url = src_domain_data.get(item)
                    domain_name = item
                    input_domains[domain_name] = domain_url
                domain_name_to_url = input_domains
            except Exception as e:
                print("Invalid domain display name entered.")
                exit()

        for domain_name, idcs_endpoint in domain_name_to_url.items():
            domain_client = oci.identity_domains.IdentityDomainsClient(config, idcs_endpoint)
            groups = domain_client.list_groups(attributes=['members'],attribute_sets=['all'])
            dyngroups = domain_client.list_dynamic_resource_groups(attributes=['matching_rule'],attribute_sets=['all'])
            index = 0

            for grp_info in groups.data.resources:
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
                # Initialize an empty list to store member names
                member_names = []
                if grp_info.members is not None:
                    for section in grp_info.members:
                        if section:
                            name = section.name
                            if name:
                              member_names.append(name)
                members_str = member_names
                grp_display_name = grp_info.display_name
                tf_name = commonTools.check_tf_variable(grp_display_name)
                tf_name = domain_name + "_" + tf_name
                import_group_id = "idcsEndpoint/" + str(idcs_endpoint) + "/groups/" + str(grp_info.id)
                importCommands[ct.home_region].write("\nterraform import \"module.groups[\\\"" + str(
                    tf_name) + "\\\"].oci_identity_domains_group.group[0]\" \"" + import_group_id + "\"")

                index = index + 1
                for col_header in values_for_column_groups.keys():
                    if (col_header == "Region"):
                        values_for_column_groups[col_header].append(ct.home_region.capitalize())
                    elif (col_header == "Name"):
                        values_for_column_groups[col_header].append(grp_display_name)
                    elif col_header == "Members":
                        members_string = ', '.join(members_str)
                        # Append the comma-separated string to the column header
                        values_for_column_groups[col_header].append(members_string)

                    elif (col_header == "Description"):
                        if hasattr(grp_info, 'urn_ietf_params_scim_schemas_oracle_idcs_extension_group_group'):
                            description = getattr(grp_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_group_group,'description', "")
                        values_for_column_groups[col_header].append(description)
                    elif (col_header == "Domain Name"):
                        domain_name = domain_name.strip()

                        # Convert to uppercase if domain_name is "Default," "DEFAULT," or "default"
                        if domain_name.lower() == 'default':
                            domain_name = 'DEFAULT'

                        values_for_column_groups[col_header].append(domain_name)

                    elif (col_header == "Matching Rule"):
                        matching_rule = ""
                        values_for_column_groups[col_header].append(matching_rule)
                    elif (col_header == "Defined Tags") and len(grp_defined_tags) != 0:
                        values_for_column_groups[col_header].append(str(grp_defined_tags))
                    else:
                        oci_objs = [grp_info]
                        values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_groups,
                                                                                    values_for_column_groups)

            for dg in dyngroups.data.resources:
                dg_defined_tags = []
                defined_tags_info = dg.urn_ietf_params_scim_schemas_oracle_idcs_extension_oci_tags
                if defined_tags_info is not None:
                    defined_tags = defined_tags_info.defined_tags
                    for tag in defined_tags:
                        namespace = tag.namespace
                        key = tag.key
                        value = tag.value
                        if namespace is not None and key is not None and value is not None:
                            dg_defined_tags.append(f"{namespace}.{key}={value}")

                    dg_defined_tags = ";".join(dg_defined_tags)
                dgrp_display_name = dg.display_name
                tf_name = commonTools.check_tf_variable(dgrp_display_name)
                tf_name = domain_name + "_" + tf_name
                import_dg_id = "idcsEndpoint/"+str(idcs_endpoint)+"/dynamicResourceGroups/"+str(dg.id)
                importCommands[ct.home_region].write("\nterraform import \"module.groups[\\\"" + str(
                    tf_name) + "\\\"].oci_identity_domains_dynamic_resource_group.dynamic_group[0]\" \"" + import_dg_id +"\"")
                index = index + 1
                for col_header in values_for_column_groups.keys():
                    if (col_header == "Region"):
                        values_for_column_groups[col_header].append(ct.home_region.capitalize())
                    elif (col_header == "Name"):
                        values_for_column_groups[col_header].append(dgrp_display_name)
                    elif (col_header == "Description"):
                        values_for_column_groups[col_header].append(dg.description)
                    elif (col_header == "Members"):
                        members = ""
                        values_for_column_groups[col_header].append(members)
                    elif (col_header == "Domain Name"):
                        domain_name = domain_name.strip()

                        # Convert to uppercase if domain_name is "Default," "DEFAULT," or "default"
                        if domain_name.lower() == 'default':
                            domain_name = 'DEFAULT'

                        values_for_column_groups[col_header].append(domain_name)

                    elif (col_header == "Matching Rule"):
                        values_for_column_groups[col_header].append(dg.matching_rule)
                    elif (col_header == "Defined Tags") and len(dg_defined_tags) != 0:
                        values_for_column_groups[col_header].append(str(dg_defined_tags))
                    else:
                        oci_objs = [dg]
                        values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                    sheet_dict_groups,
                                                                                    values_for_column_groups)

            max_list_length = max(len(lst) for lst in values_for_column_groups.values())
            for col_name in values_for_column_groups:
                lst = values_for_column_groups[col_name]
                lst.extend([""] * (max_list_length - len(lst)))

            commonTools.write_to_cd3(values_for_column_groups, cd3file, sheetName_groups)

        print("Groups exported to CD3\n")
    else:
        groups = oci.pagination.list_call_get_all_results(idc.list_groups, compartment_id = config['tenancy'])
        dyngroups = oci.pagination.list_call_get_all_results(idc.list_dynamic_groups,
                                                             compartment_id = config['tenancy'])
        index = 0
        groupsDict = {}

        for group in groups.data:
            grp_info = group
            members = []
            group_id = group.id
            group_membership = oci.pagination.list_call_get_all_results(idc.list_user_group_memberships,
                                                                        compartment_id = config['tenancy'],group_id = group_id)
            for user in group_membership.data:
                user_id = user.user_id
                user_data = idc.get_user(user_id).data
                user_name = user_data.name
                members.append(user_name)
            members_str = members
            if (grp_info.lifecycle_state == "ACTIVE"):
                groupsDict[grp_info.id] = grp_info.name
                grp_display_name = grp_info.name
                tf_name = commonTools.check_tf_variable(grp_display_name)
                importCommands[ct.home_region].write("\nterraform import \"module.iam-groups[\\\"" + str(
                    tf_name) + "\\\"].oci_identity_group.group[0]\" " + grp_info.id)
                index = index + 1
                for col_header in values_for_column_groups.keys():
                    if (col_header == "Region"):
                        values_for_column_groups[col_header].append(ct.home_region.capitalize())
                    elif col_header == "Members":
                        members_string = ', '.join(members_str)
                        # Append the comma-separated string to the column header
                        values_for_column_groups[col_header].append(members_string)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_groups = commonTools.export_tags(grp_info, col_header,
                                                                           values_for_column_groups)
                    else:
                        oci_objs = [grp_info]
                        values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                    sheet_dict_groups,
                                                                                    values_for_column_groups)

        for group in dyngroups.data:
            grp_info = group
            if (grp_info.lifecycle_state == "ACTIVE"):
                groupsDict[grp_info.id] = grp_info.name
                grp_display_name = grp_info.name
                tf_name = commonTools.check_tf_variable(grp_display_name)
                importCommands[ct.home_region].write("\nterraform import \"module.iam-groups[\\\"" + str(
                    tf_name) + "\\\"].oci_identity_dynamic_group.dynamic_group[0]\" " + grp_info.id)
                index = index + 1
                for col_header in values_for_column_groups.keys():
                    if (col_header == "Region"):
                        values_for_column_groups[col_header].append(ct.home_region.capitalize())
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_groups = commonTools.export_tags(grp_info, col_header,
                                                                           values_for_column_groups)
                    else:
                        oci_objs = [grp_info]
                        values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                    sheet_dict_groups,
                                                                                    values_for_column_groups)

        commonTools.write_to_cd3(values_for_column_groups, cd3file, sheetName_groups)
        print("Groups exported to CD3\n")



    # Fetch Policies
    print("\nFetching Policies...")
    importCommands[ct.home_region].write("\n\n######### Writing import for Policies #########\n\n")
    comp_ocid_done = []
    index = 0
    for ntk_compartment_name in export_compartments:
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
    print("{0} Policies exported into CD3.\n".format(len(values_for_column_policies["Region"])))

    with open(script_file, 'a') as importCommands[ct.home_region]:
        importCommands[ct.home_region].write('\n\nterraform plan\n')


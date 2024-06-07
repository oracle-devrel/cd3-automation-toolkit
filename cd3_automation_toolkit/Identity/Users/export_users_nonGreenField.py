#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
# Users

# Author: Gaurav
# Oracle Consulting
#

import sys
import oci
from oci.identity import IdentityClient
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *

# Execution of the code begins here
def export_users(inputfile, outdir, service_dir, config, signer, ct):
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

    sheetName_users = "Users"

    # Read CD3 Identity Sheets
    df, values_for_column_users = commonTools.read_cd3(cd3file, sheetName_users)


    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab - Users would be overwritten during export process!!!\n")

    # Create backup
    resource = 'tf_import_users'
    file_name='tf_import_commands_users_nonGF.sh'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/'+file_name
    if(os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir,resource,file_name)
    importCommands[ct.home_region] = open(script_file, "w")
    importCommands[ct.home_region].write("#!/bin/bash")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].write("terraform init")

    config.__setitem__("region", ct.region_dict[ct.home_region])
    idc=IdentityClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

    #retrieve group information..this is required to get group name for user-groupmembership
    groups = oci.pagination.list_call_get_all_results(idc.list_groups, compartment_id=config['tenancy'])
    dyngroups = oci.pagination.list_call_get_all_results(idc.list_dynamic_groups, compartment_id=config['tenancy'])
    index = 0
    groupsDict = {}

    for group in groups.data:
        grp_info = group
        if (grp_info.lifecycle_state == "ACTIVE"):
            groupsDict[grp_info.id] = grp_info.name

    for group in dyngroups.data:
        grp_info = group
        if (grp_info.lifecycle_state == "ACTIVE"):
            groupsDict[grp_info.id] = grp_info.name

    # Fetch Users
    print("\nFetching Users...")
    importCommands[ct.home_region].write("\n######### Writing import for Users #########\n")
    users = oci.pagination.list_call_get_all_results(idc.list_users, compartment_id=config['tenancy'])

    index = 0
    for user in users.data:
        user_info = user
        if (user_info.identity_provider_id != None):
            continue
        if (user_info.lifecycle_state == "ACTIVE"):
            username = user_info.name
            tf_name = commonTools.check_tf_variable(username)
            importCommands[ct.home_region].write("\nterraform import \"module.iam-users[\\\"" + str(
                tf_name) + "\\\"].oci_identity_user.user\" " + user_info.id)
            user_group_memberships = None
            user_group_memberships = idc.list_user_group_memberships(user_id= user_info.id ,compartment_id=config['tenancy'])

            index = index + 1
            for col_header in values_for_column_users.keys():
                if (col_header == "Region"):
                    values_for_column_users[col_header].append(ct.home_region.capitalize())
                elif (col_header == "User Name"):
                    values_for_column_users[col_header].append(username)
                elif (col_header == "User email"):
                    values_for_column_users[col_header].append(user_info.email)
                elif (col_header == "User Description"):
                    values_for_column_users[col_header].append(user_info.description)
                elif (col_header == "Disable Capabilities"):
                    #check if any of the capability is set to false
                    # generate comma separated list of capability which are disabled for user
                    capabilities = ""
                    if(not user_info.capabilities.can_use_api_keys):
                        if(capabilities == ""):
                            capabilities = "can_use_api_keys"
                        else:
                            capabilities = capabilities + "," + "can_use_api_keys"
                    if(not user_info.capabilities.can_use_auth_tokens):
                        if (capabilities == ""):
                            capabilities = "can_use_auth_tokens"
                        else:
                            capabilities = capabilities + "," + "can_use_auth_tokens"
                    if (not user_info.capabilities.can_use_console_password):
                        if (capabilities == ""):
                            capabilities = "can_use_console_password"
                        else:
                            capabilities = capabilities + "," + "can_use_console_password"
                    if (not user_info.capabilities.can_use_customer_secret_keys):
                        if(capabilities == ""):
                            capabilities = "can_use_customer_secret_keys"
                        else:
                            capabilities = capabilities + "," + "can_use_customer_secret_keys"
                    if (not user_info.capabilities.can_use_db_credentials):
                        if (capabilities == ""):
                            capabilities = "can_use_db_credentials"
                        else:
                            capabilities = capabilities + "," + "can_use_db_credentials"
                    if (not user_info.capabilities.can_use_o_auth2_client_credentials):
                        if (capabilities == ""):
                            capabilities = "can_use_o_auth2_client_credentials"
                        else:
                            capabilities = capabilities + "," + "can_use_o_auth2_client_credentials"
                    if (not user_info.capabilities.can_use_smtp_credentials):
                        if (capabilities == ""):
                            capabilities = "can_use_smtp_credentials"
                        else:
                            capabilities = capabilities + "," + "can_use_smtp_credentials"
                    values_for_column_users[col_header].append(capabilities)
                    if(not capabilities == ""):
                        importCommands[ct.home_region].write("\nterraform import \"module.iam-users[\\\"" + str(
                            tf_name) + "\\\"].oci_identity_user_capabilities_management.user_capabilities_management[0]\" capabilities/" + user_info.id)

                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_users = commonTools.export_tags(user_info, col_header, values_for_column_users)
                elif (col_header == "Group Names"):
                    if(user_group_memberships.data != []):
                        groups_name = ""
                        count = 0
                        for membership in user_group_memberships.data:
                            if (count == 0):
                                groups_name = groupsDict[membership.group_id]
                            else:
                                groups_name = groups_name + "," + groupsDict[membership.group_id]


                            importCommands[ct.home_region].write("\nterraform import \"module.iam-users[\\\"" + str(
                                tf_name) + "\\\"].oci_identity_user_group_membership.user_group_membership["+ str(count)+"]\" " + membership.id)

                            count = count + 1

                        values_for_column_users[col_header].append(groups_name)

                    else:
                        values_for_column_users[col_header].append("")

    commonTools.write_to_cd3(values_for_column_users, cd3file, sheetName_users)
    print("{0} Users exported into CD3.\n".format(len(values_for_column_users["Region"])))

    with open(script_file, 'a') as importCommands[ct.home_region]:
        importCommands[ct.home_region].write('\n\nterraform plan\n')

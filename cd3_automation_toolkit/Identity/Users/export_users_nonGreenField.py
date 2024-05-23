#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
# Users

# Author: Gaurav
# Oracle Consulting
#Modified By: Ranjini Rajendran

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

    # Fetch Users
    print("\nFetching Users...")
    importCommands[ct.home_region].write("\n######### Writing import for Users #########\n")
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
        domain_display_name = input("Enter the ',' separated Domain names to export the users OR Enter 'all' to export from all domains OR leave it Blank to export from default domain : ")
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
            # retrieve group information. This is required to get group name for user-group membership
            domain_client = oci.identity_domains.IdentityDomainsClient(config, idcs_endpoint)
            users = domain_client.list_users()
            index = 0

            for user in users.data.resources:
                defined_tags_info = user.urn_ietf_params_scim_schemas_oracle_idcs_extension_oci_tags
                user_defined_tags = []

                if defined_tags_info is not None:
                    defined_tags = defined_tags_info.defined_tags
                    for tag in defined_tags:
                        namespace = tag.namespace
                        key = tag.key
                        value = tag.value
                        if namespace is not None and key is not None and value is not None:
                            user_defined_tags.append(f"{namespace}.{key}={value}")

                    user_defined_tags = ";".join(user_defined_tags)
                user_info = user
                if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_user_user.is_federated_user != "True" and user_info.active !="False":
                    username = user_info.user_name
                    family_name = user_info.name.family_name
                    description = user_info.description
                    email = None

                    for email_info in user_info.emails:
                        if email_info.primary:
                            email = email_info.value
                            break

                    tf_name = commonTools.check_tf_variable(username)
                    tf_name = domain_name + "_" + tf_name
                    import_user_id = "idcsEndpoint/" + str(idcs_endpoint) + "/users/" + str(user_info.id)
                    importCommands[ct.home_region].write("\nterraform import \"module.users[\\\"" + str(
                        tf_name) + "\\\"].oci_identity_domains_user.user\" \"" + import_user_id + "\"" )

                    index = index + 1
                    for col_header in values_for_column_users.keys():
                        if (col_header == "Region"):
                            values_for_column_users[col_header].append(ct.home_region.capitalize())
                        elif (col_header == "User Name"):
                            values_for_column_users[col_header].append(username)
                        elif (col_header == "Family Name"):
                            values_for_column_users[col_header].append(family_name)
                        elif (col_header == "User Description"):
                            values_for_column_users[col_header].append(description)
                        elif (col_header == "User Email"):
                            values_for_column_users[col_header].append(email)
                        elif (col_header == "Domain Name"):
                            values_for_column_users[col_header].append(domain_name)
                        elif (col_header == "Defined Tags") and len(user_defined_tags) != 0:
                            values_for_column_users[col_header].append(str(user_defined_tags))
                        elif (col_header == "Enable Capabilities"):
                            capabilities = []

                            # Check if each capability is enabled and add to the list if it is
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_api_keys:
                                capabilities.append("can_use_api_keys")
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_auth_tokens:
                                capabilities.append("can_use_auth_tokens")
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_console_password:
                                capabilities.append("can_use_console_password")
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_customer_secret_keys:
                                capabilities.append("can_use_customer_secret_keys")
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_db_credentials:
                                capabilities.append("can_use_db_credentials")
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_o_auth2_client_credentials:
                                capabilities.append("can_use_oauth2client_credentials")
                            if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user.can_use_smtp_credentials:
                                capabilities.append("can_use_smtp_credentials")

                            # Join the enabled capabilities with commas and append to the values_for_column_users dictionary
                            values_for_column_users[col_header].append(",".join(capabilities))

            max_list_length = max(len(lst) for lst in values_for_column_users.values())
            for col_name in values_for_column_users:
                lst = values_for_column_users[col_name]
                lst.extend([""] * (max_list_length - len(lst)))

            commonTools.write_to_cd3(values_for_column_users, cd3file, sheetName_users)
            print("Users exported to CD3\n")

            importCommands[ct.home_region].write('\n\nterraform plan\n')
    else:
        users = oci.pagination.list_call_get_all_results(idc.list_users, compartment_id = config['tenancy'])
        index = 0
        for user in users.data:
            user_info = user
            if (user_info.identity_provider_id != None):
                continue
            if (user_info.lifecycle_state == "ACTIVE"):
                username = user_info.name
                description = user_info.description
                tf_name = commonTools.check_tf_variable(username)
                importCommands[ct.home_region].write("\nterraform import \"module.iam-users[\\\"" + str(
                    tf_name) + "\\\"].oci_identity_user.user\" " + user_info.id)

                index = index + 1
                for col_header in values_for_column_users.keys():
                    if (col_header == "Region"):
                        values_for_column_users[col_header].append(ct.home_region.capitalize())
                    elif (col_header == "User Name"):
                        values_for_column_users[col_header].append(username)
                    elif (col_header == "User Email"):
                        values_for_column_users[col_header].append(user_info.email)
                    elif (col_header == "Description"):
                        values_for_column_users[col_header].append(description)
                    elif col_header == "Enable Capabilities":
                        # List to store enabled capabilities
                        enabled_capabilities = []

                        # Check each capability individually
                        if user_info.capabilities.can_use_api_keys:
                            enabled_capabilities.append("can_use_api_keys")
                        if user_info.capabilities.can_use_auth_tokens:
                            enabled_capabilities.append("can_use_auth_tokens")
                        if user_info.capabilities.can_use_console_password:
                            enabled_capabilities.append("can_use_console_password")
                        if user_info.capabilities.can_use_customer_secret_keys:
                            enabled_capabilities.append("can_use_customer_secret_keys")
                        if user_info.capabilities.can_use_db_credentials:
                            enabled_capabilities.append("can_use_db_credentials")
                        if user_info.capabilities.can_use_o_auth2_client_credentials:
                            enabled_capabilities.append("can_use_o_auth2_client_credentials")
                        if user_info.capabilities.can_use_smtp_credentials:
                            enabled_capabilities.append("can_use_smtp_credentials")

                        # Join enabled capabilities into a comma-separated string
                        capabilities = ",".join(enabled_capabilities)

                        # Append the string of enabled capabilities to the appropriate column
                        values_for_column_users[col_header].append(capabilities)

                        if (not capabilities == ""):
                            importCommands[ct.home_region].write("\nterraform import \"module.iam-users[\\\"" + str(
                                tf_name) + "\\\"].oci_identity_user_capabilities_management.user_capabilities_management[0]\" capabilities/" + user_info.id)

                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_users = commonTools.export_tags(user_info, col_header,
                                                                          values_for_column_users)

        max_list_length = max(len(lst) for lst in values_for_column_users.values())
        for col_name in values_for_column_users:
            lst = values_for_column_users[col_name]
            lst.extend([""] * (max_list_length - len(lst)))

        commonTools.write_to_cd3(values_for_column_users, cd3file, sheetName_users)
        print("Users exported to CD3\n")

        with open(script_file, 'a') as importCommands[ct.home_region]:
            importCommands[ct.home_region].write('\n\nterraform plan\n')
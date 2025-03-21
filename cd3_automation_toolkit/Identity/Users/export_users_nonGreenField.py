#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
# Users

# Author: Gaurav
# Oracle Consulting
# Modified By: Ranjini Rajendran

import sys
import oci
from oci.identity import IdentityClient
import os
import subprocess as sp
sys.path.append(os.getcwd() + "/..")
from commonTools import *
def append_user_info(values_for_column_users,sheet_dict_users, ct, user_info, username, family_name, given_name, recovery_email, display_name, description, email, domain_key, user_defined_tags):
    def add_capabilities(user_info):
        capabilities = []
        cap_ext = getattr(user_info, 'urn_ietf_params_scim_schemas_oracle_idcs_extension_capabilities_user',
                          getattr(user_info, 'capabilities', None))
        if cap_ext:
            capability_map = {
                "can_use_api_keys": "api_keys",
                "can_use_auth_tokens": "auth_tokens",
                "can_use_console_password": "console_password",
                "can_use_customer_secret_keys": "customer_secret_keys",
                "can_use_db_credentials": "db_credentials",
                "can_use_o_auth2_client_credentials": "oauth2client_credentials",
                "can_use_smtp_credentials": "smtp_credentials"
            }
            for attr, cap in capability_map.items():
                if getattr(cap_ext, attr, False):
                    capabilities.append(cap)
        return ",".join(capabilities)
    def map_columns(col_header):
        column_map = {
            "Region": ct.home_region.capitalize(),
            "User Name": username,
            "Family Name": family_name if hasattr(user_info, 'name') else "",
            "First Name": given_name if hasattr(user_info, 'name') else "",
            "Description": description,
            "Display Name": display_name if hasattr(user_info, 'display_name') else "",
            "User Email": email,
            "Recovery Email": recovery_email,
            "Domain Name": domain_key,
            "Defined Tags": str(user_defined_tags) if user_defined_tags else "",
            "Enable Capabilities": add_capabilities(user_info),
            "Middle Name": getattr(user_info.name, 'middle_name', "") if hasattr(user_info, 'name') else "",
            "Prefix": getattr(user_info.name, 'honorific_prefix', "") if hasattr(user_info, 'name') else "",
            "Home Phone Number": next((phone.value for phone in user_info.phone_numbers if phone.type == "home"), None)
            if hasattr(user_info, 'phone_numbers') and user_info.phone_numbers else None,
            "Mobile Phone Number": next((phone.value for phone in user_info.phone_numbers if phone.type == "mobile"),
                                        None)
            if hasattr(user_info, 'phone_numbers') and user_info.phone_numbers else None
        }
        return column_map.get(col_header, None)

    for col_header in values_for_column_users.keys():
        value = map_columns(col_header)
        if value is not None:
            values_for_column_users[col_header].append(value)
        else:
            oci_objs = [user_info]
            values_for_column_users = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_users, values_for_column_users)
# Execution start here
def export_users(inputfile, outdir, service_dir, config, signer, ct,export_domains={}):
    global sheet_dict_users
    global cd3file,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile

    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    importCommands = ""
    sheetName_users = "Users"
    count_u = 0

    # Read CD3 Identity Sheets
    df, values_for_column_users = commonTools.read_cd3(cd3file, sheetName_users)
    sheet_dict_users = ct.sheet_dict[sheetName_users]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab - Users would be overwritten during export process!!!\n")

    config.__setitem__("region", ct.region_dict[ct.home_region])
    state = {'path': f'{outdir}/{ct.home_region}/{service_dir}', 'resources': []}
    try:
        byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
        output = byteOutput.decode('UTF-8').rstrip()
        for item in output.split('\n'):
            state["resources"].append(item.replace("\"", "\\\""))
    except Exception as e:
        pass
    idc=IdentityClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

    # Create backup
    resource = 'import_' + sheetName_users.lower()
    file_name = 'import_commands_' + sheetName_users.lower() + ".sh"
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
    if (os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)

    print("\nFetching Users...")
    if ct.identity_domain_enabled:
        for domain_key, idcs_endpoint in export_domains.items():
            domain_name = domain_key.split("@")[1]
            domain_client = oci.identity_domains.IdentityDomainsClient(config=config, signer=signer,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                                       service_endpoint=idcs_endpoint)
            list_users_response = domain_client.list_users() # change this to pagination once api supports
            users = list_users_response.data.resources
            while list_users_response.has_next_page:
                list_users_response = domain_client.list_users(page=list_users_response.next_page)
                users.extend(list_users_response.data.resources)

            index = 0
            for user in users:
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

                user_defined_tags = ";".join(user_defined_tags) if user_defined_tags else ""

                user_info = user
                if user_info.urn_ietf_params_scim_schemas_oracle_idcs_extension_user_user.is_federated_user != "True" and user_info.active !="False":
                    username = user_info.user_name
                    family_name = user_info.name.family_name
                    given_name  = user_info.name.given_name
                    description = user_info.description
                    display_name = user_info.display_name
                    email = None
                    recovery_email = None
                    if hasattr(user_info.emails, "email_info"):
                        for email_info in user_info.emails:
                            if email_info.primary:
                                email = email_info.value
                            elif email_info.type == "recovery":
                                recovery_email = email_info.value


                    tf_name = commonTools.check_tf_variable(username)
                    if domain_name == "Default" or domain_name == "default":
                        domain_name = "DEFAULT"
                    tf_name = domain_name + "_" + tf_name
                    import_user_id = "idcsEndpoint/" + str(idcs_endpoint) + "/users/" + str(user_info.id)
                    tf_resource = f'module.users[\\"{str(tf_name)}\\"].oci_identity_domains_user.user'
                    if tf_resource not in state["resources"]:
                        importCommands += f'\n{tf_or_tofu} import "{tf_resource}" "{import_user_id}"'
                    count_u += 1
                    append_user_info(values_for_column_users,sheet_dict_users, ct, user_info, username, family_name, given_name,recovery_email, display_name,description, email, domain_key,user_defined_tags)

    else:
        users = oci.pagination.list_call_get_all_results(idc.list_users, compartment_id=config['tenancy']).data
        index=0
        for user in users:
            user_info = user
            if (user_info.identity_provider_id != None):
                continue
            if (user_info.lifecycle_state == "ACTIVE"):
                username = user_info.name
                description = user_info.description
                email = user_info.email
                user_defined_tags = []
                tf_name = commonTools.check_tf_variable(username)
                import_user_id = user_info.id
                tf_resource = f'module.iam-users[\\"{str(tf_name)}\\"].oci_identity_user.user'
                if tf_resource not in state["resources"]:
                    importCommands += f'\n{tf_or_tofu} import "{tf_resource}" "{import_user_id}"'

                count_u += 1
                #append_user_info(values_for_column_users,sheetName_users, ct, user_info, username, "", description, email, "", [])
                append_user_info(values_for_column_users, sheet_dict_users, ct, user_info, username, "", "", "", "",
                    description, email, "", user_defined_tags)

            if user.capabilities:
                tf_resource = f'module.iam-users[\\"{str(tf_name)}\\"].oci_identity_user_capabilities_management.user_capabilities_management[0]'
                if tf_resource not in state["resources"]:
                    importCommands += f'\n{tf_or_tofu} import "{tf_resource}" capabilities/{user_info.id}'

            for col_header in values_for_column_users.keys():
                if col_header.lower() in commonTools.tagColumns:
                    values_for_column_users = commonTools.export_tags(user, col_header, values_for_column_users)

    max_list_length = max(len(lst) for lst in values_for_column_users.values())
    for col_name in values_for_column_users:
        lst = values_for_column_users[col_name]
        lst.extend([""] * (max_list_length - len(lst)))

    commonTools.write_to_cd3(values_for_column_users, cd3file, sheetName_users)
    print("{0} Users exported into CD3.\n".format(count_u))

    init_commands = f'\n######### Writing import for Identity Users #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    if importCommands != "":
        importCommands += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands)


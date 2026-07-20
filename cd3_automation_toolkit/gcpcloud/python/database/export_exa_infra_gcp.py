#!/usr/bin/python3
# Copyright (c) 2025, 2026, Oracle and/or its affiliates. All rights reserved.
# This script will Export ADB @GCP resources into CD3 (existing worksheet) and write Terraform/tofu import commands
# Author: Ulaganathan N
# Oracle Consulting
###############################################################################

import os
import sys
import subprocess as sp

from google.api_core.exceptions import GoogleAPIError

sys.path.append(os.getcwd()+"/..")
from common.python.commonTools import *
import gcpcloud.python.gcpCommonTools as gcpCommonTools
from typing import Dict, List, Optional
from google.cloud import oracledatabase_v1

# Global declaration
importCommands: Dict[str, str] = {}


def pick_first_not_none(*values):
    """Return the first non-None value from a list of values."""
    for v in values:
        if v is not None:
            return v
    return None


def normalize_enum_token(value):
    """
    Return the enum/member token expected by tfvars as a string.
    For Example:
      'WorkloadType.OLTP' -> 'OLTP'
    """
    if value is None:
        return ""
    s = str(value)
    return s.split(".", 1)[1] if "." in s else s


def _format_rg_vnet_subnet_from_id(net_id: str) -> str:
    """Return 'resourceGroup@vnet::subnet' from a subnet ARM ID."""
    if not net_id:
        return ""
    parts = net_id.strip("/").split("/")
    try:
        rg = parts[parts.index("resourceGroups") + 1]
        vnet = parts[parts.index("virtualNetworks") + 1]
        subnet = parts[parts.index("subnets") + 1]
        return f"{rg}@{vnet}::{subnet}"
    except (ValueError, IndexError):
        return ""


def _get_rg_from_id(resource_id: str) -> str:
    # ARM ID format: /subscriptions/<sub>/resourceGroups/<rg>/providers/.../autonomousDatabases/<name>
    try:
        parts = resource_id.split("/")
        idx = parts.index("resourceGroups")
        return parts[idx + 1]
    except Exception:
        return ""


def _list_exa_infra(active_projects,regions):
    """Yield ADB @GCP resources across pall projects"""
    for project in active_projects:
        for region in regions:
            response=[]
            parent_path = f"projects/{project}/locations/{region}"
            try:
                request = oracledatabase_v1.ListCloudExadataInfrastructuresRequest(parent=parent_path)
                response = client.list_cloud_exadata_infrastructures(request)
            except Exception as e:
                print("Skipping Region: "+region)
                pass
            count = 0
            for exa_infra in response:
                print("Fetching for "+str(request))
                yield exa_infra
                count += 1



def print_exa_infra_gcp(exa_infra, values_for_column: Dict[str, List], state: Dict, tf_or_tofu: str,  ):
    """Populate CD3 columns for a single ADB @GCP and queue Terraform import commands."""


    print(exa_infra)
    print("==================")
    props = getattr(exa_infra, "properties", None) or exa_infra
    print(props)

    # Resource names and IDs
    exa_infra_name = getattr(exa_infra, "name", "")
    parts=exa_infra_name.split("/")
    project=parts[parts.index("projects") + 1]
    location=parts[parts.index("locations") + 1]


    # Contacts (list of objects with .email)
    contacts_csv = ""
    try:
        contacts = getattr(props, "customer_contacts", None)
        if contacts:
            emails = []
            for c in contacts:
                email = getattr(c, "email", None) or getattr(c, "contact", None)
                if email:
                    emails.append(email)
            contacts_csv = ",".join(emails)
    except Exception:
        contacts_csv = ""


    # Tags (dict) — kept as metadata only if the sheet has 'Common Tags' column(not used yet)
    #common_tags = gcpCommonTools._flatten_tags(getattr(adb, "tags", None))

    common_tags=""
    display_name = exa_infra.display_name

    shape = getattr(props, "shape", None)
    compute_count = getattr(props, "compute_count", None)
    storage_count = getattr(props, "storage_count", None)
    maintenance_window = getattr(props, "maintenance_window", None)
    preference = maintenance_window.preference.name
    months = maintenance_window.months
    months=",".join(str(num) for num in months)
    weeks_of_month = maintenance_window.weeks_of_month
    weeks_of_month=",".join(str(num) for num in weeks_of_month)
    days_of_week = maintenance_window.days_of_week
    days_of_week = ",".join(str(num) for num in days_of_week)
    hours_of_day = maintenance_window.hours_of_day
    hours_of_day = ",".join(str(num) for num in hours_of_day)
    lead_time_week = maintenance_window.lead_time_week
    if lead_time_week ==0:
        lead_time_week=""

    patching_mode = maintenance_window.patching_mode.name
    gcp_oracle_zone = exa_infra.gcp_oracle_zone

    module_name = "exa-infra-gcp"
    resource_type = "google_oracle_database_cloud_exadata_infrastructure"
    resource_name_in_module = "exadata_infrastructure"

    exa_infra_tf_name = commonTools.check_tf_variable(display_name)

    # module.<module_name>["<key>"].<resource_type>.<resource_name>
    tf_address = f'module.{module_name}["{exa_infra_tf_name}"].{resource_type}.{resource_name_in_module}'

    # Avoid duplicate imports by checking current state addresses
    if tf_address not in state.get("resources", []):
        # Wrap ADDRESS in single quotes to avoid escaping the ["] in a POSIX shell
        importCommands["global"] += f"\n{tf_or_tofu} import '{tf_address}' {getattr(exa_infra, 'name', '')}"

    # Populate CD3 columns as per provided header list (write only if column exists)
    for col_header in values_for_column:
        if col_header in ("Location"):
            values_for_column[col_header].append(location)
        elif col_header == "Project":
            values_for_column[col_header].append(project)
        elif col_header == "GCP Oracle Zone":
            values_for_column[col_header].append(gcp_oracle_zone)
        elif col_header == "Exadata Infra Display Name":
            values_for_column[col_header].append(display_name)
        elif col_header == "Shape":
            values_for_column[col_header].append(shape)
        elif col_header == "Database Servers":
            values_for_column[col_header].append(compute_count)
        elif col_header == "Storage Servers":
            values_for_column[col_header].append(storage_count)
        elif col_header == "Maintenance Method":
            values_for_column[col_header].append(patching_mode)
        elif col_header == "Preference":
            values_for_column[col_header].append(preference)
        elif col_header == "Months":
            values_for_column[col_header].append(months)
        elif col_header == "Weeks of Month":
            values_for_column[col_header].append(weeks_of_month)
        elif col_header == "Hours of Day":
            values_for_column[col_header].append(hours_of_day)
        elif col_header == "Days of Week":
            values_for_column[col_header].append(days_of_week)
        elif col_header == "Lead Time in Weeks":
            values_for_column[col_header].append(lead_time_week)
        elif col_header == "Email":
            values_for_column[col_header].append(contacts_csv)
        elif col_header == "Common Tags":
            values_for_column[col_header].append(common_tags)
        else:
            values_for_column[col_header].append("")
        '''
        elif col_header.lower() in azrCommonTools.tagColumns:
            try:
                values_for_column = commonTools.export_tags(adb, col_header, values_for_column)
            except Exception:
                values_for_column[col_header].append("")

        else:
            # Extra/custom columns via Excel_Columns mapping
            try:
                oci_objs = [adb]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict,
                                                                     values_for_column)
            except Exception:
                values_for_column[col_header].append("")
        '''



def export_exa_infra_gcp(inputfile: str, outdir: str,credentials,active_projects: [List[str]],regions: [List[str]],) :
    """
    Export Exa-Infra @GCP resources into CD3 (existing worksheet) and write Terraform/tofu import commands.
      - No region/service_dir/export_tags/compartment scoping.
      - Single import script at outdir/gcp folder.
    """
    global importCommands, sheet_dict, client

    tf_or_tofu = "terraform"

    # Validate input Excel
    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        sys.exit(1)
    sheetName = "EXA-Infra-GCP"
    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- EXA-INFRA-GCP will be overwritten during export process!!!\n")

    # Prepare a single import commands script at outdir (subscription scope)

    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    script_file = os.path.join(outdir, file_name)
    if os.path.exists(script_file):
        commonTools.backup_file(outdir, resource, file_name)
    os.makedirs(outdir, exist_ok=True)
    importCommands["global"] = ""


    client = oracledatabase_v1.OracleDatabaseClient(credentials=credentials)
    print("\nFetching details of Exa Infra @GCP...")

    # Build state resources (to avoid duplicate import lines) at outdir
    state = {'path': outdir, 'resources': []}
    try:
        tf_state_list = [tf_or_tofu, "state", "list"]
        byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
        output = byteOutput.decode('UTF-8').rstrip()
        for item in output.split('\n'):
            state["resources"].append(item.replace("\"", "\\\""))
    except Exception:
        pass

    # Iterate Exa Infra

    for exa_infra in _list_exa_infra(active_projects,regions):
        print_exa_infra_gcp(exa_infra, values_for_column, state, tf_or_tofu)

    # Write back to CD3
    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    # Region count if present, else any main column (e.g., ADB Display Name)
    count_col = "Exadata Infra Display Name" if "Exadata Infra Display Name" in values_for_column else next(iter(values_for_column.keys()))
    print("{0} Exa Infra @GCP exported into CD3.\n".format(len(values_for_column.get(count_col, []))))

    # Write import script
    init_commands = f'\n######### Writing import for Exa Infra @GCP #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    if importCommands.get("global"):
        importCommands["global"] += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a', encoding='utf-8') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands["global"])
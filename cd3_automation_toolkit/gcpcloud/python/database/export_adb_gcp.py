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


def _list_adbs(active_projects,regions):
    """Yield ADB @GCP resources across pall projects"""
    for project in active_projects:
        for region in regions:
            response=[]
            parent_path = f"projects/{project}/locations/{region}"
            try:
                request = oracledatabase_v1.ListAutonomousDatabasesRequest(parent=parent_path)
                response = client.list_autonomous_databases(request)
            except Exception as e:
                print("Skipping Region: "+region)
                pass
            count = 0
            for adb in response:
                print("Fetching for "+str(request))
                yield adb
                count += 1



def print_adbs_gcp(adb, values_for_column: Dict[str, List], state: Dict, tf_or_tofu: str,  ):
    """Populate CD3 columns for a single ADB @GCP and queue Terraform import commands."""

    props = getattr(adb, "properties", None) or adb

    # Resource names and IDs
    adb_name = getattr(adb, "name", "")
    parts=adb_name.split("/")
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

    odb_network_details=""
    subnet_id=""
    try:
        network=adb.odb_subnet
        parts = network.strip("/").split("/")
        network_project_id=parts[parts.index("projects") + 1]
        odb_network_id=parts[parts.index("odbNetworks") + 1]
        subnet_id = parts[parts.index("odbSubnets") + 1]

        # Retrieve the ODB Network resource
        response = client.get_odb_network(name=adb.odb_network)
        # Access the mapped GCP VPC network URI
        gcp_vpc_uri = response.network
        parts = gcp_vpc_uri.strip("/").split("/")
        gcp_vpc= parts[parts.index("networks") + 1]

        odb_network_details = network_project_id+"::"+gcp_vpc+"::"+odb_network_id

    except Exception as e:
        print("Network Details empty for "+adb.display_name)



    compute_count = (
            getattr(props, "compute_count", None)
            or getattr(props, "computeCount", None)
            or ""
    )
    ocpu_cores = (
            getattr(props, "cpu_core_count", None)
            or getattr(props, "ocpuCoreCount", None)
            or ""
    )

    database_name = adb.database
    display_name = adb.display_name
    name=adb.name
    parts = name.strip("/").split("/")
    autonomous_database_id = parts[parts.index("autonomousDatabases") + 1]


    db_version = getattr(props, "db_version", None)  or ""
    db_edition = getattr(props, "db_edition", None)
    db_edition = db_edition.name
    storage_tbs = getattr(props, "data_storage_size_tb", None) or ""
    storage_gbs = ""
    if storage_tbs == "":
        storage_gbs = getattr(props, "data_storage_size_gb", None) or ""
    workload= getattr(props, "db_workload", None)
    workload = workload.name

    private_endpoint_ip = getattr(props, "private_endpoint_ip", None) or ""
    private_endpoint_label = getattr(props, "private_endpoint_label", None) or ""

    license_type = getattr(props, "license_type", None)
    license_type=license_type.name

    backup_retention_days = (getattr(props, "backup_retention_period_days", None) or getattr(props, "backupRetentionDays",
                                                                            None) or "")
    # Character sets
    char_set = pick_first_not_none(
        getattr(props, "character_set", None),
        getattr(props, "characterSet", None),
    )
    nchar_set = pick_first_not_none(
        getattr(props, "n_character_set", None),
        getattr(props, "ncharacterSet", None),
    )

    maintenance_schedule_type = getattr(props, "maintenance_schedule_type", None)
    maintenance_schedule_type = maintenance_schedule_type.name

    # Auto-scaling flags
    auto_scaling_storage = pick_first_not_none(
        getattr(props, "is_storage_auto_scaling_enabled", None))
    auto_scaling_enabled = pick_first_not_none(
        getattr(props, "is_auto_scaling_enabled", None))

    # mTLS requirement
    mtls_required = pick_first_not_none(
        getattr(props, "mtls_connection_required", None),
        getattr(props, "isMtlsConnectionRequired", None),
    )

    module_name = "adb-gcp"
    resource_type = "google_oracle_database_autonomous_database"
    resource_name_in_module = "autonomous_database"  # Need to change if tf module uses a different name

    adb_tf_name =   location +"_"+project+"_"+autonomous_database_id

    # module.<module_name>["<key>"].<resource_type>.<resource_name>
    tf_address = f'module.{module_name}["{adb_tf_name}"].{resource_type}.{resource_name_in_module}'

    # Avoid duplicate imports by checking current state addresses
    if tf_address not in state.get("resources", []):
        # Wrap ADDRESS in single quotes to avoid escaping the ["] in a POSIX shell
        importCommands["global"] += f"\n{tf_or_tofu} import '{tf_address}' {getattr(adb, 'name', '')}"

    # Populate CD3 columns as per provided header list (write only if column exists)
    for col_header in values_for_column:
        if col_header in ("Location"):
            values_for_column[col_header].append(location)
        elif col_header == "Project":
            # If the sheet still has Region, fill it from GCP location (no per-region scripting)
            values_for_column[col_header].append(project)
        elif col_header == "ADB Display Name":
            values_for_column[col_header].append(display_name)
        elif col_header == "Autonomous Database ID":
            values_for_column[col_header].append(autonomous_database_id)
        elif col_header == "ODB Network Details":
            values_for_column[col_header].append(odb_network_details)
        elif col_header == "ODB Network Subnet Details":
            values_for_column[col_header].append(subnet_id)
        elif col_header == "Private Endpoint IP":
            values_for_column[col_header].append(private_endpoint_ip)
        elif col_header == "Private Endpoint Label":
            values_for_column[col_header].append(private_endpoint_label)
        elif col_header == "Maintenance Schedule Type":
            values_for_column[col_header].append(maintenance_schedule_type)
        elif col_header == "Database Name":
            values_for_column[col_header].append(database_name)
        elif col_header == "DB Version":
            values_for_column[col_header].append(db_version)
        elif col_header == "DB Edition":
            values_for_column[col_header].append(db_edition)
        elif col_header == "Admin Password":
            values_for_column[col_header].append("Rand0mPaswd#123")  # never retrievable

        elif col_header == "Compute Count":
            values_for_column[col_header].append(compute_count)

        elif col_header in ("Data Storage Size TB"):
            values_for_column[col_header].append(storage_tbs)
        elif col_header in ("Data Storage Size GB"):
            values_for_column[col_header].append(storage_gbs)
        elif col_header == "Database Workload":
            if workload == "DW":
                workload = "LakeHouse"
            elif workload == "AJD":
                workload = "JSON"
            elif workload == "OLTP":
                workload = "ATP"
            elif workload == "APEX":
                workload = "APEX"
            values_for_column[col_header].append(workload.upper())
        elif col_header == "License Type":
            values_for_column[col_header].append(license_type)
        elif col_header == "Backup Retention Period In Days":
            values_for_column[col_header].append(backup_retention_days)
        elif col_header == 'Character Set':
            values_for_column[col_header].append(char_set)
        elif col_header == 'nCharacter Set':
            values_for_column[col_header].append(nchar_set)
        elif col_header == "Is Storage Auto Scaling Enabled":
            values_for_column[col_header].append(auto_scaling_storage)
        elif col_header == "Is Auto Scaling Enabled":
            values_for_column[col_header].append(auto_scaling_enabled)
        elif col_header == "MTLS Connection Required":
            values_for_column[col_header].append(mtls_required)
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



def export_adb_gcp(inputfile: str, outdir: str,credentials,active_projects: [List[str]],regions: [List[str]],) :
    """
    Export ADB @GCP resources into CD3 (existing worksheet) and write Terraform/tofu import commands.
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
    sheetName = "ADB-GCP"
    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- ADB-GCP will be overwritten during export process!!!\n")

    # Prepare a single import commands script at outdir (subscription scope)

    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    script_file = os.path.join(outdir, file_name)
    if os.path.exists(script_file):
        commonTools.backup_file(outdir, resource, file_name)
    os.makedirs(outdir, exist_ok=True)
    importCommands["global"] = ""


    client = oracledatabase_v1.OracleDatabaseClient(credentials=credentials)
    print("\nFetching details of ADB @GCP...")

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

    # Iterate ADBs

    for adb in _list_adbs(active_projects,regions):
        print_adbs_gcp(adb, values_for_column, state, tf_or_tofu)

    # Write back to CD3
    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    # Region count if present, else any main column (e.g., ADB Display Name)
    count_col = "ADB Display Name" if "ADB Display Name" in values_for_column else next(iter(values_for_column.keys()))
    print("{0} ADB @GCP exported into CD3.\n".format(len(values_for_column.get(count_col, []))))

    # Write import script
    init_commands = f'\n######### Writing import for ADB @GCP #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    if importCommands.get("global"):
        importCommands["global"] += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a', encoding='utf-8') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands["global"])

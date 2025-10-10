#!/usr/bin/python3
# Copyright (c) 2025, 2026, Oracle and/or its affiliates. All rights reserved.
# This script will Export ADB @Azure resources into CD3 (existing worksheet) and write Terraform/tofu import commands
# Author: Ulaganathan N
# Oracle Consulting
###############################################################################
import os
import sys
import subprocess as sp
sys.path.append(os.getcwd()+"/..")
from common.python.commonTools import *
import azurecloud.python.azrCommonTools as azrCommonTools
from typing import Dict, List, Optional
try:
    from azure.mgmt.oracledatabase import OracleDatabaseMgmtClient as OracleDBClient
except ImportError:
    from azure.mgmt.oracledatabase import OracleDatabaseManagementClient as OracleDBClient


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


def _list_adbs(client: "OracleDBClient", resource_groups: Optional[List[str]] = None):
    """Yield ADB @Azure resources across provided RGs or entire subscription."""
    if resource_groups:
        for rg in resource_groups:
            try:
                for adb in client.autonomous_databases.list_by_resource_group(rg):
                    yield adb
            except HttpResponseError as e:
                print(f"[WARN] Failed listing ADBs in RG '{rg}': {e}")
    else:
        for adb in client.autonomous_databases.list_by_subscription():
            yield adb


def print_adbs_azure(adb, values_for_column: Dict[str, List], state: Dict, tf_or_tofu: str,  ):
    """Populate CD3 columns for a single ADB @Azure and queue Terraform import commands."""
    props = getattr(adb, "properties", None) or adb

    # Resource names and IDs
    rg_name = _get_rg_from_id(getattr(adb, "id", ""))
    adb_name = getattr(adb, "name", "")
    adb_location = getattr(adb, "location", "")

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
    common_tags = azrCommonTools._flatten_tags(getattr(adb, "tags", None))

    # Prefer subnetId to derive rg@vnet::subnet; private endpoint IDs don't contain vnet/subnet names
    subnet_id = pick_first_not_none(
        getattr(props, "subnet_id", None),
        getattr(props, "subnetId", None),
    )
    formatted_net = _format_rg_vnet_subnet_from_id(subnet_id)

    # Optional: keep raw IDs if needed elsewhere
    network_details_raw = pick_first_not_none(
        getattr(props, "subnet_id", None),
        getattr(props, "subnetId", None),
        getattr(props, "private_endpoint_id", None),
        getattr(props, "privateEndpointId", None),
        "",
    )

    # Whitelisted IPs (array of strings)
    ips_list = pick_first_not_none(
        getattr(props, "whitelisted_ips", None),  # snake_case (SDK model)
        getattr(props, "whitelistedIps", None),  # camelCase (REST casing)
    )
    whitelisted_ips = ",".join(ips_list) if isinstance(ips_list, list) else ""

    # Compute details
    compute_model_raw = (getattr(props, "compute_model", None) or getattr(props, "computeModel", None) or "")
    compute_model = normalize_enum_token(compute_model_raw)

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

    db_version = getattr(props, "db_version", None) or getattr(props, "databaseVersion", None) or ""
    db_edition_raw = getattr(props, "database_edition", None) or getattr(props, "databaseEdition", None) or ""
    db_edition = normalize_enum_token(db_edition_raw)
    storage_tbs = getattr(props, "data_storage_size_in_tbs", None) or getattr(props, "dataStorageSizeInTbs", None) or ""
    workload_raw = getattr(props, "db_workload", None) or getattr(props, "databaseWorkload", None) or ""
    workload = normalize_enum_token(workload_raw)
    license_model_raw = getattr(props, "license_model", None) or getattr(props, "licenseModel", None) or ""
    license_model = normalize_enum_token(license_model_raw)
    backup_retention_days = \
        (getattr(props, "backup_retention_period_in_days", None) or getattr(props, "backupRetentionDays",
                                                                            None) or "")
    # Character sets
    char_set = pick_first_not_none(
        getattr(props, "character_set", None),
        getattr(props, "characterSet", None),
    )
    nchar_set = pick_first_not_none(
        getattr(props, "ncharacter_set", None),
        getattr(props, "ncharacterSet", None),
    )

    # Auto-scaling flags
    auto_scaling_storage = pick_first_not_none(
        getattr(props, "is_auto_scaling_for_storage_enabled", None),
        getattr(props, "isAutoScalingForStorageEnabled", None),
    )
    auto_scaling_enabled = pick_first_not_none(
        getattr(props, "is_auto_scaling_enabled", None),
        getattr(props, "isAutoScalingEnabled", None),
    )

    # mTLS requirement
    mtls_required = pick_first_not_none(
        getattr(props, "is_mtls_connection_required", None),
        getattr(props, "isMtlsConnectionRequired", None),
    )

    module_name = "adb-azure"
    resource_type = "azurerm_oracle_autonomous_database"
    resource_name_in_module = "autonomous_database"  # Need to change if tf module uses a different name

    adb_tf_name = commonTools.check_tf_variable(adb_name)

    # module.<module_name>["<key>"].<resource_type>.<resource_name>
    tf_address = f'module.{module_name}["{adb_tf_name}"].{resource_type}.{resource_name_in_module}'

    # Avoid duplicate imports by checking current state addresses
    if tf_address not in state.get("resources", []):
        # Wrap ADDRESS in single quotes to avoid escaping the ["] in a POSIX shell
        importCommands["global"] += f"\n{tf_or_tofu} import '{tf_address}' {getattr(adb, 'id', '')}"

    # Populate CD3 columns as per provided header list (write only if column exists)
    for col_header in values_for_column:
        if col_header in ("Resource Group", "Resource Group", "Resource Group Name"):
            values_for_column[col_header].append(rg_name)
        elif col_header == "Region":
            # If the sheet still has Region, fill it from Azure location (no per-region scripting)
            values_for_column[col_header].append(adb_location)
        elif col_header == "ADB Display Name":
            values_for_column[col_header].append(adb_name)
        elif col_header == "Network Details":
            # Write the formatted rg@vnet::subnet if available; else leave blank or fall back to raw
            values_for_column[col_header].append(formatted_net or "")
        elif col_header == "Whitelisted IP Addresses":
            values_for_column[col_header].append(whitelisted_ips)
        elif col_header == "DB Name":
            values_for_column[col_header].append("")  # Not exposed in Azure UI/API
        elif col_header == "DB Version":
            values_for_column[col_header].append(db_version)
        elif col_header == "Database Edition":
            values_for_column[col_header].append(db_edition)
        elif col_header == "Admin Password":
            values_for_column[col_header].append("Rand0mPaswd#123")  # never retrievable
        elif col_header == "Compute Model":
            values_for_column[col_header].append(compute_model)
        elif col_header == "Compute Count":
            values_for_column[col_header].append(compute_count)
        elif col_header in ("OCPU Core Count", "OCPU Core Count"):
            values_for_column[col_header].append(ocpu_cores)
        elif col_header in ("Data Storage Size in TBs", "Data Storage Size in TB"):
            values_for_column[col_header].append(storage_tbs)
        elif col_header == "Database Workload":
            if workload == "DW":
                workload = "adw"
            elif workload == "AJD":
                workload = "json"
            elif workload == "OLTP":
                workload = "atp"
            elif workload == "APEX":
                workload = "apex"
            values_for_column[col_header].append(workload.upper())
        elif col_header == "License Model":
            values_for_column[col_header].append(license_model)
        elif col_header == "Backup Retention Period In Days":
            values_for_column[col_header].append(backup_retention_days)
        elif col_header == 'Character Set':
            values_for_column[col_header].append(char_set)
        elif col_header == 'nCharacter Set':
            values_for_column[col_header].append(nchar_set)
        elif col_header == "Auto Scaling for Storage Enabled":
            values_for_column[col_header].append(auto_scaling_storage)
        elif col_header == "Auto Scaling Enabled":
            values_for_column[col_header].append(auto_scaling_enabled)
        elif col_header == "MTLS Connection Required":
            values_for_column[col_header].append(mtls_required)
        elif col_header == "Customer Contacts":
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



def export_adb_azure(inputfile: str, outdir: str,credentials,
                      export_resource_groups: Optional[List[str]] = None):
    """
    Export ADB @Azure resources into CD3 (existing worksheet) and write Terraform/tofu import commands.
      - No region/service_dir/export_tags/compartment scoping.
      - Single import script at outdir/azure folder.
    """
    global importCommands, sheet_dict

    tf_or_tofu = "terraform"

    # Validate input Excel
    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        sys.exit(1)
    sheetName = "ADB-Azure"
    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- ADB-Azure will be overwritten during export process!!!\n")

    # Prepare a single import commands script at outdir (subscription scope)

    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    script_file = os.path.join(outdir, file_name)
    if os.path.exists(script_file):
        commonTools.backup_file(outdir, resource, file_name)
    os.makedirs(outdir, exist_ok=True)
    importCommands["global"] = ""


    client = OracleDBClient(credential=credentials[0], subscription_id=credentials[1])

    print("\nFetching details of ADB @Azure...")

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

    # Iterate ADBs in requested RGs or entire subscription
    rgs = export_resource_groups if export_resource_groups else None
    for adb in _list_adbs(client, rgs):
        print_adbs_azure(adb, values_for_column, state, tf_or_tofu)

    # Write back to CD3
    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    # Region count if present, else any main column (e.g., ADB Display Name)
    count_col = "ADB Display Name" if "ADB Display Name" in values_for_column else next(iter(values_for_column.keys()))
    print("{0} ADB @Azure exported into CD3.\n".format(len(values_for_column.get(count_col, []))))

    # Write import script
    init_commands = f'\n######### Writing import for ADB @Azure #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    if importCommands.get("global"):
        importCommands["global"] += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a', encoding='utf-8') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands["global"])
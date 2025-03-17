#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export MySQL Database Systems
#
# Author: Generated by Cascade
# Oracle Consulting
#
import oci
import os
import subprocess as sp
from commonTools import *
from oci.config import DEFAULT_LOCATION

importCommands = {}
oci_obj_names = {}

region_mapping = {
    'phoenix': 'us-phoenix-1',
    'ashburn': 'us-ashburn-1',
    'frankfurt': 'eu-frankfurt-1',
    'london': 'uk-london-1',
    'mumbai': 'ap-mumbai-1',
    'seoul': 'ap-seoul-1',
    'tokyo': 'ap-tokyo-1',
    'toronto': 'ca-toronto-1',
    'sydney': 'ap-sydney-1',
    'sanjose': 'us-sanjose-1',
    'singapore': 'ap-singapore-1',
    'amsterdam': 'eu-amsterdam-1',
    'chuncheon': 'ap-chuncheon-1',
    'melbourne': 'ap-melbourne-1',
    'montreal': 'ca-montreal-1',
    'hyderabad': 'ap-hyderabad-1',
    'jeddah': 'me-jeddah-1',
    'dubai': 'me-dubai-1',
    'milan': 'eu-milan-1',
    'santiago': 'sa-santiago-1',
    'marseille': 'eu-marseille-1',
    'paris': 'eu-paris-1',
    'zurich': 'eu-zurich-1'
}

def print_mysql(region, vnc_client, mysql_db, values_for_column, ntk_compartment_name, state, ct, row):
    mysql_tf_name = commonTools.check_tf_variable(mysql_db.display_name)
    mysql_subnet_id = mysql_db.subnet_id

    if mysql_subnet_id is not None:
        mysql_subnet_info = vnc_client.get_subnet(mysql_subnet_id)
        mysql_subnet_name = mysql_subnet_info.data.display_name
        mysql_vcn_name = vnc_client.get_vcn(mysql_subnet_info.data.vcn_id).data.display_name

        ntk_compartment_id = vnc_client.get_vcn(mysql_subnet_info.data.vcn_id).data.compartment_id
        network_compartment_name = ntk_compartment_name
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if comp_id == ntk_compartment_id:
                network_compartment_name = comp_name

        subnet_name = network_compartment_name + "@" + mysql_vcn_name + "::" + mysql_subnet_name

    # Get configuration details if present
    config_name = ""
    config_compartment_name = ""
    config_id = ""
    
    if hasattr(mysql_db, 'configuration_id') and mysql_db.configuration_id:
        config_id = mysql_db.configuration_id
        try:
            # Create MySQL client with the same config as the parent client
            config_copy = dict(vnc_client.base_client.config)
            # Create a copy of the config and set the region from Excel row
            config_copy = config_copy.copy()
            excel_region = row['Region'].lower().strip()
            config_copy['region'] = region_mapping.get(excel_region, excel_region)
            
            # Try with both client types
            try:
                mysql_client = oci.mysql.MysqlaasClient(config=config_copy, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=vnc_client.base_client.signer)
                config_obj = mysql_client.get_configuration(mysql_db.configuration_id).data
            except Exception as e1:
                try:
                    mysql_client = oci.mysql.MysqlaasClient(config=config_copy, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=vnc_client.base_client.signer)
                    config_obj = mysql_client.get_configuration(mysql_db.configuration_id).data
                except Exception as e2:
                    print(f"\nWarning2: Could not fetch configuration details for {mysql_db.display_name}: {str(e2)}")
                    config_obj = None
            
            if hasattr(config_obj, 'display_name'):
                config_name = config_obj.display_name
                
                # Get configuration compartment name
                for comp_name, comp_id in ct.ntk_compartment_ids.items():
                    if comp_id == config_obj.compartment_id:
                        config_compartment_name = comp_name
                        break
                
                # Format configuration name similar to subnet_name
                if config_compartment_name and config_name:
                    config_id = config_compartment_name +'@' + config_name
                
        except Exception as e:
            print(f"\nWarning1: Could not fetch configuration details for {mysql_db.display_name}: {str(e)}")

    # Check if resource exists in terraform state
    tf_resource = f'module.mysql_db_system[\\"{mysql_tf_name}\\"].oci_mysql_mysql_db_system.db_system'
    if tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{ct.tf_or_tofu} import "{tf_resource}" {str(mysql_db.id)}'
    
    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'Display Name':
            values_for_column[col_header].append(mysql_db.display_name)
        elif col_header == 'Description':
            values_for_column[col_header].append(mysql_db.description if mysql_db.description else "")
        elif col_header == 'Configuration id':
            values_for_column[col_header].append(config_id)  # Use config_id directly
        elif col_header == 'Configuration Name':  
            if config_name and config_compartment_name:
                config_value = f"{config_compartment_name}@{config_name}"
                values_for_column[col_header].append(config_value)
            elif config_name:
                values_for_column[col_header].append(config_name)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'Hostname Label':
            hostname = mysql_db.hostname_label if mysql_db.hostname_label else mysql_db.display_name.lower().replace("-", "")
            values_for_column[col_header].append(hostname)
        elif col_header == 'Shape':
            values_for_column[col_header].append(mysql_db.shape_name)
        elif col_header == 'Network Details':
            if mysql_subnet_id is not None:
                values_for_column[col_header].append(subnet_name)
            else:
                values_for_column[col_header].append("")
        elif col_header == 'Username':
            values_for_column[col_header].append("")
        elif col_header == 'Password':
            values_for_column[col_header].append("") # For security, don't export passwords
        elif col_header == 'HA':
            values_for_column[col_header].append(str(mysql_db.is_highly_available).lower())
        elif col_header == 'Availability Domain(AD1|AD2|AD3)':
            ad_value = mysql_db.availability_domain
            ad = ""
            if "AD-1" in ad_value.upper() or "-1" in ad_value:
                ad = "AD1"
            elif "AD-2" in ad_value.upper() or "-2" in ad_value:
                ad = "AD2"
            elif "AD-3" in ad_value.upper() or "-3" in ad_value:
                ad = "AD3"
            values_for_column[col_header].append(ad)
        elif col_header == 'Fault Domain':
            values_for_column[col_header].append(mysql_db.fault_domain if mysql_db.fault_domain else "")
        elif col_header == 'IP Address':
            values_for_column[col_header].append(mysql_db.ip_address if mysql_db.ip_address else "")
        elif col_header == 'Port':
            values_for_column[col_header].append(str(mysql_db.port) if mysql_db.port else "")
        elif col_header == 'Port_x':
            values_for_column[col_header].append(str(mysql_db.port_x) if mysql_db.port_x else "")
        elif col_header == 'Data Storage (in Gbs)':
            values_for_column[col_header].append(str(mysql_db.data_storage_size_in_gbs))
        elif col_header == 'Backup policy is enabled':
            values_for_column[col_header].append(str(mysql_db.backup_policy.is_enabled).lower() if mysql_db.backup_policy else "")
        elif col_header == 'Backup policy pitr policy is enabled':
            values_for_column[col_header].append(str(mysql_db.backup_policy.pitr_policy.is_enabled).lower() if mysql_db.backup_policy and mysql_db.backup_policy.pitr_policy else "")
        elif col_header == 'Backup policy Retention in days':
            values_for_column[col_header].append(str(mysql_db.backup_policy.retention_in_days) if mysql_db.backup_policy else "")
        elif col_header == 'Backup policy window start time':
            values_for_column[col_header].append(mysql_db.backup_policy.window_start_time if mysql_db.backup_policy and mysql_db.backup_policy.window_start_time else "")
        elif col_header == 'Deletion policy final backup':
            values_for_column[col_header].append(str(mysql_db.deletion_policy.final_backup).lower() if mysql_db.deletion_policy else "")
        elif col_header == 'Deletion policy is deleted protected':
            values_for_column[col_header].append(str(mysql_db.deletion_policy.is_delete_protected).lower() if mysql_db.deletion_policy else "")
        elif col_header == 'Maintenance window start time':
            values_for_column[col_header].append(mysql_db.maintenance.window_start_time if mysql_db.maintenance else "")
        elif col_header == 'Database Management is Enabled':
            values_for_column[col_header].append(mysql_db.database_management if mysql_db.database_management else "DISABLED")
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(mysql_db, col_header, values_for_column)
        else:
            oci_objs = [mysql_db]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

def export_mysql_db(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[],export_tags=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global cd3file
    global reg
    global values_for_column
    global tf_or_tofu

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "MySQL-DBSystems"

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- MySQL-DBSystems will be overwritten during export process!!!\n")

    # Create backups and initialize importCommands
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    importCommands = {}
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        importCommands[reg] = ''
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(script_file), exist_ok=True)
        
        # Backup existing files
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
            #os.remove(script_file)  # Remove the old file after backup

    print("\nFetching MySQL DB Systems...")

    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                if item:  # Only add non-empty lines
                    state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        
        region = reg.capitalize()
        vnc_client = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)

        for ntk_compartment_name in export_compartments:
            mysql_dbs = oci.pagination.list_call_get_all_results(oci.mysql.DbSystemClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer).list_db_systems,
                                                               compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                               lifecycle_state="ACTIVE")
            for mysql_db in mysql_dbs.data:

                mysql_db = oci.mysql.DbSystemClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer).get_db_system(mysql_db.id).data
                # Tags filter
                defined_tags = mysql_db.defined_tags
                tags_list = []
                for tkey, tval in defined_tags.items():
                    for kk, vv in tval.items():
                        tag = tkey + "." + kk + "=" + vv
                        tags_list.append(tag)

                if export_tags == []:
                    check = True
                else:
                    check = any(e in tags_list for e in export_tags)
                # None of Tags from export_tags exist on this instance; Dont export this instance
                if check == False:
                    continue

                print_mysql(region, vnc_client, mysql_db, values_for_column, ntk_compartment_name, state, ct, df.iloc[0])

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} MySQL Database Systems exported into CD3.\n".format(len(values_for_column["Region"])))

    # Writing import commands
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if importCommands[reg]:
            init_commands = f'#!/bin/bash\n\n######### Writing import for MySQL Database Systems #########\n\n{tf_or_tofu} init'
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            
            # Write to file in append mode
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])
            os.chmod(script_file, 0o755)  # Make the script executable


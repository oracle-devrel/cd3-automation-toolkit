#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will export MySQL Configuration from OCI
#
# Author: Mukund Murali
# Oracle Consulting
#

import oci
import os
from commonTools import *
from oci.exceptions import ServiceError

def export_mysql_configurations(inputfile, outdir, service_dir, config, signer, ct, export_regions=[], export_compartments=[]):
    # Get list of compartments
    print("Getting list of all compartments...")
    all_compartments = ct.get_compartment_map(export_compartments)
    
    # Create output directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Export MySQL Configurations
    print("\nExporting MySQL Configurations...")
    export_mysql_configuration(inputfile, outdir, service_dir, config, signer, ct, export_regions, export_compartments)
    print("Export completed!")

def export_mysql_configuration(inputfile, outdir, service_dir, config, signer, ct, export_regions=[], export_compartments=[],export_tags=[]):
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

    sheetName = "MySQL-Configurations"

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Initialize all columns
    values_for_column = {
        'Region': [], 'Compartment Name': [], 'Display Name': [], 'Description': [],
        'Shape Name': [], 'Configuration Type': [], 'Parent Configuration Id': [],
        'Configuration id': [], 'users_variable_name': [], 'users_variable_value': [],
        'Defined Tags': [], 'Freeform Tags': []  # Adding tag columns
    }

    # Get dict for columns from Excel_Columns
    sheet_dict = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- MySQL-Configurations will be overwritten during export process!!!\n")

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

    total_configs = 0
    processed_configs = set()
    
    print("\nFetching MySQL Configurations...")
    
    for reg in export_regions:
        region = reg.lower()
        script_file = f'{outdir}/{reg}/{service_dir}/{file_name}'

        config["region"] = ct.region_dict[reg]
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass

        # Use MysqlaasClient for MySQL configurations
        try:
            mysql_client = oci.mysql.MysqlaasClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        except Exception as e:
            print(f"\nError: Could not create MySQL configuration client: {str(e)}")
            continue
        
        for ntk_compartment_name in export_compartments:
            try:
                configs = oci.pagination.list_call_get_all_results(
                    mysql_client.list_configurations,
                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name]
                )

                for config_obj in configs.data:
                    if config_obj.lifecycle_state not in ["DELETED", "PENDING_DELETION", "SCHEDULING_DELETION"] and config_obj.compartment_id:
                        config_id = config_obj.id
                        
                        # Skip if we've already processed this configuration
                        if config_id in processed_configs:
                            continue

                        # Tags filter
                        defined_tags = config_obj.defined_tags
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
                            
                        processed_configs.add(config_id)
                        total_configs += 1
                        config_tf_name = commonTools.check_tf_variable(config_obj.display_name)

                        # Check if resource exists in terraform state
                        tf_resource = f'module.mysql_configuration[\\"{config_tf_name}\\"].oci_mysql_mysql_configuration.mysql_configuration'
                        if tf_resource not in state["resources"]:
                            importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {config_obj.id}'

                        # Initialize all values for this row
                        row_values = {
                            'Region': region,
                            'Compartment Name': ntk_compartment_name,
                            'Display Name': config_obj.display_name,
                            'Description': config_obj.description if hasattr(config_obj, 'description') else "",
                            'Shape Name': config_obj.shape_name if hasattr(config_obj, 'shape_name') else "",
                            'Configuration Type': config_obj.type if hasattr(config_obj, 'type') else "",
                            'Parent Configuration Id': "",
                            'Configuration id': f"{ntk_compartment_name}@{config_obj.display_name}" if hasattr(config_obj, 'display_name') and config_obj.display_name else config_id,
                            'users_variable_name': "",
                            'users_variable_value': "",
                            'Defined Tags': str(config_obj.defined_tags) if hasattr(config_obj, 'defined_tags') and config_obj.defined_tags else "",
                            'Freeform Tags': str(config_obj.freeform_tags) if hasattr(config_obj, 'freeform_tags') and config_obj.freeform_tags else ""
                        }

                        # Add all values to their respective lists at once
                        for key, value in row_values.items():
                            values_for_column[key].append(value)

                        # Get detailed configuration
                        try:
                            # Extract region from config_id
                            config_region = None
                            if '.phx.' in config_id:
                                config_region = 'us-phoenix-1'
                            elif '.iad.' in config_id:
                                config_region = 'us-ashburn-1'
                            else:
                                config_region = region  # Use current region as fallback
                            

                            # Create MySQL client with the correct region
                            config_copy = config.copy()
                            config_copy["region"] = config_region
                            mysql_client = oci.mysql.MysqlaasClient(config=config_copy, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
                            
                            # Get the configuration details
                            config_obj = mysql_client.get_configuration(config_id).data
                            
                            # Get configuration compartment name and format Configuration id
                            config_compartment_name = ntk_compartment_name  # Default to network compartment name
                            if hasattr(config_obj, 'compartment_id') and config_obj.compartment_id:
                                for comp_name, comp_id in ct.ntk_compartment_ids.items():
                                    if comp_id == config_obj.compartment_id:
                                        config_compartment_name = comp_name
                                        break

                            # Format Configuration id as compartmentname@config_name
                            if hasattr(config_obj, 'display_name') and config_obj.display_name:
                                formatted_id = f"{config_compartment_name}@{config_obj.display_name}"
                                values_for_column['Configuration id'][-1] = formatted_id
                            else:
                                values_for_column['Configuration id'][-1] = config_id

                            # Add other configuration details
                            values_for_column['Display Name'][-1] = config_obj.display_name
                            values_for_column['Description'][-1] = config_obj.description if hasattr(config_obj, 'description') else ""
                            values_for_column['Shape Name'][-1] = config_obj.shape_name if hasattr(config_obj, 'shape_name') else ""
                            values_for_column['Configuration Type'][-1] = config_obj.type if hasattr(config_obj, 'type') else ""
                            values_for_column['Parent Configuration Id'][-1] = ""

                        except Exception as e:
                            print(f"\nWarning: Could not fetch configuration details for {config_id}: {str(e)}")
                            values_for_column['Configuration id'][-1] = config_id
                            values_for_column['Display Name'][-1] = ""
                            values_for_column['Description'][-1] = ""
                            values_for_column['Shape Name'][-1] = ""
                            values_for_column['Configuration Type'][-1] = ""
                            values_for_column['Parent Configuration Id'][-1] = ""

                        # Handle variables as key-value pairs
                        if hasattr(config_obj, 'variables'):
                            vars_obj = config_obj.variables
                            variables = {}
                            for attr_name in dir(vars_obj):
                                if not attr_name.startswith('_') and attr_name not in ['attribute_map', 'swagger_types']:
                                    attr_value = getattr(vars_obj, attr_name)
                                    if attr_value is not None:
                                        variables[attr_name] = str(attr_value)

                            # Add first variable in the main row
                            if variables:
                                first_var = next(iter(variables.items()))
                                values_for_column['users_variable_name'][-1] = first_var[0]
                                values_for_column['users_variable_value'][-1] = first_var[1]

                                # Add additional rows for remaining variables
                                remaining_vars = list(variables.items())[1:]
                                for var_name, var_value in remaining_vars:
                                    values_for_column['Region'].append("")
                                    values_for_column['Compartment Name'].append("")
                                    values_for_column['Display Name'].append("")
                                    values_for_column['Description'].append("")
                                    values_for_column['Shape Name'].append("")
                                    values_for_column['Configuration Type'].append("")
                                    values_for_column['Parent Configuration Id'].append("")
                                    values_for_column['Configuration id'].append("")
                                    values_for_column['users_variable_name'].append(var_name)
                                    values_for_column['users_variable_value'].append(var_value)
                                    values_for_column['Defined Tags'].append("")
                                    values_for_column['Freeform Tags'].append("")
                        else:
                            values_for_column['users_variable_name'][-1] = ""
                            values_for_column['users_variable_value'][-1] = ""

            except ServiceError as e:
                print(f"Error fetching MySQL configurations in {reg} region, compartment {ntk_compartment_name}: {str(e)}")
                continue

    # Validate list lengths before writing to CD3
    def validate_list_lengths():
        # Get the length of the first list
        first_key = next(iter(values_for_column))
        expected_length = len(values_for_column[first_key])
        
        # Check all lists have the same length
        for key, value_list in values_for_column.items():
            if len(value_list) != expected_length:
                print(f"Warning: List length mismatch for {key}: {len(value_list)} != {expected_length}")
                # Pad shorter lists with empty strings
                while len(value_list) < expected_length:
                    value_list.append("")

    validate_list_lengths()

    # Write to CD3
    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print(f"Processed {total_configs} MySQL configurations.")

    # Write import commands
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/{file_name}'
        if importCommands[reg]:
            init_commands = f'#!/bin/bash\n\n######### Writing import for MySQL configurations #########\n\n{tf_or_tofu} init'
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            
            # Write to file in append mode
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])
            os.chmod(script_file, 0o755)  # Make the script executable

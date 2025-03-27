#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# MySQL Database System
#
# Author: Mukund Murali
# Oracle Consulting
#

import os
import sys
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *

def create_terraform_mysql_db(inputfile, outdir, service_dir, prefix, ct):
    ADS = ["AD1", "AD2", "AD3"]
    filename = inputfile
    sheetName = "MySQL-DBSystems"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('mysql-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    #print("\nAvailable columns in Excel:", dfcolumns) 

    # Initialize empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip().lower()

        if (region in commonTools.endNames):
            break
        region=region.strip().lower()

        # Skip if region is not in regions
        if region not in [x.lower() for x in ct.all_regions]:
            print(f"\nERROR!!! Invalid Region {str(df.loc[i, 'Region']).strip()} in MySQL DB System sheet. Skipping row!", file=sys.stderr)
            continue

        # Get the actual region name with correct case from ct.all_regions
        region = next(x for x in ct.all_regions if x.lower() == region)

        # Print row data for debugging
        #print(f"\nProcessing row {i}:")
        #for col in dfcolumns:
            #print(f"{col}: {str(df.loc[i, col]).strip()}")

        # Initialize the template dictionary
        tempdict = {
            'display_tf_name': commonTools.check_tf_variable(str(df.loc[i, 'Display Name']).strip()),
            #'compartment_name': str(df.loc[i, 'Compartment Name']).strip(),
            'compartment_name': commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip()),
            'display_name': str(df.loc[i, 'Display Name']).strip(),
            'description': str(df.loc[i, 'Description']).strip(),
            'hostname_label': str(df.loc[i, 'Hostname Label']).strip(),
            'is_highly_available': str(df.loc[i, 'HA']).strip().lower() == 'true',
            'shape': str(df.loc[i, 'Shape']).strip() or 'MySQL.VM.Standard.E3.1.8GB',
            'admin_username': str(df.loc[i, 'Username']).strip(),
            'admin_password': str(df.loc[i, 'Password']).strip(),
            'ip_address': str(df.loc[i, 'IP Address']).strip(),
            'port': int(str(df.loc[i, 'Port']).strip() or '3306'),
            'port_x': int(str(df.loc[i, 'Port_x']).strip() or '33060'),
            'data_storage_size_in_gb': int(str(df.loc[i, 'Data Storage (in Gbs)']).strip() or '50'),
            'backup_policy_is_enabled': str(df.loc[i, 'Backup policy is enabled']).strip().lower() == 'true',
            'backup_policy_window_start_time': str(df.loc[i, 'Backup policy window start time']).strip() or '06:26',
            'backup_policy_retention_in_days': int(str(df.loc[i, 'Backup policy Retention in days']).strip() or '7'),
            'backup_policy_pitr_policy_is_enabled': str(df.loc[i, 'Backup policy pitr policy is enabled']).strip().lower() == 'true',
            'deletion_policy_is_delete_protected': str(df.loc[i, 'Deletion policy is deleted protected']).strip().lower() == 'true',
            'deletion_policy_final_backup': str(df.loc[i, 'Deletion policy final backup']).strip() or 'RETAIN',
            'deletion_policy_automatic_backup_retention': str(df.loc[i, 'Deletion policy automatic backup retention']).strip() or 'RETAIN',
            'crash_recovery': str(df.loc[i, 'Crash Recovery is Enabled']).strip() or 'ENABLED',
            'database_management': str(df.loc[i, 'Database Management is Enabled']).strip() or 'ENABLED',
            'source': str(df.loc[i, 'Source Type']).strip() or 'NONE',
            'configuration_id': '',
            'configurations_compartment_id': '',
            'fault_domain': str(df.loc[i, 'Fault Domain']).strip() or 'FAULT-DOMAIN-1',
        }

        # Process configuration ID to get compartment@name format
        config_id = str(df.loc[i, 'Configuration id']).strip()
        if config_id and config_id.lower() != 'nan':
            if '@' in config_id:
                # Split into compartment and name
                config_parts = config_id.split('@')
                if len(config_parts) == 2:
                    config_compartment_name = commonTools.check_tf_variable(config_parts[0].strip())
                    config_name = config_parts[1].strip()
                    
                    # Set both the configuration_id and configuration_compartment_id
                    tempdict['configuration_compartment_id'] = config_compartment_name
                    tempdict['configuration_id'] = config_name
                    # Add depends_on attribute to ensure MySQL configuration is created first
                    tempdict['depends_on_mysql_configuration'] = True
                else:
                    print(f"\nWARNING: Invalid configuration_id format: {config_id}. Expected format: compartment@name",
                          file=sys.stderr)
                    tempdict['configuration_id'] = config_id
                    tempdict['configuration_compartment_id'] = tempdict[
                        'compartment_name']  # Use MySQL compartment as default
                    tempdict['depends_on_mysql_configuration'] = False
            else:
                # If it's not in compartment@name format, check if it's an OCID or just a name
                if config_id.startswith('ocid1.'):
                    # It's an OCID, no dependency needed
                    tempdict['configuration_id'] = config_id
                    tempdict['configuration_compartment_id'] = tempdict[
                        'compartment_name']  # Use MySQL compartment as default
                    tempdict['depends_on_mysql_configuration'] = False
                else:
                    # It's just a name, we need to add dependency
                    tempdict['configuration_id'] = config_id
                    tempdict['configuration_compartment_id'] = tempdict[
                        'compartment_name']  # Use MySQL compartment as default
                    tempdict['depends_on_mysql_configuration'] = True
        else:
            tempdict['configuration_id'] = ''
            tempdict['configuration_compartment_id'] = tempdict['compartment_name']  # Use MySQL compartment as default
            tempdict['depends_on_mysql_configuration'] = False

        # Process Availability Domain
        ad = str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).strip()
        if ad and ad.lower() != 'nan':
            # Convert AD name to index (AD1->0, AD2->1, AD3->2)
            ad_num = ad.replace('AD', '')
            try:
                ad_index = str(int(ad_num) - 1)  # Convert to 0-based index
                tempdict['availability_domain'] = ad_index
            except ValueError:
                print(f"\nWARNING: Invalid AD format {ad}, using default", file=sys.stderr)
                tempdict['availability_domain'] = "0"
        else:
            tempdict['availability_domain'] = "0"

        # Process Subnet Name to get network compartment, vcn and subnet
        subnet_name = str(df.loc[i, 'Network Details']).strip()
        if subnet_name and subnet_name.lower() != 'nan':
            subnet_parts = subnet_name.split('@')
            if len(subnet_parts) == 2:
                network_compartment = commonTools.check_tf_variable(subnet_parts[0].strip())
                vcn_subnet = subnet_parts[1].strip()
                vcn_subnet_parts = vcn_subnet.split('::')
                if len(vcn_subnet_parts) == 2:
                    # Ensure network_compartment is never empty
                    if network_compartment:
                        tempdict['network_compartment_id'] = network_compartment
                    else:
                        tempdict['network_compartment_id'] = tempdict['compartment_name']
                    
                    tempdict['vcn_names'] = vcn_subnet_parts[0].strip()
                    tempdict['subnet_id'] = vcn_subnet_parts[1].strip()
                else:
                    print(f"\nERROR!!! Invalid VCN/Subnet format in {subnet_name}. Expected format: network_compartment@vcn_subnet", file=sys.stderr)
                    continue
            else:
                print(f"\nERROR!!! Invalid Subnet Name format {subnet_name}. Expected format: network_compartment@vcn_subnet", file=sys.stderr)
                continue
        else:
            # If subnet name is missing/nan, use the same compartment as the MySQL instance
            tempdict['network_compartment_id'] = tempdict['compartment_name']
            tempdict['vcn_names'] = ''
            tempdict['subnet_id'] = ''

        # Handle backup policy settings
        backup_window = str(df.loc[i, 'Backup policy window start time']).strip()
        if backup_window and backup_window.lower() != 'nan':
            # Preserve the existing backup window time format
            if ':' in backup_window:
                # If it's already in HH:MM:SS or HH:MM format, use it as is
                tempdict['backup_policy_window_start_time'] = backup_window
            else:
                # Default to a standard time if not in correct format
                print(f"\nWARNING: Invalid backup window time format {backup_window}, using default", file=sys.stderr)
                tempdict['backup_policy_window_start_time'] = "00:00:00"
        else:
            tempdict['backup_policy_window_start_time'] = "00:00:00"

        # Handle other backup policy settings
        backup_enabled = str(df.loc[i, 'Backup policy is enabled']).strip()
        tempdict['backup_policy_is_enabled'] = backup_enabled.lower() == 'true' if backup_enabled.lower() != 'nan' else True

        pitr_enabled = str(df.loc[i, 'Backup policy pitr policy is enabled']).strip()
        tempdict['backup_policy_pitr_policy_is_enabled'] = pitr_enabled.lower() == 'true' if pitr_enabled.lower() != 'nan' else True

        retention_days = str(df.loc[i, 'Backup policy Retention in days']).strip()
        tempdict['backup_policy_retention_in_days'] = int(retention_days) if retention_days.lower() != 'nan' else 7

        # Format maintenance window time
        maintenance_time = str(df.loc[i, 'Maintenance window start time']).strip()
        if maintenance_time and maintenance_time.lower() != 'nan':
            # Check if it's already in the format "DAY HH:MM"
            if any(day in maintenance_time.upper() for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']):
                # Split into day and time parts
                day_part = next(day for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'] 
                              if day in maintenance_time.upper())
                time_part = maintenance_time.upper().replace(day_part, '').strip()
                
                # Keep HH:MM format, don't add seconds
                if ':' in time_part:
                    if time_part.count(':') == 2:  # HH:MM:SS format
                        time_part = ':'.join(time_part.split(':')[:2])  # Keep only HH:MM
                    tempdict['maintenance_window_start_time'] = f"{day_part} {time_part}"
                else:
                    tempdict['maintenance_window_start_time'] = "TUESDAY 12:50"
            else:
                # If only time is provided, default to TUESDAY
                if ':' in maintenance_time:
                    # Keep HH:MM format, don't add seconds
                    if maintenance_time.count(':') == 2:  # HH:MM:SS format
                        maintenance_time = ':'.join(maintenance_time.split(':')[:2])  # Keep only HH:MM
                    tempdict['maintenance_window_start_time'] = f"TUESDAY {maintenance_time}"
                else:
                    tempdict['maintenance_window_start_time'] = "TUESDAY 12:50"
        else:
            tempdict['maintenance_window_start_time'] = "TUESDAY 12:50"

        # Ensure deletion policy values are in correct case
        final_backup = str(df.loc[i, 'Deletion policy final backup']).strip().upper()
        if final_backup == 'REQUIRE_FINAL_BACKUP':
            tempdict['deletion_policy_final_backup'] = 'REQUIRE_FINAL_BACKUP'
        elif final_backup == 'SKIP_FINAL_BACKUP':
            tempdict['deletion_policy_final_backup'] = 'SKIP_FINAL_BACKUP'
        else:
            tempdict['deletion_policy_final_backup'] = 'SKIP_FINAL_BACKUP'

        retention = str(df.loc[i, 'Deletion policy automatic backup retention']).strip().upper()
        if retention == 'RETAIN':
            tempdict['deletion_policy_automatic_backup_retention'] = 'RETAIN'
        elif retention == 'DELETE':
            tempdict['deletion_policy_automatic_backup_retention'] = 'DELETE'
        else:
            tempdict['deletion_policy_automatic_backup_retention'] = 'DELETE'

        # Handle database management setting
        db_mgmt = str(df.loc[i, 'Database Management is Enabled']).strip()
        if db_mgmt and db_mgmt.lower() != 'nan':
            tempdict['database_management'] = db_mgmt
        else:
            tempdict['database_management'] = "DISABLED"  # Default to DISABLED to match existing instances

        # Handle nan values and set defaults
        if str(df.loc[i, 'Source Type']).strip().lower() == 'nan':
            tempdict['source'] = {'source_type': 'NONE'}
        else:
            tempdict['source'] = {'source_type': str(df.loc[i, 'Source Type']).strip()}

        if str(df.loc[i, 'Username']).strip().lower() == 'nan':
            tempdict['admin_username'] = ''
        else:
            tempdict['admin_username'] = str(df.loc[i, 'Username']).strip()

        if str(df.loc[i, 'Password']).strip().lower() == 'nan':
            tempdict['admin_password'] = ''
        else:
            tempdict['admin_password'] = str(df.loc[i, 'Password']).strip()

        # Add data storage details
        storage_size = str(df.loc[i, 'Data Storage (in Gbs)']).strip()
        tempdict['data_storage'] = {
            'data_storage_size_in_gb': int(storage_size if storage_size.lower() != 'nan' else '50'),
            'is_auto_expand_storage_enabled': False
        }

        # Add secure connections
        tempdict['secure_connections'] = {
            'certificate_generation_type': 'SYSTEM',
            'is_ssl_enabled': True
        }

        # Handle empty description
        if str(df.loc[i, 'Description']).strip().lower() == 'nan':
            tempdict['description'] = ''
        else:
            tempdict['description'] = str(df.loc[i, 'Description']).strip()

        # Remove any remaining nan values
        for key in tempdict:
            if isinstance(tempdict[key], str) and tempdict[key].lower() == 'nan':
                tempdict[key] = ''

        # Add to terraform string
        if region in tfStr:
            tfStr[region] += template.render(count=1, **tempdict)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

        if tfStr[reg] != '':
            src = "##Add New MySQL Database System for " + reg.lower() + " here##"
            # Remove any trailing commas from the last entry
            tfStr[reg] = tfStr[reg].rstrip(',\n') + "\n"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            
            with open(outfile[reg], 'w') as f:
                f.write(tfStr[reg])
                print(f"Created MySQL DBsystem for region {reg} in {outfile[reg]}")
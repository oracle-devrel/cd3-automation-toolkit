#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Database
# MySQL Configuration
#
# Author: Generated by Cascade
# Oracle Consulting
#

import os
import re
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *

def create_terraform_mysql_configuration(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile
    sheetName = "MySQL-Configurations"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Initialize tracking variables
    prev_values = {
        'region': '',
        'compartment_name': '',
        'display_name': '',
        'description': '',
        'shape_name': ''
    }
    
    tfStr = {}
    mysql_config_vars = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('mysql-configuration-template')

    # Add custom functions to template environment
    def make_config_keys(config):
        return lambda: config.keys()
    def make_config_value(config):
        return lambda key: config.get(key, '')
    env.globals['config_keys'] = None
    env.globals['config_value'] = None

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    # Initialize empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
        mysql_config_vars[reg] = {}

    # Process each row
    for i in df.index:
        # Get values from row
        region = str(df.loc[i, 'Region']).strip()
        compartment_name = str(df.loc[i, 'Compartment Name']).strip()
        display_name = str(df.loc[i, 'Display Name']).strip()
        description = str(df.loc[i, 'Description']).strip()
        shape_name = str(df.loc[i, 'Shape Name']).strip()
        
        # Handle empty values using previous values
        if region.lower() == 'nan' or region == '':
            region = prev_values['region']
        if compartment_name.lower() == 'nan' or compartment_name == '':
            compartment_name = prev_values['compartment_name']
        if display_name.lower() == 'nan' or display_name == '':
            display_name = prev_values['display_name']
        if description.lower() == 'nan' or description == '':
            description = prev_values['description']
        if shape_name.lower() == 'nan' or shape_name == '':
            shape_name = prev_values['shape_name']

        # Update previous values
        prev_values.update({
            'region': region,
            'compartment_name': compartment_name,
            'display_name': display_name,
            'description': description,
            'shape_name': shape_name
        })

        # Skip if essential values are missing
        if region.lower() == 'nan' or display_name.lower() == 'nan':
            continue

        # Initialize region if needed
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Check for variable row
        user_var_name = str(df.loc[i, 'users_variable_name']).strip()
        user_var_value = str(df.loc[i, 'users_variable_value']).strip()

        # Initialize config if needed
        config_tf_name = commonTools.check_tf_variable(display_name)
        if config_tf_name not in mysql_config_vars[region]:
            mysql_config_vars[region][config_tf_name] = {
                'config_display_tf_name': config_tf_name,
                'compartment_tf_name': commonTools.check_tf_variable(compartment_name),
                'display_name': display_name,
                'description': description,
                'shape_name': shape_name
            }

        # Only process variable if both name and value are present and not empty
        if (user_var_name.lower() != 'nan' and user_var_name != '' and 
            user_var_value.lower() != 'nan' and user_var_value != ''):
            # Add variable with mysql_configuration_ prefix
            var_name = f"mysql_configuration_variables_{user_var_name}"
            # Handle boolean values
            if user_var_value.lower() in ['true', 'false']:
                mysql_config_vars[region][config_tf_name][var_name] = user_var_value.capitalize()
            else:
                mysql_config_vars[region][config_tf_name][var_name] = user_var_value

    # Generate terraform configuration for each region
    for region in mysql_config_vars:
        if not mysql_config_vars[region]:
            continue

        # Start with count = 0 to generate opening
        env.globals['count'] = 0
        tfStr[region] = template.render()
        
        configs = list(mysql_config_vars[region].items())
        for i, (config_name, config) in enumerate(configs):
            # Update template functions for this config
            env.globals['config_keys'] = make_config_keys(config)
            env.globals['config_value'] = make_config_value(config)
            config['loop'] = {'last': i == len(configs) - 1}
            env.globals['count'] = 1
            
            # Render configuration
            rendered_config = template.render(**config)
            tfStr[region] += rendered_config

        # Add closing brace
        env.globals['count'] = 2
        tfStr[region] += template.render()

    # Write files
    for region in tfStr:
        if tfStr[region] != '':
            srcdir = outdir + "/" + region + "/" + service_dir + "/"
            os.makedirs(srcdir, exist_ok=True)
            
            outfile = srcdir + "/" + auto_tfvars_filename
            # Clean up the output
            tfStr[region] = tfStr[region].strip()
            # Fix any potential formatting issues
            tfStr[region] = re.sub(r'\s+mysql_configuration_variables_', '\n    mysql_configuration_variables_', tfStr[region])
            tfStr[region] = re.sub(r'}\s*,\s*', '},\n', tfStr[region])
            tfStr[region] = re.sub(r'\n\s*\n\s*\n', '\n\n', tfStr[region])
            
            with open(outfile, 'w') as f:
                f.write(tfStr[region])
            print(f"Created MySQL configuration for region {region} in {outfile}")
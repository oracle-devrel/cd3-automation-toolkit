#!/usr/bin/python3
# Copyright (c) 2019, 2023, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Users
#
# Author: Gaurav Goyal
# Oracle Consulting
# Modified by: Ranjini Rajendran
#
import os
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_users(inputfile, outdir, service_dir, prefix, ct):
    # Read the arguments
    filename = inputfile

    sheetName = 'Users'
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    users_template = env.get_template('users-template')
    identity_domain_users_template = env.get_template('identity-domain-users-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    tfStr[ct.home_region] = ''


    # Take backup of files
    srcdir = outdir + "/" + ct.home_region + "/" + service_dir + "/"
    resource = sheetName.lower()
    commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region=region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = { "count" : i }
        tempdict = {}
        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'User Name']).lower() == 'nan' :
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit(1)

        all_capabilities = [
            "can_use_api_keys",
            "can_use_auth_tokens",
            "can_use_console_password",
            "can_use_customer_secret_keys",
            "can_use_db_credentials",
            "can_use_oauth2client_credentials",
            "can_use_smtp_credentials"
        ]
        # Initialize domain variable
        domain = str(df.loc[i, 'Domain Name']).strip()
        if domain.lower() == 'default':
            domain = 'DEFAULT'
        elif pd.isna(domain) or domain.lower() == 'nan':
            domain = 'nan'

        for columnname in dfcolumns:

            if 'Description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df[columnname][i]).strip()

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'User Name':
                columnvalue = columnvalue.strip()
                domain = df.loc[i, 'Domain Name']
                # Convert to uppercase if domain is "Default," "DEFAULT," or "default"
                if domain == 'default':
                    domain = 'DEFAULT'
                elif pd.isna(domain):
                    domain = ''
                user_tf_name = f"{domain}_{commonTools.check_tf_variable(columnvalue)}"
                if user_tf_name.startswith('_'):
                    user_tf_name = user_tf_name[1:]
                tempdict = {'user_tf_name': user_tf_name}

            if columnname == 'Family Name':
                columnvalue = columnvalue.strip()
                tempdict = {'last_name': columnvalue}

            if columnname == 'User Email':
                email = commonTools.check_columnvalue(columnvalue)
                tempdict['email'] = email

                # Initialize the template variable
                selected_template = users_template if domain == '' else identity_domain_users_template

                if domain == '':
                    tempdict['name'] = df.loc[i, 'User Name']
                    tempdict['email'] = email

            if columnname == 'Enable Capabilities':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    if domain == '':
                        provided_capabilities = [cap.strip() for cap in columnvalue.split(",") if cap.strip()]
                        remaining_capabilities = [cap for cap in all_capabilities if cap not in provided_capabilities]
                        capability_str = ",".join(f"\"{cap}\"" for cap in remaining_capabilities)
                    else:
                        capabilities = columnvalue.split(",")
                        capability_str = ""
                        k = 0
                        while k < len(capabilities):
                            if capabilities[k].strip() == "":
                                k += 1
                                continue
                            capability = "\"" + capabilities[k].strip() + "\""
                            capability_str += capability
                            if k != len(capabilities) - 1:
                                capability_str += ","
                            k += 1
                    tempdict = {'capabilities': capability_str}
                    tempStr.update(tempdict)
                continue

            # Process Defined and Freeform Tags based on columnname and 'Domain Name'
            if columnname.lower() in commonTools.tagColumns:
                if domain == '':
                    # Process tags using the existing code
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                else:
                    # When 'Domain Name' is not 'nan', process 'Defined Tags' differently
                    if columnname == 'Defined Tags':
                        defined_tags = columnvalue.strip()
                        tag_strings = defined_tags.split(';')

                        defined_tags_list = []
                        for tag_string in tag_strings:
                            parts = tag_string.split('=')
                            if len(parts) == 2:
                                namespace_key = parts[0]
                                value = parts[1]
                                namespace, key = namespace_key.split('.')
                                tempdict = {'namespace': namespace, 'key': key, 'value': value}
                                defined_tags_list.append(tempdict)


            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region]= tfStr[region][:-1] + selected_template.render(tempStr)
    # Write TF string to the file in respective region directory
    reg=ct.home_region

    reg_out_dir = outdir + "/" + reg + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

    if(tfStr[reg]!=''):
        tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " for Users has been created for region "+reg)

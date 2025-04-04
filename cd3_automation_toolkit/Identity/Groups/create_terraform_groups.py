#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Groups
#
# Author: Suruchi Singla
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
def create_terraform_groups(inputfile, outdir, service_dir, prefix, ct):
    # Read the arguments
    filename = inputfile

    sheetName = 'Groups'
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    groups_template = env.get_template('groups-template')
    identity_domain_groups_template = env.get_template('identity-domain-groups-template')

    selected_template = identity_domain_groups_template if ct.identity_domain_enabled else groups_template

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

        # If some invalid region is specified in a row
        if region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = { "count" : i }
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Name']).lower() == 'nan' :
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit(1)

        # Initialize domain variable
        domain = str(df.loc[i, 'Domain Name']).strip()
        compartment_id = ""

        if not ct.identity_domain_enabled:
            domain=''
        if ct.identity_domain_enabled and domain.lower() == 'nan':
            domain = 'DEFAULT'
            compartment_id = 'root'
        if ct.identity_domain_enabled and domain.lower() != 'nan':
            domain = str(domain).strip()
            split_domain = domain.split('@', 1)
            if len(split_domain) == 2:
                compartmentVarName, domain = split_domain
                if compartmentVarName.lower() == 'root' or compartmentVarName == '':
                    compartment_id = 'root'
                else:
                    if compartmentVarName.startswith('root::'):
                        compartmentVarName = compartmentVarName[len('root::'):]
                    compartment_id = compartmentVarName.strip()
                    compartment_id = commonTools.check_tf_variable(compartment_id)
                    compartment_id = str(compartment_id)
                if domain.lower() == 'default':
                    domain = 'DEFAULT'
            else:
                domain = domain
                compartment_id = 'root'

        for columnname in dfcolumns:
            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df[columnname][i]).strip()

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Name':
                group_tf_name = f"{domain}_{commonTools.check_tf_variable(columnvalue)}"
                if group_tf_name.startswith('_'):
                    group_tf_name = group_tf_name[1:]
                tempdict = {'group_tf_name': group_tf_name,'domain': domain , 'compartment_id': compartment_id}

            if columnname == 'Members':
                members=''
                if columnvalue.lower()!='nan' and columnvalue!='':
                    members=[x.strip() for x in columnvalue.split(',')]
                    members = ','.join(members)
                tempdict = {'members': members}

            # Process Defined and Freeform Tags based on columnname and 'Domain Name'
            if columnname.lower() in commonTools.tagColumns:
                # for IDCS tenancies
                if not ct.identity_domain_enabled:
                    # Process tags using the existing code
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                else:
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
        tfStr[region]= tfStr[region].rsplit('}',1)[0] + selected_template.render(tempStr)

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
        print(outfile[reg] + " for Groups has been created for region "+reg)


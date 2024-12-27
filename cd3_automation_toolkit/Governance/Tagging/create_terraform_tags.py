#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Tags
#
# Author: Shruthi Subramanian
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import pandas as pd
import os
from pathlib import Path
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######
# Execution of the code begins here
def create_terraform_tags(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile

    sheetName = "Tags"
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    namespace = env.get_template('tags-namespaces-template')
    tagkey = env.get_template('tags-keys-template')
    defaulttag = env.get_template('tags-defaults-template')
    namespaces_auto_tfvars_filename = "_" + sheetName.lower() + "-namespaces.auto.tfvars"
    tagkey_auto_tfvars_filename = "_" + sheetName.lower() + "-keys.auto.tfvars"
    default_tags_auto_tfvars_filename = "_" + sheetName.lower() + "-defaults.auto.tfvars"

    tagnamespace_list = {}
    defaulttagtemp = {}
    namespacetemp = {}
    tagkeytemp = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    # Take backup of files
    #for reg in ct.all_regions:
    reg = ct.home_region
    resource = sheetName.lower()
    srcdir = outdir + "/" + reg + "/" + service_dir + "/"
    commonTools.backup_file(srcdir, resource, namespaces_auto_tfvars_filename)
    commonTools.backup_file(srcdir, resource, tagkey_auto_tfvars_filename)
    commonTools.backup_file(srcdir, resource, default_tags_auto_tfvars_filename)

    tagnamespace_list[reg] = []
    defaulttagtemp[reg] = ''
    namespacetemp[reg] = ''
    tagkeytemp[reg] = ''

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}
    default_tags = []
    key_tf_name=''


    #fill the empty values with that in previous row.
    dffill = df[['Region','Compartment Name','Tag Namespace']]
    dffill= dffill.fillna(method='ffill')

    dfdrop = df[['Region','Compartment Name','Tag Namespace']]
    dfdrop = df.drop(dfdrop,axis=1)

    df = pd.concat([dffill, dfdrop], axis=1)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        region = region.strip().lower()

        regions = df['Region']
        check_diff_region = []
        values_list = ''
        namespace_tf_name = ''

        # Get a list of unique region names
        for j in regions.index:
            if (regions[j] not in check_diff_region and regions[j] not in commonTools.endNames and str(regions[j]).lower() != "nan"):
                check_diff_region.append(regions[j])

        # If some invalid region is specified in a row
        if region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)

        if str(df.loc[i,'Default Tag Compartment=Default Tag Value']).strip().lower() != 'nan' and str(df.loc[i,'Tag Keys']).strip().lower() == 'nan':
            print("\nERROR!!! Tag Keys cannot be null when there is a Default Tag Compartment...Exiting!")
            exit(1)

        if str(df.loc[i,'Cost Tracking']).strip().lower() == 'true' and str(df.loc[i,'Tag Keys']).strip().lower() == 'nan':
            print("\nERROR!!! Tag Keys cannot be null when Cost Tracking is set to TRUE...Exiting!")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
            else:
                columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values Do for columns other than Validator
            if columnname == 'Validator':
                if (columnvalue.lower() == 'nan'):
                    columnvalue = ""
            else:
                columnvalue = commonTools.check_columnvalue(columnvalue)

            if "::" in columnvalue:
                if columnname != "Compartment Name" and columnname != 'Validator' and columnname != 'Default Tag Compartment':
                    # Check for multivalued columns
                    tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Compartment Name":
                columnvalue = str(columnvalue).strip()
                compartmentVarName = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartmentVarName}

            if columnname == 'Tag Namespace':
                columnvalue = str(columnvalue).strip()
                if ' ' in columnvalue or '.' in columnvalue:
                    print("\nSpaces and Periods are not allowed in Tag Namespaces. Please correct the value at row "+str(i+3)+" and run again....Exiting!!")
                    exit(1)
                namespace_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'namespace_tf_name':namespace_tf_name}

            if columnname == 'Namespace Description':
                description = str(columnvalue)
                if columnvalue == '':
                    description = "Create Tag Namespace - " + namespace_tf_name
                tempdict = {'description' : description}

            if columnname == 'Tag Keys':
                columnvalue = str(columnvalue).strip()
                tag_keys = columnvalue
                if ' ' in tag_keys or '.' in tag_keys:
                    print("\nSpaces and Periods are not allowed in Tag Keys. Please correct the value at row "+str(i+3)+" and run again....Exiting!!")
                    exit(1)
                if columnvalue != '':
                    key_tf_name = commonTools.check_tf_variable(columnvalue)
                    key_tf_name = namespace_tf_name +"_"+key_tf_name
                    tempdict = {'key_tf_name':key_tf_name}

            if columnname == 'Tag Description':
                description_keys = str(columnvalue)
                if columnvalue == '':
                    description_keys =  "Create Tag Key "+key_tf_name+" for Namespace - "+namespace_tf_name
                tempdict = {'description_keys' : description_keys.replace('$','$$')}

            if columnname == 'Cost Tracking':
                if str(columnvalue).lower().strip() != 'true':
                    columnvalue = "false"

            if columnname == 'Validator':
                if str(columnvalue).strip() != '' and str(columnvalue).strip().lower() != 'nan':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip().replace('$','$$') if part and '$' in part else str(part).strip() for part in multivalues ]
                    tempdict = {columnname: multivalues}

                    values_list = multivalues[1].split(',')
                    values_list = [values[1:-1].strip().replace("\"",'') for values in values_list]

            if columnname == 'Default Tag Compartment=Default Tag Value':
                default_value = ''
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    columnvalue = columnvalue.split(";")
                    for values in columnvalue:
                        values = values.split("=")
                        if values != '' and values != [''] :
                            default_compartment = commonTools.check_tf_variable(values[0]).strip()
                            try:
                                if values[1] and values[1] != "" and str(values[1]).lower() != 'nan':
                                    default_value = values[1]
                                else:
                                    default_value = ""
                            except IndexError as e:
                                if "list index out of range" in str(e):
                                    default_value = ""

                            if values_list and values_list != []:
                                if '$' not in str(default_value):
                                    if str(default_value) not in values_list and str(default_value) != "nan" and str(default_value) != "":
                                        print("\nERROR!! Value - "+str(default_value)+" in Default Tag Value is not present in Column Validator...Exiting!")
                                        exit(1)
                                else:
                                    if '$'+str(default_value) not in values_list:
                                        print("\nERROR!! Value - "+str(default_value)+" in Default Tag Value is not present in Column Validator...Exiting!")
                                        exit(1)

                            if default_value != "" and str(default_value).lower() != "nan":
                                if '$' in default_value and default_value.count('$') == 1:
                                    default_value = str(default_value).strip().replace('$','$$')
                                is_required = 'false' #Uncomment this line if needed
                                columnvalue = key_tf_name+"="+default_compartment+"="+default_value+"="+is_required #Uncomment this if needed
                                if columnvalue not in default_tags:
                                    default_tags.append(columnvalue)
                            else:
                                if default_value == '' or default_value.strip().lower() == 'nan':
                                    if str(df.loc[i,'Validator']).strip() != '' and  str(df.loc[i,'Validator']).strip().lower() != 'nan' and str(df.loc[i,'Validator']).strip() != []:
                                        is_required_updated = 'true' #Uncomment this if needed
                                        default_value = values_list[0]
                                        columnvalue = key_tf_name+"="+default_compartment+"="+default_value+"="+is_required_updated #Uncomment this if needed
                                        if columnvalue not in default_tags:
                                            default_tags.append(columnvalue)
                                    else:
                                        if str(df.loc[i, 'Validator']).strip() == '' or  str(df.loc[i, 'Validator']).strip().lower() == 'nan':
                                            is_required_updated = 'true' #Uncomment this if needed
                                            default_value = '[CANNOT_BE_EMPTY]'
                                            columnvalue = key_tf_name+"="+default_compartment+"="+default_value+"="+is_required_updated #Uncomment this if needed
                                            if columnvalue not in default_tags:
                                                default_tags.append(columnvalue)

                tempdict = {'default_tags': default_tags}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if str(df.loc[i,'Default Tag Compartment=Default Tag Value']).strip() != '' and str(df.loc[i,'Default Tag Compartment=Default Tag Value']).lower().strip() != 'nan':
            defaulttagtemp[region] = defaulttag.render(tempStr)

        if namespace_tf_name not in tagnamespace_list[region]:
            namespacetemp[region] = namespacetemp[region]+ namespace.render(tempStr)
            tagnamespace_list[region].append(namespace_tf_name)

        # Write all info to TF string; Render template
        if tag_keys != "":
            tagkeytemp[region] = tagkeytemp[region] + tagkey.render(tempStr)

    # Write TF string to the file in respective region directory
    #for reg in ct.all_regions:

    if defaulttagtemp[reg] != '':

        defaulttagtemp[reg] = defaulttag.render(tempStr, count = 0).replace("##Add New Tag Defaults for "+reg.lower()+" here##", defaulttagtemp[reg]+"\n"+"##Add New Tag Defaults for "+reg.lower()+" here##")
        defaulttagtemp[reg] = "".join([s for s in defaulttagtemp[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + default_tags_auto_tfvars_filename
        oname = open(outfile, "w+")
        print("Writing to "+outfile)
        oname.write(defaulttagtemp[reg])
        oname.close()

    if namespacetemp[reg] != '':

        namespacetemp[reg] = namespace.render(tempStr, count = 0).replace("##Add New Tag Namespaces for "+reg.lower()+" here##", namespacetemp[reg]+"\n"+"##Add New Tag Namespaces for "+reg.lower()+" here##")
        namespacetemp[reg] = "".join([s for s in namespacetemp[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + namespaces_auto_tfvars_filename
        oname = open(outfile, "w+")
        print("Writing to "+outfile)
        oname.write(namespacetemp[reg])
        oname.close()

    if tagkeytemp[reg] != '':

        tagkeytemp[reg] = tagkey.render(tempStr, count = 0).replace("##Add New Tag Keys for "+reg.lower()+" here##", tagkeytemp[reg]+"\n"+"##Add New Tag Keys for "+reg.lower()+" here##")
        tagkeytemp[reg] = "".join([s for s in tagkeytemp[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + tagkey_auto_tfvars_filename
        oname = open(outfile, "w+")
        print("Writing to "+outfile)
        oname.write(tagkeytemp[reg])
        oname.close()


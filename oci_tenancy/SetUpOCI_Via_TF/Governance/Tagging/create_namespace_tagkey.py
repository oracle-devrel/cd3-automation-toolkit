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
import argparse
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######

# If input in cd3 file
def main():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Create vars files for the each row in csv file.")
    parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.file
    outdir = args.outdir
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    namespace = env.get_template('namespace-template')
    tagkey = env.get_template('key-template')
    defaulttag = env.get_template('default-tag-template')

    tagnamespace_list = {}
    defaulttagtemp = {}
    namespacetemp = {}
    tagkeytemp = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Tags")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    unique_region = df['Region'].unique()

    # Take backup of files
    for eachregion in unique_region:
        eachregion = str(eachregion).strip().lower()

        if eachregion in commonTools.endNames:
            continue
        if eachregion == 'nan':
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        resource='Tagging'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-tagging.tf")

    for reg in ct.all_regions:
        tagnamespace_list[reg] = []
        defaulttagtemp[reg] = ''
        namespacetemp[reg] = ''
        tagkeytemp[reg] = ''

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}

    namespace_tf_name=''
    key_tf_name=''
    description_keys=''

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

        # Get a list of unique region names
        for j in regions.index:
            if (regions[j] not in check_diff_region and regions[j] not in commonTools.endNames and str(regions[j]).lower() != "nan"):
                check_diff_region.append(regions[j])

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
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
                if (columnvalue.lower() == 'root'):
                    compartmentVarName="tenancy_ocid"
                else:
                    compartmentVarName = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartmentVarName}

            if columnname == 'Tag Namespace':
                columnvalue = str(columnvalue).strip()
                namespace_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'namespace_tf_name':namespace_tf_name}

            if columnname == 'Namespace Description':
                description = str(columnvalue).strip()
                if columnvalue == '':
                    description = "Create Tag Namespace - " + namespace_tf_name
                tempdict = {'description' : description}

            if columnname == 'Tag Keys':
                columnvalue = str(columnvalue).strip()
                tag_keys = columnvalue
                if columnvalue != '':
                    key_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'description_keys':description_keys,'key_tf_name':key_tf_name}

            if columnname == 'Tag Description':
                description_keys = str(columnvalue).strip()
                if columnvalue == '':
                    description_keys =  "Create Tag Key "+key_tf_name+" for Namespace - "+namespace_tf_name
                tempdict = {'description_keys' : description_keys}

            if columnname == 'Cost Tracking':
                if str(columnvalue).lower().strip() != 'true':
                    columnvalue = "false"

            if columnname == 'Default Tag Compartment':
                columnvalue = str(columnvalue).strip()
                if columnvalue != '':
                    columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == 'Validator':
                if str(columnvalue).strip() != '':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

                    values_list = multivalues[1].replace('"','').split(',')
                    if str(df.loc[i,'Default Tag Compartment']).strip() != '' and str(df.loc[i,'Default Tag Compartment']).lower().strip() != 'nan':
                        if str(df.loc[i, 'Default Tag Value']) not in values_list and str(df.loc[i, 'Default Tag Value']).strip() != '' and str(df.loc[i, 'Default Tag Value']).strip().lower() != 'nan':
                            print("\nERROR!! Value - "+str(df.loc[i, 'Default Tag Value'])+" in Default Tag Value is not present in Column Validator...Exiting!")
                            exit()


            if columnname == 'Default Tag Value':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    is_required = 'false'
                    if '$' in columnvalue and columnvalue.count('$') == 1:
                        columnvalue = '$'+columnvalue
                    tempdict = {'is_required' : is_required}

                else:
                    if columnvalue == '' or columnvalue.strip().lower() == 'nan':
                        if str(df.loc[i,'Default Tag Compartment']).strip() != '' and str(df.loc[i,'Default Tag Compartment']).lower().strip() != 'nan':
                            if str(df.loc[i,'Validator']).strip() != '' and  str(df.loc[i,'Validator']).strip().lower() != 'nan':
                                is_required = 'true'
                                columnvalue = values_list[0]
                                tempdict = {'is_required': is_required}

                            else:
                                if str(df.loc[i, 'Validator']).strip() == '' or  str(df.loc[i, 'Validator']).strip().lower() == 'nan':
                                    is_required = 'true'
                                    columnvalue = '-'
                                    tempdict = {'is_required': is_required}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if str(df.loc[i,'Default Tag Compartment']).strip() != '' and str(df.loc[i,'Default Tag Compartment']).lower().strip() != 'nan':
            defaulttagtemp[region] = defaulttagtemp[region] + defaulttag.render(tempStr)

        if namespace_tf_name not in tagnamespace_list[region]:
            namespacetemp[region] = namespacetemp[region]+ namespace.render(tempStr)
            tagnamespace_list[region].append(namespace_tf_name)

        # Write all info to TF string; Render template
        if tag_keys != "":
            tagkeytemp[region] = tagkeytemp[region] + tagkey.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:

        if defaulttagtemp[reg] != '':

            outfile = outdir + "/" + reg + "/default-tags-tagging.tf"
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(defaulttagtemp[reg])
            oname.close()

        if namespacetemp[reg] != '':

            outfile = outdir + "/" + reg + "/namespaces-tagging.tf"
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(namespacetemp[reg])
            oname.close()

        if tagkeytemp[reg] != '':

            outfile = outdir + "/" + reg + "/tag-keys-tagging.tf"
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(tagkeytemp[reg])
            oname.close()

if __name__ == '__main__':

    # Execution of the code begins here
    main()
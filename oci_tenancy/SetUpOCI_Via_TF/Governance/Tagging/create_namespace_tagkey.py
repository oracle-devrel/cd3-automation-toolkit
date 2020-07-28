#!/usr/bin/python3
# Author: Shruthi Subramanian
# Create Tag Namespace, Default Tags and TagKeys from CD3 file

import sys
import argparse
import pandas as pd
import datetime
import os
from os import path
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


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
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

x = datetime.datetime.now()
date = x.strftime("%f").strip()

# Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
namespace = env.get_template('namespace-template')
tagkey = env.get_template('key-template')
defaulttag = env.get_template('default-tag-template')

tagnamespace_list={}
defaulttagtemp={}
namespacetemp={}
tagkeytemp={}

# Creates the namespaces
if ('.xlsx' in filename):

    df = pd.read_excel(filename, sheet_name='Tags', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    reg = str(df['Region'].unique())

    for reg in ct.all_regions:
        if reg not in commonTools.endNames and  reg != 'nan':
            tagnamespace_list[reg] = []
            defaulttagtemp[reg] = ''
            namespacetemp[reg] = ''
            tagkeytemp[reg] = ''

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}

    tmpstr=''
    namespace_tf_name=''
    key_tf_name=''
    description=''
    description_keys=''
    region=''
    values_list=[]

    #fill the empty values with that in previous row.
    dffill = df[['Region','Compartment Name','Tag Namespace','Namespace Description']]
    dffill= dffill.fillna(method='ffill')

    dfdrop = df[['Region','Compartment Name','Tag Namespace','Namespace Description']]
    dfdrop = df.drop(dfdrop,axis=1)

    pd.set_option('display.max_columns', 500)

    df = pd.concat([dffill, dfdrop], axis=1)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        region = region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions and region != 'nan':
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if str(df.loc[i, 'Default Tag']) == "1.0" or str(df.loc[i, 'Default Tag']) == "true":
            if str(df.loc[i,'Default Tag Value']) == 'nan':
                print("ERROR!! Default Tag Value cannot be left empty when Default Tag is set to TRUE...Exiting!")
                exit()

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            if (columnvalue.lower() == 'nan'):
                columnvalue = ""

            if columnvalue == '1.0' or  columnvalue == '0.0':
                if columnname != 'Cost Tracking' or columnname != 'Default Tag' :
                    if columnvalue == '1.0':
                        columnvalue = "true"
                    else:
                        columnvalue = "false"

            if "::" in columnvalue:
                if columnname != "Compartment Name" and columnname != 'Validator':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Compartment Name":
                columnvalue = str(columnvalue).strip()
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
                key_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'description_keys':description_keys,'key_tf_name':key_tf_name}

            if columnname == 'Tag Descriptopn':
                description_keys = str(columnvalue).strip()
                if columnvalue == '':
                    description_keys =  "Create Tag Key "+key_tf_name+" for Namespace - "+namespace_tf_name
                tempdict = {'description_keys' : description_keys}

            if columnname == 'Cost Tracking':
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

            if columnname == 'Validator':
                if str(columnvalue).strip() != '':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

                    values_list = multivalues[1].replace('"','').split(',')
                    if str(df.loc[i,'Default Tag']).lower().strip() == '1.0' or str(df.loc[i,'Default Tag']).lower().strip() == 'true':
                        if str(df.loc[i, 'Default Tag Value']) not in values_list:
                            print("ERROR!! Value - "+str(df.loc[i, 'Default Tag Value'])+" in Default Tag Value is not present in Column Validator...Exiting!")
                            exit()

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if str(df.loc[i,'Default Tag']).lower().strip() == '1.0' or str(df.loc[i,'Default Tag']).lower().strip() == 'true':
            defaulttagtemp[region] = defaulttagtemp[region] + defaulttag.render(tempStr)

        if namespace_tf_name not in tagnamespace_list[region]:
            namespacetemp[region] = namespacetemp[region]+ namespace.render(tempStr)
            tagnamespace_list[region].append(namespace_tf_name)

        tagkeytemp[region] = tagkeytemp[region] + tagkey.render(tempStr)


for reg in ct.all_regions:

    namespace_src = outdir + "/" + reg + "/namespaces.tf"
    if path.exists(namespace_src):
        namespace_dst = outdir + "/" + reg + "/namespaces_backup" + date
        os.rename(namespace_src, namespace_dst)

    defaulttags_src = outdir + "/" + reg + "/default-tags.tf"
    if path.exists(defaulttags_src):
        defaulttag_dst = outdir + "/" + reg + "/default-tags_backup" + date
        os.replace(defaulttags_src, defaulttag_dst)

    keys_src = outdir + "/" + reg + "/tagkeys.tf"
    if path.exists(keys_src):
        key_dst = outdir + "/" + reg + "/tagkeys_backup" + date
        os.replace(keys_src, key_dst)

    if defaulttagtemp[reg] != '':

        outfile = outdir + "/" + reg + "/default-tags.tf"
        oname = open(outfile, "w+")
        print("Writing to ..."+outfile)
        oname.write(defaulttagtemp[reg])
        oname.close()

    if namespacetemp[reg] != '':

        outfile = outdir + "/" + reg + "/namespaces.tf"
        oname = open(outfile, "w+")
        print("Writing to ..."+outfile)
        oname.write(namespacetemp[reg])
        oname.close()

    if tagkeytemp[reg] != '':

        outfile = outdir + "/" + reg + "/tagkeys.tf"
        oname = open(outfile, "w+")
        print("Writing to ..."+outfile)
        oname.write(tagkeytemp[reg])
        oname.close()
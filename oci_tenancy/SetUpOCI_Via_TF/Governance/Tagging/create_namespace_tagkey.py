#!/usr/bin/python3
# Author: Shruthi Subramanian
# Create Tag Namespace and TagKeys from CD3 file
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
namespacetemplate = env.get_template('namespace-template')
tagkeytemplate = env.get_template('key-template')

tagnamespace_list={}

# Creates the namespaces
if ('.xlsx' in filename):
    for reg in ct.all_regions:
        tagnamespace_list[reg] = []
        namespace_src=outdir + "/"+reg+"/namespaces.tf"
        if path.exists(namespace_src):
            namespace_dst = outdir + "/"+reg+ "/namespaces_backup" + date
            os.rename(namespace_src, namespace_dst)
        keys_src=outdir + "/"+reg+"/tagkeys.tf"
        if path.exists(keys_src):
            key_dst = outdir + "/"+reg+"/tagkeys_backup" + date
            os.rename(keys_src, key_dst)

    df = pd.read_excel(filename, sheet_name='Tags', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}

    tmpstr=''
    namespace_tf_name=''
    key_tf_name=''
    description=''
    description_keys=''
    namespace=''
    region=''
    tagkeytemp=''

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

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            if columnvalue == '1.0' or  columnvalue == '0.0':
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

            if (columnvalue.lower() == 'nan'):
                columnvalue = ""

            if "::" in columnvalue:
                if columnname != "Compartment Name":
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


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if namespace_tf_name not in tagnamespace_list[region]:
            namespace = namespacetemplate.render(tempStr)

            outfile = outdir + "/" + region + "/namespaces.tf"
            oname = open(outfile, "a+")
            oname.write(namespace)
            oname.close()
            tagnamespace_list[region].append(namespace_tf_name)


        tagkeytemp = tagkeytemplate.render(tempStr)
        outfile = outdir + "/" + region + "/tagkeys.tf"
        oname = open(outfile, "a+")
        oname.write(tagkeytemp)
        oname.close()

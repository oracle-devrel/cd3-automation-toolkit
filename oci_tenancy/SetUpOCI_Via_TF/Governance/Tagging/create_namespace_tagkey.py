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

# Creates the namespaces
if ('.xlsx' in filename):
    for reg in ct.all_regions:
        namespace_src=outdir + "/"+reg+"/tagnamespaces.tf"
        if path.exists(namespace_src):
            namespace_dst = outdir + "/"+reg+ "/tagnamespaces_backup" + date
            os.rename(namespace_src, namespace_dst)
        keys_src=outdir + "/"+reg+"/tagkeys.tf"
        if path.exists(keys_src):
            key_dst = outdir + "/"+reg+"/tagkeys_backup" + date
            os.rename(keys_src, key_dst)

    df = pd.read_excel(filename, sheet_name='Tags', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for i in df.keys():
        if (i == 'compartment_name'):
            for j in df.index:
                if (str(df[i][j]) == 'nan'):
                    continue
                else:
                    compartment_var_name = df[i][j]
                    continue
        if (i == 'TagNamespace'):
            continue
        elif (i == 'compartment_name'):
            continue
        elif (i == 'Region'):
            for j in df.index:
                if (str(df[i][j]) == 'nan'):
                    continue
                else:
                    Region = df[i][j].strip().lower()
                    if(Region in commonTools.endNames):
                        exit()
                    if(Region not in ct.all_regions):
                        print("Invalid region "+Region)
                        break

        else:
            tagnamespace = i
            tagnamespace_tf=commonTools.check_tf_variable(tagnamespace)
            compartment_var_name_tf=commonTools.check_tf_variable(compartment_var_name)
            tmpstr = """
            resource "oci_identity_tag_namespace" \"""" + tagnamespace_tf + """\" {
                #Required
                compartment_id = "${var.""" + compartment_var_name_tf + """}"
                description = "Create Tag Namespace for """ + tagnamespace + """\"
                name = \"""" + tagnamespace + """\"
                is_retired = false
            }
            """

            outfile = outdir + "/" + Region + "/tagnamespaces.tf"
            oname = open(outfile, "a+")
            oname.write(tmpstr)
            oname.close()

# Adds the tag to the namespaces created
if ('.xlsx' in filename):
    df = pd.read_excel(filename, sheet_name='Tags', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    for i in df.keys():

        if (i == 'Region'):
            for j in df.index:
                if (str(df[i][j]) == 'nan'):
                    continue
                else:
                    Region = df[i][j].strip().lower()

        elif (i == 'compartment_name'):
            continue
        else:
            key = i

            for j in df.index:
                if (str(df[i][j]) == 'nan'):
                    continue
                else:

                    tagkey = df[i][j]

                    if (tagkey == 'Keys') and (key == 'TagNamespace'):
                        continue
                    else:
                        key_tf = commonTools.check_tf_variable(key)
                        tagkey_tf = commonTools.check_tf_variable(tagkey)
                        tmpstr = """
                        resource "oci_identity_tag" \"""" + tagkey_tf + """\" {
                        #Required
                        description = "Creating """ + tagkey + """ in Namespace """ + key + """\"
                        name = \"""" + tagkey + """\"
                        tag_namespace_id = \"${oci_identity_tag_namespace.""" + key_tf + """.id}\"
                        is_retired = false
                    }
                    """
                    outfile = outdir + "/" + Region + "/tagkeys.tf"
                    oname = open(outfile, "a+")
                    oname.write(tmpstr)
                    oname.close()


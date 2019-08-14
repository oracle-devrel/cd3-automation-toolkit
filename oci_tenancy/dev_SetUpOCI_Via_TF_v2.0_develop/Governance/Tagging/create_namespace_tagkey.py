#!/bin/bash
# Author: Shruthi Subramanian
# Create Tag Namespace and TagKeys from CD3 file
import sys
import argparse
import pandas as pd
import datetime
import os
from os import path
import glob


parser = argparse.ArgumentParser(description="Create vars files for the each row in csv file.")
parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir

x = datetime.datetime.now()
date = x.strftime("%f").strip()

# Creates the namespaces
if ('.xlsx' in filename):
    df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    for reg in all_regions:
        namespace_src=outdir + "/"+reg+"/tagnamespaces.tf"
        if path.exists(namespace_src):
            namespace_dst = outdir + "/"+reg+ "/tagnamespaces_backup" + date
            os.rename(namespace_src, namespace_dst)
        keys_src=outdir + "/"+reg+"/tagkeys.tf"
        if path.exists(keys_src):
            key_dst = outdir + "/"+reg+"/tagkeys_backup" + date
            os.rename(keys_src, key_dst)

    df = pd.read_excel(filename, sheet_name='Tags', skiprows=1)
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

        else:
            tagnamespace = i
            tmpstr = """
            resource "oci_identity_tag_namespace" \"""" + tagnamespace + """\" {
                #Required
                compartment_id = "${var.""" + compartment_var_name + """}"
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
    df1 = pd.read_excel(filename, sheet_name='Tags', skiprows=1)
    df = df1.dropna(how='all')
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
                        tmpstr = """

                        resource "oci_identity_tag" \"""" + tagkey + """\" {
                        #Required
                        description = "Creating """ + tagkey + """ in Namespace """ + key + """\"
                        name = \"""" + tagkey + """\"
                        tag_namespace_id = \"${oci_identity_tag_namespace.""" + key + """.id}\"
                        is_retired = false
                    }
                    """
                    outfile = outdir + "/" + Region + "/tagkeys.tf"
                    oname = open(outfile, "a+")
                    oname.write(tmpstr)
                    oname.close()


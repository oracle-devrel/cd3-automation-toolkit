#!/bin/bash
# Author: Shruthi Subramanian
# Create Tag Namespace and TagKeys from CD3 file
import sys
import argparse
import pandas as pd
import datetime
import os
from os import path


x = datetime.datetime.now()
date = x.strftime("%f").strip()

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


src = outdir+'/tag.tf'
if path.exists(src):
    dst = outdir+'/tag_backup'+date
    os.rename(src, dst)


src1 = outdir+'/tagkeys.tf'
if path.exists(src1):
    dst1 = outdir+'/tagkeys_backup'+date
    os.rename(src1, dst1)

# Creates the namespaces
if ('.xlsx' in filename):
    df = pd.read_excel(filename, sheet_name='Tags')
    print (df.keys())
    for i in df.keys():
        if (i == 'TagNamespace'):
            continue;
        else:
            print i
            tagnamespace = i
            tmpstr = """
            resource "oci_identity_tag_namespace" \""""+tagnamespace+"""\" {
                #Required
                compartment_id = "${var.tenancy_ocid}"
                description = "Create Tag Namespace for """+tagnamespace+"""\"
                name = \""""+tagnamespace+"""\"
                is_retired = false
            }
            """
            outfile = outdir +"/tag.tf"
            oname = open(outfile, "a+")
            oname.write(tmpstr)
            oname.close()

# Adds the tag to the namespaces created
if ('.xlsx' in filename):
    df1 = pd.read_excel(filename, sheet_name='Tags')
    df = df1.dropna(how='all')
    print df
    for i in df.keys():
        print ("\n")
        print i
        key = i

        print "----------------------"
        for j in df.index:
            if (str(df[i][j]) == 'nan'):
                continue
            else:
                print df[i][j]
                tagkey = df[i][j]

                tmpstr = """

                resource "oci_identity_tag" \"""" + tagkey + """\" {
                #Required
                description = "Creating """ + tagkey + """ in Namespace """ + key + """\"
                name = \"""" + tagkey + """\"
                tag_namespace_id = \"""" + key + """\"
                is_retired = false
            }
            """
            outfile = outdir + "/tagkeys.tf"
            oname = open(outfile, "a+")
            oname.write(tmpstr)
            oname.close()


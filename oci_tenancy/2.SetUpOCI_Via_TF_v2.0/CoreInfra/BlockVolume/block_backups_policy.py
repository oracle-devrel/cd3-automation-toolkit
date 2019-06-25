#!/bin/bash
# Author: Shruthi Subramanian
#shruthi.subramanian@oracle.com
import sys
import argparse
import pandas as pd
import os
import datetime
from os import path

x = datetime.datetime.now()
date = x.strftime("%f").strip()

parser = argparse.ArgumentParser(description="Atatches back up policy to Block Volumes")
parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf file ")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir

tmpstr="""
data "oci_core_volume_backup_policies" "block_gold" {
	filter {
		name = "display_name"
		values = [ "gold" ]
		}
}

data "oci_core_volume_backup_policies" "block_silver" {
	filter {
		name = "display_name"
		values = [ "silver" ]
		}
}

data "oci_core_volume_backup_policies" "block_bronze" {
	filter {
		name = "display_name"
		values = [ "bronze" ]
		}
}

## Add policy attachment ##
"""
outfile = outdir + "/attach_block_backups_policy.tf"
src = outfile

if path.exists(src):
    dst = outdir + '/attach_block_backups_policy_backup' + date
    os.rename(src, dst)


oname = open(outfile, "a+")
oname.write(tmpstr)
oname.close()

if ('.xlsx' in filename):
    df = pd.read_excel(filename, sheet_name='BlockVols')
    for i in df.index:
        for j in df.keys():
            if (str(df[j][i]) == 'nan'):
                continue
            else:
                block_name = df['block_name'][i]
                policy = df['Backup Policy'][i].lower().strip()

        res_name=block_name+"_bkupPolicy"
        tmpstr = """resource "oci_core_volume_backup_policy_assignment" \"""" + res_name + """\"{
        #Required
        asset_id = "${oci_core_volume.""" + block_name + """.id}"
        policy_id = "${data.oci_core_volume_backup_policies.block_""" + policy + """.volume_backup_policies.0.id}"
}
## Add policy attachment ##
    """

        testToSearch = "## Add policy attachment ##"

        with open(outfile, 'r+') as file:
            filedata = file.read()
        file.close()
        # Replace the target string
        filedata = filedata.replace(testToSearch, tmpstr)

        # Write the file out again
        with open(outfile, 'w+') as file:
            file.write(filedata)
        file.close()

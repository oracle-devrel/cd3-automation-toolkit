#!/usr/bin/python3
# Author: Shruthi Subramanian
#shruthi.subramanian@oracle.com
import sys
import argparse
import pandas as pd
import os
import datetime
from os import path
sys.path.append(os.getcwd()+"/../..")
from commonTools import *


x = datetime.datetime.now()
date = x.strftime("%S").strip()

parser = argparse.ArgumentParser(description="Attaches back up policy to Boot Volumes")
parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf file ")
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

tmpstr = """
data "oci_core_volume_backup_policies" "gold" {
	filter {
		name = "display_name"
		values = [ "gold" ]
		}
}

data "oci_core_volume_backup_policies" "silver" {
	filter {
		name = "display_name"
		values = [ "silver" ]
		}
}

data "oci_core_volume_backup_policies" "bronze" {
	filter {
		name = "display_name"
		values = [ "bronze" ]
		}
}

## Add policy attachment ##
"""
first_tmpstr = tmpstr
policy_file={}
endnames= ['<end>','<END>','<End>']

# If the input is CD3
if ('.xls' in filename):

    for reg in ct.all_regions:
        policy_file[reg] = outdir + "/" + reg + "/attach_boot_backups_policy.tf"
        src = policy_file[reg]
        if path.exists(src):
            dst = outdir + "/" + reg + "/attach_boot_backups_policy_backup" + date
            os.rename(src, dst)
        fname = open(policy_file[reg], "a+")
        fname.write(tmpstr)
        fname.close()

    df = pd.read_excel(filename, sheet_name='Instances',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for i in df.index:
        for j in df.keys():
            if (str(df[j][i]) in endnames):
                exit()
            if (str(df[j][i]) == 'nan'):
                continue

            elif (j == 'Region'):
                Region = df['Region'][i].strip().lower()
                if (Region in commonTools.endNames):
                    exit()

                if(Region not in ct.all_regions):
                    print("Invalid Region "+ Region)
                    break

            elif (j == 'Hostname'):
                Host_name = df['Hostname'][i]
                if (str(df['Backup Policy'][i]) == 'nan'):
                    continue
                else:
                    policy = df['Backup Policy'][i].lower().strip()
                    res_name = Host_name + "_bkupPolicy"
                    tmpstr = """resource "oci_core_volume_backup_policy_assignment" \"""" + res_name + """\"{
                                #Required
                                asset_id = "${oci_core_instance.""" + Host_name + """.boot_volume_id}"
                                policy_id = "${data.oci_core_volume_backup_policies.""" + policy + """.volume_backup_policies.0.id}"
                        }
                        ## Add policy attachment ##
                            """

                    textToSearch = "## Add policy attachment ##"

                    with open(policy_file[Region], 'r+') as file:
                        filedata = file.read()
                    file.close()
                    # Replace the target string
                    filedata = filedata.replace(textToSearch, tmpstr)

                    # Write the file out again
                    with open(policy_file[Region], 'w+') as file:
                        file.write(filedata)
                    file.close()

elif('.csv' in filename):
    fname = open(filename, "r")
    all_regions = os.listdir(outdir)
    for reg in all_regions:
        policy_file[reg] = outdir + "/" + reg + "/attach_boot_backups_policy.tf"
        src = policy_file[reg]
        if path.exists(src):
            dst = outdir + "/" + reg + "/attach_boot_backups_policy_backup" + date
            os.rename(src, dst)
        fname = open(policy_file[reg], "a+")
        fname.write(tmpstr)
        fname.close()

    for line in fname:
        if not line.startswith('#'):
            linearr = line.split(",")
            region = linearr[0].strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                continue

            Hostname = linearr[1].strip()
            res_name = Hostname + "_bkupPolicy"
            policy = linearr[11].strip()

            tmpstr = """resource "oci_core_volume_backup_policy_assignment" \"""" + res_name + """\"{
                                        #Required
                                        asset_id = "${oci_core_instance.""" + Hostname + """.boot_volume_id}"
                                        policy_id = "${data.oci_core_volume_backup_policies.""" + policy + """.volume_backup_policies.0.id}"
                                }
                                ## Add policy attachment ##
                                    """

            textToSearch = "## Add policy attachment ##"

            with open(policy_file[region], 'r+') as file:
                filedata = file.read()
            file.close()
            # Replace the target string
            filedata = filedata.replace(textToSearch, tmpstr)

            # Write the file out again
            with open(policy_file[region], 'w+') as file:
                file.write(filedata)
            file.close()

    fname.close()
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx")
    exit()

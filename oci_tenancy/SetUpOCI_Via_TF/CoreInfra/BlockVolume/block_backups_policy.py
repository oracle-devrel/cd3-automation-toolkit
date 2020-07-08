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

parser = argparse.ArgumentParser(description="Attaches back up policy to Block Volumes")
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
first_tmpstr = tmpstr
policy_file={}
endnames= ['<end>','<END>','<End>']

if ('.xls' in filename):

    for reg in ct.all_regions:
        policy_file[reg] = outdir + "/"+reg+"/attach_block_backups_policy.tf"
        src=policy_file[reg]
        if path.exists(src):
            dst = outdir + "/"+reg+"/attach_block_backups_policy_backup" + date
            os.rename(src, dst)
        fname=open(policy_file[reg],"a+")
        fname.write(tmpstr)
        fname.close()

    df = pd.read_excel(filename, sheet_name='BlockVols',skiprows=1)
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
                if(Region in commonTools.endNames):
                    exit()
                if(Region not in ct.all_regions):
                    print("Invalid Region "+ Region)
                    break


            elif (j == 'block_name'):
                block_name = df['block_name'][i]
                if (str(df['Backup Policy'][i]) == 'nan'):
                    continue
                else:

                    policy = df['Backup Policy'][i].lower().strip()

                    block_name_tf=commonTools.check_tf_variable(block_name)
                    res_name=block_name_tf+"_bkupPolicy"
                    tmpstr = """resource "oci_core_volume_backup_policy_assignment" \"""" + res_name + """\"{
                        #Required
                        asset_id = "${oci_core_volume.""" + block_name_tf + """.id}"
                        policy_id = "${data.oci_core_volume_backup_policies.block_""" + policy + """.volume_backup_policies.0.id}"
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
        policy_file[reg] = outdir + "/"+reg+"/attach_block_backups_policy.tf"
        src=policy_file[reg]
        if path.exists(src):
            dst = outdir + "/"+reg+"/attach_block_backups_policy_backup" + date
            os.rename(src, dst)
        fname=open(policy_file[reg],"a+")
        fname.write(tmpstr)
        fname.close()

    for line in fname:
        if not line.startswith('#'):
            #[block_name,size_in_gb,availability_domain(AD1|AD2|AD3),attached_to_instance,attach_type(iscsi|paravirtualized,compartment_var_name] = line.split(',')
            linearr = line.split(",")
            region = linearr[0].strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                continue

            block_vol_name = linearr[1].strip()
            res_name = block_vol_name + "_bkupPolicy"
            policy = linearr[7].strip()

            tmpstr = """resource "oci_core_volume_backup_policy_assignment" \"""" + res_name + """\"{
                                #Required
                                asset_id = "${oci_core_volume.""" + block_vol_name + """.id}"
                                policy_id = "${data.oci_core_volume_backup_policies.block_""" + policy + """.volume_backup_policies.0.id}"
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

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
from jinja2 import Environment, FileSystemLoader

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

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('block-backup-policy-template')

policy_file={}
backuppolicy=''
if ('.xls' in filename):

    df = pd.read_excel(filename, sheet_name='BlockVols',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    reg = df['Region'].unique()

    # Take backup of files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()
        resource='BlockBackupPolicy'
        if (eachregion in commonTools.endNames or eachregion == 'nan'):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-backup-policy.tf")

    for i in df.index:
        region = df.loc[i,"Region"]
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        policy_data_file = outdir + "/"+region+"/oci-backup-policy-data.tf"
        datasource = env.get_template('datasource-template')

        fname=open(policy_data_file,"w+")
        # To add the 'data' resource - required for fetching the policy id
        fname.write(datasource.render())
        fname.close()

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        #Check if values are entered for mandatory fields
        if str(df.loc[i,"Region"]).lower() == 'nan' or str(df.loc[i, 'Block Name']).lower() == 'nan' or str(df.loc[i,'Backup Policy']).lower()  == 'nan':
            print( "The values for Region, Block Name and Backup Policy cannot be left empty. Please enter a value and try again !!")
            exit()

        # Fetch data ; loop through columns
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

            elif "::" in columnvalue:
                if columnname != 'Compartment Name':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = { columnname : multivalues }

            if (columnname == 'Block Name'):
                columnvalue = commonTools.check_tf_variable(columnvalue)
                blockname_tf = columnvalue
                tempdict = {'block_tf_name' : blockname_tf}

            if (columnname == 'Backup Policy'):
                columnname = 'backup_policy'
                columnvalue = columnvalue.lower()


            columnname = commonTools.check_column_headers(columnname)

            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        #Render template
        backuppolicy =  template.render(tempStr)

        file = outdir + "/" + region + "/" + blockname_tf + "-backup-policy.tf"
        oname = open(file, "w+")
        print("Writing " + file)
        oname.write(backuppolicy)
        oname.close()


elif('.csv' in filename):
    tmpstr =""
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

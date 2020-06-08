#!/bin/bash
# Author: Kartikey Rajput
# kartikey.rajput@oracle.com
#Autonomous DataWarehouse | Autonomous Transaction

import sys
import argparse
import pandas as pd
import os
import datetime
sys.path.append(os.getcwd()+"/..")
from commonTools import *


x = datetime.datetime.now()
date = x.strftime("%S").strip()

parser = argparse.ArgumentParser(description="Create ADW/ATP")
parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf file ")
parser.add_argument("prefix", help="customer name/prefix for all file names")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir
prefix = args.prefix

host_file = {}

# If the input is CD3
if ('.xls' in filename):
    #df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    #properties = df_info['Property']
    #values = df_info['Value']

    #all_regions_v = str(values[7]).strip()
    #all_regions_v = all_regions_v.split(",")
    #all_regions_v = [x.strip().lower() for x in all_regions_v]

    all_regions_f = os.listdir(outdir)

    df = pd.read_excel(filename, sheet_name='ADW_ATP', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for i in df.index:
        Region = df.iat[i, 0]
        Region = Region.strip().lower()
        if Region not in all_regions_f:
            if Region == '<end>' and '<END>':
                print('This is the end of the file')
                break
            else:
                print("Invalid Region -> " + Region + "; It should be one of the values mentioned in VCN Info tab and directory with region name in Output directory")
                continue

        name = df['Display Name'][i].strip()

        autonomous_data_warehouse_db_name = df['DB Name'][i].strip()

        compartment_var_name = df['Compartment Name'][i].strip()

        autonomous_data_warehouse_admin_password = df['Admin Password'][i].strip()

        autonomous_data_warehouse_cpu_core_count = int(df['CPU Count'][i])

        autonomous_data_warehouse_data_storage_size_in_tbs = int(df['Size in TB'][i])

        adw_atp = df['ADW or ATP'][i].strip()

        name_tf = commonTools.check_tf_variable(name)
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        if adw_atp == 'ADW':
            # print("-------------------Inside ADW--------------------")
            tmpstr = """resource "oci_database_autonomous_data_warehouse" \"""" + name_tf + """\"{
			                            display_name = \"""" + name + """\"
                                        compartment_id = "${var.""" + compartment_var_name + """}"
                    					admin_password = \"""" + autonomous_data_warehouse_admin_password + """\"
                    					cpu_core_count = \"""" + str(autonomous_data_warehouse_cpu_core_count) + """\"
                    					data_storage_size_in_tbs = \"""" + str(autonomous_data_warehouse_data_storage_size_in_tbs) + """\"
                    					db_name = \"""" + autonomous_data_warehouse_db_name + """\"
                    				}\n"""
            reg = Region[:1].upper()
            outfile = outdir + "/" + Region + "/" + reg + '_' + prefix + "_ADW_CD3_" + name + ".tf"
            print("Writing " + outfile)
            oname = open(outfile, "w")
            oname.write(tmpstr)
            oname.close()
        elif adw_atp == 'ATP':
            tmpstr = """resource "oci_database_autonomous_database" \"""" + name_tf + """\"{
                			                            display_name = \"""" + name + """\"
                                                        compartment_id = "${var.""" + compartment_var_name + """}"
                                    					admin_password = \"""" + autonomous_data_warehouse_admin_password + """\"
                                    					cpu_core_count = \"""" + str(autonomous_data_warehouse_cpu_core_count) + """\"
                                    					data_storage_size_in_tbs = \"""" + str(autonomous_data_warehouse_data_storage_size_in_tbs) + """\"
                                    					db_name = \"""" + autonomous_data_warehouse_db_name + """\"
                                    				}\n"""
            reg = Region[:1].upper()
            outfile = outdir + "/" + Region + "/" + reg + '_' + prefix + "_ATP_CD3_" + name + ".tf"
            print("Writing " + outfile)
            oname = open(outfile, "w")
            oname.write(tmpstr)
            oname.close()
        else:
            print("--Enter Valid Database type in ADW or ATP tab--")

# If the input is CSV
elif ('.csv' in filename):
    fname = open(filename, "r")
    all_regions = os.listdir(outdir)
    for line in fname:
        if not line.startswith('#'):
            linearr = line.split(",")
            region = linearr[0].strip().lower()
            if region not in all_regions:
                print("Invalid Region -> " + region + "; It should be one of the values mentioned in VCN Info tab and directory with region name in Output directory")
                continue

            name = linearr[1].strip()

            autonomous_data_warehouse_db_name = linearr[2].strip()

            compartment_var_name = linearr[3].strip()

            autonomous_data_warehouse_admin_password = linearr[4].strip()

            autonomous_data_warehouse_cpu_core_count = int(linearr[5])

            autonomous_data_warehouse_data_storage_size_in_tbs = int(linearr[6])

            adw_atp = linearr[7].strip()

            if adw_atp == 'ADW':
                tmpstr = """resource "oci_database_autonomous_data_warehouse" \"""" + name + """\"{
                                                    display_name = \"""" + name + """\"
                                                    compartment_id = "${var.""" + compartment_var_name + """}"
                                                    admin_password = \"""" + autonomous_data_warehouse_admin_password + """\"
                                                    cpu_core_count = \"""" + str(autonomous_data_warehouse_cpu_core_count) + """\"
                                                    data_storage_size_in_tbs = \"""" + str(
                    autonomous_data_warehouse_data_storage_size_in_tbs) + """\"
                                                    db_name = \"""" + autonomous_data_warehouse_db_name + """\"
                                                }\n"""
                reg = region[:1].upper()
                outfile = outdir + "/" + region + "/" + reg + '_' + prefix + "_ADW_CSV_" + name + ".tf"
                print("Writing " + outfile)
                oname = open(outfile, "w")
                oname.write(tmpstr)
                oname.close()
            elif adw_atp == 'ATP':
                tmpstr = """resource "oci_database_autonomous_database" \"""" + name + """\"{
                                                                    display_name = \"""" + name + """\"
                                                                    compartment_id = "${var.""" + compartment_var_name + """}"
                                                                    admin_password = \"""" + autonomous_data_warehouse_admin_password + """\"
                                                                    cpu_core_count = \"""" + str(
                    autonomous_data_warehouse_cpu_core_count) + """\"
                                                                    data_storage_size_in_tbs = \"""" + str(
                    autonomous_data_warehouse_data_storage_size_in_tbs) + """\"
                                                                    db_name = \"""" + autonomous_data_warehouse_db_name + """\"
                                                                }\n"""
                reg = region[:1].upper()
                outfile = outdir + "/" + region + "/" + reg + '_' + prefix + "_ATP_CSV_" + name + ".tf"
                print("Writing " + outfile)
                oname = open(outfile, "w")
                oname.write(tmpstr)
                oname.close()
            else:
                print("--Enter Valid Database type in ADW or ATP tab--")
else:
    print("Enter valid file type")

#!/bin/bash
# Author: Kartikey Rajput
# kartikey.rajput@oracle.com
#Autonomous DataWarehouse | Autonomous Transaction

import sys
import argparse
import pandas as pd
import os
import datetime
import array as arr
from os import path
import csv

import array

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
    df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]

    df = pd.read_excel(filename, sheet_name='ADW_ATP', skiprows=1)
    for i in df.index:
        for j in df.keys():
            if (str(df[j][i]) == 'nan'):
                continue

            elif (j == 'Region'):
                Region = df['Region'][i].strip().lower()
                print("Region----------------> "+Region)
                print(f"Value of i --------> {i} and Value of j --------> {j}")

            name = df['Display Name'][i].strip()
            print("Hostname-----------------------------> "+name)

            autonomous_data_warehouse_db_name = df['DB Name'][i].strip()
            print("Hostname-----------------------------> " + autonomous_data_warehouse_db_name)

            compartment_var_name = df['Compartment Name'][i].strip()
            print("Compartment---------------------------> "+compartment_var_name)

            autonomous_data_warehouse_admin_password = df['Admin Password'][i].strip()
            print("AdminPassword-------------------------> "+autonomous_data_warehouse_admin_password)

            autonomous_data_warehouse_cpu_core_count = int(df['CPU Count'][i])
            print(f"CPU Count-------------------------> {autonomous_data_warehouse_cpu_core_count}")

            autonomous_data_warehouse_data_storage_size_in_tbs = int(df['Size in TB'][i])
            print(f"Size in TB-------------------------> {autonomous_data_warehouse_data_storage_size_in_tbs}")

            adw_atp = df['ADW or ATP'][i].strip()
            print("ADW or ATP -----------------> "+adw_atp)

            if adw_atp == 'ADW':
                print("-------------------Inside ADW--------------------")
                tmpstr = """resource "oci_database_autonomous_data_warehouse" \"""" + name + """\"{
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
                print("-------------------Inside ATP--------------------")
                tmpstr = """resource "oci_database_autonomous_database" \"""" + name + """\"{
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


elif ('.csv' in filename):
    fname = open(filename, "r")
    with open(filename, 'rt')as f:
        reader = csv.reader(f)
        value_1 = int(len(list(csv.reader(open(filename)))))
        row_count = int(value_1 - 1)
        print(f"Number of rows---------------> {row_count}")
    all_regions = os.listdir(outdir)
    for line in fname:
        linearr = line.split(",")
        region = linearr[0].strip().lower()
        if region not in all_regions:
            # print("Invalid Region")
            continue

        name = linearr[1].strip()
        print("Hostname-----------------------------> " + name)

        autonomous_data_warehouse_db_name = linearr[2].strip()
        print("DB name-----------------------------> " + autonomous_data_warehouse_db_name)

        compartment_var_name = linearr[3].strip()
        print("Compartment---------------------------> " + compartment_var_name)

        autonomous_data_warehouse_admin_password = linearr[4].strip()
        print("AdminPassword-------------------------> " + autonomous_data_warehouse_admin_password)

        autonomous_data_warehouse_cpu_core_count = int(linearr[5])
        print(f"CPU Count-------------------------> {autonomous_data_warehouse_cpu_core_count}")

        autonomous_data_warehouse_data_storage_size_in_tbs = int(linearr[6])
        print(f"Size in TB-------------------------> {autonomous_data_warehouse_data_storage_size_in_tbs}")

        adw_atp = linearr[7].strip()
        print("ADW or ATP--------------> "+adw_atp)

        if adw_atp == 'ADW':
            print("-------------------Inside ADW--------------------")
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
            print("-------------------Inside ATP--------------------")
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










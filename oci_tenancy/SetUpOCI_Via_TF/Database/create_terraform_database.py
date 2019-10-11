#!/usr/bin/python3
# Author: Kartikey Rajput
# kartikey.rajput@oracle.com
#Autonomous DataWarehouse | Autonomous Transaction

import sys
import argparse
import pandas as pd
import os
import datetime
import csv

import array

x = datetime.datetime.now()
date = x.strftime("%S").strip()

parser = argparse.ArgumentParser(description="Create DB_System")
parser.add_argument("file", help="Full Path of CD3 excel file. eg CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf file ")
parser.add_argument("prefix", help="customer name/prefix for all file names")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
#print(f"FILENAME----------------------> {filename}")
outdir = args.outdir
#print("Outdir in file above---------------------> "+outdir)
prefix = args.prefix
#print("Prefix----------------------> "+prefix)

ADS = ["AD1", "AD2", "AD3"]

# host_file = {}
# If the input is CD3
if ('.xls' in filename):
    #df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    #properties = df_info['Property']
    #values = df_info['Value']

    #all_regions_v = str(values[7]).strip()
    #all_regions_v = all_regions_v.split(",")
    #all_regions_v = [x.strip().lower() for x in all_regions_v]
    #print(f"REGIONs in VCN info---------------------> {all_regions_v}")

    all_regions_f = os.listdir(outdir)
    #print(f"REGIONs folders---------------------> {all_regions_f}")

    df = pd.read_excel(filename, sheet_name='Database', skiprows=1)
    for i in df.index:
        for j in df.keys():
            if (str(df[j][i]) == 'nan'):
                continue

            elif (j == 'Region'):
                Region = df['Region'][i].strip().lower()
                #print("Region----------------> "+Region)
                #print(f"Value of i --------> {i} and Value of j --------> {j}")

            if Region not in all_regions_f:
                print("Invalid Region -> " + Region + "; It should be one of the values mentioned in VCN Info tab")
                continue

            database_system_availability_domain = df['Availability domain'][i].strip()
            # print("AD-------kkkkkkkkkkkkkk---------> " + database_system_availability_domain)

            AD = df.iat[i, 3]
            # print("AD------DH.iat--------->" + AD)
            AD = AD.upper()
            # print("AD------------UPPER------>" + AD)
            ad = ADS.index(AD)
            # print(f"ADS----------INDEX------------->{ad}")

            ad_type = type(database_system_availability_domain)
            # #print("ad type ------------------------------------------=====================> "+ad_type)

            compartment_var_name = df['Compartment Name'][i].strip()
            # #print("Compartment---------------> "+compartment_var_name)

            database_shape = df['Shape'][i].strip()
            # #print("Shape----------------> "+database_shape)

            database_cpu_core = int(df['CPU Core'][i])
            # #print(f"CPU Cores-----------------------> {database_cpu_core}")

            database_soft_edition = df['Oracle database software edition'][i].strip()
            # #print("Edition--------------------------> "+database_soft_edition)

            database_admin_password = df['Database admin password'][i].strip()
            # #print("AdminPassword-------------------> "+database_admin_password)

            database_name = df['Database name'][i].strip()
            # #print("Database name-------------------> "+database_name)

            database_version = df['Database version'][i].strip()
            # #print("Database version-------------------> "+database_version)

            database_home_display_name = df['Name your DB system'][i].strip()
            # #print("Home display name ------------------> "+database_home_display_name)

            database_disk_redundancy = df['Database Disk Redundancy'][i].strip()
            # #print("Disk Redundancy------------------------> "+database_disk_redundancy)

            database_system_display_name = df['Name your DB system'][i].strip()
            # #print("System Display name--------------------> "+database_system_display_name)

            database_hostname_prefix = df['Hostname prefix'][i].strip()
            # #print("Hostname --------------------> "+database_hostname_prefix)

            database_host_user_name = df['Database username'][i].strip()
            # #print("Host user name----------------------> "+database_host_user_name)

            database_workload_type = df['Select workload type'][i].strip()
            # #print("Workload type-----------------------> "+database_workload_type)

            database_PDB_name = df['PDB name (Optional)'][i].strip()
            # #print("Pdb name--------------------> "+database_PDB_name)

            database_storage = int(df['Database Size (GB)'][i])
            # #print(f"Database storage---------------------> {database_storage}")

            database_license = df['Choose a license type'][i].strip()
            # #print(f"License-------------------> {database_license}")

            database_node_count_int = int(df['Total node count'][i])
            # #print(f"Node count--------------------> {database_node_count_int}")
            # #print(f"type of node count-----------------> {type(database_node_count_int)}")

            database_node_count_str = str(database_node_count_int)
            # #print(f"type of node count-----------------> {type(database_node_count_str)}")


            database_auto_backup_option = df['Enable Automatic Backups'][i].strip()
            # #print("Backup Option------------------> "+database_auto_backup_option)

            database_subnet_name = df['Subnet name'][i].strip()
            # #print("Subnet name ------------> "+database_subnet_name)

            database_ssh_key = df['SSH Key'][i].strip()
            # print("SSH KEY-----------> "+database_ssh_key)

            if (database_auto_backup_option.lower() == 'yes'):
                database_auto_backup_option = "true"
            else:
                database_auto_backup_option = "false"

            resources_content = """
                resource "oci_database_db_system" \"""" + database_system_display_name + """\" {
                  availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
                  compartment_id = "${var.""" + compartment_var_name + """}"
                  cpu_core_count      = \"""" + str(database_cpu_core) + """\"
                  database_edition    = \"""" + database_soft_edition + """\"
                  db_home {
                    database {
                      admin_password = \"""" + database_admin_password + """\"
                      db_name        = \"""" + database_name + """\"
                      character_set  = "AL32UTF8"
                      ncharacter_set = "AL16UTF16"
                      db_workload    = \"""" + database_workload_type + """\"
                      pdb_name       = \"""" + database_PDB_name + """\"
                      db_backup_config {
                        auto_backup_enabled     = \"""" + database_auto_backup_option + """\"
                        recovery_window_in_days = "10"
                      }
                    }
                    db_version   = \"""" + database_version + """\"
                    display_name = \"""" + database_home_display_name + """\"
                  }
                  disk_redundancy = \"""" + database_disk_redundancy + """\"
                  shape           = \"""" + database_shape + """\"
                  subnet_id       = "${oci_core_subnet.""" + database_subnet_name + """.id}"
                  ssh_public_keys = ["${var.""" + database_ssh_key + """}"]
                  display_name    = \"""" + database_system_display_name + """\"
                  hostname                = \"""" + database_hostname_prefix + """\"
                  data_storage_size_in_gb = \"""" + str(database_storage) + """\"
                  license_model           = \"""" + database_license + """\"
                  node_count              = \"""" + str(database_node_count_str) + """\"
                }
                """

            # def write_variables_tf(source_file, source_file_sheet, outdir):
            reg = Region[:1].upper()
            outfile = outdir + "/" + Region + "/" + reg + '_' + prefix + """_DBS_CD3_""" + database_system_display_name + ".tf"
            print("Writing " + outfile)
            oname = open(outfile, "w")
            oname.write(resources_content)
            oname.close()


elif ('.csv' in filename):
    fname = open(filename, "r")
    all_regions = os.listdir(outdir)
    #print(f"REGION---------------------> {all_regions}")
    for line in fname:
        if not line.startswith('#'):
            linearr = line.split(",")
            region = linearr[0].strip().lower()
            #print("Region-------------------------------> "+region)
    # #print("---------------INSIDE LOOP------------")
            if region not in all_regions:
                print("Invalid Region -> " + region + "; It should be one of the values mentioned in VCN Info tab and directory with region name in Output directory")
                continue

            database_system_availability_domain = linearr[3].strip()
            #print("AD----------------> " + database_system_availability_domain)

            ad = ADS.index(database_system_availability_domain)
            #print(f"ADS----------INDEX------------->{ad}")

            compartment_var_name = linearr[1].strip()
            #print("Compartment---------------> " + compartment_var_name)

            database_shape = linearr[5].strip()
            #print("Shape----------------> " + database_shape)

            database_cpu_core = int(linearr[6])
            #print(f"CPU Cores-----------------------> {database_cpu_core}")

            database_soft_edition = linearr[8].strip()
            #print("Edition--------------------------> " + database_soft_edition)

            database_admin_password = linearr[17].strip()
            #print("AdminPassword-------------------> " + database_admin_password)

            database_name = linearr[13].strip()
            #print("Database name-------------------> " + database_name)

            database_version = linearr[14].strip()
            #print("Database version-------------------> " + database_version)

            database_home_display_name = linearr[4].strip()
            #print("Home display name ------------------> " + database_home_display_name)

            database_disk_redundancy = linearr[10].strip()
            #print("Disk Redundancy------------------------> " + database_disk_redundancy)

            database_system_display_name = linearr[4].strip()
            #print("System Display name--------------------> " + database_system_display_name)

            database_hostname_prefix = linearr[12].strip()
            #print("Hostname --------------------> " + database_hostname_prefix)

            database_host_user_name = linearr[16].strip()
            #print("Host user name----------------------> " + database_host_user_name)

            database_workload_type = linearr[18].strip()
            #print("Workload type-----------------------> " + database_workload_type)

            database_PDB_name = linearr[15].strip()
            #print("Pdb name--------------------> " + database_PDB_name)

            database_storage = int(linearr[9])
            #print(f"Database storage---------------------> {database_storage}")

            database_license = linearr[11].strip()
            #print(f"License-------------------> {database_license}")

            database_node_count_int = int(linearr[7])
            #print(f"Node count--------------------> {database_node_count_int}")
            #print(f"type of node count-----------------> {type(database_node_count_int)}")

            database_node_count_str = str(database_node_count_int)
            #print(f"type of node count-----------------> {type(database_node_count_str)}")

            database_auto_backup_option = linearr[19].strip()
            #print("Backup Option------------------> " + database_auto_backup_option)

            database_subnet_name = linearr[2].strip()
            #print("Subnet name ------------> " + database_subnet_name)

            database_ssh_key = linearr[20].strip()

            if (database_auto_backup_option.lower() == 'yes'):
                database_auto_backup_option = "true"
            else:
                database_auto_backup_option = "false"

            resources_content = """
                            resource "oci_database_db_system" \"""" + database_system_display_name + """\" {
                              availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
                              compartment_id = "${var.""" + compartment_var_name + """}"
                              cpu_core_count      = \"""" + str(database_cpu_core) + """\"
                              database_edition    = \"""" + database_soft_edition + """\"
                              db_home {
                                database {
                                  admin_password = \"""" + database_admin_password + """\"
                                  db_name        = \"""" + database_name + """\"
                                  character_set  = "AL32UTF8"
                                  ncharacter_set = "AL16UTF16"
                                  db_workload    = \"""" + database_workload_type + """\"
                                  pdb_name       = \"""" + database_PDB_name + """\"
                                  db_backup_config {
                                    auto_backup_enabled     = \"""" + database_auto_backup_option + """\"
                                    recovery_window_in_days = "10"
                                  }
                                }
                                db_version   = \"""" + database_version + """\"
                                display_name = \"""" + database_home_display_name + """\"
                              }
                              disk_redundancy = \"""" + database_disk_redundancy + """\"
                              shape           = \"""" + database_shape + """\"
                              subnet_id       = "${oci_core_subnet.""" + database_subnet_name + """.id}"
                              ssh_public_keys = ["${var.""" + database_ssh_key + """}"]
                              display_name    = \"""" + database_system_display_name + """\"
                              hostname                = \"""" + database_hostname_prefix + """\"
                              data_storage_size_in_gb = \"""" + str(database_storage) + """\"
                              license_model           = \"""" + database_license + """\"
                              node_count              = \"""" + str(database_node_count_str) + """\"
                            }
                            """
            #print("OutDir inside file------------------------------> "+outdir)
            reg = region[:1].upper()
            outfile = outdir + "/" + region + "/" + reg + '_' + prefix + """_DBS_CSV_""" + database_system_display_name + ".tf"
            print("Writing " + outfile)
            oname = open(outfile, "w")
            oname.write(resources_content)
            oname.close()

else:
    print("Enter valid file type")

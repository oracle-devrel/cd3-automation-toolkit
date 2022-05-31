#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Database System Virtual Machine
#
# Author: Suruchi
# Oracle Consulting
#

import sys
import argparse
import os
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Create DB VM and DB BM terraform file")
    parser.add_argument('inputfile', help='Full Path of input CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


#If input is cd3 file
def create_terraform_dbsystems_vm_bm(inputfile, outdir, prefix, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config

    sheetName = "DBSystems-VM-BM"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'
    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('dbsystems-vm-bm-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/"
        resource = sheetName.lower()
        #commonTools.backup_file(srcdir, resource, sheetName.lower()+".tf")
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    regions_done_count = []

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        #if region.lower() == 'nan':
        #    continue

        region=region.strip().lower()


        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region.lower() != 'nan' and region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}
        nsg_id = ''
        backup_nsg_id = ''

        #Check if it is different DB home on same BM DB
        if str(df.loc[i, 'Region']).lower() == 'nan' and \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' and \
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' and \
                str(df.loc[i, 'DB System Display Name']).lower() == 'nan' and \
                str(df.loc[i, 'Subnet Name']).lower() == 'nan' and \
                str(df.loc[i, 'Shape']).lower() == 'nan' and \
                str(df.loc[i, 'Node Count']).lower() == 'nan' and \
                str(df.loc[i, 'CPU Core Count']).lower() == 'nan' and \
                str(df.loc[i, 'Database Edition']).lower() == 'nan' and \
                str(df.loc[i, 'Data Storage Size in GB']).lower() == 'nan' and \
                str(df.loc[i, 'Data Storage Percentage']).lower() == 'nan' and \
                str(df.loc[i, 'Disk Redundancy']).lower() == 'nan' and \
                str(df.loc[i, 'License Model']).lower() == 'nan' and \
                str(df.loc[i, 'Hostname Prefix']).lower() == 'nan' and \
                str(df.loc[i, 'DB Name']).lower() != 'nan':
            continue

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or \
                str(df.loc[i, 'SSH Key Var Name']).lower() == 'nan' or \
                str(df.loc[i, 'Subnet Name']).lower() == 'nan' or \
                str(df.loc[i, 'Hostname Prefix']).lower() == 'nan' or \
                str(df.loc[i, 'Shape']).lower() == 'nan' :
            print("\nRegion, Compartment Name, Availability Domain(AD1|AD2|AD3), SSH Key Var Name, Subnet Name, Hostname, Shape are mandatory fields. Please enter a value and try again.......Exiting!!")
            exit()
        if str(df.loc[i, 'DB Name']).lower() == 'nan' or \
                str(df.loc[i, 'DB Version']).lower() == 'nan' or \
                str(df.loc[i, 'Database Edition']).lower() == 'nan' or \
                str(df.loc[i, 'DB Admin Password']).lower() == 'nan':
            print("\nDB Name, DB Version, Database Edition, DB Admin Password are mandatory fields. Please enter a value and try again.......Exiting!!")
            exit()

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {columnname: columnvalue}

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "DB System Display Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == 'Subnet Name':
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == 'Backup Subnet Name':
                columnvalue = commonTools.check_tf_variable(columnvalue)


            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain': columnvalue}


            if columnname == 'NSGs':
                if columnvalue != '':
                    db_nsgs = str(columnvalue).strip().split(",")
                    if len(db_nsgs) == 1:
                        for nsg in db_nsgs:
                            if "ocid" in nsg.strip():
                                nsg_id = "\"" + nsg.strip() + "\""
                            else:
                                nsg_id = "\"" + commonTools.check_tf_variable(str(nsg).strip()) + "\""

                    elif len(db_nsgs) >= 2:
                        c = 1
                        for nsg in db_nsgs:
                            if "ocid" in nsg.strip():
                                data = "\"" + nsg.strip() + "\""
                            else:
                                data = "\"" + commonTools.check_tf_variable(str(nsg).strip()) + "\""

                            if c == len(db_nsgs):
                                nsg_id = nsg_id + data
                            else:
                                nsg_id = nsg_id + data + ","
                            c += 1
                columnvalue = nsg_id

            if columnname == 'Backup Network NSGs':
                if columnvalue != '':
                    backup_nsgs = str(columnvalue).strip().split(",")
                    if len(backup_nsgs) == 1:
                        for nsgs in backup_nsgs:
                            if "ocid" in nsgs.strip():
                                backup_nsg_id = "\"" + nsgs.strip() + "\""
                            else:
                                backup_nsg_id = "\"" + commonTools.check_tf_variable(str(nsgs).strip()) + "\""

                    elif len(backup_nsgs) >= 2:
                        c = 1
                        for nsgs in backup_nsgs:
                            if "ocid" in nsgs.strip():
                                data = "\"" + nsgs.strip() + "\""
                            else:
                                data = "\"" + commonTools.check_tf_variable(str(nsgs).strip()) + "\""

                            if c == len(backup_nsgs):
                                backup_nsg_id = backup_nsg_id + data
                            else:
                                backup_nsg_id = backup_nsg_id + data + ","
                            c += 1
                columnvalue = backup_nsg_id

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if (region not in regions_done_count):
            tempdict = {"count": 0}
            regions_done_count.append(region)
        else:
            tempdict = {"count": i}
        tempStr.update(tempdict)


        # Write all info to TF string
        tfStr[region]=tfStr[region][:-1] + template.render(tempStr)


    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        #outfile[reg] = reg_out_dir + "/" + prefix + "_"+sheetName.lower()+".tf"
        outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

        if(tfStr[reg]!=''):
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg]=open(outfile[reg],'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for DBSystems-VM-BM has been created for region "+reg)


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_dbsystems_vm_bm(args.inputfile, args.outdir, args.prefix, args.config)
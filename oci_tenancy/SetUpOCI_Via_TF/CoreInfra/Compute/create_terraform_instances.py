#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Instances
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from .boot_backups_policy import create_boot_backup_policy
sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


def parse_args():
    parser = argparse.ArgumentParser(description='Creates Instances TF file')
    parser.add_argument('file', help='Full Path of CD3 excel file. eg  CD3-template.xlsx in example folder')
    parser.add_argument('outdir', help='directory path for output tf files ')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


#If input is CD3 excel file
def create_terraform_instances(inputfile, outdir, config):

    ADS = ["AD1", "AD2", "AD3"]

    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('instance-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Instances")
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()
    display_tf_name=''

    reg = df['Region'].unique()

    # Take backup of files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()

        if (eachregion in commonTools.endNames or eachregion == 'nan'):
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        resource = 'Instances'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_instance.tf")

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        display_name = str(df.loc[i,'Display Name'])
        shapeField = str(df.loc[i,'Shape'])
        shapeField = shapeField.strip()
        shape_error=0

        if(shapeField.lower()!="nan" and ".Flex" in shapeField):
            if("::" not in shapeField):
                shape_error=1
            else:
                shapeField=shapeField.split("::")
                if(shapeField[1].strip()==""):
                    shape_error=1

        if(shape_error==1):
            print("\nERROR!!! "+ display_name +" is missing ocpus for Flex shape....Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Display Name']).lower() == 'nan' or str(df.loc[i, 'Shape']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Pub Address']).lower() == 'nan' or str(
                df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or str(df.loc[i, 'Subnet Name']).lower() == 'nan' or str(df.loc[i, 'Source Details']).lower() == 'nan'):
            print("\nColumn Region, Shape, Compartment Name, Availability Domain, Display Name, Pub Address, Source Details and Subnet Name cannot be left empty in Instances sheet of CD3..exiting...")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Shape':
                if ".Flex" not in columnvalue:
                    columnvalue = columnvalue.strip()
                    tempdict = { 'shape' : [columnvalue] }

            if columnname == "Subnet Name":
                subnet_tf_name = commonTools.check_tf_variable(columnvalue.strip())
                tempdict = { 'subnet_tf_name' : subnet_tf_name }

            if columnname == 'Display Name':
                columnvalue = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain' : columnvalue}

            if columnname == 'Dedicated VM Host':
                if columnvalue.strip() != '' and columnvalue.strip() != 'nan':
                    dedicated_vm_host_tf = "oci_core_dedicated_vm_host."+commonTools.check_tf_variable(columnvalue)+".id"
                else:
                    dedicated_vm_host_tf = "\"\""
                tempdict = {'dedicated_vm_host_tf': dedicated_vm_host_tf}


            if columnname == 'NSGs':
                if columnvalue != '' and columnvalue.strip().lower()  != 'nan':
                    nsg_str = ""
                    nsg = ""
                    NSGs = columnvalue.split(",")
                    k=0
                    while k < len(NSGs):
                        if "ocid" in NSGs[k].strip():
                            nsg = "\""+NSGs[k].strip()+"\""
                        else:
                            nsg = "oci_core_network_security_group."+commonTools.check_tf_variable(NSGs[k].strip())+ ".id"
                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    tempdict = {'nsg_ids': nsg_str}
                    tempStr.update(tempdict)
                continue


            if columnname == "SSH Key Var Name":
                if columnvalue.strip() != '' and  columnvalue.strip().lower() != 'nan':
                    if "ssh-rsa" in columnvalue.strip():
                        ssh_key_var_name = "\"" + columnvalue.strip() + "\""
                    else:
                        ssh_key_var_name = "var." + columnvalue.strip()
                    tempdict = {'ssh_key_var_name': ssh_key_var_name}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string; Render template
        hostStr = template.render(tempStr)

        # Write to output
        file = outdir + "/" + region + "/" + display_tf_name + "_instance.tf"
        oname = open(file, "w+")
        print("Writing to " + file)
        oname.write(hostStr)
        oname.close()

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_instances(args.inputfile, args.outdir, args.config)
    # Create Boot Backup Policy
    print("Processing Boot Volume Backup Policies...")
    create_boot_backup_policy(args.inputfile, args.outdir, args.config)

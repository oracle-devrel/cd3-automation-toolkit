#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Dedicated Hosts
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path

sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######

# If input is CD3 excel file
# Execution of the code begins here
def create_terraform_dedicatedhosts(inputfile, outdir, service_dir,prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('dedicatedvmhosts-template')

    filename = inputfile

    sheetName = "DedicatedVMHosts"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # Take backup of files
    for eachregion in ct.all_regions:
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
        tfStr[eachregion] = ''

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Shape']).lower() == 'nan' or str(
                df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or str(
            df.loc[i, 'Display Name']).lower() == 'nan'):
            print("\nAll Fields are mandatory except Fault Domain. Exiting...")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Display Name':
                columnvalue = columnvalue.strip()
                host_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'dedicated_vm_host_tf': host_tf_name, 'dedicated_vm_host': columnvalue}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain': columnvalue}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string; Render template
        tfStr[region] = tfStr[region] + template.render(tempStr) + "\n"

    # Write to output
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if (tfStr[reg] != ''):
            src = "##Add New Dedicated VM Host for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            # Write to TF file
            outfile = reg_out_dir + "/" + auto_tfvars_filename
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print(outfile + " for dedicated vm hosts has been created for region  " + reg)
            oname.write(tfStr[reg])
            oname.close()

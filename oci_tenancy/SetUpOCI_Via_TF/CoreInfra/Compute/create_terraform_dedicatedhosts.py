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
import argparse
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    # Read input arguments
    parser = argparse.ArgumentParser(description='Create Dedicated VM Hosts terraform file')
    parser.add_argument('inputfile', help='Full Path of input file. It could be the CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


# If input is CD3 excel file
def create_terraform_dedicatedhosts(inputfile, outdir, config):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('dedicated-hosts-template')

    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "DedicatedVMHosts")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    unique_region = df['Region'].unique()

    # Take backup of files
    for eachregion in unique_region:
        eachregion = str(eachregion).strip().lower()

        if (eachregion in commonTools.endNames):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        resource='DedicatedHosts'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "dedicated_vm_hosts.tf")

        tfStr[eachregion] = ''

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i,'Region'])

        if (region in commonTools.endNames):
            break

        region=region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Shape']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or str(df.loc[i, 'Hostname']).lower() == 'nan'):
            print("\nAll Fields are mandatory except Fault Domain. Exiting...")
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

            if columnname == 'Hostname':
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
                tempdict = {'availability_domain' : columnvalue}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string; Render template
        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write to output
    for regions in unique_region:
        regions=regions.lower()
        for reg in ct.all_regions:
            if reg == regions:
                reg_out_dir = outdir + "/" + reg
                outfile[reg] = reg_out_dir + "/dedicated_vm_hosts.tf"

                if(tfStr[reg]!=''):
                    oname[reg]=open(outfile[reg],'w')
                    oname[reg].write(tfStr[reg])
                    oname[reg].close()
                    print(outfile[reg] + " containing TF for dedicated vm hosts has been created for region "+reg)

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_dedicatedhosts(args.inputfile, args.outdir, args.config)

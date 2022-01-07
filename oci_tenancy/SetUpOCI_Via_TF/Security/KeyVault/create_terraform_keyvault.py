#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Key/Vault
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import argparse
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from commonTools import *

######
# Required Inputs- Config file, prefix AND outdir
######

def parse_args():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Create Key/Vault terraform file")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("region_name", help="region name")
    parser.add_argument("comp_name", help="compartment name")
    parser.add_argument("--configFileName", help="Config file name", required=False)
    return parser.parse_args()

def create_cis_keyvault(outdir, prefix, region_name, comp_name, config=DEFAULT_LOCATION):

    # Declare variables
    configFileName = config
    region_name = region_name.strip().lower()
    comp_name = comp_name.strip()

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    if region_name not in ct.all_regions:
        print("Invalid Region!! Tenancy is not subscribed to this region. Please try again")
        exit()


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('keyvault-template')

    tempStr = {}
    tfStr = ''

    compartmentVarName = commonTools.check_tf_variable(comp_name)
    columnvalue = str(compartmentVarName)
    tempStr['compartment_tf_name'] =  columnvalue

    key_name = prefix+"-"+region_name+"-kms-key"
    vault_name = prefix+"-"+region_name+"-kms-vault"
    management_endpoint = 'oci_kms_vault.'+vault_name+'.management_endpoint'

    tempStr['key_name'] = key_name
    tempStr['key_tf_name'] = key_name
    tempStr['vault_name'] = vault_name
    tempStr['vault_tf_name'] = vault_name
    tempStr['management_endpoint'] = management_endpoint

    tfStr = tfStr + template.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + region_name
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/cis-keyvault.tf"

    srcdir = reg_out_dir + "/"
    resource = 'keyvault'
    commonTools.backup_file(srcdir, resource, "cis-keyvault.tf")


    if(tfStr!=''):
        oname=open(outfile,'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for Key/Vault has been created for region "+region_name)

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_cis_keyvault(args.outdir, args.prefix, args.config, args.region_name, args.comp_name)

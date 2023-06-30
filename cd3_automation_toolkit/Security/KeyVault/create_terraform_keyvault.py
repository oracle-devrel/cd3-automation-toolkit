#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Security components
# Key/Vault
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from commonTools import *

######
# Required Inputs- Config file, prefix AND outdir
######
# Execution of the code begins here
def create_cis_keyvault(outdir, service_dir, service_dir_iam, prefix, region_name, comp_name, config=DEFAULT_LOCATION):

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
    vault_template = env.get_template('vaults-template')
    key_template = env.get_template('keys-template')

    tempStr = {}
    vaultStr = ''
    keyStr = ''
    auto_tfvars_filename = "cis-keyvault.auto.tfvars"

    compartmentVarName = commonTools.check_tf_variable(comp_name)
    columnvalue = str(compartmentVarName)
    tempStr['compartment_tf_name'] =  columnvalue

    key_name = prefix+"-"+region_name+"-kms-key"
    vault_name = prefix+"-"+region_name+"-kms-vault"

    tempStr['key_name'] = key_name
    tempStr['key_tf_name'] = key_name
    tempStr['vault_name'] = vault_name
    tempStr['vault_tf_name'] = vault_name
    tempStr['management_endpoint'] = vault_name
    tempStr['algorithm'] = "AES"

    vaultStr = vaultStr + vault_template.render(tempStr)
    keyStr= keyStr + key_template.render(tempStr)

    if vaultStr != '':
        # Generate Final String
        src = "##Add New Vaults for " + region_name + " here##"
        vaultStr = vault_template.render(skeleton=True, count=0, region=region_name).replace(src, vaultStr+"\n"+src)

    if keyStr != '':
        # Generate Final String
        src = "##Add New Keys for " + region_name + " here##"
        keyStr = key_template.render(skeleton=True, count=0, region=region_name).replace(src, keyStr+"\n"+src)

    finalstring = vaultStr + keyStr
    finalstring = "".join([s for s in finalstring.strip().splitlines(True) if s.strip("\r\n").strip()])

    if finalstring != "":
        resource = "keyvault"
        srcdir = outdir + "/" + region_name + "/" + service_dir +"/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

        # Write to TF file
        outfile = outdir + "/" + region_name + "/" + service_dir + "/" + auto_tfvars_filename
        oname = open(outfile, "w+")
        print(outfile + " containing TF for Key/Vault has been created for region "+region_name)
        oname.write(finalstring)
        oname.close()

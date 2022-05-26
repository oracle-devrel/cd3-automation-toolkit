#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# OSS Bucket
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
    parser = argparse.ArgumentParser(description="Create Groups terraform file")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("region_name", help="region name")
    parser.add_argument("comp_name", help="compartment name")
    parser.add_argument("--configFileName", deafult=DEFAULT_LOCATION, help="Config file name", required=False)

def create_cis_oss(outdir, prefix, region_name, comp_name, config):
    # Declare variables
    configFileName = config
    comp_name = comp_name.strip()
    region_name=region_name.strip().lower()

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    home_region=ct.home_region

    if region_name not in ct.all_regions:
        print("Invalid Region!! Tenancy is not subscribed to this region. Please try again")
        exit()

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('oss-template')
    policyTemplate = env.get_template('oss-policy-template')

    #region_key = ct.region_dict[region_name]

    tempStr = {}
    tempPolStr = {}
    tfStr = ''
    tfPolStr = ''

    compartmentVarName = commonTools.check_tf_variable(comp_name)
    cname = str(compartmentVarName)

    oss_name= prefix+"-"+region_name+"-oss-bucket"
    key_name=prefix+"-"+region_name+"-kms-key"

    tempStr['compartment_tf_name'] =  cname
    tempStr['bucket_name'] = oss_name
    tempStr['bucket_tf_name'] = oss_name
    tempStr['kms_key_id'] = key_name
    tfStr = tfStr + template.render(tempStr)


    tempPolStr['policy_tf_name']=prefix+"-oss-kms-policy"
    tempPolStr['name'] = prefix + "-oss-kms-policy"
    tempPolStr['compartment_tf_name']='tenancy_ocid'
    tempPolStr['description']="Policy allowing OCI OSS service to access Key in the Vault service."
    tempPolStr['policy_statements'] = ''
    for reg in ct.all_regions:
        actual_policy_statement = "Allow service objectstorage-"+ct.region_dict[reg]+" to use keys in compartment "+comp_name
        tempPolStr['policy_statements'] = "\""+actual_policy_statement + "\","+tempPolStr['policy_statements']
    tfPolStr=tfPolStr + policyTemplate.render(tempPolStr)
    tfPolStr = tfPolStr + """ ]
                    } \n
        } \n"""
    tfPolStr = tfPolStr.replace('-#Addstmt]', '')

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + region_name
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    home_reg_out_dir = outdir + "/" + home_region
    outfile = reg_out_dir + "/cis-oss.tf"
    outPolfile= home_reg_out_dir+"/cis-osskeyvault-policy.auto.tfvars"

    srcdir = reg_out_dir + "/"
    resource = 'oss'
    commonTools.backup_file(srcdir, resource, "cis-oss.tf")
    commonTools.backup_file(srcdir, resource, "cis-osskeyvault-policy.auto.tfvars")

    if(tfStr!=''):
        # Generate Final String
        src = "##Add New Object Storage for " + home_region.lower() + " here##"
        tfStr = template.render(skeleton=True, count=0, region= home_region.lower()).replace(src, tfStr +"\n" + src)
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname=open(outfile,'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for OSS has been created for region "+region_name)

    if (tfPolStr != ''):
        tfPolStr = "".join([s for s in tfPolStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname = open(outPolfile, 'w')
        oname.write(tfPolStr)
        oname.close()
        print(outPolfile + " containing TF for Policy allow OSS to access Key/Vault has been created for home region " + home_region)

    print("\nPlease run terraform apply from home region directory to create policy first and then proceed to run terraform apply for OSS/Key/Vault in specified region directory")
    print("terraform apply will create below components ")
    print(prefix + "-oss-kms-policy")
    print("under root compartment and below components under compartment "+cname+ " : ")
    print(prefix + "-kms-vault")
    print(prefix + "-kms-key")
    print(prefix + "-oss-bucket")
    print(prefix + "-oss-log-group")
    print(prefix + "-oss-log")

if __name__ == '__main__':
    args = parse_args()
    create_cis_oss(args.outdir, args.prefix, args.region_name, args.comp_name, args.config)

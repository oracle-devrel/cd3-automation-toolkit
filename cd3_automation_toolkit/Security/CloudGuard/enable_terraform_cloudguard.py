#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI security components
# Cloud Guard
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from commonTools import *

######
# Required Inputs- Config file, prefix AND outdir
######
# Execution of the code begins here
def enable_cis_cloudguard(outdir, service_dir,prefix, ct, region):

    #home_region=ct.home_region
    region_key = ct.region_dict[region]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    cgconfigtemplate = env.get_template('cloud-guard-config-template')
    cgtargettemplate = env.get_template('cloud-guard-target-template')
    cg_auto_tfvars_filename = "cis-cloudguard.auto.tfvars"


    tempStr ={}
    configtfStr = ''
    targettfStr = ''

    compartment_id = 'root'
    cg_tf_name = prefix+"-cloud_guard"
    cg_target_tf_name = prefix + "-" + compartment_id +"-cloudguard-target"
    cg_target_name = prefix + "-" + compartment_id +"-cloudguard-target"
    cg_target_desc = "Cloud Guard for root compartment for "+prefix
    cg_target_comp_tf_name='root'

    tempStr['compartment_tf_name'] = str(compartment_id).strip()
    tempStr['region'] = region_key
    tempStr['cg_tf_name'] = cg_tf_name
    tempStr['cg_target_tf_name'] = cg_target_tf_name
    tempStr['cg_target_name'] = cg_target_name
    tempStr['cg_target_desc'] = cg_target_desc
    tempStr['cg_target_comp_tf_name'] = cg_target_comp_tf_name
    tempStr['cg_target_comp_tf_name'] = cg_target_comp_tf_name
    tempStr['prefix'] = prefix

    configtfStr = configtfStr + cgconfigtemplate.render(tempStr)
    targettfStr = targettfStr + cgtargettemplate.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + region + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/" + cg_auto_tfvars_filename

    srcdir = reg_out_dir + "/"
    resource = 'cloudguard'
    commonTools.backup_file(srcdir, resource, cg_auto_tfvars_filename)

    if configtfStr != '':
        # Generate Final String
        src = "##Add New Cloud Guard Configurations for " + region + " here##"
        configtfStr = cgconfigtemplate.render(skeleton=True, count=0, region=region).replace(src, configtfStr+"\n"+src)

    if targettfStr != '':
        # Generate Final String
        src = "##Add New Cloud Guard Targets for " + region + " here##"
        targettfStr = cgtargettemplate.render(skeleton=True, count=0, region=region).replace(src, targettfStr+"\n"+src)

    finalstring = configtfStr + "\n" + targettfStr
    finalstring = "".join([s for s in finalstring.strip().splitlines(True) if s.strip("\r\n").strip()])

    if(finalstring!=''):
        oname=open(outfile,'w+')
        oname.write(finalstring)
        oname.close()
        print(outfile + " containing TF for cloud-guard has been created for region "+region)
        print("Once you apply the Terraform, Cloud Guard will be enabled from the specified Region, cloned recipes will be created from Oracle Managed recipes and Target will be created with cloned Recipes for the root compartment")

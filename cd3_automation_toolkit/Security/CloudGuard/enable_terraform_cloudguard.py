#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Cloud Guard
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
    parser.add_argument("service_dir",help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("--configFileName", help="Config file name", required=False)
    return parser.parse_args()


def enable_cis_cloudguard(outdir, service_dir,prefix, config=DEFAULT_LOCATION):
    configFileName = config
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    home_region=ct.home_region
    home_region_key = ct.region_dict[home_region]

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
    cg_target_tf_name = prefix + "-cloudguard-target"
    cg_target_name = prefix + "-cloudguard-target"
    cg_target_desc = "Cloud Guard for root compartment for "+prefix
    cg_target_comp_tf_name='root'

    tempStr['compartment_tf_name'] = str(compartment_id).strip()
    tempStr['home_region'] = home_region_key
    tempStr['cg_tf_name'] = cg_tf_name
    tempStr['cg_target_tf_name'] = cg_target_tf_name
    tempStr['cg_target_name'] = cg_target_name
    tempStr['cg_target_desc'] = cg_target_desc
    tempStr['cg_target_comp_tf_name'] = cg_target_comp_tf_name
    tempStr['cg_target_comp_tf_name'] = cg_target_comp_tf_name
    tempStr['target_detector_recipes'] = [ "OCI_Activity_Detector_Recipe","OCI_Configuration_Detector_Recipe","OCI_Threat_Detector_Recipe"]
    tempStr['target_responder_recipes'] = ["OCI_Responder_Recipe"]

    configtfStr = configtfStr + cgconfigtemplate.render(tempStr)
    targettfStr = targettfStr + cgtargettemplate.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + home_region + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/" + cg_auto_tfvars_filename

    srcdir = reg_out_dir + "/"
    resource = 'cloudguard'
    commonTools.backup_file(srcdir, resource, cg_auto_tfvars_filename)

    if configtfStr != '':
        # Generate Final String
        src = "##Add New Cloud Guard Configurations for " + home_region + " here##"
        configtfStr = cgconfigtemplate.render(skeleton=True, count=0, region=home_region).replace(src, configtfStr+"\n"+src)

    if targettfStr != '':
        # Generate Final String
        src = "##Add New Cloud Guard Targets for " + home_region + " here##"
        targettfStr = cgtargettemplate.render(skeleton=True, count=0, region=home_region).replace(src, targettfStr+"\n"+src)

    finalstring = configtfStr + "\n" + targettfStr
    finalstring = "".join([s for s in finalstring.strip().splitlines(True) if s.strip("\r\n").strip()])

    if(finalstring!=''):
        oname=open(outfile,'w+')
        oname.write(finalstring)
        oname.close()
        print(outfile + " containing TF for cloud-guard has been created for region "+home_region)
        print("TF has been generated in Home Region Directory.\nOnce you apply the Terraform, Cloud Guard will be enabled from Home Region and Target will be created with Oracle Managed Recipes for root compartment.")

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    enable_cis_cloudguard(args.outdir, args.service_dir, args.prefix, args.config)

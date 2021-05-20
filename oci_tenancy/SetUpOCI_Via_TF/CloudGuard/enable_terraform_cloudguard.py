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
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--configFileName", help="Config file name", required=False)
    return parser.parse_args()


def enable_cis_cloudguard(outdir, prefix, config=DEFAULT_LOCATION):
    configFileName = config
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    home_region=ct.home_region
    home_region_key = ct.region_dict[home_region]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('cloudguard-template')

    tempStr ={}
    tfStr = ''

    compartment_id = 'tenancy_ocid'
    cg_tf_name = prefix+"-cloud_guard"
    cg_target_tf_name = prefix + "-cloudguard-target"
    cg_target_name = prefix + "-cloudguard-target"
    cg_target_desc = "Cloud Guard for root compartment for "+prefix
    cg_target_comp_tf_name='tenancy_ocid'

    tempStr['compartment_tf_name'] = str(compartment_id).strip()
    tempStr['home_region'] = home_region_key
    tempStr['cg_tf_name'] = cg_tf_name
    tempStr['cg_target_tf_name'] = cg_target_tf_name
    tempStr['cg_target_name'] = cg_target_name
    tempStr['cg_target_desc'] = cg_target_desc
    tempStr['cg_target_comp_tf_name'] = cg_target_comp_tf_name

    tfStr=tfStr + template.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + home_region
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/cis-cloudguard.tf"

    srcdir = reg_out_dir + "/"
    resource = 'cloudguard'
    commonTools.backup_file(srcdir, resource, "cis-cloudguard.tf")

    if(tfStr!=''):
        oname=open(outfile,'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for cloud-guard has been created for region "+home_region)

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    enable_cis_cloudguard(args.outdir, args.prefix, args.config)

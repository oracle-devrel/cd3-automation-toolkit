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
    parser = argparse.ArgumentParser(description="Create Budget terraform file")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("amount", help="budget amount")
    parser.add_argument("threshold", help="budget threshold percentage")
    parser.add_argument("--configFileName", help="Config file name", required=False)
    return parser.parse_args()

def create_cis_budget(outdir, prefix, amount, threshold,config=DEFAULT_LOCATION):

    # Declare variables
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)



    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('budget-template')
    template_alert_rule = env.get_template('budget-alert-rule-template')

    tempStr = {}

    tfStr = ''

    budget_name = prefix+"-main-budget"
    tempStr['budget_name'] = budget_name
    tempStr['budget_tf_name'] = budget_name
    tempStr['amount'] = amount
    tempStr['description'] = "Tracks spending from the root compartment and down"
    tempStr['period_start'] = "1"
    tempStr['target_type'] = 'COMPARTMENT'
    tempStr['target_ocid'] = 'var.tenancy_ocid'
    tfStr = tfStr + template.render(tempStr)+"\n"

    tempStr = {}
    tempStr['budget_name'] = budget_name
    tempStr['budget_tf_name'] = budget_name
    tempStr['threshold_type'] = "PERCENTAGE"
    tempStr['type']="FORECAST"
    tempStr['threshold']=threshold
    tempStr["description"]="Budget Alert Rule"
    tfStr = tfStr + template_alert_rule.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + ct.home_region
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/cis-budget.tf"

    srcdir = reg_out_dir + "/"
    resource = 'budget'
    commonTools.backup_file(srcdir, resource, "cis-budget.tf")


    if(tfStr!=''):
        oname=open(outfile,'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for Budget has been created for home region "+ct.home_region)

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_cis_budget(args.outdir, args.prefix, args.config, args.amount,args.threshold)

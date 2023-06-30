#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Budget
# Key/Vault
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
def create_cis_budget(outdir, service_dir, prefix, amount, threshold,config=DEFAULT_LOCATION):

    # Declare variables
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('budget-template')
    template_alert_rule = env.get_template('budget-alert-rule-template')
    budget_auto_tfvars_filename = "cis-budget.auto.tfvars"

    tempStr = {}

    budgettfStr = ''
    budgetalerttfStr = ''

    budget_name = prefix+"-main-budget"
    tempStr['budget_name'] = budget_name
    tempStr['budget_tf_name'] = budget_name
    tempStr['amount'] = amount
    tempStr['description'] = "Tracks spending from the root compartment and down"
    tempStr['period_start'] = "1"
    tempStr['target_type'] = 'COMPARTMENT'
    tempStr['target_ocid'] = 'root'
    budgettfStr = budgettfStr + template.render(tempStr)+"\n"

    tempStr = {}
    tempStr['budget_name'] = budget_name
    tempStr['budget_tf_name'] = budget_name
    tempStr['threshold_type'] = "PERCENTAGE"
    tempStr['type']="FORECAST"
    tempStr['threshold']=threshold
    tempStr["description"]="Budget Alert Rule"
    budgetalerttfStr = budgetalerttfStr + template_alert_rule.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + ct.home_region + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/" + budget_auto_tfvars_filename

    srcdir = reg_out_dir + "/"
    resource = 'budget'
    commonTools.backup_file(srcdir, resource, budget_auto_tfvars_filename)

    budgettfStr = template.render(count=0,region=ct.home_region).replace("##Add New Budgets for "+ct.home_region+" here##",budgettfStr)
    budgetalerttfStr = template_alert_rule.render(count=0, region=ct.home_region).replace("##Add New Budget Alert Rules for " + ct.home_region + " here##", budgetalerttfStr)
    budgettfStr = budgettfStr + "\n" + budgetalerttfStr

    if(budgettfStr!=''):
        budgettfStr = "".join([s for s in budgettfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname=open(outfile,'w+')
        oname.write(budgettfStr)
        oname.close()
        print(outfile + " containing TF for Budget has been created for home region "+ct.home_region)

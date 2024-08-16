#!/usr/bin/python3
# Copyright (c) 2024 Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export budgets
#
#Author: Bhanu P. Lohumi
#Oracle Consulting
#

import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../..")
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_budgets(inputfile, outdir, service_dir, prefix,ct):
    filename = inputfile
    sheetName = "Budgets"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'
    tfStr_budget = {}
    tfStr_budget_alert_rule = {}
    reg_budget_done = []
    tempStr = {}
    prev_budget = ""
    prev_region = ""

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    budget_template = env.get_template('budget-template')
    budget_alert_template = env.get_template('budget-alert-rule-template')

    # Read CD3
    df = data_frame(filename, sheetName)
    regions = df['Region']
    regions.dropna()

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in [ct.home_region]:
        tfStr_budget[eachregion] = ''
        tfStr_budget_alert_rule[eachregion] = ''
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir + "/", resource, auto_tfvars_filename)


    for i in df.index:
        alert_tf_name = ""
        region = str(df.loc[i,"Region"])
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if (region == 'nan'):
            pass
        if region!='nan' and region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)
        region = region if region != 'nan' else prev_region
        prev_region = region
        # Temporary dictionary1
        tempdict = {}


        # Check if values are entered for mandatory fields
        #### to be added
        current_budget = str(df.loc[i, 'Name'])
        budget_name = current_budget if current_budget != 'nan' else prev_budget
        prev_budget = budget_name
        budget_tf_name = commonTools.check_tf_variable(budget_name)

        alert_rules = str(df.loc[i,'Alert Rules']).strip()
        if alert_rules != 'nan':
            alert_list = alert_rules.split("::")
            if len(alert_list) < 2:
                print("Provide correct value to \"Alert Rules\" ")
                exit(1)
            alert_type = str(alert_list[0]).strip().upper()
            if "%" in str(alert_list[1]):
                alert_threshold_type = "PERCENTAGE"
                alert_threshold = str(alert_list[1])[:-1]
            else:
                alert_threshold_type = "ABSOLUTE"
                alert_threshold = str(alert_list[1])

            alert_tf_name = budget_tf_name + "_" + alert_type + "_" + alert_threshold_type+ "_" + alert_threshold
            tempStr['alert_tf_name'] = commonTools.check_tf_variable(alert_tf_name)
            tempStr['type'] = alert_type
            tempStr['threshold'] = alert_threshold
            tempStr['threshold_type'] = alert_threshold_type

        tempStr['budget_tf_name'] = budget_tf_name
        tempStr['budget_name'] = budget_name


        # Fetch data; loop through columns
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df.loc[i, columnname])

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            #Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Name":
                tempdict = {'budget_name': budget_name}

            elif columnname == 'Description':
                tempdict = {'description': columnvalue}

            # Process Freeform Tags and Defined Tags
            elif columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            elif columnname == "Scope":
                tempdict = {'target_type': columnvalue.upper().strip()}

            elif columnname == "Target":
                columnvalue = columnvalue.strip()
                scope = str(df.loc[i, "Scope"]).strip()
                if (scope.upper()=="COMPARTMENT"):
                    if ("ocid1.compartment.oc" not in columnvalue):
                        columnvalue=commonTools.check_tf_variable(columnvalue)
                tempdict = {'target': columnvalue}

            elif (columnname == 'Schedule'):
                tempdict = {'processing_period_type': columnvalue.upper().strip()}

            elif (columnname == 'Amount'):
                tempdict = {'amount': columnvalue.strip()}

            elif columnname == "Start Day" and columnvalue != 'nan':
                tempdict = {'period_start': columnvalue.strip()}

            elif columnname == "Budget Start Date" and columnvalue != 'nan':
                tempdict = {'budget_start_date': columnvalue.strip()}

            elif columnname == "Budget End Date" and columnvalue != 'nan':
                tempdict = {'budget_end_date': columnvalue.strip()}

            elif columnname == "Alert Recipients" and columnvalue != 'nan':
                tempdict = {'alert_recipients': columnvalue.strip()}

            elif columnname == "Alert Message" and columnvalue != 'nan':
                tempdict = {'alert_message': columnvalue}

            else:
                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = str(columnvalue).strip()

            tempStr.update(tempdict)

        # Write all info to TF string
        reg_budget = region.lower()+budget_tf_name
        if reg_budget not in reg_budget_done:
            tfStr_budget[region] = tfStr_budget[region] + budget_template.render(tempStr)
            reg_budget_done.append(reg_budget)
        if alert_tf_name:
            tfStr_budget_alert_rule[region] = tfStr_budget_alert_rule[region] + budget_alert_template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in [ct.home_region]:

        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if tfStr_budget[reg] != '':
            outfile = outdir + "/" + reg + "/" + service_dir + "/" + auto_tfvars_filename

            budget_str = "##Add New Budgets for " + reg.lower() + " here##"
            budget_alert_Str = "##Add New Budgets-Alert-Rules for " + reg.lower() + " here##"

            tfStr_budget[reg] = budget_template.render(count=0, region=reg).replace(budget_str,tfStr_budget[reg])
            tfStr_budget[reg] += budget_alert_template.render(count=0, region=reg).replace(budget_alert_Str,tfStr_budget_alert_rule[reg])
            tfStr_budget[reg] = "".join([s for s in tfStr_budget[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            oname = open(outfile, "w+")
            oname.write(tfStr_budget[reg])
            oname.close()
            print(outfile + " for Budgets has been created for region " + reg)


#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Modify Security Rules
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import csv
import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *
# Execution of the code begins here
def modify_terraform_secrules(inputfile, outdir, service_dir,prefix, ct, non_gf_tenancy):

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    default_seclist = env.get_template('default-seclist-template')
    secrule = env.get_template('sec-rule-template')
    seclist = env.get_template('seclist-template')

    secrulesfilename = inputfile

    seclists_done = {}
    default_ruleStr = {}
    default_seclists_done = {}
    defaultname = {}
    auto_tfvars_filename = "_seclists.auto.tfvars"
    default_auto_tfvars_filename = "_default-seclists.auto.tfvars"
    vcns = parseVCNs(secrulesfilename)

    def generate_security_rules(region_seclist_name,processed_seclist,tfStr,region,tempStr, ingress_rule, tempdict2, egress_rule):
        if region_seclist_name not in processed_seclist:
            tfStr[region] = tfStr[region] + seclist.render(tempStr,
                                                                 ingress_sec_rules="####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",
                                                                 egress_sec_rules="####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####")

            processed_seclist.append(region_seclist_name)

        if str(row['Rule Type']).lower() == 'ingress':
            new_ingress_sec_rule = ct.create_ingress_rule_string(secrule, tempStr, ingress_rule, tempdict2, region_seclist_name)
            tfStr[region] = tfStr[region].replace("####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####", new_ingress_sec_rule)

        if str(row['Rule Type']).lower() == 'egress':
            new_egress_sec_rule = ct.create_egress_rule_string(secrule, tempStr, egress_rule, tempdict2, region_seclist_name)
            tfStr[region] = tfStr[region].replace("####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####", new_egress_sec_rule)

        return tfStr[region]

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(secrulesfilename, "SecRulesinOCI")
    df = df.to_csv('out.csv')

    totalRowCount = sum(1 for row in csv.DictReader(ct.skipCommentedLine(open('out.csv'))))
    i = 0
    region_included = []
    tempSkeleton = {}
    default_seclist_tempSkeleton = {}
    sectfStr = {}
    deftfStr = {}

    for reg in ct.all_regions:
        default_ruleStr[reg] = ''
        default_seclists_done[reg] = []
        seclists_done[reg] = []
        tempSkeleton[reg] = ''
        deftfStr[reg] = ''
        default_seclist_tempSkeleton[reg] = ''
        sectfStr[reg] = ''

        # Backup existing seclist files in ash and phx dir
        resource = "SLs"
        commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, prefix+auto_tfvars_filename)
        commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, prefix + default_auto_tfvars_filename)

    with open('out.csv') as secrulesfile:
        reader = csv.DictReader(secrulesfile)
        ingress_rule = ''
        egress_rule = ''
        processed_seclist = []

        for row in reader:
            display_name = row['SecList Name']
            vcn_name = row['VCN Name']
            vcn_tf_name = commonTools.check_tf_variable(vcn_name)
            comp_name = row['Compartment Name']
            rt_var = vcn_name + "_" + display_name
            seclist_tf_name = commonTools.check_tf_variable(rt_var)

            region = row['Region']
            if (region in commonTools.endNames):
                break
            region = region.strip().lower()

            region_seclist_name = "#"+region+"_"+seclist_tf_name+"#"

            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)
                # Check if values are entered for mandatory fields
            if (region == 'nan' or str(vcn_name).lower() == 'nan' or str(comp_name).lower() == 'nan'):
                    print("\nColumn Region, VCN Name and Compartment Name cannot be left empty in SecRulesinOCI sheet of CD3..Exiting!")
                    exit(1)

            # Process only those VCNs which are present in cd3(and have been created via TF)

            check = vcn_name.strip(), region
            if (check not in vcns.vcn_names):
                print("\nskipping seclist: " + display_name + " as its VCN is not part of VCNs tab in cd3")
                continue

            if (str(display_name).lower() == "nan"):
                continue

            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            # temporary dictionary1, dictionary2 and list
            tempStr = {}
            tempdict = {'vcn_tf_name': vcn_tf_name, 'rt_var': rt_var, 'seclist_tf_name': seclist_tf_name,
                        'region': region}
            tempdict2= {}


            tempStr.update({'count': 1})
            if ('Default Security List for' in display_name.strip()):
                if ('Default Security List for'+region not in region_included):
                    tempStr.update({'count': 0})
                    region_included.append('Default Security List for'+region)
            elif region not in region_included:
                    tempStr.update({'count': 0})
                    region_included.append(region)

            # Create Skeleton Template
            if tempStr['count'] == 0:
                if ('Default Security List for' in display_name.strip()):
                    default_seclist_tempSkeleton[region] = default_seclist.render(tempStr,skeleton=True,region=region)
                elif ('Default Security List for' not in display_name.strip()):
                    tempSkeleton[region] = seclist.render(tempStr,skeleton=True,region=region)

            for columnname in row:

                # Column value
                if 'description' in columnname.lower():
                    columnvalue = str(row[columnname])
                    tempdict = {'rule_description': columnvalue}
                else:
                    columnvalue = str(row[columnname]).strip()

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Check for multivalued columns
                if columnname.lower() not in ["source", "destination"]: # this is to support IPv6 CIDRs as it contains "::"
                    tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

                # Process Defined and Freeform Tags
                if columnname.lower() in commonTools.tagColumns:
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

                if columnname == 'SecList Name':
                    display_name = columnvalue.strip()
                    tempdict = {'display_name': display_name}

                if columnname == 'Compartment Name':
                    columnname = 'compartment_name'
                    compartment_tf_name =  commonTools.check_tf_variable(columnvalue.strip())
                    tempdict = {'compartment_tf_name': compartment_tf_name}

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = str(columnvalue).strip()
                tempStr.update(tempdict)

            if ('Default Security List for' in display_name):
                deftfStr[region] = generate_security_rules(region_seclist_name = region_seclist_name,processed_seclist = processed_seclist,tfStr =deftfStr, region=region,tempStr = tempStr, ingress_rule = ingress_rule, tempdict2 = tempdict2, egress_rule= egress_rule)
            elif ('Default Security List for' not in display_name.strip()):
                sectfStr[region] = generate_security_rules(region_seclist_name = region_seclist_name,processed_seclist = processed_seclist,tfStr =sectfStr, region=region,tempStr = tempStr, ingress_rule = ingress_rule, tempdict2 = tempdict2, egress_rule= egress_rule)

    for reg in ct.all_regions:
        textToAddSeclistSearch = "##Add New Seclists for " + reg + " here##"
        defaultTextToAddSeclistSearch = "##Add New Default Seclists for " + reg + " here##"

        outfile = outdir + "/" + reg + "/" + service_dir+ "/" + prefix + auto_tfvars_filename
        default_outfile = outdir + "/" + reg + "/" + service_dir+ "/" + prefix + default_auto_tfvars_filename

        default_seclist_tempSkeleton[reg] = default_seclist_tempSkeleton[reg].replace(defaultTextToAddSeclistSearch,deftfStr[reg] +"\n"+ defaultTextToAddSeclistSearch)
        tempSkeleton[reg] = tempSkeleton[reg].replace(textToAddSeclistSearch,sectfStr[reg] + textToAddSeclistSearch)
        none_rule = """[
        ####ADD_NEW_"""
        optional_data = """[
           {
            options = {
                none = []
                }
            }
        ####ADD_NEW_"""
        default_seclist_tempSkeleton[reg] = default_seclist_tempSkeleton[reg].replace(none_rule,optional_data)
        tempSkeleton[reg] = tempSkeleton[reg].replace(none_rule,optional_data)

        if sectfStr[reg] != '':
            tempSkeleton[reg] = "".join([s for s in tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            oname.write(tempSkeleton[reg])
            oname.close()
            print(outfile + " for seclist has been created for region " + reg)

        if deftfStr[reg] != '':
            default_seclist_tempSkeleton[reg] = "".join([s for s in default_seclist_tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(default_outfile, "w+")
            oname.write(default_seclist_tempSkeleton[reg])
            oname.close()
            print(default_outfile + " for default seclist has been created for region " + reg)


    os.remove('out.csv')

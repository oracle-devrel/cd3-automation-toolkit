#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Security List
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import re
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + '/../../..')
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, Modify Network AND outdir
######
# Execution of the code begins here
def create_terraform_seclist(inputfile, outdir, service_dir, prefix,ct, modify_network=False):

    def purge(dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                print("Purge ....." + os.path.join(dir, f))
                os.remove(os.path.join(dir, f))


    filename = inputfile

    tempSkeleton = {}
    tempSecList = {}
    modify_network_seclists = {}
    tempSecListModifyNetwork = {}
    ADS = ["AD1", "AD2", "AD3"]

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('seclist-template')
    secrule = env.get_template('sec-rule-template')

    auto_tfvars_filename = "_seclists.auto.tfvars"
    common_seclist = []
    seclists_from_secRulesInOCI_sheet = []

    # Option "Modify Network"
    if modify_network:
        # Read cd3 using pandas dataframe
        dfseclist, col_headers = commonTools.read_cd3(filename, "SecRulesinOCI")

        dfseclist = dfseclist.dropna(how='all')
        dfseclist = dfseclist.reset_index(drop=True)

        # Start processing each seclist
        for i in dfseclist.index:
            region = dfseclist.loc[i, 'Region']
            if (region in commonTools.endNames):
                break
            seclists_tf_from_secRulesInOCI_sheet_name = "#"+commonTools.check_tf_variable(dfseclist.loc[i, 'Region']).lower()+"_"+commonTools.check_tf_variable(dfseclist.loc[i, 'VCN Name'])+"_"+commonTools.check_tf_variable(dfseclist.loc[i, 'SecList Name'])+"#"
            if seclists_tf_from_secRulesInOCI_sheet_name not in seclists_from_secRulesInOCI_sheet:
                seclists_from_secRulesInOCI_sheet.append(seclists_tf_from_secRulesInOCI_sheet_name)

    for reg in ct.all_regions:
        tempSkeleton[reg] = ''
        tempSecList[reg] = ''
        modify_network_seclists[reg] = ''
        tempSecListModifyNetwork[reg] = ''

    def processSubnet(tempStr, service_dir):
        filedata = ""
        region_in_lowercase = tempStr['region'].lower().strip()
        subnet_cidr = tempStr['cidr_block'].strip()
        seclist_count = 0

        # Seclist name specifiied as 'n' - dont create any seclist
        if tempStr['seclist_names'].lower() == 'n':
            # Create Skeleton Template
            if seclist_count == 0 and tempStr['count'] == 0:
                tempSkeleton[region_in_lowercase] = template.render(tempStr,skeleton=True)

            return

        vcn_name = tempStr['vcn_name']
        vcn_tf_name = commonTools.check_tf_variable(tempStr['vcn_name'])
        tempStr['vcn_tf_name'] = vcn_tf_name

        seclist_names = tempStr['sl_names']
        index = 0

        for sl_name in seclist_names:
            sl_name = sl_name.strip()
            display_name = sl_name
            tempStr['display_name'] = display_name

            sl_tf_name = vcn_name+ "_" + display_name
            sl_tf_name = commonTools.check_tf_variable(sl_tf_name)
            tempStr['seclist_tf_name'] = sl_tf_name

            outfile = outdir + "/" + region_in_lowercase + "/" + service_dir +"/" + prefix + auto_tfvars_filename

            # Create Skeleton Template
            if seclist_count == 0 and tempStr['count'] == 0:
                tempSkeleton[region_in_lowercase] = template.render(tempStr,skeleton=True)

            region_seclist_name = "#"+region_in_lowercase + "_" + sl_tf_name+"#"
            start = "# Start of " + region_seclist_name + " #"
            end = "# End of " + region_seclist_name + " #"

            # Option "Modify Network"
            if modify_network:

                # Read the file if it exists
                if os.path.exists(outfile):
                    # Read the contents of file in outdir
                    with open(outfile, 'r+') as file:
                        filedata = file.read()
                    file.close()

                # If seclist is present in auto.tfvars but not in modify_network_seclists
                if start in filedata:
                    if start not in modify_network_seclists[region_in_lowercase]:
                        modify_network_seclists[region_in_lowercase] = ct.copy_data_from_file(outfile,region_seclist_name,modify_network_seclists[region_in_lowercase])

                for seclists in seclists_from_secRulesInOCI_sheet:
                    if "# Start of " + seclists + " #" in filedata and "# Start of " + seclists + " #" not in modify_network_seclists[region_in_lowercase]:
                        modify_network_seclists[region_in_lowercase] = ct.copy_data_from_file(outfile, seclists,modify_network_seclists[region_in_lowercase])

            # Create Seclist for all the unique names in Subnet Sheet
            if (start not in modify_network_seclists[region_in_lowercase] and region_seclist_name not in common_seclist):
                modify_network_seclists[region_in_lowercase] = modify_network_seclists[region_in_lowercase]+ template.render(tempStr,ingress_sec_rules="####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",egress_sec_rules="####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####")
                seclist_count = seclist_count + 1

            # If same seclist name is used for subsequent subnets
            if (index == 0 and start in modify_network_seclists[region_in_lowercase] and region_seclist_name in common_seclist and region_seclist_name not in filedata):
                tempStr['rule_type'] = "ingress"
                tempStr['source'] = subnet_cidr
                tempStr['protocol_code'] = 'all'
                tempStr['protocol'] = 'all'
                tempStr['isstateless'] = "false"

                if "#"+sl_tf_name+"_"+subnet_cidr+"#" not in modify_network_seclists[region_in_lowercase]:
                    # Replace the target string
                    Str = secrule.render(tempStr)
                    textToSearch = "####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####"
                    Str = Str + "\n" + textToSearch
                    modify_network_seclists[region_in_lowercase] = modify_network_seclists[region_in_lowercase].replace(textToSearch, Str)
                    index = index + 1
                    common_seclist.append(region_seclist_name)
                    continue

            # Create seclist rules for new seclists
            if index != 0:
                modify_network_seclists[region_in_lowercase] = modify_network_seclists[region_in_lowercase] + "\n"
            elif index == 0:
                if modify_network and start in filedata and end in filedata:
                    index = index + 1
                    common_seclist.append(region_seclist_name)
                    continue
                else:
                    rule_type = ['ingress','egress']
                    for rule in rule_type:
                        tempStr['destination'] = '0.0.0.0/0'
                        tempStr['protocol_code'] = 'all'
                        tempStr['protocol'] = 'all'
                        tempStr['source'] = subnet_cidr
                        tempStr['rule_type'] = rule
                        tempStr['isstateless'] = "false"
                        if rule == 'ingress':
                            ingress_secrule_data = secrule.render(tempStr)
                            textToSearch = "####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####"
                            ingress_secrule_data = ingress_secrule_data + "\n" + textToSearch
                            modify_network_seclists[region_in_lowercase] = modify_network_seclists[region_in_lowercase].replace(textToSearch, ingress_secrule_data)
                        else:
                            egress_secrule_data = secrule.render(tempStr)
                            textToSearch = "####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####"
                            egress_secrule_data = egress_secrule_data + "\n" + textToSearch
                            modify_network_seclists[region_in_lowercase] = modify_network_seclists[region_in_lowercase].replace(textToSearch, egress_secrule_data)

            index = index + 1
            common_seclist.append(region_seclist_name)

    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Purge existing seclist files
    if not modify_network:
        for reg in ct.all_regions:
            purge(outdir + "/" + reg + "/" +service_dir + "/", prefix + auto_tfvars_filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "SubnetsVLANs")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    region_included = []

    # Start processing each subnet
    for i in df.index:
        region = df.loc[i, 'Region']
        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Skip row if it's a VLAN
        subnet_vlan_in_excel = str(df.loc[i, 'Subnet or VLAN']).strip()
        if 'vlan' in subnet_vlan_in_excel.lower():
            continue

        # temporary dictionary1, dictionary2, string  and list
        tempStr = {}
        tempdict = {}
        sl_names = []

        compartment_var_name = ''

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i,'VCN Name']).lower() == 'nan':
            print("\nThe values for Region, Compartment Name and VCN Name cannot be left empty in Subnets Tab. Please enter a value and try again !!")
            exit(1)

        for columnname in dfcolumns:
            # Column value
            if (columnname != 'Rule Description'):
                columnvalue = str(df[columnname][i]).strip()
            else:
                columnvalue = str(df[columnname][i])

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process the Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue
            vcn_name = str(df.loc[i,'VCN Name'].strip())

            check = vcn_name.strip(), region
            if (check not in vcns.vcn_names):
                print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
                exit(1)

            if columnname == 'Availability Domain(AD1|AD2|AD3|Regional)':
                columnname = 'availability_domain'
                columnvalue = columnvalue.strip()

            if columnname == 'Seclist Names':
                columnvalue = columnvalue.strip()
                if columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    sl_names = columnvalue.split(",")
                else:
                    sl_names.append(str(df.loc[i,'Display Name']).strip())
                compartment_var_name = compartment_var_name.strip()
                tempdict = {'compartment_tf_name' : compartment_var_name, 'sl_names' : sl_names}

            #Added to check if compartment name is compatible with TF variable name syntax
            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = columnvalue
            tempStr.update(tempdict)

        tempStr.update({'count': 1})
        if region not in region_included:
            tempStr.update({'count': 0})
            region_included.append(region)

        processSubnet(tempStr,service_dir)

    for reg in ct.all_regions:
        textToAddSeclistSearch = "##Add New Seclists for "+reg+" here##"
        outfile = outdir + "/" + reg + "/" + service_dir + "/" +prefix + auto_tfvars_filename

        if modify_network_seclists[reg] != '':
            if reg in region_included:
                if not modify_network:
                    tempSkeleton[reg] = tempSkeleton[reg].replace(textToAddSeclistSearch,modify_network_seclists[reg] + textToAddSeclistSearch)
                    none_rule = """[
        ####ADD_NEW_"""
                    optional_data = """[
           {
            options = {
                none = []
                }
            }
####ADD_NEW_"""
                    tempSkeleton[reg] = tempSkeleton[reg].replace(none_rule, optional_data)
                    tempSkeleton[reg] = "".join([s for s in tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                    oname = open(outfile, "w+")
                    oname.write(tempSkeleton[reg])
                    oname.close()
                    print(outfile + " containing seclists has been created for region " + reg)
                else:
                    tempSkeleton[reg] = tempSkeleton[reg].replace(textToAddSeclistSearch,modify_network_seclists[reg] + textToAddSeclistSearch)
                    srcdir = outdir + "/" + reg + "/" + service_dir + "/"
                    resource = 'SLs'
                    commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
                    none_rule = """[
        ####ADD_NEW_"""
                    optional_data = """[
                               {
                                options = {
                                    none = []
                                    }
                                }
####ADD_NEW_"""
                    tempSkeleton[reg] = tempSkeleton[reg].replace(none_rule, optional_data)
                    tempSkeleton[reg] = "".join([s for s in tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                    oname = open(outfile, "w+")
                    oname.write(tempSkeleton[reg])
                    oname.close()
                    print(outfile + " containing seclists has been updated for region " + reg)
            else:
                if reg not in region_included:
                    srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                    resource = 'SLs'
                    commonTools.backup_file(srcdir, resource, 'seclists.auto.tfvars')
        else:
            srcdir = outdir + "/" + reg + "/" + service_dir +"/"
            resource = 'SLs'
            commonTools.backup_file(srcdir, resource, '_seclists.auto.tfvars')

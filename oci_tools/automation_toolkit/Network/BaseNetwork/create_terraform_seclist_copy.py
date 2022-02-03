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

import argparse
import csv
import re
import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *


def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Takes in an input file mentioning sec rules to be added for the subnet. See update_seclist-example.csv/CD3 for format under example folder. It will then take backup of all existing sec list files in outdir and create new one with modified rules")
    parser.add_argument("inputfile",help="Full Path of input file: It could be either the properties file eg CD3 excel file")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


def modify_terraform_secrules(inputfile, outdir, prefix=None, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    defaultseclist = env.get_template('default-seclist-template')
    secrule = env.get_template('module-sec-rule-template')
    seclist = env.get_template('module-seclist-template')

    secrulesfilename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    seclists_done = {}
    default_ruleStr = {}
    default_seclists_done = {}
    defaultname = {}
    auto_tfvars_filename = "_seclist.auto.tfvars"
    vcns = parseVCNs(secrulesfilename)

    def skipCommentedLine(lines):
        """
        A filter which skip/strip the comments and yield the
        rest of the lines
        :param lines: any object which we can iterate through such as a file
        object, list, tuple, or generator
        """
        for line in lines:
            comment_pattern = re.compile(r'\s*#.*$')
            line = re.sub(comment_pattern, '', line)
            if line:
                yield line


    def create_ingress_rule_string(tempStr,ingress_rule,tempdict2):

        rule_desc = tempStr['rule_description']
        protocol = tempStr['protocol'].lower().strip()
        isstateless = str(tempStr['isstateless'].lower())
        if (str(rule_desc).lower() == "nan" or str(rule_desc).lower() == ""):
            rule_desc = ""
            tempdict2 ={'rule_description' : rule_desc}
        else:
            rule_desc = str(rule_desc)
            tempdict2 = {'rule_description': rule_desc}
        tempStr.update(tempdict2)

        if ("services-in-oracle-services-network" in tempStr['source'] or "objectstorage" in tempStr['source']):
            source_type = "SERVICE_CIDR_BLOCK"
            tempdict2 = {'source_type' : source_type}
        tempStr.update(tempdict2)

        tempdict2 = {'protocol_code': get_protocol(protocol),'isstateless':isstateless}
        tempStr.update(tempdict2)

        ingress_rule = ingress_rule + secrule.render(tempStr)
        ingress_rule = ingress_rule + "\n" + "####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####"
        return ingress_rule


    def create_egress_rule_string(tempStr,egress_rule,tempdict2):

        rule_desc = tempStr['rule_description']
        protocol = tempStr['protocol'].lower().strip()
        isstateless = str(tempStr['isstateless'].lower())

        if (str(rule_desc).lower() == "nan"):
            rule_desc = ""
            tempdict2 ={'rule_description' : rule_desc}
        else:
            rule_desc = str(rule_desc)
            tempdict2 ={'rule_description' : rule_desc}
        tempStr.update(tempdict2)

        if ("services-in-oracle-services-network" in tempStr['destination'] or "objectstorage" in tempStr['destination']):
            destination_type = "SERVICE_CIDR_BLOCK"
            tempdict2 = {'destination_type': destination_type}
        tempStr.update(tempdict2)

        tempDict2 = {'protocol_code': get_protocol(protocol),'isstateless':isstateless}
        tempStr.update(tempDict2)

        egress_rule = egress_rule + secrule.render(tempStr)
        egress_rule = egress_rule + "\n" + "####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####"
        return egress_rule


    def get_protocol(strprotocol):
        if str(strprotocol).lower() == "all":
            return "all"
        else:
            protocol_dict = commonTools().protocol_dict
            for k, v in protocol_dict.items():
                if (strprotocol).lower() == v.lower():
                    return k


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(secrulesfilename, "SecRulesinOCI")
    df = df.to_csv('out.csv')

    totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open('out.csv'))))
    i = 0
    region_included = []
    tempSkeleton = {}
    tfStr = {}

    for reg in ct.all_regions:
        if (os.path.exists(outdir + "/" + reg)):
            defaultname[reg] = open(outdir + "/" + reg + "/VCNs_Default_SecList.tf", "w")
        default_ruleStr[reg] = ''
        default_seclists_done[reg] = []
        seclists_done[reg] = []
        tempSkeleton[reg] = ''
        tfStr[reg] = ''

        # Backup existing seclist files in ash and phx dir
        resource = "SLs"
        commonTools.backup_file(outdir + "/" + reg, resource, prefix+auto_tfvars_filename)

    with open('out.csv') as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        rowCount = 0

        oname = None

        ingress_rule = ''
        egress_rule = ''
        default_rules = ''
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

            region_seclist_name = region+"_"+seclist_tf_name

            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)
                # Check if values are entered for mandatory fields
            if (region == 'nan' or str(vcn_name).lower() == 'nan' or str(comp_name).lower() == 'nan'):
                    print("\nColumn Region, VCN Name and Compartment Name cannot be left empty in SecRulesinOCI sheet of CD3..Exiting!")
                    exit(1)

            # Process only those VCNs which are present in cd3(and have been created via TF)
            if (vcn_name not in vcns.vcn_names):
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
            if region not in region_included:
                tempStr.update({'count': 0})
                region_included.append(region)

            # Create Skeleton Template
            if tempStr['count'] == 0:
                tempSkeleton[region] = seclist.render(tempStr,skeleton=True,region=region)

            for columnname in row:

                # Column value
                if 'description' in columnname.lower():
                    columnvalue = str(row[columnname])
                    tempdict = {'rule_description': columnvalue}
                else:
                    columnvalue = str(row[columnname].strip())

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Check for multivalued columns
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

            new_sec_rule = ""
            textToAddSeclistSearch = "##Add New Seclists for "+region+" here##"
            new_ingress_sec_rule = ""
            new_egress_sec_rule = ""
            # if ('Default Security List for' in display_name):
            #     if (seclist_tf_name not in default_seclists_done[region]):
            #         if (len(default_seclists_done[region]) == 0):
            #             default_ruleStr[region] = default_ruleStr[region] + defaultseclist.render(tempStr)
            #         else:
            #             default_ruleStr[region] = default_ruleStr[region] +  defaultseclist.render(tempStr)
            #         default_seclists_done[region].append(seclist_tf_name)
            #
            #     if str(row['Rule Type']).lower() == 'ingress':
            #         new_sec_rule = create_ingress_rule_string(tempStr,ingress_rule,tempdict2)
            #
            #
            #     if str(row['Rule Type']).lower() == 'egress':
            #         new_sec_rule = create_egress_rule_string(tempStr,egress_rule,tempdict2)
            #
            #     new_sec_rule = new_sec_rule +"\n"+ srcStr
            #     default_ruleStr[region] = default_ruleStr[region].replace(srcStr,new_sec_rule)
            #     continue

            # Process other seclists
            # if (seclist_tf_name not in seclists_done[region]):
            #     if (tfStr != ""):
            #         print("Writing to..."+str(oname.name))
            #         oname.write(tfStr)
            #         oname.close()
            #         tfStr = ""

                # oname = open(outdir + "/" + region + "/" + prefix + auto_tfvars_filename, "w")
                # tfStr[reg] = seclist.render(tempStr)
                # seclists_done[region].append(seclist_tf_name)

            if region_seclist_name not in processed_seclist:
                tfStr[region] = tfStr[region] + seclist.render(tempStr,
                                                          ingress_sec_rules="####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",
                                                          egress_sec_rules="####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####")

                processed_seclist.append(region_seclist_name)

            if str(row['Rule Type']).lower() == 'ingress':
                new_ingress_sec_rule = create_ingress_rule_string(tempStr, ingress_rule, tempdict2)
                tfStr[region] = tfStr[region].replace("####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",new_ingress_sec_rule)

            if str(row['Rule Type']).lower() == 'egress':
                new_egress_sec_rule = create_egress_rule_string(tempStr, egress_rule, tempdict2)
                tfStr[region] = tfStr[region].replace("####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####",new_egress_sec_rule)




            # print(tfStr[reg])
            #new_sec_rule = new_ingress_sec_rule + "\n" + srcStr
            #print(tfStr[region],tempStr)

    for reg in ct.all_regions:
        textToAddSeclistSearch = "##Add New Seclists for " + reg + " here##"

        # Rename the modules file in outdir to .tf
        module_txt_filenames = ['seclists']
        for modules in module_txt_filenames:
            module_filename = outdir + "/" + reg + "/" + modules.lower() + ".txt"
            rename_module_filename = outdir + "/" + reg + "/" + modules.lower() + ".tf"

            if not os.path.isfile(rename_module_filename):
                if os.path.isfile(module_filename):
                    os.rename(module_filename, rename_module_filename)

        outfile = outdir + "/" + reg + "/" + prefix + auto_tfvars_filename
        tempSkeleton[reg] = tempSkeleton[reg].replace(textToAddSeclistSearch,
                                                      tfStr[reg] + textToAddSeclistSearch)
        print("Final", tempSkeleton[reg])
        # oname = open(outfile, "w")
        # oname.write(tempSkeleton[reg])
        # oname.close()
        # print(outfile + " containing TF for seclist has been created for region " + reg)
        # if (tfStr != ''):
        #     print("Writing to..." + str(oname.name))
        #     oname.write(tfStr)
        #     oname.close()
        # for reg in ct.all_regions:
        #     if (default_ruleStr[reg] != ''):
        #         print("Writing to..." + str(defaultname[reg].name))
        #         defaultname[reg].write(default_ruleStr[reg])
        #         defaultname[reg].close()

    os.remove('out.csv')

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    modify_terraform_secrules(args.inputfile, args.outdir, None, args.config)
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

import argparse
import csv
import re
import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *


def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Takes in an input file mentioning sec rules to be added for the subnet. See update_seclist-example.csv/CD3 for format under example folder. It will then take backup of all existing sec list files in outdir and create new one with modified rules")
    parser.add_argument("inputfile",help="Full Path of input file: It could be either the properties file eg CD3 excel file")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


def modify_terraform_secrules(inputfile, outdir, prefix=None, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    defaultseclist = env.get_template('default-seclist-template')
    secrule = env.get_template('module-sec-rule-template')
    seclist = env.get_template('module-seclist-template')

    secrulesfilename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    seclists_done = {}
    default_ruleStr = {}
    default_seclists_done = {}
    defaultname = {}
    auto_tfvars_filename = "_seclist.auto.tfvars"
    vcns = parseVCNs(secrulesfilename)

    def skipCommentedLine(lines):
        """
        A filter which skip/strip the comments and yield the
        rest of the lines
        :param lines: any object which we can iterate through such as a file
        object, list, tuple, or generator
        """
        for line in lines:
            comment_pattern = re.compile(r'\s*#.*$')
            line = re.sub(comment_pattern, '', line)
            if line:
                yield line


    def create_ingress_rule_string(tempStr,ingress_rule,tempdict2):

        rule_desc = tempStr['rule_description']
        protocol = tempStr['protocol'].lower().strip()
        isstateless = str(tempStr['isstateless'].lower())
        if (str(rule_desc).lower() == "nan" or str(rule_desc).lower() == ""):
            rule_desc = ""
            tempdict2 ={'rule_description' : rule_desc}
        else:
            rule_desc = str(rule_desc)
            tempdict2 = {'rule_description': rule_desc}
        tempStr.update(tempdict2)

        if ("services-in-oracle-services-network" in tempStr['source'] or "objectstorage" in tempStr['source']):
            source_type = "SERVICE_CIDR_BLOCK"
            tempdict2 = {'source_type' : source_type}
        tempStr.update(tempdict2)

        tempdict2 = {'protocol_code': get_protocol(protocol),'isstateless':isstateless}
        tempStr.update(tempdict2)

        ingress_rule = ingress_rule + secrule.render(tempStr)
        ingress_rule = ingress_rule + "\n" + "####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####"
        return ingress_rule


    def create_egress_rule_string(tempStr,egress_rule,tempdict2):

        rule_desc = tempStr['rule_description']
        protocol = tempStr['protocol'].lower().strip()
        isstateless = str(tempStr['isstateless'].lower())

        if (str(rule_desc).lower() == "nan"):
            rule_desc = ""
            tempdict2 ={'rule_description' : rule_desc}
        else:
            rule_desc = str(rule_desc)
            tempdict2 ={'rule_description' : rule_desc}
        tempStr.update(tempdict2)

        if ("services-in-oracle-services-network" in tempStr['destination'] or "objectstorage" in tempStr['destination']):
            destination_type = "SERVICE_CIDR_BLOCK"
            tempdict2 = {'destination_type': destination_type}
        tempStr.update(tempdict2)

        tempDict2 = {'protocol_code': get_protocol(protocol),'isstateless':isstateless}
        tempStr.update(tempDict2)

        egress_rule = egress_rule + secrule.render(tempStr)
        egress_rule = egress_rule + "\n" + "####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####"
        return egress_rule


    def get_protocol(strprotocol):
        if str(strprotocol).lower() == "all":
            return "all"
        else:
            protocol_dict = commonTools().protocol_dict
            for k, v in protocol_dict.items():
                if (strprotocol).lower() == v.lower():
                    return k


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(secrulesfilename, "SecRulesinOCI")
    df = df.to_csv('out.csv')

    totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open('out.csv'))))
    i = 0
    region_included = []
    tempSkeleton = {}
    tfStr = {}

    for reg in ct.all_regions:
        if (os.path.exists(outdir + "/" + reg)):
            defaultname[reg] = open(outdir + "/" + reg + "/VCNs_Default_SecList.tf", "w")
        default_ruleStr[reg] = ''
        default_seclists_done[reg] = []
        seclists_done[reg] = []
        tempSkeleton[reg] = ''
        tfStr[reg] = ''

        # Backup existing seclist files in ash and phx dir
        resource = "SLs"
        commonTools.backup_file(outdir + "/" + reg, resource, prefix+auto_tfvars_filename)

    with open('out.csv') as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        rowCount = 0

        oname = None

        ingress_rule = ''
        egress_rule = ''
        default_rules = ''
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

            region_seclist_name = region+"_"+seclist_tf_name

            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)
                # Check if values are entered for mandatory fields
            if (region == 'nan' or str(vcn_name).lower() == 'nan' or str(comp_name).lower() == 'nan'):
                    print("\nColumn Region, VCN Name and Compartment Name cannot be left empty in SecRulesinOCI sheet of CD3..Exiting!")
                    exit(1)

            # Process only those VCNs which are present in cd3(and have been created via TF)
            if (vcn_name not in vcns.vcn_names):
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
            if region not in region_included:
                tempStr.update({'count': 0})
                region_included.append(region)

            # Create Skeleton Template
            if tempStr['count'] == 0:
                tempSkeleton[region] = seclist.render(tempStr,skeleton=True,region=region)

            for columnname in row:

                # Column value
                if 'description' in columnname.lower():
                    columnvalue = str(row[columnname])
                    tempdict = {'rule_description': columnvalue}
                else:
                    columnvalue = str(row[columnname].strip())

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Check for multivalued columns
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

            new_sec_rule = ""
            textToAddSeclistSearch = "##Add New Seclists for "+region+" here##"
            new_ingress_sec_rule = ""
            new_egress_sec_rule = ""
            # if ('Default Security List for' in display_name):
            #     if (seclist_tf_name not in default_seclists_done[region]):
            #         if (len(default_seclists_done[region]) == 0):
            #             default_ruleStr[region] = default_ruleStr[region] + defaultseclist.render(tempStr)
            #         else:
            #             default_ruleStr[region] = default_ruleStr[region] +  defaultseclist.render(tempStr)
            #         default_seclists_done[region].append(seclist_tf_name)
            #
            #     if str(row['Rule Type']).lower() == 'ingress':
            #         new_sec_rule = create_ingress_rule_string(tempStr,ingress_rule,tempdict2)
            #
            #
            #     if str(row['Rule Type']).lower() == 'egress':
            #         new_sec_rule = create_egress_rule_string(tempStr,egress_rule,tempdict2)
            #
            #     new_sec_rule = new_sec_rule +"\n"+ srcStr
            #     default_ruleStr[region] = default_ruleStr[region].replace(srcStr,new_sec_rule)
            #     continue

            # Process other seclists
            # if (seclist_tf_name not in seclists_done[region]):
            #     if (tfStr != ""):
            #         print("Writing to..."+str(oname.name))
            #         oname.write(tfStr)
            #         oname.close()
            #         tfStr = ""

                # oname = open(outdir + "/" + region + "/" + prefix + auto_tfvars_filename, "w")
                # tfStr[reg] = seclist.render(tempStr)
                # seclists_done[region].append(seclist_tf_name)

            if region_seclist_name not in processed_seclist:
                tfStr[region] = tfStr[region] + seclist.render(tempStr,
                                                          ingress_sec_rules="####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",
                                                          egress_sec_rules="####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####")

                processed_seclist.append(region_seclist_name)

            if str(row['Rule Type']).lower() == 'ingress':
                new_ingress_sec_rule = create_ingress_rule_string(tempStr, ingress_rule, tempdict2)
                tfStr[region] = tfStr[region].replace("####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",new_ingress_sec_rule)

            if str(row['Rule Type']).lower() == 'egress':
                new_egress_sec_rule = create_egress_rule_string(tempStr, egress_rule, tempdict2)
                tfStr[region] = tfStr[region].replace("####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####",new_egress_sec_rule)




            # print(tfStr[reg])
            #new_sec_rule = new_ingress_sec_rule + "\n" + srcStr
            #print(tfStr[region],tempStr)

    for reg in ct.all_regions:
        textToAddSeclistSearch = "##Add New Seclists for " + reg + " here##"

        # Rename the modules file in outdir to .tf
        module_txt_filenames = ['seclists']
        for modules in module_txt_filenames:
            module_filename = outdir + "/" + reg + "/" + modules.lower() + ".txt"
            rename_module_filename = outdir + "/" + reg + "/" + modules.lower() + ".tf"

            if not os.path.isfile(rename_module_filename):
                if os.path.isfile(module_filename):
                    os.rename(module_filename, rename_module_filename)

        outfile = outdir + "/" + reg + "/" + prefix + auto_tfvars_filename
        tempSkeleton[reg] = tempSkeleton[reg].replace(textToAddSeclistSearch,
                                                      tfStr[reg] + textToAddSeclistSearch)
        print("Final", tempSkeleton[reg])
        # oname = open(outfile, "w")
        # oname.write(tempSkeleton[reg])
        # oname.close()
        # print(outfile + " containing TF for seclist has been created for region " + reg)
        # if (tfStr != ''):
        #     print("Writing to..." + str(oname.name))
        #     oname.write(tfStr)
        #     oname.close()
        # for reg in ct.all_regions:
        #     if (default_ruleStr[reg] != ''):
        #         print("Writing to..." + str(defaultname[reg].name))
        #         defaultname[reg].write(default_ruleStr[reg])
        #         defaultname[reg].close()

    os.remove('out.csv')

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    modify_terraform_secrules(args.inputfile, args.outdir, None, args.config)

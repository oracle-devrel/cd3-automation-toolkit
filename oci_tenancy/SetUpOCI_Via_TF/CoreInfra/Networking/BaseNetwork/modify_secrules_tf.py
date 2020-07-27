#!/usr/bin/python3

import argparse
import csv
import os
import re
import sys
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
defaultseclist = env.get_template('default-seclist-template')
ingress_egress = env.get_template('ingress-egress-template')
seclist = env.get_template('seclist-template')

def skipCommentedLine(lines):
    """
    A filter which skip/strip the comments and yield the
    rest of the lines
    :param lines: any object which we can iterate through such as a file
    object, list, tuple, or generator
    """
    for line in lines:
        comment_pattern = re.compile(r'\s*#.*$')
        line = re.sub(comment_pattern, '', line).strip()
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
        rule_desc = str(rule_desc).strip()
        tempdict2 = {'rule_description': rule_desc}
    tempStr.update(tempdict2)

    if ("services-in-oracle-services-network" in tempStr['source'] or "objectstorage" in tempStr['source']):
        source_type = "SERVICE_CIDR_BLOCK"
        tempdict2 = {'source_type' : source_type}
    tempStr.update(tempdict2)

    tempdict2 = {'protocol_code': get_protocol(protocol),'isstateless':isstateless}
    tempStr.update(tempdict2)

    ingress_rule = ingress_rule + ingress_egress.render(tempStr)
    return ingress_rule


def create_egress_rule_string(tempStr,egress_rule,tempdict2):

    rule_desc = tempStr['rule_description']
    protocol = tempStr['protocol'].lower().strip()
    isstateless = str(tempStr['isstateless'].lower())

    if (str(rule_desc).lower() == "nan"):
        rule_desc = ""
        tempdict2 ={'rule_description' : rule_desc}
    else:
        rule_desc = str(rule_desc).strip()
        tempdict2 ={'rule_description' : rule_desc}
    tempStr.update(tempdict2)

    if ("services-in-oracle-services-network" in tempStr['destination'] or "objectstorage" in tempStr['destination']):
        destination_type = "SERVICE_CIDR_BLOCK"
        tempdict2 = {'destination_type': destination_type}
    tempStr.update(tempdict2)

    tempDict2 = {'protocol_code': get_protocol(protocol),'isstateless':isstateless}
    tempStr.update(tempDict2)

    egress_rule = egress_rule + ingress_egress.render(tempStr)
    return egress_rule


def get_protocol(strprotocol):
    if str(strprotocol).lower() == "all":
        return "all"
    else:
        protocol_dict = commonTools().protocol_dict
        for k, v in protocol_dict.items():
            if (strprotocol).lower() == v.lower():
                return k


"""    if str(strprotocol).lower() == "tcp":
        return "6"
    elif str(strprotocol).lower() == "icmp":
        return "1"
    elif str(strprotocol).lower() == "udp":
        return "17"
    elif str(strprotocol).lower() == "all":
        return "all"
    else:
        return strprotocol
"""
parser = argparse.ArgumentParser(description="Takes in an input file mentioning sec rules to be added for the subnet. See update_seclist-example.csv/CD3 for format under example folder. It will then take backup of all existing sec list files in outdir and create new one with modified rules")
parser.add_argument("inputfile",help="Full Path of input file: It could be either the properties file eg vcn-info.properties or CD3 excel file")
parser.add_argument("outdir", help="directory path for output tf files ")
parser.add_argument("secrulesfile",help="Input file(either csv or CD3 excel) containing new secrules to be added for Security List of a given subnet")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

secrulesfilename = args.secrulesfile
outdir = args.outdir
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName = ""

ct = commonTools()
ct.get_subscribedregions(configFileName)

seclists_done = {}
default_ruleStr = {}
default_seclists_done = {}
defaultname = {}


# Read input file containing new sec rules to be added
# If input is CD3 excel file
if ('.xls' in secrulesfilename):
    vcns = parseVCNs(secrulesfilename)

    df = pd.read_excel(secrulesfilename, sheet_name='SecRulesinOCI', skiprows=1, dtype=object).to_csv('out.csv')
    totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open('out.csv'))))
    i = 0



    for reg in ct.all_regions:
        if (os.path.exists(outdir + "/" + reg)):
            defaultname[reg] = open(outdir + "/" + reg + "/VCNs_Default_SecList.tf", "w")
        default_ruleStr[reg] = ''
        default_seclists_done[reg] = []
        seclists_done[reg] = []
        # Backup existing seclist files in ash and phx dir
        print("Backing up all existing SL TF files for region " + reg + " to")
        commonTools.backup_file(outdir + "/" + reg, "_seclist.tf")

    with open('out.csv') as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        rowCount = 0
        tfStr = ""
        oname = None

        ingress_rule = ''
        egress_rule = ''
        default_rules = ''
        for row in reader:
            display_name = row['SecList Name']
            vcn_name = row['VCN Name']
            vcn_tf_name = commonTools.check_tf_variable(vcn_name)
            rt_var = vcn_name + "_" + display_name
            seclist_tf_name = commonTools.check_tf_variable(rt_var)

            region = row['Region']
            region = region.strip().lower()


            # Process only those VCNs which are present in cd3(and have been created via TF)
            if (vcn_name not in vcns.vcn_names):
                print("skipping seclist: " + display_name + " as its VCN is not part of VCNs tab in cd3")
                continue

            if (str(display_name).lower() == "nan"):
                continue

            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            # temporary dictionary1, dictionary2 and list
            tempStr = {}
            tempdict = {}
            tempdict2 = {}
            compartment_tf_name = ''

            for columnname in row:
                # Column value
                columnvalue = str(row[columnname].strip())

                if columnvalue == 'True' or columnvalue == 'TRUE' or columnvalue == 'False' or columnvalue == 'FALSE':
                    columnvalue = columnvalue.lower()

                if (columnvalue.lower() == 'nan'):
                    columnvalue = ""

                if "::" in columnvalue:
                    if columnname != 'Compartment Name':
                        columnname = commonTools.check_column_headers(columnname)
                        multivalues = columnvalue.split("::")
                        multivalues = [str(part).strip() for part in multivalues if part]
                        tempdict = {columnname: multivalues}

                if columnname in commonTools.tagColumns:
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

                if columnname == 'SecList Name':
                    display_name = columnvalue.strip()

                if columnname == 'Compartment Name':
                    columnname = 'compartment_name'
                    compartment_tf_name =  commonTools.check_tf_variable(columnvalue.strip())

                tempdict = {'vcn_tf_name': vcn_tf_name,'rt_var' : rt_var,'seclist_tf_name': seclist_tf_name,'region' : region,'compartment_tf_name' : compartment_tf_name,'display_name' : display_name}

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = columnvalue
                tempStr.update(tempdict)
                srcStr = "##Add More rules for "+vcn_tf_name+"_"+seclist_tf_name+"##"

            new_sec_rule = ""

            if ('Default Security List for' in display_name):
                if (seclist_tf_name not in default_seclists_done[region]):
                    if (len(default_seclists_done[region]) == 0):
                        default_ruleStr[region] = default_ruleStr[region] + defaultseclist.render(tempStr)
                    else:
                        default_ruleStr[region] = default_ruleStr[region] +  defaultseclist.render(tempStr)
                    default_seclists_done[region].append(seclist_tf_name)

                if row['Rule Type'] == 'ingress':
                    new_sec_rule = create_ingress_rule_string(tempStr,ingress_rule,tempdict2)


                if row['Rule Type'] == 'egress':
                    new_sec_rule = create_egress_rule_string(tempStr,egress_rule,tempdict2)

                new_sec_rule = new_sec_rule +"\n"+ srcStr
                default_ruleStr[region] = default_ruleStr[region].replace(srcStr,new_sec_rule)
                continue

            # Process other seclists
            if (seclist_tf_name not in seclists_done[region]):
                if (tfStr != ""):
                    oname.write(tfStr)
                    oname.close()
                    tfStr = ""

                oname = open(outdir + "/" + region + "/" + seclist_tf_name + "_seclist.tf", "w")
                tfStr = seclist.render(tempStr)
                seclists_done[region].append(seclist_tf_name)

            new_sec_rule = ""
            srcStr =  "####ADD_NEW_SEC_RULES####"+vcn_tf_name+"_"+seclist_tf_name

            if row['Rule Type'] == 'ingress':
                new_sec_rule = create_ingress_rule_string(tempStr, ingress_rule, tempdict2)

            if row['Rule Type'] == 'egress':
                new_sec_rule = create_egress_rule_string(tempStr, egress_rule, tempdict2)

            new_sec_rule = new_sec_rule + "\n" + srcStr
            tfStr = tfStr.replace(srcStr,new_sec_rule)

        if (tfStr != ''):
            oname.write(tfStr)
            oname.close()
        for reg in ct.all_regions:
            if (default_ruleStr[reg] != ''):
                defaultname[reg].write(default_ruleStr[reg])
                defaultname[reg].close()

    os.remove('out.csv')

# If input is a csv file
"""
elif ('.csv' in secrulesfilename):
    totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open(secrulesfilename))))
    with open(secrulesfilename) as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        rowCount = 0
        for row in reader:
            subnetName = row['SubnetName/SecurityListName']
            if(subnetName=='<END>' or subnetName=='<end>'):
                break

            ruleType = row['RuleType']
            protocol = row['Protocol']
            region = row['Region']
            region = region.strip().lower()

            new_sec_rule =""
            if ruleType == 'ingress':
                    new_sec_rule = create_ingress_rule_string(row)
            if ruleType == 'egress':
                    new_sec_rule = create_egress_rule_string(row)

            strDefault = 'Default Security List for'
            if (strDefault.lower() in subnetName.lower()):
                print("file to modify :: VCNs_Default_SecList.tf")
                sec_list_file = "VCNs_Default_SecList.tf"
                vcn_name = subnetName.split('for')[1].strip()
                text_to_replace = "##Add More rules for " + vcn_name + "##"
                new_sec_rule = new_sec_rule + "\n" + text_to_replace
                commonTools.backup_file(outdir + "/" + region, sec_list_file)
                updateSecRules(outdir + "/" + region + "/" + sec_list_file, text_to_replace, new_sec_rule, 0)


            elif (subnetName != ''):
                # sec_list_file = seclist_files[subnetName]
                sec_list_file = vcn_name+"_"+subnetName + "_seclist.tf"
                print("file to modify ::::: " + sec_list_file)
                # text_to_replace = getReplacementStr(sec_rule_per_seclist, subnetName)
                text_to_replace = getReplacementStr(seclist_rule_count_limit[vcn_name+"_"+subnetName], vcn_name+"_"+subnetName)
                new_sec_rule = new_sec_rule + "\n" + text_to_replace
                commonTools.backup_file(outdir + "/" + region, sec_list_file)
                updateSecRules(outdir + "/" + region + "/" + sec_list_file, text_to_replace, new_sec_rule, 0)
                incrementRuleCount(vcn_name+"_"+subnetName)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
"""
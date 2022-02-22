#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core network security
# group and network security group security rules.
#
# Author: Andrew Vuong
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

"""
Stage 1
(Will be part of a larger pandas wrapper module)

All information will be parsed from CD3Parser.py
Each sheet which represents the type of setup would have its own distinct class that holds all
relevant information.

Starting with security group, the program would parse and separate by region such as Ashburn or
Phoenix then map all compartment, VCN, and subnet into a unique key.
The remaining rules would follow its unique key as its value.

This new class would contain the unique key and all its values. This class would further be placed
into a list.

Stage 2
Run through the list of relevant classes and perform factory action on them to write the TF file.


"""
import argparse
from .cd3parser import CD3Parser as cd3parser
import os
import pandas as pd
import sys
from oci.config import DEFAULT_LOCATION
from pathlib import Path

sys.path.append(os.getcwd() + "/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

DEBUG = False

# Load the template file
file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('module-nsg-template')
nsgrule = env.get_template('module-nsg-rule-template')
nsg_auto_tfvars_filename = '_nsgs.auto.tfvars'
nsg_rules_auto_tfvars_filename = '_nsg-rules.auto.tfvars'

tempStr = {}
freeform_tags = {}
defined_tags = {}
nsg_done = []
region_included = []

# Stage 1 Parse into NetSec class and store into dictionary unique_id:rules
def directionOptionals(nsgParser, options, tempStr):
    destination_type = str(options[6])
    source_type = str(options[4])
    source = str(options[5])
    destination = str(options[7])

    if source_type != 'nan':
        if (source_type.lower() == 'cidr') or (source_type == 'CIDR_BLOCK'):
            source_type = "CIDR_BLOCK"
        elif (source_type.lower() == 'service') or (source_type == 'SERVICE_CIDR_BLOCK'):
            source_type = "SERVICE_CIDR_BLOCK"
        elif (source_type.lower() == 'nsg') or (source_type == 'NETWORK_SECURITY_GROUP'):
            source_type = "NETWORK_SECURITY_GROUP"
            if "ocid" not in str(source):
                source = commonTools.check_tf_variable(str(source))
    else:
        source_type = ""

    if destination_type != 'nan':
        if (destination_type.lower() == 'cidr') or (destination_type == 'CIDR_BLOCK'):
            destination_type = 'CIDR_BLOCK'
        elif (destination_type.lower() == 'service') or (destination_type == 'SERVICE_CIDR_BLOCK'):
            destination_type = 'SERVICE_CIDR_BLOCK'
        elif (destination_type.lower() == 'nsg') or (destination_type == 'NETWORK_SECURITY_GROUP'):
            destination_type = "NETWORK_SECURITY_GROUP"
            if "ocid" not in str(destination):
                destination = commonTools.check_tf_variable(str(destination))
    else:
        destination_type = ""

    if source == 'nan':
        source = ""

    if destination == 'nan':
        destination = ""

    tempStr['source_type'] = source_type
    tempStr['destination_type'] = destination_type
    tempStr['source'] = source
    tempStr['destination'] = destination

    return tempStr


def protocolOptionals(nsgParser, options, tempStr):
    protocol = options[2].lower()
    code = ''
    type = ''
    if protocol == "all":
        return ""
    elif protocol == "icmp":
        protocolHeader = protocol
        code = "" if nsgParser.checkOptionalEmpty(options[13]) \
            else int(options[13])
        type = "" if nsgParser.checkOptionalEmpty(options[12]) \
            else int(options[12])
    elif protocol == "tcp":
        protocolHeader = protocol
    elif protocol == "udp":
        protocolHeader = protocol
    else:
        return ""
    tempStr['protocol'] = protocolHeader
    tempStr['icmptype'] = type
    tempStr['icmpcode'] = code
    if str(options[11]) != '' and str(options[11]) != 'nan':
        tempStr['dportmax'] = int(options[11])
    else:
        tempStr['dportmax'] = ""
    if str(options[10]) != '' and str(options[10]) != 'nan':
        tempStr['dportmin'] = int(options[10])
    else:
        tempStr['dportmin'] = ""
    if str(options[9]) != '' and str(options[9]) != 'nan':
        tempStr['sportmax'] = int(options[9])
    else:
        tempStr['sportmax'] = ""
    if str(options[8]) != '' and str(options[8]) != 'nan':
        tempStr['sportmin'] = int(options[8])
    else:
        tempStr['sportmin'] = ""

    return tempStr

def statelessOptional(nsgParser, options, tempStr):
    if not nsgParser.checkOptionalEmpty(options[3]) and str(options[3]).lower() == "true":
        tempStr['isstateless'] = 'true'
    else:
        tempStr['isstateless'] = 'false'
    return tempStr

# templates to build NSG and NSG_Sec_Rules Terraform
def NSGtemplate(region, prefix,nsgParser, key, value, outdir, columnname):
    """Required: compartment_id and vcn_id"""
    if str(key[0]).lower() == 'nan':
        print("\n Compartment Name cannot be left empty....Exiting!!")
        exit(1)
    if str(key[2]).lower() == 'nan':
        print(str(key[2]))
        print("\n NSG Name cannot be left empty....Exiting!!")
        exit(1)
    compartment_var_name = str(key[0]).strip()

    # Added to check if compartment name is compatible with TF variable name syntax
    compartment_tf_name = commonTools.check_tf_variable(compartment_var_name)
    nsg_tf_name = commonTools.check_tf_variable(str(key[2]))
    vcn_tf_name = commonTools.check_tf_variable(str(key[1]))
    tempDict = {'compartment_tf_name': compartment_tf_name, 'display_name': str(key[2]), 'nsg_tf_name': nsg_tf_name,
                'vcn_tf_name': vcn_tf_name, 'region' : region}

    # Dictionary of column headers : column value
    updatedcols = []
    updatedrule = []
    ruleindex = 1

    for rule in value:
        rule = list(rule)
        # Replace nan to "" in each value
        for eachvalue in rule:
            eachvalue = str(eachvalue)

            # Check for boolean/null in column values
            eachvalue = commonTools.check_columnvalue(eachvalue)

            updatedrule.append(eachvalue)

        # Change column header names to lower case for matching template
        for column in columnname:
            column = commonTools.check_column_headers(column)
            if column != '':
                updatedcols.append(column)

        tempStr = dict(zip(updatedcols, updatedrule))

        # process tags
        freeform_tags = commonTools.split_tag_values('freeform_tags', tempStr['freeform_tags'], tempStr)
        defined_tags = commonTools.split_tag_values('defined_tags', tempStr['defined_tags'], tempStr)


        tempStr.update(defined_tags)
        tempStr.update(freeform_tags)
        tempStr.update(tempDict)

        # NSG template; Write only for the first apperance.
        nsg_name = commonTools.check_tf_variable(str(key[2]))


        if nsg_name not in nsg_done:
            nsg_done.append(nsg_name)
            resource_group = template.render(tempStr)

            with open(outdir + "/"+ prefix + nsg_auto_tfvars_filename, 'a+') as f:
                f.write(resource_group)

        with open(outdir + "/"+ prefix + nsg_rules_auto_tfvars_filename, 'a+') as f:

            null_rule = 0
            for i in range(1, 3):
                if (str(rule[i]).lower() == 'nan'):
                    # print("Creating Empty NSG: "+rule[0])
                    null_rule = 1
                    break
            if (null_rule == 1):
                continue

            tempStr.update(NSGrulesTemplate(nsgParser, rule, ruleindex, tempStr))
            tempStr.update(statelessOptional(nsgParser, rule, tempStr))
            tempStr.update(directionOptionals(nsgParser, rule, tempStr))
            tempStr.update(protocolOptionals(nsgParser, rule, tempStr))

            nsg_rule = nsgrule.render(tempStr)
            f.write(nsg_rule)
            ruleindex += 1
        f.close()

def NSGrulesTemplate(nsgParser, rule, index, tempStr):
    if (str(rule[14]).lower() == 'nan'):
        rule[14] = ""

    nsg_rule_tf_name = commonTools.check_tf_variable(str(rule[0])) + "_security_rule" + str(index)
    direction = str(rule[1]).upper()
    protocol = getProtocolNumber(str(rule[2]))
    tempdict = {'nsg_rule_tf_name': nsg_rule_tf_name, 'direction': direction, 'protocol_code': protocol}
    tempStr.update(tempdict)

    return tempStr


def getProtocolNumber(protocol):
    if protocol.lower() == 'all':
        return "all"
    else:
        protocol_dict = commonTools().protocol_dict
        for k, v in protocol_dict.items():
            if (protocol).lower() == v.lower():
                return k

def parse_args():
    parser = argparse.ArgumentParser(
        description='Create NSG and its NSG rules based on inputs given in vcn-info.properties, separated by regions.')
    parser.add_argument('inputfile', help='Full Path of cd3 excel file or csv containing NSG info')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument('--config', help='Config file name')
    return parser.parse_args()


def create_terraform_nsg(inputfile, outdir, prefix, config, nongf_tenancy=False):
    configFileName = config
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    columnname = ''

    # tested path allows for space, full or relative path acceptable
    nsgParser = cd3parser(os.path.realpath(inputfile)).getNSG()


    regionDict = nsgParser.getRegionDict()
    headerDict = nsgParser.getHeaderDict()
    listOfRegions = nsgParser.regions

    # Backup of existing NSG files
    for reg in ct.all_regions:
        if (os.path.exists(outdir + "/" + reg)):
            resource = "NSG"
            commonTools.backup_file(outdir + "/" + reg, resource, prefix + nsg_auto_tfvars_filename)
            commonTools.backup_file(outdir + "/" + reg, resource, prefix + nsg_rules_auto_tfvars_filename)

        # Rename the modules file in outdir to .tf
        module_txt_filenames = ['nsgs']
        for modules in module_txt_filenames:
            module_filename = outdir + "/" + reg + "/" + modules.lower() + ".txt"
            rename_module_filename = outdir + "/" + reg + "/" + modules.lower() + ".tf"

            if not os.path.isfile(rename_module_filename):
                if os.path.isfile(module_filename):
                    os.rename(module_filename, rename_module_filename)

    # creates all region directories in specified out directory
    for region in listOfRegions:
        region = region.lower()

        if (region in commonTools.endNames):
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        regionDirPath = outdir + "/{}".format(region)

        if not os.path.exists(regionDirPath):
            os.makedirs(regionDirPath)

        resource_group = template.render(tempStr, region=region, skeleton=True)
        resource_group_nsg_rule = nsgrule.render(tempStr, region=region, skeleton=True)

        if resource_group != '':
            with open(regionDirPath + "/" + prefix + nsg_auto_tfvars_filename, 'w+') as f:
                f.write(resource_group)
        if resource_group_nsg_rule != '':
            with open(regionDirPath + "/" + prefix + nsg_rules_auto_tfvars_filename, 'w+') as f:
                f.write(resource_group_nsg_rule)

        print(regionDirPath + "/" + prefix + nsg_auto_tfvars_filename + " for NSGs has been created")
        print(regionDirPath + "/" + prefix + nsg_rules_auto_tfvars_filename + " for NSG Rules has been created")

    # Stage 2 using the dictionary of unique_id:rules, use factory method to produces resources and
    # rules
    for region in listOfRegions:
        region = region.lower()
        if (region in commonTools.endNames):
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        reg_outdir = outdir + "/" + region

        for k, v in headerDict.items():
            for unique_headers, other_headers in v.items():
                for name in other_headers:
                    columnname = name

        for k, v in nsgParser.getRegionSpecificDict(regionDict, region).items():
            NSGtemplate(region, prefix, nsgParser, k, v, reg_outdir, columnname)

        with open(reg_outdir + "/" + prefix + nsg_auto_tfvars_filename, 'a+') as f:
            f.write("\n"+"}")

        with open(reg_outdir + "/" + prefix + nsg_rules_auto_tfvars_filename, 'a+') as f:
            f.write("\n"+"}")

    if DEBUG:
        nsgParser.debug()
        print("Rules only list and its indice:\n{}".format({k: v for v, k in enumerate(nsgParser.nsg.columns[3:])}))


if __name__ == '__main__':
    args = parse_args()
    create_terraform_nsg(args.inputfile, args.outdir, args.prefix, args.config)

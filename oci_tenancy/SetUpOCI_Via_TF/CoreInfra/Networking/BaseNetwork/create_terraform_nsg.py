#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core network security
# group and network security group security rules.
#
# Author: Andrew Vuong
# Oracle Consulting
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
from cd3parser import CD3Parser as cd3parser
import os
import pandas as pd
import sys
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

DEBUG = False

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('nsg-template')
nsgrule = env.get_template('nsg-rule-template')

tempStr ={}
freeform_tags={}
defined_tags={}

# Stage 1 Parse into NetSec class and store into dictionary unique_id:rules
def directionOptionals(nsgParser, options,tempStr):

    srcdestType = ""
    srcdest = ""
    source_type=''
    destination_type=''
    source=''
    destination =''
    '''
    ingressegressStrTemplate = "source" if options[1].lower() == "ingress" else "destination"
    if options[1].lower() == "ingress":  # check source option 4,5
        srcdestType = options[4]
        srcdest = options[5]
    else:  # else dest option 6,7
        srcdestType = options[6]
        srcdest = options[7]
    # processing becomes the same from this point
    
    # if srcType or destType is not empty, respective src/dest req.
    if(srcdestType.lower()=='cidr'):
        srcdestType="CIDR_BLOCK"
    if (srcdestType.lower() == 'nsg'):
        srcdestType = "NETWORK_SECURITY_GROUP"
        srcdest="oci_core_network_security_group."+srcdest+".id"
    if (srcdestType.lower() == 'service'):
        srcdestType = "SERVICE_CIDR_BLOCK"
    '''
    destination_type = str(options[6])
    source_type = str(options[4])
    source = str(options[5])
    destination =  str(options[7])

    if source_type != 'nan':
        if (source_type.lower() == 'cidr'):
            source_type="CIDR_BLOCK"
        elif (source_type.lower()=='service'):
            source_type = "SERVICE_CIDR_BLOCK"
        elif (source_type.lower()=='nsg'):
            source_type = "NETWORK_SECURITY_GROUP"
            source = "oci_core_network_security_group."+source+".id"
    else:
        source_type = ""

    if destination_type != 'nan':
        if (destination_type.lower() == 'cidr'):
            destination_type='CIDR_BLOCK'
        elif (destination_type.lower() == 'service'):
            destination_type='SERVICE_CIDR_BLOCK'
        elif (destination_type.lower() == 'cidr'):
            destination_type = "NETWORK_SECURITY_GROUP"
            destination = "oci_core_network_security_group."+destination+".id"
    else:
        destination_type = ""

    if ('oci_core_network_security_group' not in source):
        if source == 'nan':
            source = ""
        source = "\""+source+"\""

    if ('oci_core_network_security_group' not in destination):
        if destination == 'nan':
            destination = ""
        destination = "\""+destination+"\""

    tempStr['source_type'] = source_type
    tempStr['destination_type'] = destination_type
    tempStr['source'] = source
    tempStr['destination'] = destination


    '''
    if nsgParser.checkOptionalEmpty(srcdestType):
        return ""
    else:
        return ("\n\n" \
                "    {} = \"{}\"\n" \
                "    {}_type = \"{}\"\n" \
                ).format(ingressegressStrTemplate, srcdest, ingressegressStrTemplate, srcdestType)
    '''
    return tempStr

def protocolOptionals(nsgParser, options, tempStr):

    protocol = options[2].lower()
    protocolHeader = ""
    code=''
    type=''
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
        #return "SELECTION UNCOMMON and NOT HANDLED, please use TCP instead and specify ports"
    dPort = "" if nsgParser.checkOptionalEmpty(options[10]) \
        else ("        destination_port_range {{\n"
              "            max = \"{}\"\n" \
              "            min = \"{}\"\n" \
              "        }}\n" \
              ).format(int(options[11]), int(options[10]))
    sPort = "" if nsgParser.checkOptionalEmpty(options[8]) \
        else ("        source_port_range {{\n"
              "            max = \"{}\"\n" \
              "            min = \"{}\"\n" \
              "        }}\n" \
              ).format(int(options[9]), int(options[8]))

    tempStr['protocol'] = protocolHeader
    tempStr['icmptype'] = type
    tempStr['icmpcode'] = code
    if str(options[11]) != '' and str(options[11]) != 'nan':
        tempStr['dportmax'] =  int(options[11])
    else:
        tempStr['dportmax'] =""
    if str(options[10]) != '' and str(options[10]) != 'nan':
        tempStr['dportmin'] = int(options[10])
    else:
        tempStr['dportmin'] =""
    if str(options[9]) != '' and str(options[9]) != 'nan':
        tempStr['sportmax'] =  int(options[9])
    else:
        tempStr['sportmax'] =""
    if str(options[8]) != '' and str(options[8]) != 'nan':
        tempStr['sportmin'] = int(options[8])
    else:
        tempStr['sportmin'] =""

    return tempStr
'''
        ("\n" \
            "    {}_options {{\n" \
            "{}" \
            "{}" \
            "    }}" \
            ).format(protocolHeader, dPort, sPort)
'''

def statelessOptional(nsgParser, options,tempStr):
    if not nsgParser.checkOptionalEmpty(options[3]) and str(options[3]).lower() == "true":
        tempStr['isstateless'] = 'true'
    else:
        tempStr['isstateless'] = 'false'
    return   tempStr


"""{'NSGName': 0, 'Direction': 1, 'Protocol': 2, 'isStateless': 3, 'SourceType': 4, 'Source': 5, 
DestType': 6, 'Destination': 7, 'SPortMin': 8, 'SPortMax': 9, 'DPortMin': 10, 'DPortMax': 11, 
'ICMPType': 12, 'ICMPCode': 13}"""


# templates to build NSG and NSG_Sec_Rules Terraform
def NSGtemplate(nsgParser, key, value, outdir, columnname):
    """Required: compartment_id and vcn_id"""
    columnvalue=''
    compartment_var_name = key[0].strip()
    # Added to check if compartment name is compatible with TF variable name syntax
    compartment_tf_name = commonTools.check_tf_variable(compartment_var_name)
    nsg_tf_name = commonTools.check_tf_variable(key[2])
    vcn_tf_name = commonTools.check_tf_variable(key[1])
    tempDict = {'compartment_tf_name': compartment_tf_name, 'display_name': key[2], 'nsg_tf_name': nsg_tf_name,
                'vcn_tf_name': vcn_tf_name}

    #Dictionary of column headers : column value
    updatedcols=[]
    nsg_done = []
    updatedrule=[]
    ruleindex = 1

    for rule in value:
        rule = list(rule)
        #Replace nan to "" in each value
        for eachvalue in rule:
            eachvalue = str(eachvalue)

            # Check for boolean/null in column values
            eachvalue = commonTools.check_columnvalue(eachvalue)

            updatedrule.append(eachvalue)

        #Change column header names to lower case for matching template
        for column in columnname:
            column = commonTools.check_column_headers(column)
            if column != '':
                updatedcols.append(column)

        tempStr = dict(zip(updatedcols, updatedrule))

        #process tags
        freeform_tags = commonTools.split_tag_values('freeform_tags', tempStr['freeform_tags'], tempStr)
        defined_tags = commonTools.split_tag_values('defined_tags', tempStr['defined_tags'], tempStr)

        tempStr.update(freeform_tags)
        tempStr.update(defined_tags)

        tempStr.update(tempDict)
        #NSG template; Write only for the first apperance.
        nsg_name = commonTools.check_tf_variable(key[2])

        resource_group = template.render(tempStr)
        if nsg_done == [] :
            nsg_done.append(nsg_name)
            with open(outdir + "/{}_nsg.tf".format(commonTools.check_tf_variable(key[2])), 'w') as f:
                f.write(resource_group)
        else:
            if nsg_name not in nsg_done:
                with open(outdir + "/{}_nsg.tf".format(commonTools.check_tf_variable(key[2])), 'w') as f:
                    f.write(resource_group)

        with open(outdir + "/{}_nsg.tf".format(commonTools.check_tf_variable(key[2])), 'a') as f:

            null_rule = 0
            for i in range(1,3):
                if(str(rule[i]).lower()=='nan'):
                    #print("Creating Empty NSG: "+rule[0])
                    null_rule=1
                    break
            if(null_rule==1):
                continue

            tempStr.update(NSGrulesTemplate(nsgParser, rule, ruleindex,tempStr))
            tempStr.update(statelessOptional(nsgParser, rule, tempStr))
            tempStr.update(directionOptionals(nsgParser, rule,tempStr))
            tempStr.update(protocolOptionals(nsgParser, rule,tempStr))

            nsg_rule = nsgrule.render(tempStr)
            f.write(nsg_rule)
            ruleindex += 1
        f.close()
    print("\n"+outdir + "/{}_nsg.tf".format(key[2]) + " containing TF for NSG has been created")


def NSGrulesTemplate(nsgParser, rule, index, tempStr):
    if(str(rule[14]).lower()=='nan'):
        rule[14]=""

    nsg_rule_tf_name = commonTools.check_tf_variable(rule[0])+"_security_rule"+str(index)
    direction = rule[1].upper()
    protocol = getProtocolNumber(rule[2])
    tempdict = { 'nsg_rule_tf_name' : nsg_rule_tf_name, 'direction' : direction, 'protocol_code' : protocol}
    tempStr.update(tempdict)

    return tempStr


def getProtocolNumber(protocol):
    if protocol.lower() == 'all':
        return "all"
    else:
        protocol_dict=commonTools().protocol_dict
        for k, v in protocol_dict.items():
            if (protocol).lower() == v.lower():
                return k
"""
    if protocol.lower() == 'tcp':
        return "6"
    if protocol.lower() == 'udp':
        return "17"
    if protocol.lower() == 'icmp':
        return "1"
"""

"""
The rules should be further organized with ingress or egress as a parent level to the optional fts.
factory methods
"""


def main():
    parser = argparse.ArgumentParser(description="Create NSG and its NSG rules based on inputs given in vcn-info.properties, separated by regions.")
    parser.add_argument("inputfile", help="Full Path of cd3 excel file or csv containing NSG info")
    parser.add_argument("outdir", help="Output directory")
    parser.add_argument("--configFileName", help="Config file name", required=False)
    args = parser.parse_args()
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    columnname=''

    if('.csv' in args.inputfile):
        df = pd.read_csv(args.inputfile)
        excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
        df.to_excel(excel_writer, 'NSGs')
        excel_writer.save()
        args.inputfile='tmp_to_excel.xlsx'

    # tested path allows for space, full or relative path acceptable
    nsgParser = cd3parser(os.path.realpath(args.inputfile)).getNSG()


    if('tmp_to_excel' in args.inputfile):
        os.remove(args.inputfile)
    outdir = args.outdir

    regionDict = nsgParser.getRegionDict()
    headerDict = nsgParser.getHeaderDict()
    listOfRegions = nsgParser.regions

    # creates all region directories in specified out directory
    for region in listOfRegions:
        if (region in commonTools.endNames):
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)
        regionDirPath = outdir + "/{}".format(region)
        """if os.path.exists(regionDirPath):
            nsgParser.purge(regionDirPath, "nsg.tf")
        else:
            os.makedirs(regionDirPath)
        """
        if not os.path.exists(regionDirPath):
            os.makedirs(regionDirPath)
    # Stage 2 using the dictionary of unique_id:rules, use factory method to produces resources and
    # rules
    for region in listOfRegions:
        if (region in commonTools.endNames):
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Backup of existing NSG files
        for region in ct.all_regions:
            if (os.path.exists(outdir + "/" + region)):
                resource = "NSG"
                print("Backing up all existing NSG TF files for region " + region + " to")
                commonTools.backup_file(outdir + "/" + region, resource, "_nsg.tf")

        # with open(outdir + "/{}/{}-NSG.tf".format(region,region), 'w') as f:
        reg_outdir = outdir + "/" + region

        for k,v in headerDict.items():
            for unique_headers,other_headers in v.items():
                for name in other_headers:
                    columnname = name

        [NSGtemplate(nsgParser, k, v, reg_outdir, columnname) for k, v in
         nsgParser.getRegionSpecificDict(regionDict, region).items()]

        #   f.close()
    #print("\nTerraform files write out to respective {}/[region]/[NSG Name]_nsg.tf".format(outdir))

    if DEBUG:
        nsgParser.debug()
        print("Rules only list and its indice:\n{}".format({k: v for v, k in enumerate(nsgParser.nsg.columns[3:])}))

if __name__ == '__main__':
    main()
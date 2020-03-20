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


DEBUG = False


# Stage 1 Parse into NetSec class and store into dictionary unique_id:rules
def directionOptionals(nsgParser, options):
    srcdestType = ""
    srcdest = ""

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
        srcdest="${oci_core_network_security_group."+srcdest+".id}"
    if (srcdestType.lower() == 'service'):
        srcdestType = "SERVICE_CIDR_BLOCK"

    if nsgParser.checkOptionalEmpty(srcdestType):
        return ""
    else:
        return ("\n\n" \
                "    {} = \"{}\"\n" \
                "    {}_type = \"{}\"\n" \
                ).format(ingressegressStrTemplate, srcdest, ingressegressStrTemplate, srcdestType)


def protocolOptionals(nsgParser, options):

    protocol = options[2].lower()
    protocolHeader = ""
    if protocol == "all":
        return ""
    elif protocol == "icmp":
        code = "" if nsgParser.checkOptionalEmpty(options[13]) \
            else "        code = \"{}\"\n".format(int(options[13]))
        if nsgParser.checkOptionalEmpty(options[12]):
            return (" ")
        else:
            return ("\n" \
                    "    icmp_options {{\n" \
                    "        type = \"{}\"\n" \
                    "{}"
                    "    }}" \
                    ).format(int(options[12]), code)
    elif protocol == "tcp":
        protocolHeader = protocol
    elif protocol == "udp":
        protocolHeader = protocol
    else:
        return "SELECTION UNCOMMON and NOT HANDLED, please use TCP instead and specify ports"
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

    return ("\n" \
            "    {}_options {{\n" \
            "{}" \
            "{}" \
            "    }}" \
            ).format(protocolHeader, dPort, sPort)


def statelessOptional(nsgParser, options):
    return "\n    stateless = \"True\"\n" if not nsgParser.checkOptionalEmpty(options[3]) and \
                                             str(options[3]).lower() == "true" else ""


"""{'NSGName': 0, 'Direction': 1, 'Protocol': 2, 'isStateless': 3, 'SourceType': 4, 'Source': 5, 
DestType': 6, 'Destination': 7, 'SPortMin': 8, 'SPortMax': 9, 'DPortMin': 10, 'DPortMax': 11, 
'ICMPType': 12, 'ICMPCode': 13}"""


# templates to build NSG and NSG_Sec_Rules Terraform
def NSGtemplate(nsgParser, key, value, outdir):
    """Required: compartment_id and vcn_id"""

    resource_group = ( \
        "resource \"oci_core_network_security_group\" \"{}\" {{\n"
        "    display_name = \"{}\" \n"
        "    compartment_id = \"${{var.{}}}\"\n"
        "    vcn_id = \"${{oci_core_vcn.{}.id}}\"\n"
        "}}\n" \
        ).format("{}".format(key[2]), key[2],key[0], commonTools.tfname.sub("-", key[1]))
    with open(outdir + "/{}_nsg.tf".format(key[2]), 'w') as f:
        f.write(resource_group)
        ruleindex = 1
        for rule in value:
            null_rule = 0
            for i in range(1,3):
                if(str(rule[i]).lower()=='nan'):
                    #print("Creating Empty NSG: "+rule[0])
                    null_rule=1
                    break
            if(null_rule==1):
                continue

            f.write("{}{}{}{}\n}}\n".format(NSGrulesTemplate(nsgParser, rule, ruleindex), \
                                            statelessOptional(nsgParser, rule), directionOptionals(nsgParser, rule), \
                                            protocolOptionals(nsgParser, rule)))

            ruleindex += 1
        f.close()
        print(outdir + "/{}_nsg.tf".format(key[2]) + " containing TF for NSG has been created")


def NSGrulesTemplate(nsgParser, rule, index):
    if(str(rule[14]).lower()=='nan'):
        rule[14]=""
    resource_group_rule = ( \
        "resource \"oci_core_network_security_group_security_rule\" \"{}_security_rule{}\" {{\n"
        "    network_security_group_id = \"${{oci_core_network_security_group.{}.id}}\"\n"
        "    description = \"{}\"\n"
        "    direction = \"{}\"\n"
        "    protocol = \"{}\""
    ).format(rule[0], index, rule[0], rule[14],rule[1].upper(), getProtocolNumber(rule[2]))
    return resource_group_rule


def getProtocolNumber(protocol):
    if protocol.lower() == 'all':
        return "all"
    if protocol.lower() == 'tcp':
        return "6"
    if protocol.lower() == 'udp':
        return "17"
    if protocol.lower() == 'icmp':
        return "1"


"""
The rules should be further organized with ingress or egress as a parent level to the optional fts.
factory methods
"""


def main():
    parser = argparse.ArgumentParser(description="Create NSG and its NSG rules based on\
        inputs given in vcn-info.properties, separated by regions.")
    parser.add_argument("inputfile", help="Full Path of cd3 excel file or csv containing NSG info")
    parser.add_argument("outdir", help="Output directory")
    args = parser.parse_args()

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
    listOfRegions = nsgParser.regions

    # creates all region directories in specified out directory
    # creates all region directories in specified out directory
    for region in listOfRegions:
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
        # with open(outdir + "/{}/{}-NSG.tf".format(region,region), 'w') as f:
        reg_outdir = outdir + "/" + region
        [NSGtemplate(nsgParser, k, v, reg_outdir) for k, v in
         nsgParser.getRegionSpecificDict(regionDict, region).items()]
        #   f.close()
    #print("\nTerraform files write out to respective {}/[region]/[NSG Name]_nsg.tf".format(outdir))

    if DEBUG:
        nsgParser.debug()
        print("Rules only list and its indice:\n{}".format({k: v for v, k in enumerate(nsgParser.nsg.columns[3:])}))


if __name__ == '__main__':
    main()
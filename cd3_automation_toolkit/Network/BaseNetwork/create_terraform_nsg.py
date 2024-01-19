#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Network Security Groups
#
# Author: Suruchi Singla
# Oracle Consulting
#

import math
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
def directionOptionals(row, tempStr):
    destination_type = str(row['Destination Type']).strip()
    source_type = str(row['Source Type']).strip()
    source = str(row['Source']).strip()
    destination = str(row['Destination']).strip()

    if source_type != 'nan':
        if (source_type.lower() == 'cidr') or (source_type == 'CIDR_BLOCK'):
            source_type = "CIDR_BLOCK"
        elif (source_type.lower() == 'service') or (source_type == 'SERVICE_CIDR_BLOCK'):
            source_type = "SERVICE_CIDR_BLOCK"
        elif (source_type.lower() == 'nsg') or (source_type == 'NETWORK_SECURITY_GROUP'):
            source_type = "NETWORK_SECURITY_GROUP"
            if "ocid" not in str(source):
                source = commonTools.check_tf_variable(str(row['VCN Name']).strip()+"_"+str(source))
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
                destination = commonTools.check_tf_variable(str(row['VCN Name']).strip()+"_"+str(destination))
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


def checkOptionalEmpty(option):
    return isinstance(option, (int, float)) and math.isnan(option)

def getProtocolNumber(protocol):
    if protocol.lower() == 'all':
        return "all"
    else:
        protocol_dict = commonTools().protocol_dict
        for k, v in protocol_dict.items():
            if (protocol).lower() == v.lower():
                return k


def protocolOptionals(row,tempStr):
    protocol = row['Protocol'].strip().lower()
    code = ''
    type = ''
    if protocol == "all":
        return ""
    elif protocol == "icmp":
        protocolHeader = protocol
        code = "" if checkOptionalEmpty(row['ICMPCode']) \
            else int(row['ICMPCode'])
        type = "" if checkOptionalEmpty(row['ICMPType']) \
            else int(row['ICMPType'])
    elif protocol == "tcp":
        protocolHeader = protocol
    elif protocol == "udp":
        protocolHeader = protocol
    else:
        return ""
    tempStr['protocol'] = protocolHeader
    tempStr['icmptype'] = type
    tempStr['icmpcode'] = code

    if str(row['DPortMax']).strip() != '' and str(row['DPortMax']) != 'nan':
        tempStr['dportmax'] = int(row['DPortMax'])
    else:
        tempStr['dportmax'] = ""
    if str(row['DPortMin']).strip() != '' and str(row['DPortMin']) != 'nan':
        tempStr['dportmin'] = int(row['DPortMin'])
    else:
        tempStr['dportmin'] = ""
    if str(row['SPortMax']).strip() != '' and str(row['SPortMax']) != 'nan':
        tempStr['sportmax'] = int(row['SPortMax'])
    else:
        tempStr['sportmax'] = ""
    if str(row['SPortMin']).strip() != '' and str(row['SPortMin']) != 'nan':
        tempStr['sportmin'] = int(row['SPortMin'])
    else:
        tempStr['sportmin'] = ""

    return tempStr

def statelessOptional(row, tempStr):
    if not checkOptionalEmpty(row['isStateless']) and str(row['isStateless']).lower() == "true":
        tempStr['isstateless'] = 'true'
    else:
        tempStr['isstateless'] = 'false'
    return tempStr


# Execution of the code begins here
def create_terraform_nsg(inputfile, outdir, service_dir, prefix, ct):
    # Read the arguments
    filename = inputfile

    sheetName = 'NSGs'
    nsg_auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'
    nsg_rules_auto_tfvars_filename = '_nsg-rules.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}
    tfrule = {}
    tempStr ={}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('nsg-template')
    nsgrule_template = env.get_template('nsg-rule-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" +service_dir + "/"
        commonTools.backup_file(srcdir, resource, nsg_auto_tfvars_filename)
        commonTools.backup_file(srcdir, resource, nsg_rules_auto_tfvars_filename)
        tfStr[eachregion] = ''
        tfrule[eachregion] = ''

    # Iterate over rows
    prevregion=""
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region=region.strip().lower()

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if(region!=prevregion):
            nsg_done = []
        prevregion = region

        # temporary dictionary1 and dictionary2
        tempdict = {}
        tempStr = {}

        empty_nsg=0
        if(str(df["Direction"][i]).strip()=='nan' or str(df["Protocol"][i]).strip()=='nan' or str(df["isStateless"][i]).strip()=="nan"):
            empty_nsg=1
        nsg_tf_name = commonTools.check_tf_variable(str(df["VCN Name"][i]).strip()+"_"+str(df["NSG Name"][i]).strip())

        for columnname in dfcolumns:

            # Column value
            if (columnname != 'Rule Description'):
                columnvalue = str(df[columnname][i]).strip()
            else:
                columnvalue = str(df[columnname][i])

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'NSG Name':
                columnvalue = columnvalue.strip()
                tempdict = {'display_name':columnvalue}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            columnname = commonTools.check_column_headers(columnname)
            if (columnname != 'rule_description'):
                tempStr[columnname] = str(columnvalue).strip()

            else:
                tempStr[columnname] = columnvalue

            tempStr.update(tempdict)
            tempStr.update({"nsg_tf_name":nsg_tf_name})

        if nsg_tf_name not in nsg_done:
            ruleindex = 1
            nsg_done.append(nsg_tf_name)
            tfStr[region] = tfStr[region] + template.render(tempStr)


        if empty_nsg==1:
            continue
        nsg_rule_tf_name = nsg_tf_name + "_security_rule" + str(ruleindex)
        direction = str(df['Direction'][i]).strip().upper()
        protocol = getProtocolNumber(str(df['Protocol'][i]).strip())
        tempdict = {'nsg_rule_tf_name': nsg_rule_tf_name, 'direction': direction, 'protocol_code': protocol}
        tempStr.update(tempdict)
        tempStr.update(statelessOptional(df.iloc[i], tempStr))
        tempStr.update(directionOptionals(df.iloc[i], tempStr))
        tempStr.update(protocolOptionals(df.iloc[i], tempStr))

        nsg_rule = nsgrule_template.render(tempStr)
        tfrule[region]=tfrule[region]+nsg_rule
        ruleindex += 1

    # Write to output
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if (tfStr[reg] != ''):
            outfile[reg] = reg_out_dir + "/" + prefix + nsg_auto_tfvars_filename
            srcStr = "##Add New NSGs for " + str(reg).lower() + " here##"
            tfStr[reg] = template.render(skeleton=True, region=reg).replace(srcStr, tfStr[reg] + "\n" + srcStr)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg] = open(outfile[reg], 'w+')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for NSGs has been created for region " + reg)

            with open(reg_out_dir + "/" + prefix + nsg_auto_tfvars_filename, 'a+') as f:
                f.write("\n" + "}")

        if (tfrule[reg] != ''):
            outfile[reg] = reg_out_dir + "/" + prefix + nsg_rules_auto_tfvars_filename
            srcStr = "##Add New NSG Rules for " + str(reg).lower() + " here##"
            tfrule[reg] = nsgrule_template.render(skeleton=True, region=reg).replace(srcStr, tfrule[reg] + "\n" + srcStr)
            tfrule[reg] = "".join([s for s in tfrule[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg] = open(outfile[reg], 'w+')
            oname[reg].write(tfrule[reg])
            oname[reg].close()
            print(outfile[reg] + " for NSG Rules has been created for region " + reg)

            with open(reg_out_dir +  "/" + prefix + nsg_rules_auto_tfvars_filename, 'a+') as f:
                f.write("\n"+"}")

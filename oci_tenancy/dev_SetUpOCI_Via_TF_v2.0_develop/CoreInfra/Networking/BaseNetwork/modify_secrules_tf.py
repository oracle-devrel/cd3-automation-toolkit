#!/bin/python

import argparse
import configparser
import csv
import os
import shutil
import re
import sys
import oci
import pandas as pd
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient

def backup_file(dir, pattern):
    print("backing up tf files ")
    for f in os.listdir(dir):
        if f.endswith(pattern):
            print(("backing up ....." +  os.path.join(dir, f)))
            path = os.path.join(dir, f)
            shutil.copy(path, path + "_backup")


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


def is_empty(myList):
    # print myList
    if not myList:
        return True
    else:
        return False


def create_ingress_rule_string(row):
    options = ""
    temp_rule = """
          ingress_security_rules {
                protocol = \"""" + get_protocol(row['Protocol']) + """\"
                source = \"""" + row['Source'] + """\"
                stateless = """ + str(row['isStateless'].lower()) + "\n"
    # print(rule.icmp_options)
    if row['Protocol'] == 'icmp' and row['ICMPCode']!='' and row['ICMPType']!='':
        options = """
               icmp_options {
                  code = """ + row['ICMPCode'] + """
                  type =  """ + row['ICMPType'] + """
               }  """
    dest_range = ""
    source_range = ""

    if row['Protocol'] == 'tcp' and str(row['DPortMax']) and str(row['DPortMin']):
        tcp_option = " \t\ttcp_options {"
        if str(row['DPortMax']):
            dest_range = dest_range  + """
            max = """ + str(row['DPortMax']) + """
            min = """ + str(row['DPortMin']) + """
            """

        #if not is_empty(row['Source']):
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_rang= """
            source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                \t\tmax = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                \t\tmin =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t\t}  """

        options = tcp_option + dest_range + source_range + "\n\t\t   }"
        if dest_range == '' and source_range == '':
            options = ''
    udp_option = ""
    if row['Protocol'] == 'udp' and str(row['DPortMax']) and str(row['DPortMin']):
        udp_option = " \t\tudp_options {"

        dest_range = """
            max = """ + str(row['DPortMax']) + """
            min =  """ + str(row['DPortMin']) + """
            """

        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
            source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                    max = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                    min =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t }  """

        options = udp_option + dest_range + source_range + "\n\t\t   }"

    close_bracket = "\n \t}"

    temp_rule = temp_rule + options + close_bracket
    return temp_rule


def create_egress_rule_string(row):
    options = ""
    egress_rule = """
          egress_security_rules {
                protocol = \"""" + get_protocol(row['Protocol']) + """\"
                destination = \"""" + row['Destination'] + """\"
                stateless = """ + str(row['isStateless'].lower()) + "\n"
    if row['Protocol'] == 'icmp' and row['ICMPCode']!='' and row['ICMPType']!='':
        options = """
               icmp_options {
                  code = """ + row['ICMPCode'] + """
                  type =  """ + row['ICMPType'] + """
               }  """
    dest_range = ""
    source_range = ""
    if row['Protocol'] == 'tcp':
        tcp_option = " tcp_options {"

        # tcp_option = tcp_option
        dest_range = """
                    max = """ + str(row['DPortMax']) + """
                    min =  """ + str(row['DPortMin']) + """
                 """
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
                        source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                        max = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                        min =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t }  """
        options = tcp_option + dest_range + source_range + "\n  }"

    if row['Protocol'] == 'udp':
        udp_option = " udp_options {"

        dest_range = """
                            max = """ + str(row['DPortMax']) + """
                            min =  """ + str(row['DPortMin']) + """
                         """
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
                                  source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                                max = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                                min =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t }  """

        options = udp_option + dest_range + source_range + "\n\t\t\t   }"
    close_bracket = "\n \t\t}"

    egress_rule = egress_rule + options + close_bracket
    return egress_rule


def init_subnet_details(subnetid ,vcn_display_name, seclist_per_subnet, sec_rule_per_seclist, overwrite):
    global create_def_file
    subnet = vnc.get_subnet(subnetid)
    #seclist_file = subnet.data.display_name.rsplit("-", 1)[0].strip() + "_seclist.tf"
    #seclist_files[subnet.data.display_name.rsplit("-", 1)[0].strip()] = seclist_file
    display_name=subnet.data.display_name
#    print("subnet -------------------------------------"+display_name)
    if ('-ad1-10.' in display_name or '-ad2-10.' in display_name or '-ad3-10.' in display_name or '-ad1-172.' in display_name
            or '-ad2-172.' in display_name or '-ad3-172.' in display_name or '-ad1-192.' in display_name or '-ad2-192.' in display_name
            or '-ad3-192.' in display_name):
        subnet_name= display_name.rsplit("-", 2)[0]
        seclist_file = subnet_name+'_seclist.tf'
        seclist_files[display_name.rsplit("-", 2)[0]]=seclist_file


    # display name contains CIDR
    elif ('-10.' in display_name or '-172.' in display_name or '192.' in display_name):
        subnet_name = display_name.rsplit("-", 1)[0]
        seclist_file = subnet_name+'_seclist.tf'
        seclist_files[subnet_name] = seclist_file
 #       print('subnet seclist_file===12'+seclist_file)
    else:
        subnet_name = display_name
        seclist_file = subnet_name+'_seclist.tf'
        seclist_files[subnet_name] = seclist_file
  #      print('subnet seclist_file===13'+seclist_file)

    seclist_rule_count_limit[subnet_name] = sec_rule_per_seclist

    rule_count = 0
    for seclist_id in subnet.data.security_list_ids:

        seclistname_display_name = vnc.get_security_list(seclist_id).data.display_name
        if (seclistname_display_name != "Default Security List for "+vcn_display_name):
            ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
            egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
            rule_count = rule_count + len(ingressRules)+len(egressRules)
            seclist_rule_count[subnet_name] = rule_count

def updateSecRules(seclistfile, text_to_replace, new_sec_rule, flags=0):
        with open(seclistfile, "r+") as file:
            fileContents = file.read()
            textPattern = re.compile(re.escape(text_to_replace), flags)
            fileContents = textPattern.sub(new_sec_rule, fileContents)
            file.seek(0)
            file.truncate()
            file.write(fileContents)
        file.close()


def incrementRuleCount(subnet_name):
        currentSecRuleCount = seclist_rule_count[subnet_name]
        seclist_rule_count[subnet_name] = currentSecRuleCount+1


def getReplacementStr(sec_rule_per_seclist,subnet_name):
    replaceString = "####ADD_NEW_SEC_RULES####"
    if subnet_name != 'def-vcn_seclist':
        list_no = (int(seclist_rule_count[subnet_name])//int(sec_rule_per_seclist) +1)
    else:
        list_no=1
    return replaceString + str(list_no)



def get_protocol(strprotocol):
    # print myList
    if str(strprotocol).lower() == "tcp":
        return "6"
    elif str(strprotocol).lower() == "icmp":
        return "1"
    elif str(strprotocol).lower() == "udp":
        return "17"
    elif str(strprotocol).lower() == "all":
        return "all"
    else:
        return strprotocol

def get_network_compartment_id(config, compartment_name):
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments,config["tenancy"],compartment_id_in_subtree=True)
    compartment_list = comp_list.data
    for compartment in compartment_list:
        if compartment.name == compartment_name:
            return compartment.id

def get_vcn_id(config,compartment_id,vcn_display_name):
    vcn = VirtualNetworkClient(config)
    vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns, compartment_id)
    vcn_list = vcns.data
    for vcn in vcn_list:

        if vcn.display_name.upper() == vcn_display_name.upper():
            return vcn.id

parser = argparse.ArgumentParser(description="Takes in an input file mentioning sec rules to be added for the subnet. See update_seclist-example.csv/CD3 for format under example folder. It will then take backup of all existing sec list files in outdir and create new one with modified rules")
parser.add_argument("inputfile",help="Full Path of vcn info file: It could be either the properties file eg vcn-info.properties or CD3 excel file")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("secrulesfile",help="Input file(either csv or CD3 excel) containing new secrules to be added for Security List of a given subnet")
parser.add_argument("--overwrite",help="This will overwrite all sec rules in OCI with whatever is specified in cd3 excel file sheet- SecRulesinOCI (yes or no) ",required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)


if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

secrulesfilename = args.secrulesfile
outdir = args.outdir


if args.overwrite is not None:
    overwrite = str(args.overwrite)
else:
    overwrite = "no"


if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()


region_dict = {'ashburn':'us-ashburn-1','phoenix':'us-phoenix-1','london':'uk-london-1','frankfurt':'eu-frankfurt-1','toronto':'ca-toronto-1','tokyo':'ap-tokyo-1','seoul':'ap-seoul-1','mumbai':'ap-mumbai-1'}
seclist_files = {}
seclist_rule_count = {}
seclist_rule_count_limit = {}
seclist_per_subnet_limit ={}
endNames = {'<END>', '<end>'}

# Read vcn info file and get subnet info
if('.properties' in args.inputfile):
    ociprops = configparser.RawConfigParser()
    ociprops.read(args.inputfile)

    all_regions = config.get('Default', 'regions')
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    #Get VCN  info from VCN_INFO section
    vcns=ociprops.options('VCN_INFO')

    for vcn_name in vcns:
        vcn_data = ociprops.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')

        region=vcn_data[0].strip().lower()
        if region not in all_regions:
            print("Invalid Region")
            exit(1)
        sec_rule_per_seclist = vcn_data[10].strip().lower()
        compartment_name = vcn_data[12].strip()

        ntk_comp_id = get_network_compartment_id(config, compartment_name)
        config.__setitem__("region", region_dict[region])
        vnc = VirtualNetworkClient(config)

        vcn_id = get_vcn_id(config, ntk_comp_id , vcn_name)

        subnet_list =  vnc.list_subnets(ntk_comp_id, vcn_id)
        for subnet in subnet_list.data:
            init_subnet_details(subnet.id,vcn_name,overwrite)
        print("seclist rule count: ")
        print(seclist_rule_count)

elif('.xls' in args.inputfile):
    df_info = pd.read_excel(args.inputfile, sheet_name='VCN Info', skiprows=1)
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]

    df = pd.read_excel(args.inputfile, sheet_name='VCNs',skiprows=1)
    for i in df.index:
        vcn_name = df['vcn_name'][i]
        region=df['Region'][i]
        if (region in endNames):
            break

        region=region.strip().lower()
        if region not in all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)

        seclist_per_subnet = df['sec_list_per_subnet'][i]
        sec_rule_per_seclist = df['sec_rule_per_seclist'][i]
        compartment_name = df['compartment_name'][i]

        ntk_comp_id = get_network_compartment_id(config, compartment_name)
        config.__setitem__("region", region_dict[region])
        vnc = VirtualNetworkClient(config)

        vcn_id = get_vcn_id(config, ntk_comp_id, vcn_name)

        if(vcn_id!=None):
            subnet_list = vnc.list_subnets(ntk_comp_id, vcn_id)
            for subnet in subnet_list.data:
                init_subnet_details(subnet.id, vcn_name, seclist_per_subnet, sec_rule_per_seclist, overwrite)
    print("seclist rule existing data  : ")
    print("Current total SecRules count in each subnet:")
    print(seclist_rule_count)
    print("Secrules limit defined as per sec_rule_per_seclist parameter in VCNs sheet")
    print(seclist_rule_count_limit)
    #print(seclist_files)

else:
    print("Invalid input vcn info file format; Acceptable formats: .xls, .xlsx, .properties")
    exit()

subnets_done={}
seclists_done={}
tfStr = {}
oname={}
default_ruleStr={}
default_seclists_done={}
defaultname={}

# Read input file containing new sec rules to be added
#If input is CD3 excel file
if('.xls' in secrulesfilename):

    NaNstr = 'NaN'
    if(overwrite=='yes'):
        print("\nReading SecRulesinOCI sheet of cd3 for overwrite option")
        df = pd.read_excel(secrulesfilename, sheet_name='SecRulesinOCI', skiprows=0, dtype=object).to_csv('out.csv')
        totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open('out.csv'))))
        i=0

        for reg in all_regions:
            defaultname[reg] = open(outdir + "/" +reg+ "/VCNs_Default_SecList.tf", "w")
            default_ruleStr[reg]=''
            default_seclists_done[reg] = []
            tfStr[reg]=''
            subnets_done[reg]=[]
            seclists_done[reg]=[]
            # Backup existing seclist files in ash and phx dir
            backup_file(outdir + "/" + reg, "_seclist.tf")

        with open('out.csv') as secrulesfile:
            reader = csv.DictReader(skipCommentedLine(secrulesfile))
            columns = reader.fieldnames
            rowCount = 0
            for row in reader:
                seclistName = row['SubnetName']

                if (seclistName.lower() == ''):# or 'Default Security List for' in seclistName):
                    continue

                vcn_name = row['VCN Name']
                compartment_name = row['Compartment Name']
                protocol = row['Protocol']
                ruleType = row['RuleType']
                region = row['Region']
                region=region.strip().lower()

                #if(region=='ashburn'):
                #Process Default SecLists-- Create new file containign default ecurity lists for all VCNs
                if('Default Security List for' in seclistName):
                    if (seclistName not in default_seclists_done[region]):
                        if(len(default_seclists_done[region])==0):
                            default_ruleStr[region]=default_ruleStr[region]+"""
    resource "oci_core_default_security_list" "default-security_list_""" + vcn_name + """" {
        manage_default_resource_id  = "${oci_core_vcn.""" + vcn_name + """.default_security_list_id}"
        ##Add More rules for """ + vcn_name + """##
    """
                        else:
                            default_ruleStr[region] = default_ruleStr[region] + """
    }
    resource "oci_core_default_security_list" "default-security_list_""" + vcn_name + """" {
        manage_default_resource_id  = "${oci_core_vcn.""" + vcn_name + """.default_security_list_id}"
        ##Add More rules for """ + vcn_name + """##
    """
                        default_seclists_done[region].append(seclistName)

                    new_sec_rule = ""
                    if ruleType == 'ingress':
                        new_sec_rule = create_ingress_rule_string(row)
                    if ruleType == 'egress':
                        new_sec_rule = create_egress_rule_string(row)
                    default_ruleStr[region] = default_ruleStr[region] + new_sec_rule
                    continue

                #Process other seclists
                subnetName = row['SubnetName'].rsplit('-',1)[0]

                if(subnetName not in subnets_done[region] or len(subnets_done[region])==0):
                    subnets_done[region].append(subnetName)
                    if(tfStr[region]!=''):
                        tfStr[region]=tfStr[region]+"""
    }"""
                        oname[region].write(tfStr[region])
                        tfStr[region] = ''
                        seclists_done[region] = []
                        oname[region].close()
                    oname[region] = open(outdir + "/" +region+"/"+ subnetName + "_seclist.tf", "w")


                if(seclistName not in seclists_done[region]):
                    if(len(seclists_done[region])!=0):
                        tfStr[region]=tfStr[region]+"""
    }"""
                    tfStr[region]=tfStr[region]+"""
    resource "oci_core_security_list" \"""" + seclistName +  """"{
    compartment_id = "${var.""" + compartment_name + """}"
    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
    ####ADD_NEW_SEC_RULES####""" + row['SubnetName'].rsplit('-',1)[1] + """
    """
                    seclists_done[region].append(seclistName)

                new_sec_rule = ""
                if ruleType == 'ingress':
                    new_sec_rule = create_ingress_rule_string(row)
                if ruleType == 'egress':
                    new_sec_rule = create_egress_rule_string(row)
                tfStr[region] = tfStr[region] + new_sec_rule


        tfStr[region]=tfStr[region]+"""
}"""

        oname[region].write(tfStr[region])
        oname[region].close()

        default_ruleStr[region]=default_ruleStr[region]+"""
}"""

        defaultname[region].write(default_ruleStr[region])
        defaultname[region].close()


    elif(overwrite=='no'):
        print("Reading AddSecRules sheet of cd3")
        df = pd.read_excel(secrulesfilename, sheet_name='AddSecRules',skiprows=1,dtype=object).to_csv('out.csv')

        totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open('out.csv'))))

        with open('out.csv') as secrulesfile:
            reader = csv.DictReader(skipCommentedLine(secrulesfile))
            columns = reader.fieldnames
            rowCount = 0
            for row in reader:
                region = str(row['Region']).lower()

                if(region=='<END>' or region=='<end>'):
                    break

                subnetName = row['SubnetName']
                protocol = row['Protocol']
                ruleType = row['RuleType']
                region = region.strip().lower()

                new_sec_rule = ""

                if ruleType == 'ingress':
                    new_sec_rule = create_ingress_rule_string(row)
                if ruleType == 'egress':
                    new_sec_rule = create_egress_rule_string(row)

                strDefault='Default Security List for'
                if(strDefault.lower() in subnetName.lower()):
                    print("file to modify :: VCNs_Default_SecList.tf")
                    sec_list_file="VCNs_Default_SecList.tf"
                    vcn_name=subnetName.split('for')[1].strip()
                    text_to_replace="##Add More rules for " + vcn_name + "##"
                    new_sec_rule = new_sec_rule + "\n" + text_to_replace
                    updateSecRules(outdir +"/"+region+ "/" + sec_list_file, text_to_replace, new_sec_rule, 0)


                elif(subnetName!=''):
                    sec_list_file = seclist_files[subnetName]
                    print("file to modify ::::: " + sec_list_file)
                    text_to_replace = getReplacementStr(sec_rule_per_seclist, subnetName)
                    new_sec_rule = new_sec_rule + "\n" + text_to_replace
                    updateSecRules(outdir +"/"+region+ "/" + sec_list_file, text_to_replace, new_sec_rule, 0)
                    incrementRuleCount(subnetName)


# If input is a csv file
elif ('.csv' in secrulesfilename):
    totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open(secrulesfilename))))
    with open(secrulesfilename) as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        rowCount = 0
        for row in reader:
            subnetName = row['SubnetName']
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


            sec_list_file = seclist_files[subnetName]
            print("file to modify ::::: "+ sec_list_file )
            text_to_replace = getReplacementStr(sec_rule_per_seclist,subnetName)
            new_sec_rule = new_sec_rule + "\n" + text_to_replace
            updateSecRules(outdir +"/"+region+ "/" + sec_list_file, text_to_replace, new_sec_rule, 0)
            incrementRuleCount(subnetName)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")

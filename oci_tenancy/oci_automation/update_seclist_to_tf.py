#!/bin/python

import ConfigParser
import argparse
import csv
import os
import shutil
import re
import sys
import oci
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
    print("row['SPortMin'] " + row['SPortMin'])
    options = ""
    temp_rule = """
          ingress_security_rules {
                protocol = \"""" + get_protocol(row['Protocol']) + """\"
                source = \"""" + row['Source'] + """\"
                stateless = """ + str(row['isStateless'].lower()) + "\n"
    # print(rule.icmp_options)
    if row['Protocol'] == 'icmp':
        options = """
               icmp_options {
                  "code" = """ + row['ICMPCode'] + """
                  "type" =  """ + row['ICMPType'] + """
               }  """
    dest_range = ""
    source_range = ""
    if row['Protocol'] == 'tcp':
        tcp_option = " \t\ttcp_options {"

        #if not is_empty(row['Destination']):
        dest_range = """
            "max" = """ + str(row['DPortMax']) + """
            "min" =  """ + str(row['DPortMin']) + """
         """
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
                source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                \t\t"max" = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                \t\t"min" =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t\t}  """

        options = tcp_option + dest_range + source_range + "\n\t\t   }"

    udp_option = ""
    if row['Protocol'] == 'udp':
        udp_option = " \t\tudp_options {"

        dest_range = """
                    "max" = """ + str(row['DPortMax']) + """
                    "min" =  """ + str(row['DPortMin']) + """
                 """
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
                          source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                        "max" = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                        "min" =  """ + str(row['SPortMin']) + ""
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
    if row['Protocol'] == 'icmp':
        options = """
               icmp_options {
                  "code" = """ + row['ICMPCode'] + """
                  "type" =  """ + row['ICMPType'] + """
               }  """
    dest_range = ""
    source_range = ""
    if row['Protocol'] == 'tcp':
        tcp_option = " tcp_options {"

        # tcp_option = tcp_option
        dest_range = """
                    "max" = """ + str(row['DPortMax']) + """
                    "min" =  """ + str(row['DPortMin']) + """
                 """
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
                        source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                        "max" = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                        "min" =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t }  """
        options = tcp_option + dest_range + source_range + "\n  }"

    if row['Protocol'] == 'udp':
        udp_option = " udp_options {"

        dest_range = """
                            "max" = """ + str(row['DPortMax']) + """
                            "min" =  """ + str(row['DPortMin']) + """
                         """
        if str(row['SPortMax']) or str(row['SPortMin']):
            source_range = """
                                  source_port_range {"""
            if str(row['SPortMax']):
                source_range = source_range + """
                                "max" = """ + str(row['SPortMax']) + ""
            if str(row['SPortMin']):
                source_range = source_range + """
                                "min" =  """ + str(row['SPortMin']) + ""
            source_range = source_range + " \n\t\t\t }  """

        options = udp_option + dest_range + source_range + "\n\t\t\t   }"
    close_bracket = "\n \t\t}"

    egress_rule = egress_rule + options + close_bracket
    return egress_rule


def init_subnet_details(subnetid ,vcn_display_name, overwrite):
    global create_def_file
    response = vnc.get_subnet(subnetid)
    seclist_file = response.data.display_name.rsplit("-", 1)[0].strip() + "_seclist.tf"
    seclist_files[response.data.display_name.rsplit("-", 1)[0].strip()] = seclist_file

    rule_count = 0
    for seclist_id in response.data.security_list_ids:
        seclistdata = vnc.get_security_list(seclist_id).data
        seclistname = vnc.get_security_list(seclist_id).data.display_name
        # print vnc.get_security_list(seclist_id).data.ingress_security_rules
        display_name = seclistname  # +  "-" + subnet

        if (seclistname != "Default Security List for "+vcn_display_name):
            ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
            #print("ingresscount " + str(len(ingressRules)))
            egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
            #print("egresscount " + str(len(egressRules)))
            rule_count = rule_count + len(ingressRules)+len(egressRules)
            if (overwrite.lower() != "true"):
                seclist_rule_count[response.data.display_name.rsplit("-", 1)[0].strip()] = rule_count
            else:
                seclist_rule_count[response.data.display_name.rsplit("-", 1)[0].strip()] = 0
        elif create_def_file:
            print("updating Seclist  ")
            seclist_files["def-vcn_seclist"] = "def-vcn_seclist_generated.tf"
            ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
            #print("ingresscount default " + str(len(ingressRules)))
            egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
            #print("egresscount default " + str(len(egressRules)))
            rule_count = rule_count + len(ingressRules)+len(egressRules)

            if (overwrite.lower() != "true"):
                seclist_rule_count["def-vcn_seclist"] = rule_count
            else:
                seclist_rule_count["def-vcn_seclist"] = 0
            create_def_file = False
        else:
            print("......................")


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
        list_no = (int(seclist_rule_count[subnet_name])/int(sec_rule_per_seclist) +1)
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
    comp_list = identity.list_compartments(compartment_id=config["tenancy"])
    compartment_list = comp_list.data
    for compartment in compartment_list:
        if compartment.name == compartment_name:
            return compartment.id

def get_vcn_id(config,compartment_id,vcn_display_name):
    vcn = VirtualNetworkClient(config)
    vcns = vcn.list_vcns(compartment_id=compartment_id)
    vcn_list = vcns.data
    for vcn in vcn_list:
        #print(vcn.display_name)
        #print(vcn_display_name)
        if vcn.display_name == vcn_display_name:
            return vcn.id

parser = argparse.ArgumentParser(description="Takes in a csv file mentioning sec rules to be added for the subnet. See update_seclist-example.csv for format under example folder. It will then take backup of all existing sec list files and create new one with modified rules; Required Arguements: propsfile, outdir and secrulesfile")
parser.add_argument("--propsfile",help="Full Path of properties file. eg oci-tf.properties in example folder",required=True)
parser.add_argument("--outdir",help="directory path for output tf files ",required=True)
parser.add_argument("--secrulesfile",help="csv file with secrules for Security List of a given subnet")
parser.add_argument("--overwrite",help="Overwite subnet files. When this flag is used, script expect new seclist files created using create_terraform_seclist.py   ")
#parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

outdir = args.outdir
secrulesfilename = args.secrulesfile
totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open(secrulesfilename))))
#overwrite = args.overwrite
backup_file(outdir, "_seclist.tf")

if args.overwrite is not None:
    overwrite = str(args.overwrite)
else:
    overwrite = "false"

seclist_files = {}
seclist_rule_count = {}

question = 'Input Name of Network compartment where VCN exist : '
print (question)
ntk_comp_name = raw_input()

config = oci.config.from_file()
ociprops = ConfigParser.RawConfigParser()
ociprops.read(args.propsfile)

ntk_comp_id = get_network_compartment_id(config, ntk_comp_name)

vnc = VirtualNetworkClient(config)

sec_rule_per_seclist = ociprops.get('Default', 'sec_rule_per_seclist')
vcn_display_name = ociprops.get('Default', 'vcn_display_name')
vcn_id = get_vcn_id(config, ntk_comp_id , vcn_display_name)

#vcn_id = ociprops.get('Default', 'vcn_id')
#ntk_comp_id = ociprops.get('Default', 'ntk_comp_id')

subnet_list = response = vnc.list_subnets(ntk_comp_id, vcn_id)
create_def_file = True
for subnet in subnet_list.data:
    init_subnet_details(subnet.id,vcn_display_name,overwrite)

print(seclist_rule_count)
with open(secrulesfilename) as secrulesfile:
    reader = csv.DictReader(skipCommentedLine(secrulesfile))
    columns = reader.fieldnames
    print(totalRowCount)
    rowCount = 0
    maxRulesPerFile = 4
    for row in reader:
        #print(row)
        protocol = row['Protocol']
        ruleType = row['RuleType']
        subnetName = row['SubnetName']
        new_sec_rule =""
        if ruleType == 'ingress':
                new_sec_rule = create_ingress_rule_string(row)
        if ruleType == 'egress':
                new_sec_rule = create_egress_rule_string(row)


        sec_list_file = seclist_files[subnetName]
        print("file to modify ::::: "+ sec_list_file )
        #print("secrule count " + str(seclist_rule_count[subnetName]))
        text_to_replace = getReplacementStr(sec_rule_per_seclist,subnetName)
        new_sec_rule = new_sec_rule + "\n" + text_to_replace
        updateSecRules(outdir + "/" + sec_list_file, text_to_replace, new_sec_rule, 0)
        incrementRuleCount(subnetName)
        ####ADD_NEW_SEC_RULES####


#!/usr/bin/python3

import argparse
import csv
import os
import re
import sys
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

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
    ingress_rule = """
          ingress_security_rules {
                protocol = \"""" + get_protocol(row['Protocol']) + """\"
                source = \"""" + row['Source'] + """\"
                stateless = """ + str(row['isStateless'].lower()) + "\n"
    if ("services-in-oracle-services-network" in row['Source'] or "objectstorage" in row['Source']):
        ingress_rule = ingress_rule + """
                source_type = "SERVICE_CIDR_BLOCK"
        """
    if row['Protocol'] == 'icmp' and row['ICMPCode']!='' and row['ICMPType']!='':
        options = """
               icmp_options {
                  code = """ + row['ICMPCode'] + """
                  type =  """ + row['ICMPType'] + """
               }  """

    dest_range = ""
    source_range = ""
    if row['Protocol'] == 'tcp':
        tcp_option = """
                tcp_options {"""
        # tcp_option = tcp_option
        if str(row['DPortMax']) and str(row['DPortMin']):
            if str(row['DPortMax']).lower() != 'all' and str(row['DPortMin']).lower() != 'all':
                dest_range = """
                        max = """ + str(row['DPortMax']) + """
                        min =  """ + str(row['DPortMin']) + """
                     """
        if str(row['SPortMax']) and str(row['SPortMin']):
            if str(row['SPortMax']).lower() != 'all' and str(row['SPortMin']).lower() != 'all':
                source_range = """
                source_port_range {
                        max = """ + str(row['SPortMax']) + """
                        min =  """ + str(row['SPortMin']) + """
                        }
                     """
        if (dest_range != '' or source_range != ''):
            options = tcp_option + dest_range + source_range + "\n  }"

    if row['Protocol'] == 'udp':
        udp_option = """
                udp_options {"""
        if str(row['DPortMax']) and str(row['DPortMin']):
            if str(row['DPortMax']).lower() != 'all' and str(row['DPortMin']).lower() != 'all':
                dest_range = """
                        max = """ + str(row['DPortMax']) + """
                        min =  """ + str(row['DPortMin']) + """
                     """
        if str(row['SPortMax']) and str(row['SPortMin']):
            if str(row['SPortMax']).lower() != 'all' and str(row['SPortMin']).lower() != 'all':
                source_range = """
                source_port_range {
                        max = """ + str(row['SPortMax']) + """
                        min =  """ + str(row['SPortMin']) + """
                        }
                     """
        if (dest_range != '' or source_range != ''):
            options = udp_option + dest_range + source_range + "\n\t\t\t   }"

    close_bracket = "\n \t\t}"
    ingress_rule = ingress_rule + options + close_bracket


#    if row['Protocol'] == 'tcp' and str(row['DPortMax']) and str(row['DPortMin']):
#        tcp_option = " \t\ttcp_options {"
#        if str(row['DPortMax']).lower() != 'all' and str(row['DPortMin']).lower() != 'all':
#            dest_range = dest_range  + """
#            max = """ + str(row['DPortMax']) + """
#            min = """ + str(row['DPortMin']) + """
#            """
#        options = tcp_option + dest_range+ "\n\t\t   }"
#        if dest_range == '' and source_range == '':
#            options = ''
#    if row['Protocol'] == 'udp' and str(row['DPortMax']) and str(row['DPortMin']):
#        udp_option = " \t\tudp_options {"
#        if str(row['DPortMax']).lower() != 'all' and str(row['DPortMin']).lower() != 'all':
#            dest_range = """
#            max = """ + str(row['DPortMax']) + """
#            min =  """ + str(row['DPortMin']) + """
#            """
#        options = udp_option + dest_range + "\n\t\t   }"
#        if dest_range == '' and source_range == '':
#            options = ''

#    close_bracket = "\n \t}"

#    temp_rule = temp_rule + options + close_bracket
    return ingress_rule


def create_egress_rule_string(row):
    options = ""
    egress_rule = """
          egress_security_rules {
                protocol = \"""" + get_protocol(row['Protocol']) + """\"
                destination = \"""" + row['Destination'] + """\"
                stateless = """ + str(row['isStateless'].lower()) + "\n"
    if ("services-in-oracle-services-network" in row['Destination'] or "objectstorage" in row['Destination']):
        egress_rule = egress_rule + """
                destination_type = "SERVICE_CIDR_BLOCK"
        """
    if row['Protocol'] == 'icmp' and row['ICMPCode']!='' and row['ICMPType']!='':
        options = """
               icmp_options {
                  code = """ + row['ICMPCode'] + """
                  type =  """ + row['ICMPType'] + """
               }  """
    dest_range = ""
    source_range = ""
    if row['Protocol'] == 'tcp':
        tcp_option = """
                tcp_options {"""

        # tcp_option = tcp_option
        if str(row['DPortMax']) and str(row['DPortMin']):
            if str(row['DPortMax']).lower()!='all' and str(row['DPortMin']).lower()!='all':
                dest_range = """
                    max = """ + str(row['DPortMax']) + """
                    min =  """ + str(row['DPortMin']) + """
                 """
        if str(row['SPortMax']) and str(row['SPortMin']):
            source_range = """
                source_port_range {
                    max = """ + str(row['SPortMax']) + """
                    min =  """ + str(row['SPortMin']) + """
                    }
                 """
        if(dest_range!='' or source_range!=''):
            options = tcp_option + dest_range + source_range + "\n  }"

    if row['Protocol'] == 'udp':
        udp_option = """
                udp_options {"""
        if str(row['DPortMax']) and str(row['DPortMin']):
            if str(row['DPortMax']).lower() != 'all' and str(row['DPortMin']).lower() != 'all':
                dest_range = """
                    max = """ + str(row['DPortMax']) + """
                    min =  """ + str(row['DPortMin']) + """
                 """
        if str(row['SPortMax']) and str(row['SPortMin']):
            source_range = """
                source_port_range {
                    max = """ + str(row['SPortMax']) + """
                    min =  """ + str(row['SPortMin']) + """
                    }
                 """
        if (dest_range != '' or source_range != ''):
            options = udp_option + dest_range + source_range + "\n\t\t\t   }"

    close_bracket = "\n \t\t}"
    egress_rule = egress_rule + options + close_bracket
    return egress_rule

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

"""def init_subnet_details(subnetid ,vcn_display_name, sec_rule_per_seclist):
    global create_def_file
    subnet = vnc.get_subnet(subnetid)
    rule_count = 0
    for seclist_id in subnet.data.security_list_ids:
        seclistname_display_name = vnc.get_security_list(seclist_id).data.display_name
        if (seclistname_display_name != "Default Security List for "+vcn_display_name):
            ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
            egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
            rule_count = rule_count + len(ingressRules)+len(egressRules)
            #seclist_rule_count[subnet_name] = rule_count
            if ('-ad1-10.' in seclistname_display_name or '-ad2-10.' in seclistname_display_name or '-ad3-10.' in seclistname_display_name or '-ad1-172.' in seclistname_display_name
                    or '-ad2-172.' in seclistname_display_name or '-ad3-172.' in seclistname_display_name or '-ad1-192.' in seclistname_display_name or '-ad2-192.' in seclistname_display_name
                    or '-ad3-192.' in seclistname_display_name):
                secname = vcn_display_name+"_"+seclistname_display_name.rsplit("-", 3)[0]

            # display name contains CIDR
            elif ('-10.' in seclistname_display_name or '-172.' in seclistname_display_name or '192.' in seclistname_display_name):
                secname = vcn_display_name+"_"+seclistname_display_name.rsplit("-", 2)[0]

            else:
                secname = vcn_display_name+"_"+seclistname_display_name.rsplit("-", 1)[0]

            seclist_rule_count[secname] = rule_count
            seclist_rule_count_limit[secname] = sec_rule_per_seclist

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
"""
parser = argparse.ArgumentParser(description="Takes in an input file mentioning sec rules to be added for the subnet. See update_seclist-example.csv/CD3 for format under example folder. It will then take backup of all existing sec list files in outdir and create new one with modified rules")
parser.add_argument("inputfile",help="Full Path of vcn info file: It could be either the properties file eg vcn-info.properties or CD3 excel file")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("secrulesfile",help="Input file(either csv or CD3 excel) containing new secrules to be added for Security List of a given subnet")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

secrulesfilename = args.secrulesfile
outdir = args.outdir


seclist_files = {}
seclist_rule_count = {}
seclist_rule_count_limit = {}
seclist_per_subnet_limit ={}

# Read vcn info file and get subnet info
"""
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
        config.__setitem__("region", cTools.region_dict[region])
        vnc = VirtualNetworkClient(config)

        vcn_id = get_vcn_id(config, ntk_comp_id , vcn_name)

        subnet_list =  vnc.list_subnets(ntk_comp_id, vcn_id)
        for subnet in subnet_list.data:
            init_subnet_details(subnet.id,vcn_name)
        print("seclist rule count: ")
        print(seclist_rule_count)

elif('.xls' in args.inputfile):
    vcnInfo = parseVCNInfo(args.inputfile)
    vcns = parseVCNs(args.inputfile)
    sec_rule_per_seclist=vcnInfo.secrule_per_seclist

    for vcn_name in vcns.vcn_names:
        compartment_name = vcns.vcn_compartment[vcn_name]
        region=vcns.vcn_region[vcn_name]

        ntk_comp_id = get_network_compartment_id(config, compartment_name)
        config.__setitem__("region", commonTools.region_dict[region])
        vnc = VirtualNetworkClient(config)

        vcn_id = get_vcn_id(config, ntk_comp_id, vcn_name)

        if(vcn_id!=None):
            subnet_list = vnc.list_subnets(ntk_comp_id, vcn_id)
            for subnet in subnet_list.data:
                init_subnet_details(subnet.id, vcn_name, sec_rule_per_seclist)
    print("seclist rule existing data  : ")
    print("Current total SecRules count in each subnet:")
    print(seclist_rule_count)
    print("Secrules limit defined as per sec_rule_per_seclist parameter in VCNs sheet")
    print(seclist_rule_count_limit)
    #print(seclist_files)

else:
    print("Invalid input vcn info file format; Acceptable formats: .xls, .xlsx, .properties")
    exit()
"""
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
    vcns = parseVCNs(secrulesfilename)
    vcnInfo = parseVCNInfo(secrulesfilename)


    print("\nReading SecRulesinOCI sheet of cd3 for overwrite option")
    df = pd.read_excel(secrulesfilename, sheet_name='SecRulesinOCI', skiprows=0, dtype=object).to_csv('out.csv')
    totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open('out.csv'))))
    i=0

    for reg in vcnInfo.all_regions:
        defaultname[reg] = open(outdir + "/" +reg+ "/VCNs_Default_SecList.tf", "w")
        default_ruleStr[reg]=''
        default_seclists_done[reg] = []
        tfStr[reg]=''
        oname[reg]=None
        subnets_done[reg]=[]
        seclists_done[reg]=[]
        # Backup existing seclist files in ash and phx dir
        print("backing up tf files for region " + reg)
        commonTools.backup_file(outdir + "/" + reg, "_seclist.tf")

    with open('out.csv') as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        rowCount = 0
        for row in reader:
            display_name = row['SecListName']
            seclistName=""
            # display name contains AD1, AD2 or AD3 and CIDR
            if ('-ad1-10.' in display_name or '-ad2-10.' in display_name or '-ad3-10.' in display_name or '-ad1-172.' in display_name
                    or '-ad2-172.' in display_name or '-ad3-172.' in display_name or '-ad1-192.' in display_name or '-ad2-192.' in display_name
                    or '-ad3-192.' in display_name):
                seclistName = display_name.rsplit("-", 2)[0]

            # display name contains CIDR
            elif ('-10.' in display_name or '-172.' in display_name or '192.' in display_name):
                seclistName = display_name.rsplit("-", 1)[0]
            else:
                seclistName = display_name

            if (seclistName.lower() == ''):# or 'Default Security List for' in seclistName):
                continue

            vcn_name = row['VCN Name']
            # Process only those VCNs which are present in cd3(and have been created via TF)
            if(vcn_name not in vcns.vcn_names):
                print("skipping seclist: "+seclistName + " as its VCN is not part of VCNs tab in cd3")
                continue
            compartment_name = row['Compartment Name']
            protocol = row['Protocol']
            ruleType = row['RuleType']
            region = row['Region']
            region=region.strip().lower()

            if('Default Security List for' in seclistName):
                if (vcn_name+"_"+seclistName not in default_seclists_done[region]):
                    if(len(default_seclists_done[region])==0):
                        default_ruleStr[region]=default_ruleStr[region]+"""
    resource "oci_core_default_security_list" \"""" +vcn_name+"_default-security_list" """" {
        manage_default_resource_id  = "${oci_core_vcn.""" + vcn_name + """.default_security_list_id}"
        ##Add More rules for """ + vcn_name + """##
    """
                    else:
                        default_ruleStr[region] = default_ruleStr[region] + """
    }
    resource "oci_core_default_security_list" \"""" +vcn_name+"_default-security_list" """" {
        manage_default_resource_id  = "${oci_core_vcn.""" + vcn_name + """.default_security_list_id}"
        ##Add More rules for """ + vcn_name + """##
    """
                    default_seclists_done[region].append(vcn_name+"_"+seclistName)

                new_sec_rule = ""
                if ruleType == 'ingress':
                    new_sec_rule = create_ingress_rule_string(row)
                if ruleType == 'egress':
                    new_sec_rule = create_egress_rule_string(row)
                default_ruleStr[region] = default_ruleStr[region] + new_sec_rule
                continue

            #Process other seclists
            #subnetName = row['SecListName'].rsplit('-', 1)[0]
            subnetName = seclistName.rsplit('-', 1)[0]

            if(vcn_name+"_"+subnetName not in subnets_done[region] or len(subnets_done[region])==0):
                subnets_done[region].append(vcn_name+"_"+subnetName)
                if(tfStr[region]!=''):
                    tfStr[region]=tfStr[region]+"""
    }"""
                    oname[region].write(tfStr[region])
                    tfStr[region] = ''
                    seclists_done[region] = []
                    oname[region].close()
                oname[region] = open(outdir + "/" +region+"/"+ vcn_name+"_"+subnetName + "_seclist.tf", "w")


            if(vcn_name+"_"+seclistName not in seclists_done[region]):
                if(len(seclists_done[region])!=0):
                    tfStr[region]=tfStr[region]+"""
    }"""
                tfStr[region]=tfStr[region]+"""
    resource "oci_core_security_list" \"""" + vcn_name+"_"+seclistName +  """"{
    compartment_id = "${var.""" + compartment_name + """}"
    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
    display_name = \"""" +display_name +  """"
    ####ADD_NEW_SEC_RULES####""" + row['SecListName'].rsplit('-',1)[1] + """
    """
                seclists_done[region].append(vcn_name+"_"+seclistName)

            new_sec_rule = ""
            if ruleType == 'ingress':
                new_sec_rule = create_ingress_rule_string(row)
            if ruleType == 'egress':
                new_sec_rule = create_egress_rule_string(row)
            tfStr[region] = tfStr[region] + new_sec_rule


    for reg in vcnInfo.all_regions:
        tfStr[reg]=tfStr[reg]+"""
}"""
        if(oname[reg]!=None):
            oname[reg].write(tfStr[reg])
            oname[reg].close()

        if(default_ruleStr[reg]!=''):
            default_ruleStr[reg]=default_ruleStr[reg]+"""
}"""

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
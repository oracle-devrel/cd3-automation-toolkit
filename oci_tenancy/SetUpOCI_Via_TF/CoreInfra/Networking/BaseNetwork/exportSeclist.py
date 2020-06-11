#!/usr/bin/python3


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)

compartment_ids = {}

global ntk_compartment_ids
ntk_compartment_ids = {}

def get_network_compartment_ids(c_id,c_name):
    compartments = idc.list_compartments(compartment_id=c_id,compartment_id_in_subtree =False)
    for c in compartments.data:
        if c.lifecycle_state =="ACTIVE" :
            if(c_name!="root"):
                name=c_name+"::"+c.name
            else:
                name=c.name
            ntk_compartment_ids[name]=c.id

            # Put individual compartment names also in the dictionary
            if (name != c.name and c.name not in ntk_compartment_ids.keys()):
                ntk_compartment_ids[c.name] = c.id

            get_network_compartment_ids(c.id,name)

"""def get_network_compartment_id(config):#, compartment_name):
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments,config["tenancy"],compartment_id_in_subtree=True)
    compartment_list = comp_list.data

    #if(compartment_name=='root'):
    for compartment in compartment_list:
        if(compartment.lifecycle_state == 'ACTIVE'):
            compartment_ids[compartment.name]=compartment.id

    compartment_ids['root']=config['tenancy']
    return compartment_ids
"""

def print_secrules(seclists,region,vcn_name,comp_name):
    global rows

    for seclist in seclists.data:
        isec_rules = seclist.ingress_security_rules
        esec_rules = seclist.egress_security_rules
        display_name = seclist.display_name
        dn=display_name

        if (tf_import_cmd == "true"):
            tf_name = vcn_name + "_" + dn
            tf_name=commonTools.check_tf_variable(tf_name)
            if("Default Security List for " in dn):
                importCommands[region.lower()].write("\nterraform import oci_core_default_security_list." + tf_name + " " + str(seclist.id))
            else:
                importCommands[region.lower()].write("\nterraform import oci_core_security_list." + tf_name + " " + str(seclist.id))

        if(len(isec_rules)==0 and len(esec_rules)==0):
            new_row=(region,comp_name,vcn_name,dn,'','','','','','','','','','','','')
            rows.append(new_row)

        for rule in esec_rules:
            desc=str(rule.description)
            if(desc=="None"):
                desc=""
            if rule.protocol == "all":
                printstr = (dn + ",egress,all," + str(rule.is_stateless) + "," + rule.destination + ",,,,,,,,"+desc)
                new_row=(region,comp_name,vcn_name,dn,'egress','all',str(rule.is_stateless),'','','',rule.destination,'','','','',desc)
            elif rule.protocol == "1":
                if rule.icmp_options is None:
                    printstr = (dn + ",egress,icmp," + str(rule.is_stateless) + "," + rule.destination + ",,,,,,,."+desc)
                    new_row = (region,comp_name,vcn_name,dn,'egress','icmp',str(rule.is_stateless),'','','',rule.destination,'','','','',desc)
                else:
                    code = convertNullToNothing(rule.icmp_options.code)
                    type = convertNullToNothing(rule.icmp_options.type)
                    printstr = (dn + ",egress,icmp," + str(rule.is_stateless) + "," + rule.destination + ",,,,,"+type+","+code,+","+desc)
                    new_row=(region,comp_name,vcn_name,dn,'egress','icmp',str(rule.is_stateless),'','','',rule.destination,'','',type,code,desc)
            elif rule.protocol == "6":
                if rule.tcp_options is None:
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination+",,,,,"+desc)
                    new_row=(region,comp_name,vcn_name,dn,'egress','tcp',str(rule.is_stateless),'','','',rule.destination,'','','','',desc)
                elif rule.tcp_options.source_port_range is not None:
                    min = convertNullToNothing(rule.tcp_options.source_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.source_port_range.max)
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    new_row=(region,comp_name,vcn_name,dn,'egress','tcp',str(rule.is_stateless),'',min,max,rule.destination,'','','','',desc)
                elif rule.tcp_options.destination_port_range is not None:
                    min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'egress', 'tcp', str(rule.is_stateless), '', '', '',rule.destination, min, max, '', '',desc)
            elif rule.protocol == "17":
                if rule.udp_options is None:
                    printstr = (dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination+",,,,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'egress', 'udp', str(rule.is_stateless), '', '', '',rule.destination, '', '', '', '',desc)
                elif rule.udp_options.source_port_range is not None:
                    min = convertNullToNothing(rule.udp_options.source_port_range.min)
                    max = convertNullToNothing(rule.udp_options.source_port_range.max)
                    printstr = (dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'egress', 'udp', str(rule.is_stateless), '', min, max,rule.destination, '', '', '', '',desc)

                elif rule.udp_options.destination_port_range is not None:
                    min = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    printstr=(dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'egress', 'udp', str(rule.is_stateless), '', '', '',rule.destination, min, max, '', '',desc)
            #Any Other protocol
            else:
                protocol=commonTools().protocol_dict[rule.protocol].lower()
                new_row= (region, comp_name, vcn_name, dn, 'egress', protocol, str(rule.is_stateless), '', '', '',rule.destination, '', '', '', '',desc)

            rows.append(new_row)
            if(tf_import_cmd=="false"):
                print(printstr)
        for rule in isec_rules:
            desc = str(rule.description)
            if (desc == "None"):
                desc = ""

            if rule.protocol == "6":
                if rule.tcp_options is None:
                    printstr= (dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'ingress','tcp',str(rule.is_stateless),rule.source,'','','','','','','',desc)
                elif rule.tcp_options.destination_port_range is not None:
                    min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    printstr= (dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",,,," + min + "," + max+",,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'tcp', str(rule.is_stateless), rule.source, '', '', '',min, max, '', '',desc)
                else:
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'tcp', str(rule.is_stateless), rule.source, '', '', '','', '', '', '',desc)

            elif rule.protocol == "1":
                if rule.icmp_options is None:
                    printstr= (dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'icmp', str(rule.is_stateless), rule.source, '', '', '','', '', '', '',desc)
                else:
                    code = convertNullToNothing(rule.icmp_options.code)
                    type = convertNullToNothing(rule.icmp_options.type)
                    printstr= (dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",,,,,," + type + "," + code+","+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'icmp', str(rule.is_stateless), rule.source, '', '', '','', '', type, code,desc)

            elif rule.protocol == "17":
                if rule.udp_options is None:
                    printstr= (dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'udp', str(rule.is_stateless), rule.source, '', '', '','', '', '', '',desc)
                elif rule.udp_options.destination_port_range is not None:
                    min = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    printstr= (dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",,,," + min + "," + max+",,,"+desc)
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'udp', str(rule.is_stateless), rule.source, '', '', '',min, max, '', '',desc)
                else:
                    new_row = (region, comp_name, vcn_name, dn, 'ingress', 'udp', str(rule.is_stateless), rule.source, '', '', '','', '', '', '',desc)

            elif rule.protocol == "all":
                printstr= (dn + ",ingress,all," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                new_row=(region, comp_name, vcn_name, dn, 'ingress', 'all', str(rule.is_stateless), rule.source, '', '', '','', '', '', '',desc)
            #Any Other protocol
            else:
                protocol=commonTools().protocol_dict[rule.protocol].lower()
                new_row= (region, comp_name, vcn_name, dn, 'ingress', protocol, str(rule.is_stateless), rule.source, '', '','', '', '', '', '',desc)

            rows.append(new_row)
            if (tf_import_cmd == "false"):
                print(printstr)


parser = argparse.ArgumentParser(description="Export Security list on OCI to CD3")
parser.add_argument("cd3file", help="path of CD3 excel file to export rules to")
parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Networking Objects", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)
parser.add_argument("--tf_import_cmd", help="write tf import commands" , required=False)
parser.add_argument("--outdir", help="outdir for TF import commands script" , required=False)



if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
cd3file=args.cd3file

if('.xls' not in cd3file):
    print("\nAcceptable cd3 format: .xlsx")
    exit()

tf_import_cmd = args.tf_import_cmd
outdir = args.outdir

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

input_compartment_list = args.networkCompartment
if(input_compartment_list is not None):
    input_compartment_names = input_compartment_list.split(",")
    input_compartment_names = [x.strip() for x in input_compartment_names]
else:
    input_compartment_names = None

if tf_import_cmd is not None:
    tf_import_cmd="true"
    if(outdir is None):
        print("out directory is a mandatory arguement to write tf import commands ")
        exit(1)
else:
    tf_import_cmd = "false"

idc = IdentityClient(config)
ntk_compartment_ids["root"] = config['tenancy']
get_network_compartment_ids(config['tenancy'],"root")

rows=[]
all_regions=[]

if(tf_import_cmd=="true"):
    importCommands={}
    regionsubscriptions = idc.list_region_subscriptions(tenancy_id=config['tenancy'])
    for rs in regionsubscriptions.data:
        for k, v in commonTools().region_dict.items():
            if (rs.region_name == v):
                all_regions.append(k)
    for reg in all_regions:
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "a")
        importCommands[reg].write("\n\n######### Writing import for Security Lists #########\n\n")

else:
    vcnInfo = parseVCNInfo(cd3file)
    all_regions=vcnInfo.all_regions

print("\nFetching Security Rules...")

for reg in all_regions:
    config.__setitem__("region", commonTools().region_dict[reg])
    vcn = VirtualNetworkClient(config)
    region = reg.capitalize()
    comp_ocid_done = []
    for ntk_compartment_name in ntk_compartment_ids:
        if ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                continue
            comp_ocid_done.append(ntk_compartment_ids[ntk_compartment_name])
            vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
            for v in vcns.data:
                vcn_id = v.id
                vcn_name=v.display_name
                comp_ocid_done_again = []
                for ntk_compartment_name_again in ntk_compartment_ids:
                    if ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                        if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                            continue
                        comp_ocid_done_again.append(ntk_compartment_ids[ntk_compartment_name_again])
                        seclists = oci.pagination.list_call_get_all_results(vcn.list_security_lists,compartment_id=ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE',sort_by='DISPLAYNAME')
                        print_secrules(seclists,region,vcn_name,ntk_compartment_name_again)


commonTools.write_to_cd3(rows,cd3file,"SecRulesinOCI")
if (tf_import_cmd == "true"):
    for reg in all_regions:
        importCommands[reg].close()


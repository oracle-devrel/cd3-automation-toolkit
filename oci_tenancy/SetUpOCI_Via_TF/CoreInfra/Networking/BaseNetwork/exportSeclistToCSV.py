#!/bin/python


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient


def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)

def get_network_compartment_id(config, compartment_name):
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments,config["tenancy"],compartment_id_in_subtree=True)
    compartment_list = comp_list.data
    for compartment in compartment_list:
        if compartment.name == compartment_name:
            return compartment.id

def get_vcn_id(config,compartment_id,vname):
    vcncient = VirtualNetworkClient(config)
    vcnlist = vcncient.list_vcns(compartment_id=compartment_id,lifecycle_state="AVAILABLE")
    vcn_name = vname.lower()
    for v in vcnlist.data:
        name = v.display_name
        if name.lower() == vcn_name:
            return vcn.id

def get_vcns(config,compartment_id):
    vcncient = VirtualNetworkClient(config)
    vcnlist = vcncient.list_vcns(compartment_id=compartment_id,lifecycle_state="AVAILABLE")
    return vcnlist


def print_secrules(seclists):
    print ("SecListName(Destination), RuleType, Protocol, isStateless, Source, SourcePortRange, DPortMin, DPortMax, ICMPType, ICMPCode")
    oname.write("SecListName(Destination), RuleType, Protocol, isStateless, Source, SourcePortRange, DPortMin, DPortMax, ICMPType, ICMPCode\n")
    for seclist in seclists.data:
        isec_rules = seclist.ingress_security_rules
        esec_rules = seclist.egress_security_rules
        display_name = seclist.display_name
        dn = ""
        if "10" in display_name:
            dn = display_name.split("10")
            dn = dn[0][:-1]
        else:
            dn = seclist.display_name
        for rule in isec_rules:
          #  print (rule)
            if rule.protocol == "6":
                if rule.tcp_options is None:
                    print (dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",~,,,,")
                    oname.write(dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",~,,,,\n")
                else:
                    min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    print (dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max+",,")
                    oname.write(dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max+",,\n")

            if rule.protocol == "1":
                if rule.icmp_options is None:
                    print (dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",~,,,,")
                    oname.write(dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",~,,,,\n")
                else:
                    code = convertNullToNothing(rule.icmp_options.code)
                    type = convertNullToNothing(rule.icmp_options.type)
                    print (dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",~,,," + type + "," + code)
                    oname.write(dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",~,,," + type + "," + code+"\n")
            if rule.protocol == "17":
                if rule.udp_options is None:
                    print (dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",~,,,,")
                    oname.write(dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",~,,,,\n")
                else:
                    min = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    print (dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max+",,")
                    oname.write(dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max+",,\n")

            if rule.protocol == "all":
                print (dn + ",ingress,all," + str(rule.is_stateless) + "," + rule.source + ",~,,")
                oname.write(dn + ",ingress,all," + str(rule.is_stateless) + "," + rule.source + ",~,,\n")

parser = argparse.ArgumentParser(description="Export Security list on OCI to CSV")
parser.add_argument("networkCompartment", help="Compartment where VCN resides")
parser.add_argument("outdir", help="directory path for output csv file ")
parser.add_argument("--vcnName", help="VCN from which to export the sec list", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)



if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
outdir = args.outdir
vcn_name = args.vcnName
ntk_comp_name = args.networkCompartment
if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

ntk_compartment_id = get_network_compartment_id(config, ntk_comp_name)
vcn = VirtualNetworkClient(config)

outfile = outdir+"/"+ntk_comp_name+"_SecRules.csv"
print("Writing sec rules to "+outfile)
oname = open(outfile,"w")

if vcn_name is not None:
    vcn_ocid = get_vcn_id(config,ntk_compartment_id,vcn_name)
    seclists = vcn.list_security_lists(compartment_id=ntk_compartment_id, vcn_id=vcn_ocid, lifecycle_state='AVAILABLE')
    print_secrules(seclists)
else:
    vcns = get_vcns(config,ntk_compartment_id)
    for v in vcns.data:
        vcn_id = v.id
        seclists = vcn.list_security_lists(compartment_id=ntk_compartment_id, vcn_id=vcn_id, lifecycle_state='AVAILABLE')
        print_secrules(seclists)
oname.close()
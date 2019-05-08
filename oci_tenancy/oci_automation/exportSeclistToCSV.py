#!/bin/python

import ConfigParser
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
    # comp_list = identity.list_compartments(compartment_id=config["tenancy"])
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
    for vcn in vcnlist.data:
        print vcn.id
    return vcnlist


def print_secrules(seclists):

    #print "SubnetName,RuleType,Protocol,isStateless,Source,Destination,MaxOption,MinOption"
    print "SubnetName, RuleType, Protocol, isStateless, Source, SPortMin, SPortMax, Destination, DPortMin, DPortMax, ICMPType, ICMPCode"


    for seclist in seclists.data:
    #    print seclist
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
            print rule
            exit(0)
            if rule.protocol == "6":
                if rule.tcp_options is None:
                    ##				print "TCP," + rule.source + ",,"
                    print dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",,,"
                else:
                    min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
#"SubnetName, RuleType, Protocol, isStateless, Source, SPortMin, SPortMax, Destination, DPortMin, DPortMax, ICMPType, ICMPCode"
                    print dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + "," + min + "," + max

            if rule.protocol == "1":
                if rule.icmp_options is None:
                    # print "ICMP," + rule.source + ",,"
                    print dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",~,,"
                # print "ICMP " + rule.protocol + """      """  + rule.source + """        None    """ + """       None """
                else:
                    min = convertNullToNothing(rule.icmp_options.code)
                    max = convertNullToNothing(rule.icmp_options.type)
                    print dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max
                # print "ICMP," + rule.source + ","+ min + "," + max

            if rule.protocol == "17":
                if rule.udp_options is None:
                    #				print "UDP," + rule.source + ",,"
                    print dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",~,,"
                    # print "UDP " + rule.protocol + """      """  + rule.source + """        None    """ + """       None """
                else:
                    min = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    # print "UDP " + rule.protocol + """      """  + rule.source + """                """ + min + """ """ + max
                    print dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max

            if rule.protocol == "all":
                print dn + ",ingress,all," + str(rule.is_stateless) + "," + rule.source + ",~,,"



parser = argparse.ArgumentParser(description="Export Security list on OCI to CSV")
parser.add_argument("networkCompartment", help="Compartment where VCN resides")
parser.add_argument("outdir", help="directory path for output tf files ")
parser.add_argument("--vcnName", help="VCN from which to export the Subnet sec list", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)
#parser.add_argument("--subnetCompartment", help="Compartment where Subnet lives, if not in the network compartment")



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
#ntk_compartment = config['ntk_compartment_id']
#vcn_ocid = config['vcn_ocid']

vcn = VirtualNetworkClient(config)

if vcn_name is not None:
    vcn_ocid = get_vcn_id(config,ntk_compartment_id,vcn_name)
    seclists = vcn.list_security_lists(compartment_id=ntk_compartment_id, vcn_id=vcn_ocid, lifecycle_state='AVAILABLE')
    #print_secrules(seclists)
else:
    vcns = get_vcns(config,ntk_compartment_id)
    for v in vcns.data:
        vcn_id = v.id
        #print vcn_id
        seclists = vcn.list_security_lists(compartment_id=ntk_compartment_id, vcn_id=vcn_id, lifecycle_state='AVAILABLE')
    #    vcn.list_secu
        print_secrules(seclists)

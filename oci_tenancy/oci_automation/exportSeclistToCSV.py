#!/bin/python

import ConfigParser
import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient


def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)


config = oci.config.from_file()

parser = argparse.ArgumentParser(description="CSV filename")
parser.add_argument("--outdir", help="directory path for output tf files ", required=True)

if len(sys.argv) < 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
outdir = args.outdir

ntk_compartment = config['ntk_compartment_id']
vcn_ocid = config['vcn_ocid']

vcn = VirtualNetworkClient(config)

seclists = vcn.list_security_lists(compartment_id=ntk_compartment, vcn_id=vcn_ocid, lifecycle_state='AVAILABLE')

print "SubnetName,RuleType,Protocol,isStateless,Source,Destination,MaxOption,MinOption"
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
        if rule.protocol == "6":
            if rule.tcp_options is None:
                ##				print "TCP," + rule.source + ",,"
                print dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",~,,"
            else:
                min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                print dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",~," + min + "," + max

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

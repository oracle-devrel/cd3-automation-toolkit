#!/bin/python

import ConfigParser
import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient


def is_empty(myList):
    # print myList
    if not myList:
        return True
    else:
        return False


def checkStateless (stateless):
    #print (stateless)
    if stateless is None:
        #myString is not None AND myString is not empty or blank
        return False
    #myString is None OR myString is empty or blank
    return stateless


def create_ingress_rule_string(rule):
    options = ""
    temp_rule = """
          ingress_security_rules {
                protocol = \"""" + rule.protocol + """\"
                source = \"""" + rule.source + """\"
                stateless = """ + str(checkStateless(rule.is_stateless)).lower() + "\n"
    # print(rule.icmp_options)
    if not is_empty(rule.icmp_options):
        options = """
               icmp_options {
                        "code" = """ + str(rule.icmp_options.code) + """
                        "type" =  """ + str(rule.icmp_options.type) + """
                        }  """
    dest_range = ""
    source_range = ""
    tcp_option = ""
    if not is_empty(rule.tcp_options):
        tcp_option = "\t\t tcp_options {"

        if not is_empty(rule.tcp_options.destination_port_range):
            dest_range = """
                        "max" = """ + str(rule.tcp_options.destination_port_range.max) + """
                        "min" =  """ + str(rule.tcp_options.destination_port_range.min) + """
                          """
        elif not is_empty(rule.tcp_options.source_port_range):
            source_range = """
                        \tsource_port_range {
                        "max" = """ + str(rule.tcp_options.source_port_range.max) + """
                        "min" =  """ + str(rule.tcp_options.source_port_range.min) + """
                      \t\t  }  """
        # tcp_option = tcp_option
        options = tcp_option + dest_range + source_range + "\n  \t\t\t }"

    udp_option = ""
    if not is_empty(rule.udp_options):
        udp_option = " \t\t udp_options {"

        if not is_empty(rule.udp_options.destination_port_range):
            dest_range = """
                        "max" = """ + str(rule.udp_options.destination_port_range.max) + """
                        "min" =  """ + str(rule.udp_options.destination_port_range.min) + """
                          """
        elif not is_empty(rule.udp_options.source_port_range):
            source_range = """
                        source_port_range {
                        "max" = """ + str(rule.udp_options.source_port_range.max) + """
                        "min" =  """ + str(rule.udp_options.source_port_range.min) + """
                        \t\t }  """
        options = udp_option + dest_range + source_range + "\n  \t\t\t }"

    close_bracket = "\n \t\t}"

    temp_rule = temp_rule + options + close_bracket
    return temp_rule


def create_egress_rule_string(rule):
    options = ""
    egress_rule = """
          egress_security_rules {
                protocol = \"""" + rule.protocol + """\"
                destination = \"""" + rule.destination + """\"
                stateless = """ + str(checkStateless(rule.is_stateless)).lower() + "\n"
    # print(rule.icmp_options)
    if not is_empty(rule.icmp_options):
        options = """
               icmp_options {
                  "code" = """ + str(rule.icmp_options.code) + """
                  "type" =  """ + str(rule.icmp_options.type) + """
               }  """
    dest_range = ""
    source_range = ""
    tcp_option = ""
    if not is_empty(rule.tcp_options):
        tcp_option = "\t\t tcp_options {"

        if not is_empty(rule.tcp_options.destination_port_range):
            dest_range = """
                 "max" = """ + str(rule.tcp_options.destination_port_range.max) + """
                 "min" =  """ + str(rule.tcp_options.destination_port_range.min) + """
              """
        elif not is_empty(rule.tcp_options.source_port_range):
            source_range = """
                  source_port_range {
                    "max" = """ + str(rule.tcp_options.source_port_range.max) + """
                    "min" =  """ + str(rule.tcp_options.source_port_range.min) + """
                /t/t  }  """
        # tcp_option = tcp_option
        options = tcp_option + dest_range + source_range + "\n \t\t\t }"

    udp_option = ""
    if not is_empty(rule.udp_options):
        udp_option = "\t\t udp_options {"

        if not is_empty(rule.udp_options.destination_port_range):
            dest_range = """
                  "max" = """ + str(rule.udp_options.destination_port_range.max) + """
                  "min" =  """ + str(rule.udp_options.destination_port_range.min) + """
                """
        elif not is_empty(rule.udp_options.source_port_range):
            source_range = """
                  source_port_range {
                   "max" = """ + str(rule.udp_options.source_port_range.max) + """
                   "min" =  """ + str(rule.udp_options.source_port_range.min) + """
                  /t/t}  """
        options = udp_option + dest_range + source_range + "\n  \t\t\t}"

    close_bracket = "\n \t\t}"

    egress_rule = egress_rule + options + close_bracket
    return egress_rule


def create_seclist_tf_file(subnetid,create_def_file,importFlag,search_subnet_name):
    response = vnc.get_subnet(subnetid)
    if(importFlag is "False"):
        print ("Seclist file name : " + response.data.display_name.rsplit("-", 1)[0].strip() + "_seclist.tf")
        outFilename = open(outdir+"/"+ response.data.display_name.rsplit("-", 1)[0].strip() + "_seclist.tf", "a")
        for seclist_id in response.data.security_list_ids:
            seclistdata = vnc.get_security_list(seclist_id).data
            seclistname = vnc.get_security_list(seclist_id).data.display_name
            # print vnc.get_security_list(seclist_id).data.ingress_security_rules
            display_name = seclistname  # +  "-" + subnet
            if (seclistname != "Default Security List for VCN01"):
                tempStr = """
            resource "oci_core_security_list" \"""" + seclistname.rsplit("-", 1)[0] + """"{
                    compartment_id = "${var.ntk_compartment_ocid}"
                    vcn_id = "${oci_core_virtual_network.vcn01.id}"
                    display_name = \"""" + display_name.strip() + "\"\n"

                ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
                for rule in ingressRules:
                            tempStr = tempStr + create_ingress_rule_string(rule) + "\n"

                egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
                for rule in egressRules:
                            tempStr = tempStr + create_egress_rule_string(rule) + "\n"

                tempStr = tempStr + """
                    \n \t\t ####ADD_NEW_SEC_RULES####""" + seclistname.rsplit("-", 1)[0].rsplit("-",1)[1] + """
                  } \n       """
                outFilename.write(tempStr)
            elif create_def_file:
                # print("Default list Should be taken care " )
                defFilename = open(outdir + "/" + "def-vcn_seclist_generated.tf", "w")
                tempStr = """
                    resource "oci_core_security_list" \"""" + "vcn01" + """"{
                    compartment_id = "${var.ntk_compartment_ocid}"
                    vcn_id = "${oci_core_virtual_network.vcn01.id}"
                    display_name = \"""" + display_name.strip() + "\""

                ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
                for rule in ingressRules:
                            tempStr = tempStr + create_ingress_rule_string(rule) + "\n"

                egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
                for rule in egressRules:
                            tempStr = tempStr + create_egress_rule_string(rule) + "\n"

                tempStr = tempStr + """
                    \n \t\t ####ADD_NEW_SEC_RULES####""" + str(1) + """
                  } \n  """
                defFilename.write(tempStr)
                defFilename.close()
                create_def_file = False
            else:
                print("def file created ")

        outFilename.close()
    else:
        #terraform import oci_core_security_list.non-prod-app2-1 ocid1.securitylist.oc1.phx.aaaaaaaapec4t2jxrjapuudfjqvv2v4dadvusefpx37zlwcu44ovnr7evnlq
        #importCommands = open(outdir + "/" + "import_command.txt", "w")
        for seclist_id in response.data.security_list_ids:
            seclistdata = vnc.get_security_list(seclist_id).data
            seclistname = vnc.get_security_list(seclist_id).data.display_name
            print( search_subnet_name is  response.data.display_name    )
            if(search_subnet_name == response.data.display_name):
                #print("if")
                tempStr = "terraform import oci_core_security_list." + seclistname.rsplit("-", 1)[0] +" " + seclist_id + "\n"
                importCommands.write(tempStr)
                #importCommands.write("\n")
            elif (search_subnet_name is None):
                #print("else")
                tempStr = "terraform import oci_core_security_list." + seclistname.rsplit("-", 1)[0] +" " + seclist_id
                importCommands.write(tempStr)
                importCommands.write("\n")
        #importCommands.close()


parser = argparse.ArgumentParser(description="CSV filename")
parser.add_argument("--outdir",help="directory path for output tf files ",required=True)
parser.add_argument("--gen_tf_import", help="generate import TF command for given subnet", required=False)
parser.add_argument("--subnet_name", help="name of subnet ", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)

if len(sys.argv) < 1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

outdir = args.outdir
importFlag = "False"
if ( args.gen_tf_import != None):
    importFlag = args.gen_tf_import
    importCommands = open(outdir + "/" + "seclist_import_command.txt", "a")
#outdir = args.outdir

search_subnet_name = args.subnet_name
configFileName = args.configFileName

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

ociprops = ConfigParser.RawConfigParser()
ociprops.read('oci-tf.properties')


vnc = VirtualNetworkClient(config)
vcn_id = ociprops.get('Default', 'vcn_id')
ntk_comp_id = ociprops.get('Default', 'ntk_comp_id')

print(ntk_comp_id)
print(vcn_id)
subnet_list = response = vnc.list_subnets(ntk_comp_id, vcn_id)

create_def_file = True
#print("subnet_name ::: " + search_subnet_name)
for subnet in subnet_list.data:
     create_seclist_tf_file(subnet.id,True,importFlag,search_subnet_name)


#importCommands.close()

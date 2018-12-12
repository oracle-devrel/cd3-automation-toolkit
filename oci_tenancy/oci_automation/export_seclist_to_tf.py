#!/bin/python

import ConfigParser
import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient


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


def create_seclist_tf_file(vcn_dns_label,vcn_display_name,subnetid,create_def_file,importFlag,search_subnet_name,overwrite):
    response = vnc.get_subnet(subnetid)
    if(importFlag is "False"):
        print ("Seclist file name : " + response.data.display_name.rsplit("-", 1)[0].strip() + "_seclist.tf")
        outFilename = open(outdir+"/"+ response.data.display_name.rsplit("-", 1)[0].strip() + "_seclist.tf", "a")
        for seclist_id in response.data.security_list_ids:
            seclistdata = vnc.get_security_list(seclist_id).data
            seclistname = vnc.get_security_list(seclist_id).data.display_name
            # print vnc.get_security_list(seclist_id).data.ingress_security_rules
            display_name = seclistname  # +  "-" + subnet
            if (seclistname != "Default Security List for "+vcn_display_name):
                tempStr = """
            resource "oci_core_security_list" \"""" + seclistname.rsplit("-", 1)[0] + """"{
                    compartment_id = "${var.ntk_compartment_ocid}"
                    vcn_id = "${oci_core_virtual_network.""" + vcn_dns_label.strip() +""".id}"
                    display_name = \"""" + display_name.strip() + "\"\n"
                if(overwrite == "False"):
                    ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
                    for rule in ingressRules:
                                tempStr = tempStr + create_ingress_rule_string(rule) + "\n"

                    egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
                    for rule in egressRules:
                                tempStr = tempStr + create_egress_rule_string(rule) + "\n"
                #else:
                #    print("Will create dummy files for overwitting exiting secrules")

                tempStr = tempStr + """
                    \n \t\t ####ADD_NEW_SEC_RULES####""" + seclistname.rsplit("-", 1)[0].rsplit("-",1)[1] + """
                  } \n       """
                outFilename.write(tempStr)
            elif create_def_file:
                # print("Default list Should be taken care " )
                defFilename = open(outdir + "/" + "def-vcn_seclist_generated.tf", "w")
                tempStr = """
                    resource "oci_core_security_list" \"""" + vcn_dns_label.strip() + """"{
                    compartment_id = "${var.ntk_compartment_ocid}"
                    vcn_id = "${oci_core_virtual_network.""" + vcn_dns_label.strip() +""".id}"
                    display_name = \"""" + display_name.strip() + "\""
                if (overwrite == "False"):
                    ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
                    for rule in ingressRules:
                                tempStr = tempStr + create_ingress_rule_string(rule) + "\n"

                    egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
                    for rule in egressRules:
                                tempStr = tempStr + create_egress_rule_string(rule) + "\n"
                #else:
                #    print("Will create dummy files for overwitting exiting secrules")

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

parser = argparse.ArgumentParser(description="Exports existing seclists to tf files; Required Arguements: propsfile and outdir")
parser.add_argument("--propsfile",help="Full Path of properties file. eg oci-tf.properties in example folder",required=True)
parser.add_argument("--outdir",help="directory path for output tf files",required=True)
parser.add_argument("--gen_tf_import", help="generate import TF command for given subnet", required=False)
parser.add_argument("--subnet_name", help="name of subnet ", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)
parser.add_argument("--overwrite",help="Export files to overwrite existing subnet rules. ")

if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

question = 'Input Name of Network compartment where VCN exist : '
print (question)
ntk_comp_name = raw_input()

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

if args.overwrite is not None:
    overwrite = args.overwrite
else:
    overwrite = "False"


ntk_comp_id = get_network_compartment_id(config, ntk_comp_name)

ociprops = ConfigParser.RawConfigParser()
ociprops.read(args.propsfile)


vnc = VirtualNetworkClient(config)
vcn_display_name = ociprops.get('Default', 'vcn_display_name')
vcn_id = get_vcn_id(config, ntk_comp_id , vcn_display_name)
vcn_dns_label = ociprops.get('Default', 'vcn_dns_label')
#vcn_id = ociprops.get('Default', 'vcn_id')
#ntk_comp_id = ociprops.get('Default', 'ntk_comp_id')

print(ntk_comp_id)
print(vcn_id)
subnet_list = response = vnc.list_subnets(ntk_comp_id, vcn_id)

create_def_file = True
#print("subnet_name ::: " + search_subnet_name)
for subnet in subnet_list.data:
     create_seclist_tf_file(vcn_dns_label,vcn_display_name,subnet.id,True,importFlag,search_subnet_name,overwrite)


#importCommands.close()

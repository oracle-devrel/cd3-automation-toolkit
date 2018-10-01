#!/bin/python

import oci
from oci.core.virtual_network_client import VirtualNetworkClient

def is_empty(myList):
    #print myList
    if not myList:
        return True
    else:
        return False


def create_ingress_rule_string(rule):
        options = ""
        temp_rule = """
             ingress_security_rules {
                protocol = \"""" + rule.protocol + """\"
                source = \"""" + rule.source + """\"
                stateless = """ + str(rule.is_stateless).lower() +"\n"
        #print(rule.icmp_options)
        if not is_empty(rule.icmp_options):
               options = """
               icmp_options {
                        "code" = """ + str(rule.icmp_options.code) + """
                        "type" =  """ + str(rule.icmp_options.type) + """
                        }  """
        dest_range =""
        source_range=""
        tcp_option =""
        if not is_empty(rule.tcp_options):
                tcp_option = "\t tcp_options {"

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
                        }  """
                #tcp_option = tcp_option
                options = tcp_option + dest_range + source_range + "\n \t  }"

        udp_option =""
        if not is_empty(rule.udp_options):
                udp_option = "\t udp_options {"

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
                        }  """
                options = udp_option + dest_range + source_range + "\n \t  }"

        close_bracket = "\n\t }"

        temp_rule = temp_rule + options + close_bracket
        return temp_rule


def create_egress_rule_string(rule):
        options = ""
        egress_rule = """
            \t egress_security_rules {
                protocol = \"""" + rule.protocol + """\"
                destination = \"""" + rule.destination + """\"
                stateless = """ + str(rule.is_stateless).lower() +"\n"
        #print(rule.icmp_options)
        if not is_empty(rule.icmp_options):
               options = """
               icmp_options {
                        "code" = """ + str(rule.icmp_options.code) + """
                        "type" =  """ + str(rule.icmp_options.type) + """
                        }  """
        dest_range =""
        source_range=""
        tcp_option =""
        if not is_empty(rule.tcp_options):
                tcp_option = "\t tcp_options {"

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
                        }  """
                #tcp_option = tcp_option
                options = tcp_option + dest_range + source_range + "\n \t }"

        udp_option =""
        if not is_empty(rule.udp_options):
                udp_option = "\t udp_options {"

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
                        }  """
                options = udp_option + dest_range + source_range + "\n \t }"

        close_bracket = "\n\t }"

        egress_rule = egress_rule + options + close_bracket
        return egress_rule


def create_seclist_tf_file(subnetid):
        config = oci.config.from_file()
        vnc = VirtualNetworkClient(config)
        response = vnc.get_subnet(subnetid)
        vcn_var = config.get('Default','vcn_var')
        ntk_comp_var = config.get('Default','ntk_comp_var')

        print ("file name : "+ response.data.display_name.rsplit("-",1)[0].strip()+"_seclist.tf")
        outFilename = open(response.data.display_name.rsplit("-",1)[0].strip()+"_seclist.tf","a")
        create_def_file = True
        for seclist_id in response.data.security_list_ids:
                seclistdata = vnc.get_security_list(seclist_id).data
                seclistname = vnc.get_security_list(seclist_id).data.display_name
                #print vnc.get_security_list(seclist_id).data.ingress_security_rules
                display_name = seclistname  # +  "-" + subnet
                #print ("Name: " + seclistname.rsplit("-",1)[0] )
                #print ( "Seclist Displayname :::: "+display_name)
                if (seclistname != "Default Security List for VCN01"):
                        tempStr = """
                        resource "oci_core_security_list" \"""" + seclistname.rsplit("-",1)[0] +  """"{
                        compartment_id = "${var.ntk_compartment_ocid}"
                        vcn_id = "${oci_core_virtual_network.vcn01.id}"
                        display_name = \""""  + display_name.strip() + "\""

                        ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
                        for rule in ingressRules:
                                tempStr = tempStr + create_ingress_rule_string(rule) + "\n"

                        egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
                        for rule in egressRules:
                                tempStr = tempStr + create_egress_rule_string(rule) + "\n"

                        tempStr  = tempStr + """
                        }       """
                        outFilename.write(tempStr)
                elif create_def_file:
                        #print("Default list Should be taken care " )
                        defFilename = open("def-vcn-seclist_generated.tf","w")
                        tempStr = """
                        resource "oci_core_security_list" \"""" + "vcn01" +  """"{
                        compartment_id = "${var.ntk_compartment_ocid}"
                        vcn_id = "${oci_core_virtual_network.vcn01.id}"
                        display_name = \""""  + display_name.strip() + "\""

                        ingressRules = vnc.get_security_list(seclist_id).data.ingress_security_rules
                        for rule in ingressRules:
                                tempStr = tempStr + create_ingress_rule_string(rule) + "\n"

                        egressRules = vnc.get_security_list(seclist_id).data.egress_security_rules
                        for rule in egressRules:
                                tempStr = tempStr + create_egress_rule_string(rule) + "\n"

                        tempStr  = tempStr + """
                        }       """
                        defFilename.write(tempStr)
                        defFilename.close()
                        create_def_file = False
                else:
                        print("def file created ")

        outFilename.close()



config = oci.config.from_file()

vnc = VirtualNetworkClient(config)
#subnetid="ocid1.subnet.oc1.phx.aaaaaaaaqdam7g3qqdg6io3dys7xfea25ujds5bm7keaur5nn2twkrwpmnbq"
vcn_id = "ocid1.vcn.oc1.phx.aaaaaaaalkfjzndnaun7n5odcmjmz2kisf6pp5hq3qjm2rq3g37bm3y424wq"
comp_id = "ocid1.compartment.oc1..aaaaaaaaciaqqd6ncyyfaebvkevqwdvbrkfwn2mxraljbmeivposkzxyisga"
#print(comp_id)
#print(vcn_id)
subnet_list = response = vnc.list_subnets(comp_id,vcn_id)
#print(response)
#print(response.data)

create_def_file = True
for subnet in subnet_list.data:
        #print subnet.display_name + "\n" + subnet.id + "\n\n"
        #create_def_file = True
        create_seclist_tf_file(subnet.id)

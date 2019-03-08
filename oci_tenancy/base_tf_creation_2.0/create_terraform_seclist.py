#!/bin/python
##### Author : Murali Nagulakonda Venkata ###
##### Oracle Consulting ####
##### v0.1a #####


######
# Required Files
# Properties File: oci-tf.properties"
# Code will read input subnet file name from properties file
# Subnets file will contain info about each subnet. Seclists will be created based on the inputs in properties file
# Outfile
######

import sys
import os
import argparse
import configparser
import re

def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." +  os.path.join(dir, f))
            os.remove(os.path.join(dir, f))

parser = argparse.ArgumentParser(description="Creates a terraform sec list resource with name \"name-cidr\" for each subnet identified in the subnet input file.  This creates open egress (0.0.0.0/0) and All protocols within subnet ingress rules.  Any other rules should be put in manually.")
parser.add_argument("--propsfile", help="Full Path of properties file. eg oci-tf.properties in example folder")
parser.add_argument("--outdir",help="Output directory")
parser.add_argument("--omcs",help="Input Fileis of pattern \"name-cidr\" ",action="store_true")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

config = configparser.RawConfigParser()
config.optionxform = str
config.read(args.propsfile)
sections=config.sections()

outdir = args.outdir

# Purge existing sec list files
purge(outdir, "_seclist.tf")

#Get Global Properties from Default Section
ntk_comp_var = config.get(sections[0],'ntk_comp_var')
comp_var = config.get(sections[0],'comp_var')
drg_destinations = config.get(sections[0], 'drg_subnet')
drg_destinations=drg_destinations.split(",")

#Get VCN  info from VCN_INFO section
vcns=config.options(sections[1])

#Create sec rules as per Section VCN_PEERING
vcn_lpg_rules = {}
for vcn_name in vcns:
    vcn_lpg_rules.setdefault(vcn_name, '')

peering_dict = dict(config.items(sections[2]))
ocs_vcn_cidr=peering_dict['ocs_vcn_cidr']
peering_dict.pop('ocs_vcn_lpg_ocid')
add_sec_rules_ping=peering_dict['add_sec_rules_ping']
peering_dict.pop('add_sec_rules_ping')
peering_dict.pop('ocs_vcn_cidr')

if(add_sec_rules_ping.strip().lower()=='y'):
    ruleStr=""
    for left_vcn,value in peering_dict.items():
        right_vcns=value.split(",")
        for right_vcn in right_vcns:
                if(right_vcn=='ocs_vcn'):
                    # Build rule for VCN on left for OCS VCN on right
                    ruleStr = """
        ingress_security_rules {
                protocol = "1"
                source = \"""" + ocs_vcn_cidr + """"
        }
        """
                    vcn_lpg_rules[left_vcn] = vcn_lpg_rules[left_vcn] + ruleStr

                else:
                    #Build rule for VCN on left
                    ruleStr = """
        ingress_security_rules {
                protocol = "1"
                source = "${oci_core_vcn.""" + right_vcn + """.cidr_block}"
                }
        """
                    vcn_lpg_rules[left_vcn]=vcn_lpg_rules[left_vcn]+ruleStr

                    #Build rule for VCNs on right
                    ruleStr = """
        ingress_security_rules {
                protocol = "1"
                source = "${oci_core_vcn.""" + left_vcn + """.cidr_block}"
        }
        """
                    vcn_lpg_rules[right_vcn] = vcn_lpg_rules[right_vcn] + ruleStr


tempStr = ""
ADS = ["AD1", "AD2", "AD3"]

#Start processing as per vcn and subnet file info from VCN_INFO section
for vcn_name in vcns:
        vcn_data = config.get(sections[1], vcn_name)
        vcn_data = vcn_data.split(',')
        vcn_drg=vcn_data[1].strip().lower()
        hub_spoke_none = vcn_data[5].strip().lower()
        vcn_subnet_file = vcn_data[6].strip().lower()
        sps = vcn_data[8].strip().lower()
        seclists_per_subnet = int(sps)

        fname = open(vcn_subnet_file,"r")

        #Read subnet file
        for line in fname:
                i = 0
                if not line.startswith('#') :
                        if args.omcs :
                                name_sub,AD,pubpvt,dhcp,SGW,NGW,IGW = line.split(',')
                                subnet = name_sub.rsplit("-",1)[1].strip()
                                name = name_sub.rsplit("-",1)[0].strip()

                        else :
                                [name,sub,AD,pubpvt,dhcp,SGW,NGW,IGW] = line.split(',')
                                linearr = line.split(",")
                                name = linearr[0].strip()
                                subnet = linearr[1].strip()
                        if (AD.strip() != 'Regional'):
                                ad = ADS.index(AD)
                                ad_name_int = ad + 1
                                ad_name = str(ad_name_int)
                        else:
                                ad_name = "R"
                        print(' seclist file name  ************************** '+name+str(ad_name)+'_seclist.tf')
                        while i < seclists_per_subnet :
                                oname = open(outdir +"/" +name+str(ad_name)+"_seclist.tf","a")
                                seclistname = name + str(ad_name) + "-" +  str(i+1)

                                display_name = seclistname +  "-" + subnet

                                tempStr = """
resource "oci_core_security_list" \"""" + seclistname +  """"{
        compartment_id = "${var.""" + ntk_comp_var + """}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        display_name = \""""  + display_name.strip() + "\""


                                if i+1 > 1 :
                                        tempStr  = tempStr + """
       
        ####ADD_NEW_SEC_RULES####""" + str(i+1) + """
        }
        """
                                else :
                                        if(vcn_lpg_rules[vcn_name]!=""):
                                            tempStr=tempStr+vcn_lpg_rules[vcn_name]
                                        if(add_sec_rules_ping=='y' and hub_spoke_none=='hub' or vcn_drg=='y' or hub_spoke_none=='spoke'):
                                            for drg_destination in drg_destinations:
                                                if(drg_destination!=''):
                                                    tempStr=tempStr+"""
                ingress_security_rules {
                protocol = "1"
                source = \"""" + drg_destination + """"
        }
        """

                                        tempStr = tempStr + """
        ingress_security_rules {
                protocol = "all"
                source = \"""" + subnet + """"
        }
        egress_security_rules {
                destination = "0.0.0.0/0"
                protocol = "all"
        }
        #------------------------------------------------------------
        ####ADD_NEW_SEC_RULES####""" + str(i+1) + """
}
"""
                                oname.write(tempStr)
                                i = i + 1

fname.close()
oname.close()
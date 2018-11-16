#!/bin/python
##### Author : Murali Nagulakonda Venkata ###
##### Oracle Consulting ####
##### v0.1a #####

import sys
import os
import argparse
import ConfigParser
import re

def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." +  os.path.join(dir, f))
            os.remove(os.path.join(dir, f))

parser = argparse.ArgumentParser(description="Create a terraform sec list resource with name \"name-cidr\" for each subnet identified in the subnet input file.  This creates open egress (0.0.0.0/0) and All protocols within subnet ingress rules.  Any other rules should be put in manually.")
parser.add_argument("--file",help="Full Path to the Subnet file. See readme for format example ")
parser.add_argument("--outdir",help="Output directory")
parser.add_argument("--omcs",help="Input Fileis of pattern \"name-cidr\" ",action="store_true")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

config = ConfigParser.RawConfigParser()
config.read('oci-tf.properties')

filename = args.file

outdir = args.outdir

fname = open(filename,"r")

ADS = ["AD1","AD2","AD3"]

####
#ntk_comp_var=ntk_compartment_ocid
#comp_var=compartment_ocid
#vcn_var=vcn01
#####

vcn_var = config.get('Default','vcn_var')
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')
sps = config.get('Default','sec_list_per_subnet')
seclists_per_subnet = int(sps)

purge(outdir, "_seclist.tf")

for line in fname:
        i = 0
        # print "before while "
        if not line.startswith('#') :

                # print "While " + str(i)
                # print "line = " + line
                if args.omcs :
                        name_sub,AD,pubpvt,dhcp,SGW,NGW,IGW = line.split(',')
                        # line = line.split(",",1)[0]
                        subnet = name_sub.rsplit("-",1)[1].strip()
                        name = name_sub.rsplit("-",1)[0].strip()

                else :
                        [name,sub,AD,pubpvt,dhcp,SGW,NGW,IGW] = line.split(',')
                        linearr = line.split(",")
                        name = linearr[0].strip()
                        subnet = linearr[1].strip()

                print(' seclist file name  ************************** '+name+'_seclist.tf')
                while i < seclists_per_subnet :


                        oname = open(outdir +"/" +name+"_seclist.tf","a")

                        ad = ADS.index(AD)
                        ad_name = ad + 1
                        seclistname = name + str(ad_name) + "-" +  str(i+1)

                        display_name = seclistname +  "-" + subnet
                        #print "Name: " + name + " Subnet: " + subnet + "\n"
                        #print ( "Seclist Displayname :::: "+display_name)

                        tempStr = """
                resource "oci_core_security_list" \"""" + seclistname +  """"{
                    compartment_id = "${var.""" + ntk_comp_var + """}"
                    vcn_id = "${oci_core_vcn.""" + vcn_var + """.id}"
                    display_name = \""""  + display_name.strip() + "\""


                        if i+1 > 1 :
                                tempStr  = tempStr + """
                        
                        ####ADD_NEW_SEC_RULES####""" + str(i+1) + """
                }
        """
                        else :
                                tempStr = tempStr + """
                        egress_security_rules {
                                destination = "0.0.0.0/0"
                                protocol = "all"
                        }
                        ingress_security_rules {
                                protocol = "all"
                                source = \"""" + subnet + """"
                        }
                        #------------------------------------------------------------
                        ####ADD_NEW_SEC_RULES####""" + str(i+1) + """
                }

"""
                        # print "Tempstr = " + tempStr
                        oname.write(tempStr)
                        i = i + 1
        else:
                i = i + 1

fname.close()
oname.close()
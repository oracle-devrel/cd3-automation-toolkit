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
import ConfigParser
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

config = ConfigParser.RawConfigParser()
config.read(args.propsfile)

subnet_file = config.get('Default','subnet_file')
outdir = args.outdir

fname = open(subnet_file,"r")

ADS = ["AD1","AD2","AD3"]

vcn_var = config.get('Default','vcn_var')
ntk_comp_var = config.get('Default','ntk_comp_var')
comp_var = config.get('Default','comp_var')
sps = config.get('Default','sec_list_per_subnet')
seclists_per_subnet = int(sps)

# Purge existing sec list files
purge(outdir, "_seclist.tf")

#Read subnet file
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

                ad = ADS.index(AD)
                ad_name = ad + 1
                print(' seclist file name  ************************** '+name+str(ad_name)+'_seclist.tf')
                while i < seclists_per_subnet :


                        oname = open(outdir +"/" +name+str(ad_name)+"_seclist.tf","a")
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
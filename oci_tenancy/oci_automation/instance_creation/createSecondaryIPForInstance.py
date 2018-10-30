#!/bin/python
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import os
import re

import argparse
import ConfigParser


parser = argparse.ArgumentParser(description="Adds the resource block for Secondary IPs to an existing TF file")
parser.add_argument("file",help="CSV file with input of hostname,ip-name,ip")
parser.add_argument("outdir",help="directory path for output tf files. The Instance TF File must already exist.")

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir

fname = open(filename,"r")

for line in fname :
    print line
    server, subnet, ip_name, ip_addr = line.split(',')
#    server = row[0]
#   subnet = row[1]
#    ip-name = row[2]
#    ip = row[3]
    if not line.startswith("#"):
        try:
            tf_file = outdir + "/" + server + ".tf"
            sname = open(tf_file,"a")
            tempStr = """"resource "oci_core_vnic_attachment" """ +  ip_name + """_attachment  {
        #Required
        create_vnic_details {
            #Required
            subnet_id = "${oci_core_subnet.""" + subnet + """.id}"
    
            #Optional
            assign_public_ip = "false"
            private_ip = """ + ip_addr + """
            display_name = """ + ip_name + """"
        }
        instance_id = "${oci_core_instance.""" + server + """.id}"
    
        #Optional
        display_name = """ + ip_name + """"
} 
"""
            sname.write(tempStr)
            sname.close()
        except Exception as detail:
            print detail

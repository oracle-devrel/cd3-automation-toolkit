#!/bin/python
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import os
import re

import argparse
import ConfigParser


parser = argparse.ArgumentParser(description="CSV filename")
parser.add_argument("file",help="Full Path to the CSV file for creating block volume ")
parser.add_argument("outdir",help="directory path for output tf files ")


if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir

fname = open(filename,"r")

config = ConfigParser.RawConfigParser()
config.read('oci-tf.properties')

ADS = ["AD1", "AD2", "AD3"]
for line in fname:

    if not line.startswith('#'):
        #[blockname, size in gb, AD, attachedToInstance, attachType] = line.split(',')
        linearr = line.split(",")
        blockname = linearr[0].strip()
        size = linearr[1].strip()
        AD = linearr[2].strip()
        attachedToInstance = linearr[3].strip()
        attachType = linearr[4].strip()
        compartmentVarName = linearr[5].strip()
        # print "Name: " + name + " Subnet: " + subnet + "\n"
        ad = ADS.index(AD)
        display_name = blockname

        tempStr = """resource "oci_core_volume"  \"""" + blockname + """"  {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var.""" + compartmentVarName + """}"

        #Optional
        display_name = \"""" + blockname + """"
        size_in_gbs = \"""" + size + """"
        }

        resource "oci_core_volume_attachment" \"""" + blockname + """_volume_attachment" {
        #Required
        instance_id = "${oci_core_instance.""" + attachedToInstance + """.id}"
        attachment_type = \"""" + attachType + """"
        volume_id = "${oci_core_volume.""" + blockname + """.id}"

        }
        """
        outfile = outdir+"/"+blockname+".tf"
        oname = open(outfile,"w")
        oname.write(tempStr)
        oname.close()
fname.close()

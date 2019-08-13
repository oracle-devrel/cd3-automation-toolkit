#!/bin/python
# Tested only with Python 3.x - will not work with 2.x due to changes between
# the different versions of Python. See the lines with 2.x

import os
import sys
import argparse
#from backports import configparser
# Entry for 2.x
import ConfigParser

parser = argparse.ArgumentParser(description="Creates the FSS Mount Target File in defined output directory defined in propoerties file.")
parser.add_argument("--properties",help="Properties File to use. Must have a [FSS] section")
parser.add_argument("--fss",help="From Properties File, which Mount Target to create [FSS#]. Must have a [FSS#] section where # is the number of FSS to create")

if len(sys.argv) != 5:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
# Reads and Set CLI variable
properties = args.properties
fss = args.fss

if not os.path.exists(properties):
    print("Cant find the file 'oci-tf.properties in working directory.\nMake sure to create the file and try again.")
    exit(-1)

#Entry for 2.x
config = ConfigParser.RawConfigParser()
#config = configparser.ConfigParser()
config.read(properties)

compartment_ocid = config.get(fss,'mt_comp_var')
mt = config.get(fss,'mt_name')
ip = config.get(fss,'mt_ip')
network = config.get(fss,'mt_network')
ad = config.get(fss,'mt_ad')
AD = int(ad) - 1
outdir = config.get(fss,'mt_outdir')
fssize = config.get(fss,'es_max_fs_stat_bytes')
fscount = config.get(fss,'es_max_fs_stat_files')

#Checks defined path from properties file in the mt_outdir variable
if not os.path.exists(outdir):
    print("Directory does not exist\n")
    exit(-1)

# Created FSS MT File based on mt_name variable in the defined output dir defined by mt_outdir
oname = open(outdir +"/" +mt+"_FSS_MT.tf","a")

mt_body = """
resource "oci_file_storage_mount_target" \"""" + mt + """" {
    availability_domain = "${lookup(data.oci_identity_availability_domains.ADs.availability_domains[""" + str(AD) + """],"name")}"
    compartment_id = \"""" + compartment_ocid + """"
    subnet_id = \""""  + network + """"
    display_name = \""""  + mt + """"
    ip_address = \"""" + ip + """"
}

resource "oci_file_storage_export_set" \"""" + mt + "-ES1" """" {
       mount_target_id = "${oci_file_storage_mount_target.""" + mt + """.id}"
       display_name = \"""" + mt + "-ES1" """"
       max_fs_stat_bytes = \"""" + fssize + """"
       max_fs_stat_files = \"""" + fscount + """"
}
"""
oname.write(mt_body)
oname.close()
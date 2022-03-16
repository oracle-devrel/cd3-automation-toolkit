#!/bin/python

#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import os,errno
import argparse
import tarfile
import oci
import subprocess
from oci.config import validate_config


parser = argparse.ArgumentParser(description="Extract the OVA into vmdk and convert disk 2 - n to raw format.  The oci config file and staging directory must already be setup.")
parser.add_argument("ova",help="Full path to OVA.")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()


config = oci.config.from_file()
validate_config(config)

staging_dir = config["local_staging_dir"]

ova = args.ova

if not ova.endswith('.ova'):
	print ("""File must be of type and have the  ".ova" extension """)
	sys.exit(-1)

ova_extract_dir = staging_dir + "/" + ova.split("/")[-1].split(".")[-2]

print (ova_extract_dir)

print ("Extracting tar file to " + ova_extract_dir)

try:
    os.makedirs(ova_extract_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

try:
	tar = tarfile.open(ova)
	tar_member_names = tar.getnames()
	for t in tar_member_names:
		full_name = ova_extract_dir + "/" + t
		if not os.path.isfile(full_name):
			print ("Extracting " + t)
			tar.extract(t,ova_extract_dir)
		else:
			print ("File: " + full_name + " exists, skipping extraction of this file")
	tar.close()
except Exception as e:
	print ("Error extracting ova file")
	print (e.args[0])



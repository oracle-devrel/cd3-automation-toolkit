#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com

######
# Required Files
# Properties File: vcn-info.properties"
# Code will read input subnet file name for each vcn from properties file
# Subnets file will contain info about each subnet
# Outfile
######

import sys
import re
import os
import argparse
import configparser
import pandas as pd
import glob
import shutil
import datetime


parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\". "
											 "Create terraform files for subnets.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("option", help="update choice")


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
outdir = args.outdir
prefix=args.prefix
inputfile=args.inputfile
update_choice=args.option
#If input is CD3 excel file

if(update_choice=='1'):
		cmd='python create_terraform_dhcp_options.py ' + inputfile + ' ' + outdir + ' '+prefix + ' --dhcp_add true'
		os.system(cmd)
if(update_choice=='2'):
		cmd='python create_terraform_route.py ' + inputfile + ' ' + outdir + ' '+prefix + ' --subnet_add true'
		os.system(cmd)
		cmd = 'python create_terraform_seclist.py ' + inputfile + ' ' + outdir + ' ' +  ' --subnet_add true'
		os.system(cmd)
		cmd = 'python create_terraform_subnet.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --subnet_add true'
		os.system(cmd)

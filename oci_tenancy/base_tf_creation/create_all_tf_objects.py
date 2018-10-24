#!/usr/bin/python
import os
import argparse
import sys


parser = argparse.ArgumentParser(description="create terraform files based given inputs")
parser.add_argument("subnetfile", help="Full Path of sec list file. See readme for format example ")
parser.add_argument("dhcpfile", help="Full Path of DHCP file ( .ini format). See readme for format example ")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")

if len(sys.argv) < 4:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
print (args)
subnetfile = args.subnetfile
dhcpfile = args.dhcpfile
outdir = args.outdir
prefix = args.prefix


print (" Creating Major TF Objects ")
command = 'python create_major_objects.py ' + outdir+"/"+prefix+'-major-objs.tf'
os.system(command)

print (" Creating DHCP options ")
command = 'python create_terraform_dhcp_options.py ' + dhcpfile + ' ' + outdir+"/"+prefix+'-dhcp.tf'
os.system(command)

print (" Creating Route")
command = 'python create_terraform_route.py ' + subnetfile + ' ' + outdir+"/"+prefix+'-route.tf'
os.system(command)

print (" Creating Seclist  ")
command = 'python create_terraform_seclist.py  --file=' + subnetfile + ' --outdir=' + outdir
os.system(command)

print (" Creating Subnet ")
command = 'python create_terraform_subnet.py ' + subnetfile + ' ' + outdir+"/"+prefix+'-subnets.tf'
os.system(command)

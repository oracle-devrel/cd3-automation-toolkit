#!/usr/bin/python
import os
import argparse
import sys


parser = argparse.ArgumentParser(description="Creates terraform files for network resources based on given inputs; See example folder for sample input files")
parser.add_argument("propsfile", help="Full Path of properties file. eg oci-tf.properties in example folder")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")

if len(sys.argv) < 4:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
print (args)
propsfile = args.propsfile
outdir = args.outdir
prefix = args.prefix

if not os.path.exists(outdir):
    os.makedirs(outdir)


print (" Creating Major TF Objects ")
command = 'python create_major_objects.py ' + propsfile + ' ' + outdir+"/"+prefix+'-major-objs.tf'
os.system(command)

print (" Creating DHCP options ")
command = 'python create_terraform_dhcp_options.py ' + propsfile + ' ' + outdir+"/"+prefix+'-dhcp.tf'
os.system(command)

print (" Creating Route")
command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir+"/"+prefix+'-routes.tf'
os.system(command)

print (" Creating Seclist  ")
command = 'python create_terraform_seclist.py  --propsfile=' + propsfile + ' --outdir=' + outdir
os.system(command)

print (" Creating Subnet ")
command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir+"/"+prefix+'-subnets.tf'
os.system(command)

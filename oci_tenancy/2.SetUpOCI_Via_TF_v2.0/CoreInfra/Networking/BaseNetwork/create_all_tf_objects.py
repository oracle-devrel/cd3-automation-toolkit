#!/usr/bin/python
import os
import argparse
import sys


parser = argparse.ArgumentParser(description="Creates terraform files for network resources based on given inputs; See example folder for sample input files")
parser.add_argument("inputfile", help="Full Path of input file either props file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")


if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
propsfile = args.inputfile
outdir = args.outdir
prefix = args.prefix

if not os.path.exists(outdir):
    os.makedirs(outdir)


print("-----------Creating Major TF Objects-----------")
command = 'python create_major_objects.py ' + propsfile + ' ' + outdir + "/" + prefix + '-major-objs.tf'
exitVal = os.system(command)
if (exitVal == 1):
    exit()
print("--------------Creating DHCP options------------")
command = 'python create_terraform_dhcp_options.py ' + propsfile + ' ' + outdir + "/" + prefix + '-dhcp.tf'
os.system(command)

print("-----------------Creating Route----------------")
command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir + "/" + prefix + '-routes.tf'
exitVal=os.system(command)
if (exitVal == 1):
    exit()

print("---------------Creating Seclist ---------------")
command = 'python create_terraform_seclist.py  '+ propsfile + ' ' + outdir
os.system(command)

print("----------------Creating Subnet----------------")
command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir + "/" + prefix + '-subnets.tf'
os.system(command)

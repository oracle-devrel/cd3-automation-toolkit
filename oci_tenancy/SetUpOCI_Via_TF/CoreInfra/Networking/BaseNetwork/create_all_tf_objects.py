#!/usr/bin/python3
import os
import argparse
import sys


parser = argparse.ArgumentParser(description="Creates terraform files for network resources based on given inputs; See example folder for sample input files")
parser.add_argument("inputfile", help="Full Path of input file either props file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--modify_network", help="modify network: true or false", required=False)


if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
propsfile = args.inputfile
outdir = args.outdir
prefix = args.prefix

if not os.path.exists(outdir):
    os.makedirs(outdir)
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"


print("-----------Process VCNs tab-----------")
command = 'python create_major_objects.py ' + propsfile + ' ' + outdir + ' '+prefix +' --modify_network '+modify_network
exitVal = os.system(command)
if (exitVal == 1):
    exit()

print("--------------\nProcess DHCP tab------------")
command = 'python create_terraform_dhcp_options.py ' + propsfile + ' ' + outdir + ' '+prefix +' --modify_network '+modify_network
exitVal=os.system(command)
if (exitVal == 1):
    exit()

print("-----------------\nProcess Subnets tab for Routes creation----------------")
command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir + ' '+' --modify_network '+modify_network
exitVal=os.system(command)
if (exitVal == 1):
    exit()

print("---------------\nProcess Subnets tab for Seclists creation---------------")
command = 'python create_terraform_seclist.py  '+ propsfile + ' ' + outdir + ' '+' --modify_network '+modify_network
exitVal=os.system(command)
if (exitVal == 1):
    exit()

print("----------------\nProcess Subnets tab for Subnets creation----------------")
command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir + ' ' + prefix +' --modify_network '+modify_network
exitVal=os.system(command)
if (exitVal == 1):
    exit()

print("\n\n Make sure to export all SecRules and RouteRules to CD3. Use sub-option 3 under option 2(Networking) of Main Menu for the same.")
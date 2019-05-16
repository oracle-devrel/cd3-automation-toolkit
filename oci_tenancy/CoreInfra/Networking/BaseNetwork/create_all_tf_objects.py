#!/usr/bin/python
import os
import argparse
import sys


parser = argparse.ArgumentParser(description="Creates terraform files for network resources based on given inputs; See example folder for sample input files")
parser.add_argument("propsfile", help="Full Path of properties file. eg vcn-info.properties in example folder")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--inputCD3", help="input CD3 excel file", required=False)

if len(sys.argv) < 4:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
propsfile = args.propsfile
outdir = args.outdir
prefix = args.prefix

excel=''
if(args.inputCD3 is not None):
    excel=args.inputCD3


if not os.path.exists(outdir):
    os.makedirs(outdir)

if (excel == ''):
    print("CD3 Excel file not provided, using properties file and csv files to generate terraform files")
    print("-----------Creating Compartments-----------")
    command = 'python create_terraform_compartments.py ' + propsfile + ' ' + outdir + "/" + prefix + '-compartments.tf'

    print ("-----------Creating Major TF Objects-----------")
    command = 'python create_major_objects.py ' + propsfile + ' ' + outdir+"/"+prefix+'-major-objs.tf'
    exitVal=os.system(command)
    if(exitVal==1):
        exit()
    print ("--------------Creating DHCP options------------")
    command = 'python create_terraform_dhcp_options.py ' + propsfile + ' ' + outdir+"/"+prefix+'-dhcp.tf'
    os.system(command)


    print ("-----------------Creating Route----------------")
    command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir+"/"+prefix+'-routes.tf'
    os.system(command)

    print ("---------------Creating Seclist ---------------")
    command = 'python create_terraform_seclist.py  --propsfile=' + propsfile + ' --outdir=' + outdir
    os.system(command)

    print ("----------------Creating Subnet----------------")
    command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir+"/"+prefix+'-subnets.tf'
    os.system(command)

else:
    print("CD3 Excel file has been provided")
    print("-----------Creating Compartments-----------")
    command = 'python create_terraform_compartments.py ' + excel + ' ' + outdir + "/" + prefix + '-compartments.tf'

    print("-----------Creating Major TF Objects-----------")
    command = 'python create_major_objects.py ' + propsfile + ' ' + outdir + "/" + prefix + '-major-objs.tf  --inputCD3='+excel
    exitVal = os.system(command)
    if (exitVal == 1):
        exit()
    print("--------------Creating DHCP options------------")
    command = 'python create_terraform_dhcp_options.py ' + excel + ' ' + outdir + "/" + prefix + '-dhcp.tf'
    os.system(command)

    print("-----------------Creating Route----------------")
    command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir + "/" + prefix + '-routes.tf --inputCD3='+excel
    os.system(command)

    print("---------------Creating Seclist ---------------")
    command = 'python create_terraform_seclist.py  --propsfile=' + propsfile + ' --outdir=' + outdir +' --inputCD3='+excel
    os.system(command)

    print("----------------Creating Subnet----------------")
    command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir + "/" + prefix + '-subnets.tf --inputCD3='+excel
    os.system(command)

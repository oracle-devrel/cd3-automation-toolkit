#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# All TF Objects Function Calls
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import os
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Creates terraform files for network resources based on given inputs; See example folder for sample input files")
    parser.add_argument("inputfile", help="Full Path of input file either props file. eg vcn-info.properties or cd3 excel file")
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--modify_network", help="modify network: true or false", required=False)
    parser.add_argument("--nongf_tenancy", help="non greenfield tenancy: true or false", required=False)
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv) < 3:
            parser.print_help()
            sys.exit(1)

    args = parser.parse_args()
    propsfile = args.inputfile
    outdir = args.outdir
    prefix = args.prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    if args.configFileName is not None:
        input_config_file = args.configFileName
    else:
        input_config_file=""

    if args.modify_network is not None:
        modify_network = str(args.modify_network)
    else:
        modify_network = "false"

    if args.nongf_tenancy is not None:
        nongf_tenancy = "true"
    else:
        nongf_tenancy = "false"



    print("-----------Process VCNs tab-----------")
    if (input_config_file == ''):
        command = 'python create_major_objects.py ' + propsfile + ' ' + outdir + ' ' + prefix + ' --modify_network ' + modify_network
    else:
        command = 'python create_major_objects.py ' + propsfile + ' ' + outdir + ' '+prefix +' --modify_network '+modify_network + ' --configFileName ' + input_config_file
    exitVal = os.system(command)
    if (exitVal == 1):
        exit(1)

    print("\n--------------Process DHCP tab------------")
    if (input_config_file == ''):
        command = 'python create_terraform_dhcp_options.py ' + propsfile + ' ' + outdir + ' '+prefix +' --modify_network '+modify_network
    else:
        command = 'python create_terraform_dhcp_options.py ' + propsfile + ' ' + outdir + ' ' + prefix + ' --modify_network ' + modify_network + ' --configFileName ' + input_config_file
    exitVal=os.system(command)
    if (exitVal == 1):
        exit(1)

    print("\n------------------Process Subnets tab for Routes creation----------------")
    if (input_config_file == ''):
        command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir + ' '+' --modify_network '+modify_network
    else:
        command = 'python create_terraform_route.py ' + propsfile + ' ' + outdir + ' ' + ' --modify_network ' + modify_network + ' --configFileName ' + input_config_file
    exitVal=os.system(command)
    if (exitVal == 1):
        exit(1)

    print("\n---------------Process Subnets tab for Seclists creation---------------")
    if (input_config_file == ''):
        command = 'python create_terraform_seclist.py  '+ propsfile + ' ' + outdir + ' '+' --modify_network '+modify_network
    else:
        command = 'python create_terraform_seclist.py  ' + propsfile + ' ' + outdir + ' ' + ' --modify_network ' + modify_network + ' --configFileName ' + input_config_file
    exitVal=os.system(command)
    if (exitVal == 1):
        exit(1)

    print("\n----------------Process Subnets tab for Subnets creation----------------")
    if (input_config_file == ''):
        command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir + ' ' + prefix +' --modify_network '+modify_network
    else:
        command = 'python create_terraform_subnet.py ' + propsfile + ' ' + outdir + ' ' + prefix + ' --modify_network ' + modify_network + ' --configFileName ' + input_config_file
    exitVal=os.system(command)
    if (exitVal == 1):
        exit(1)

    if(nongf_tenancy=="false"):
        print("\n\n Make sure to export all SecRules and RouteRules to CD3. Use sub-option 3 under option 2(Networking) of Main Menu for the same.")
    else:
        print("\n\nRunning Modify Rules")

if __name__ == '__main__':

    # Execution of the code begins here
    main()
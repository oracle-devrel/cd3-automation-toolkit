#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# All TF Objects Function Calls
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
# Modified Rework: Stefen Ramirez (stefen.ramirez@oracle.com)

import os
import argparse
import sys
from oci.config import DEFAULT_LOCATION
from commonTools import section
from . import *


def parse_args():
    parser = argparse.ArgumentParser(description='Creates terraform files for network resources based on given inputs; See example folder for sample input files')
    parser.add_argument('inputfile', help='Full Path of input file either props file. eg vcn-info.properties or cd3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument('--modify-network', action='store_true', help='modify network')
    parser.add_argument('--nongf-tenancy', action='store_true', help='non greenfield tenancy')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


def create_all_tf_objects(inputfile, outdir, prefix, config, modify_network=False, nongf_tenancy=False):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with section('Process VCNs Tab'):
        create_major_objects(inputfile, outdir, prefix, config, modify_network)

    with section('Process DHCP Tab'):
        create_terraform_dhcp_options(inputfile, outdir, prefix, config, modify_network)

    if not nongf_tenancy:
        with section('Process Subnets tab for Routes creation'):
            create_terraform_route(inputfile, outdir, prefix, config, modify_network)

        with section('Process Subnets for Seclists creation'):
            create_terraform_seclist(inputfile, outdir, prefix, config, modify_network)

    with section('Process Subnets for Subnets creation'):
        create_terraform_subnet(inputfile, outdir, prefix, config, modify_network)

    if not nongf_tenancy:
        print('\n\n Make sure to export all SecRules and RouteRules to CD3. Use sub-option 3 under option 2(Networking) of Main Menu for the same.')
    else:
        print('\n\nRunning Modify Rules')


if __name__ == '__main__':
    args = parse_args()
    create_all_tf_objects(args.inputfile, args.outdir, args.prefix, config=args.config, modify_network=args.modify_network, nongf_tenancy=args.nongf_tenancy)

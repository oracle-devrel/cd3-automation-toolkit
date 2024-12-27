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
from commonTools import section
from .create_major_objects import create_major_objects
from .create_terraform_defaults import create_terraform_defaults
from .create_terraform_dhcp_options import create_terraform_dhcp_options
from .create_terraform_route import create_terraform_route
from .create_terraform_route import create_terraform_drg_route
from .create_terraform_seclist import create_terraform_seclist
from .create_terraform_subnet_vlan import create_terraform_subnet_vlan

# Execution starts here
def create_all_tf_objects(inputfile, outdir, service_dir,prefix, ct, non_gf_tenancy, modify_network=False,network_vlan_in_setupoci="network",network_connectivity_in_setupoci='network'):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    if len(service_dir) != 0:
        service_dir_network = service_dir['network']
    else:
        service_dir_network = ""
    with section('Process VCNs Tab and DRGs Tab'):
        create_major_objects(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy, modify_network)
        create_terraform_defaults(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy, modify_network)
    with section('Process DHCP Tab'):
        create_terraform_dhcp_options(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy, modify_network)

    with section('Process DRGs tab for DRG Route Tables and Route Distribution creation'):
        create_terraform_drg_route(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy, network_connectivity_in_setupoci, modify_network)

    #Create Workflow
    if non_gf_tenancy == False:
        with section('Process Subnets tab for Routes creation'):
            create_terraform_route(inputfile, outdir, service_dir_network, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci, modify_network)
    # Create Workflow
    if non_gf_tenancy == False:
        with section('Process Subnets for Seclists creation'):
            create_terraform_seclist(inputfile, outdir, service_dir_network, prefix, ct, modify_network)

    with section('Process Subnets for Subnets creation'):
        create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci,modify_network)

    if non_gf_tenancy == False:
        print('\n\nMake sure to export all SecRules, RouteRules and DRG RouteRules to CD3. Use sub-options 3,4,5 under option 4(Network) of Main Menu for the same.')


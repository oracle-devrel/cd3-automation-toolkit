#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
#put them into CD3 Excel and create TF files

#Author: Gaurav
#Oracle Consulting
#

import argparse
import sys
import oci
from oci.identity import IdentityClient
from oci.config import DEFAULT_LOCATION
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *


def parse_args():
    parser = argparse.ArgumentParser(description="Export NetworkSource  in OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export identity objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", required=False, nargs='*', help="comma seperated Compartments for which to export Identity Objects")
    return parser.parse_args()


def export_networkSources(inputfile, outdir, service_dir, _config, ct):
    global values_for_column_networkSources
    global config
    global cd3file

    cd3file = inputfile

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()


    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    importCommands={}

    sheetName = "NetworkSources"

    # Read CD3 Identity Sheets
    df, values_for_column_networkSources = commonTools.read_cd3(cd3file, sheetName)

    #ct = commonTools()
    #ct.get_subscribedregions(configFileName)
    #ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- Network Sources would be overwritten during export process!!!\n")

    # Create backup
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
    if (os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)
    importCommands[ct.home_region] = open(script_file, "w")
    importCommands[ct.home_region].write("#!/bin/bash")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].write("terraform init")

    config.__setitem__("region", ct.region_dict[ct.home_region])
    idc=IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    network = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

    # Fetch Network Sources
    print("\nFetching Network Sources...")
    importCommands[ct.home_region].write("\n######### Writing import for Network Sources #########\n")
    network_sources = oci.pagination.list_call_get_all_results(idc.list_network_sources ,compartment_id=config['tenancy'])

    compIDvsName = {}
    #prepare a map of compartment_id and compartment name
    for key in ct.ntk_compartment_ids:
        compIDvsName[ct.ntk_compartment_ids[key]] = key

    index = 0
    for network_source in network_sources.data:
        network_source_info = network_source
        name = network_source_info.name

        tf_name = commonTools.check_tf_variable(name)

        importCommands[ct.home_region].write("\nterraform import \"module.iam-network-sources[\\\"" + str(
            tf_name) + "\\\"].oci_identity_network_source.network_source \" " + network_source_info.id)

        index = index + 1
        for col_header in values_for_column_networkSources.keys():
            if (col_header == "Region"):
                values_for_column_networkSources[col_header].append(ct.home_region.capitalize())
            elif (col_header == "Name"):
                values_for_column_networkSources[col_header].append(name)
            elif (col_header == "Description"):
                values_for_column_networkSources[col_header].append(network_source_info.description)
            elif (col_header == "Public Networks"):
                publicSources = network_source_info.public_source_list
                strPubSources = ""
                if(publicSources):
                    strPubSources = ",".join(publicSources)
                values_for_column_networkSources[col_header].append(strPubSources)
            elif (col_header == "OCI Networks"):
                vcn_names = "";
                virtualSourceList = network_source_info.virtual_source_list
                if(virtualSourceList):
                    length = len(virtualSourceList)
                    for i in range(length):
                        virtualSource = virtualSourceList[i]
                        vcn_id = virtualSource.vcn_id;
                        ip_ranges = virtualSource.ip_ranges;
                        if (ip_ranges):
                            strIPRange = ",".join(ip_ranges)
                            #get VCN name from VCN ID
                            vcn_info = network.get_vcn(vcn_id=vcn_id)
                            vcn_name = vcn_info.data.display_name
                            compartment_id = vcn_info.data.compartment_id
                            compartmentName = compIDvsName[compartment_id]
                            if(vcn_names == ""):
                                vcn_names = compartmentName + "@" + vcn_name + "="+strIPRange
                            else:
                                vcn_names = vcn_names + ";" + compartmentName + "@" + vcn_name + "="+ strIPRange

                values_for_column_networkSources[col_header].append(vcn_names)

            elif (col_header == "Defined Tags"):
                values_for_column_networkSources = commonTools.export_tags(network_source_info, col_header, values_for_column_networkSources)

    commonTools.write_to_cd3(values_for_column_networkSources, cd3file, sheetName)
    print("Network Sources exported to CD3\n")

    with open(script_file, 'a') as importCommands[ct.home_region]:
        importCommands[ct.home_region].write('\n\nterraform plan\n')


if __name__=="__main__":
    args = parse_args()
    export_networkSources(args.inputfile, args.outdir, args.config, args.network_compartments)
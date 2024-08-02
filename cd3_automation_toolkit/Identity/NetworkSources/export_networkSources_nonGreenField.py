#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
# Network Sources

#Author: Gaurav
#Oracle Consulting
#

import sys
import oci
from oci.identity import IdentityClient
import os
import subprocess as sp
sys.path.append(os.getcwd()+"/..")
from commonTools import *

# Execution of the code begins here
def export_networkSources(inputfile, outdir, service_dir, config, signer, ct):
    global values_for_column_networkSources
    global cd3file,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    importCommands = ""

    sheetName = "NetworkSources"

    # Read CD3 Identity Sheets
    df, values_for_column_networkSources = commonTools.read_cd3(cd3file, sheetName)

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- Network Sources would be overwritten during export process!!!\n")

    # Create backup
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    script_file = f'{outdir}/{ct.home_region}/{service_dir}/' + file_name
    if (os.path.exists(script_file)):
        commonTools.backup_file(outdir + "/" + ct.home_region + "/" + service_dir, resource, file_name)

    config.__setitem__("region", ct.region_dict[ct.home_region])
    state = {'path': f'{outdir}/{ct.home_region}/{service_dir}', 'resources': []}
    try:
        byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
        output = byteOutput.decode('UTF-8').rstrip()
        for item in output.split('\n'):
            state["resources"].append(item.replace("\"", "\\\""))
    except Exception as e:
        pass
    idc=IdentityClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

    # Fetch Network Sources
    print("\nFetching Network Sources...")
    network_sources = oci.pagination.list_call_get_all_results(idc.list_network_sources ,compartment_id=config['tenancy'])

    compIDvsName = {}
    #prepare a map of compartment_id and compartment name
    for key in ct.ntk_compartment_ids:
        compIDvsName[ct.ntk_compartment_ids[key]] = key

    index = 0
    total_resource = 0

    for network_source in network_sources.data:
        total_resource = total_resource+1
        network_source_info = network_source
        name = network_source_info.name

        tf_name = commonTools.check_tf_variable(name)
        tf_resource = f'module.iam-network-sources[\\"{tf_name}\\"].oci_identity_network_source.network_source'
        if tf_resource not in state["resources"]:
            importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {str(network_source_info.id)}'

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
                strIPRange = "";
                virtualSourceList = network_source_info.virtual_source_list
                if(virtualSourceList):
                    length = len(virtualSourceList)
                    for i in range(length):
                        virtualSource = virtualSourceList[i]
                        ip_ranges = virtualSource.ip_ranges;

                        if (ip_ranges):
                            if(strIPRange == ""):
                                strIPRange = ",".join(ip_ranges)
                            else:
                                strIPRange = strIPRange + ";" + ",".join(ip_ranges)
                values_for_column_networkSources[col_header].append(strIPRange)

            elif (col_header == "Defined Tags"):
                values_for_column_networkSources = commonTools.export_tags(network_source_info, col_header, values_for_column_networkSources)

    commonTools.write_to_cd3(values_for_column_networkSources, cd3file, sheetName)
    print("{0} Network Sources exported into CD3.\n".format(total_resource))

    if importCommands != "":
        init_commands = f'\n######### Writing import for Network Sources #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        importCommands += f'\n{tf_or_tofu} plan\n'
        with open(script_file, 'a') as importCommandsfile:
            importCommandsfile.write(init_commands + importCommands)

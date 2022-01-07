#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export Alarms
#
# Author: Suruchi
# Oracle Consulting
#

import argparse
import sys
import oci
import os
from pathlib import Path
from commonTools import *


from oci.config import DEFAULT_LOCATION

importCommands = {}
oci_obj_names = {}


def print_alarms(region, alarm, ncpclient,values_for_column, ntk_compartment_name):
    alarm_tf_name = commonTools.check_tf_variable(alarm.display_name)
    suppression = alarm.suppression

    #query= alarm.query
    #metric=query[0:query.rfind('[')]
    #interval = query[query.find("[") + 1:query.rfind("]")]
    #if 'absent()' in query:
    #    statistic = 'absent'
    #else:
    #    statistic = query[query.rfind(".") + 1:query.rfind("(")]

    skip_row=0
    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'Metric Compartment Name':
            metric_comp_id=alarm.metric_compartment_id
            metric_comp_name='Not_Found'
            for k,v in ct.ntk_compartment_ids.items():
                if v==metric_comp_id:
                    metric_comp_name=k
                    break
            if(metric_comp_name == 'Not_found'):
                skip_row=1
            values_for_column[col_header].append(metric_comp_name)
        elif col_header == 'Destination Topic Name':
            topic_name="Not_Found"
            destinations = alarm.destinations
            try:
                topic=ncpclient.get_topic(topic_id=destinations[0]).data
                topic_name=topic.name
            except:
                pass
            if (topic_name == "Not_Found"):
                skip_row=1
            values_for_column[col_header].append(topic_name)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(alarm, col_header, values_for_column)
        else:
            oci_objs = [alarm,suppression]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)

    if(skip_row == 0):
        importCommands[region.lower()].write("\nterraform import oci_monitoring_alarm." + alarm_tf_name + " " + str(alarm.id))

def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export Block Volumes on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export Block Volume objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export Block Volume Objects")
    return parser.parse_args()


def export_alarms(inputfile, _outdir, _config, network_compartments=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global cd3file
    global reg
    global ct
    global outdir
    global values_for_column


    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()


    outdir = _outdir
    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    sheetName="Alarms"
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Read CD3
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    # Check Compartments
    global comp_list_fetch
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments, ct.ntk_compartment_ids)

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Alarms  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    for reg in ct.all_regions:
        script_file = f'{outdir}/{reg}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Block Volume Details
    print("\nFetching details of Alarms...")

    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for Alarms #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()

        mclient = oci.monitoring.MonitoringClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        ncpclient = oci.ons.NotificationControlPlaneClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        for ntk_compartment_name in comp_list_fetch:
            alarms = oci.pagination.list_call_get_all_results(mclient.list_alarms,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="ACTIVE")

            for alarmSummary in alarms.data:
                alarm=mclient.get_alarm(alarmSummary.id).data
                print_alarms(region, alarm,ncpclient,values_for_column, ntk_compartment_name)


        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')
        if "linux" in sys.platform:
            os.chmod(script_file, 0o755)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print(str(len(values_for_column["Region"])) +" Alarms exported to CD3\n")


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_alarms(args.inputfile, args.outdir, args.config, args.network_compartments)

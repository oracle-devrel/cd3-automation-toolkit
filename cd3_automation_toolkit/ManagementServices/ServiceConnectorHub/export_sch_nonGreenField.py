#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export Service Connector Hub
#
# Author: Ulaganathan N
# Oracle Consulting
#

import argparse
import oci
import os
from commonTools import *

from oci.config import DEFAULT_LOCATION

importCommands = {}
oci_obj_names = {}


def get_service_connectors(region, SCH_LIST, sch_client, log_client, la_client, identity_client, stream_client,
                           notification_client, func_client, ct, values_for_column, ntk_compartment_name):
    volume_comp = ""
    log_source_list = []
    target_la_string = ""
    target_log_source_identifier = ""
    target_stream_string = ""
    source_stream_string = ""
    target_topic_string = ""
    target_bucket_name = ""
    target_object_name_prefix = ""
    mon_ns_string = ""
    target_mon_ns_string = ""
    target_func_string = ""

    def get_comp_details(comp_data):
        for c_name, c_id in ct.ntk_compartment_ids.items():
            if c_id == comp_data:
                return c_name

    for schs in SCH_LIST.data:
        sch_details = sch_client.get_service_connector(service_connector_id=schs.id)
        sch_id = schs.id
        sch_compartment_id = schs.compartment_id

        source_data = getattr(sch_details.data, 'source')
        source_kind = getattr(source_data, 'kind')
        target_data = getattr(sch_details.data, 'target')
        target_kind = getattr(target_data, 'kind')

        if source_kind == "logging":
            log_sources = (getattr(source_data, 'log_sources'))

            log_source_list = []
            for log in log_sources:
                if log.log_group_id == "_Audit":
                    log_group_name = "Audit"
                    comp_name = get_comp_details(log.compartment_id)
                    log_source_list.append(f"{comp_name}&{log_group_name}&all")

                elif log.log_group_id == "_Audit_Include_Subcompartment":
                    log_group_name = "Audit_In_Subcompartment"
                    comp_name = get_comp_details(log.compartment_id)
                    log_source_list.append(f"{comp_name}&{log_group_name}&all")

                else:
                    log_group_id = log.log_group_id
                    logs_compartment_details = log_client.get_log_group(log_group_id=log_group_id)
                    log_group_name = getattr(logs_compartment_details.data, 'display_name')
                    comp_name = get_comp_details(log.compartment_id)
                    if log.log_id:
                        log_name = getattr(log_client.get_log(log_group_id=log_group_id, log_id=log.log_id).data,
                                           'display_name')
                        log_source_list.append(f"{comp_name}&{log_group_name}&{log_name}")
                    else:
                        log_source_list.append(f"{comp_name}&{log_group_name}&all")

        if source_kind == "streaming":
            source_stream_id = (getattr(source_data, 'stream_id'))
            source_stream_name = getattr(stream_client.get_stream(stream_id=source_stream_id).data, 'name')
            source_comp_id = getattr(stream_client.get_stream(stream_id=source_stream_id).data, 'compartment_id')
            source_stream_comp_name = get_comp_details(source_comp_id)
            source_stream_string = source_stream_comp_name + "&" + source_stream_name

        if source_kind == "monitoring":
            monitoring_sources = getattr(source_data, 'monitoring_sources')
            comp_ids = []
            namespaces = []
            mon_data = {}
            for item in monitoring_sources:
                for attr, value in item.__dict__.items():
                    if attr == "_compartment_id" and value not in comp_ids:
                        comp_ids.append(value)
                        mon_data.update({value: ""})
                    if attr == "_namespace_details":
                        namespace_data = getattr(value, 'namespaces')
                        namespaces = []
                        for val in namespace_data:
                            if getattr(val, 'namespace') not in namespaces:
                                namespaces.append(getattr(val, 'namespace'))
                                for k, v in mon_data.items():
                                    if v == "":
                                        mon_data[k] = namespaces

            monitoring_sources_dict = {comp_ids[i]: '[' + ', '.join(namespaces) + ']' for i in range(len(comp_ids))}

            mon_namespace_dict = {}
            for comp, ns in mon_data.items():
                comp_name = get_comp_details(comp)
                mon_namespace_dict.update({comp_name: ns})

            mon_ns_string = str(mon_namespace_dict).replace("'", "")
            mon_ns_string = mon_ns_string.replace("{", "").replace("}", "").replace("],", "];")
            mon_ns_string = mon_ns_string.replace(":", "&").replace(" ", "")
            mon_ns_string = mon_ns_string.replace("&&", "::")

        if target_kind == "monitoring":
            metric_name = getattr(target_data, 'metric')
            metric_namespace = getattr(target_data, 'metric_namespace')
            comp_id = getattr(target_data, 'compartment_id')
            comp_name = get_comp_details(comp_id)
            target_mon_ns_string = f'{comp_name}&[{metric_name},{metric_namespace}]'

        if target_kind == "loggingAnalytics":
            dest_log_group_id = getattr(target_data, 'log_group_id')
            target_log_source_identifier = getattr(target_data, 'log_source_identifier')
            dest_logs_compartment_details = la_client.get_log_analytics_log_group(
                log_analytics_log_group_id=dest_log_group_id, namespace_name=la_client.list_namespaces(
                    compartment_id=identity_client.get_user(config["user"]).data.compartment_id).data.items[
                    0].namespace_name)
            target_log_group_name = getattr(dest_logs_compartment_details.data, 'display_name')
            target_comp_id = getattr(dest_logs_compartment_details.data, 'compartment_id')
            target_comp_name = get_comp_details(target_comp_id)
            target_la_string = target_comp_name + "&" + target_log_group_name

        if target_kind == "streaming":
            target_stream_id = getattr(target_data, 'stream_id')
            target_stream_name = getattr(stream_client.get_stream(stream_id=target_stream_id).data, 'name')
            target_comp_id = getattr(stream_client.get_stream(stream_id=target_stream_id).data, 'compartment_id')
            target_stream_comp_name = get_comp_details(target_comp_id)
            target_stream_string = target_stream_comp_name + "&" + target_stream_name

        if target_kind == "notifications":
            target_topic_id = getattr(target_data, 'topic_id')
            target_topic_name = getattr(notification_client.get_topic(topic_id=target_topic_id).data, 'name')
            target_topic_comp_id = getattr(notification_client.get_topic(topic_id=target_topic_id).data,
                                           'compartment_id')
            target_topic_comp_name = get_comp_details(target_topic_comp_id)
            target_topic_string = target_topic_comp_name + "&" + target_topic_name

        if target_kind == "functions":
            target_function_id = getattr(target_data, 'function_id')
            target_function_name = getattr(func_client.get_function(function_id=target_function_id).data, 'display_name')
            target_func_comp_id = getattr(func_client.get_function(function_id=target_function_id).data, 'compartment_id')
            target_func_comp_name = get_comp_details(target_func_comp_id)
            target_application_id = getattr(func_client.get_function(function_id=target_function_id).data, 'application_id')
            target_application_name = getattr(func_client.get_application(application_id=target_application_id).data, 'display_name')
            target_func_string = target_func_comp_name + "@" + target_application_name + "@" + target_function_name

        if target_kind == "objectStorage":
            target_bucket_name = getattr(target_data, 'bucket_name')
            target_object_name_prefix = getattr(target_data, 'object_name_prefix')

        sch_tf_name = commonTools.check_tf_variable(schs.display_name)
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if sch_compartment_id == comp_id and sch_compartment_id not in comp_done_ids:
                volume_comp = comp_name
                comp_done_ids.append(sch_compartment_id)

        importCommands[region.lower()].write(
            "\nterraform import \"module.service-connectors[\\\"" + sch_tf_name + "\\\"].oci_sch_service_connector.service_connector\" " + str(
                sch_id))

        for col_header in values_for_column:
            if col_header == 'Region':
                values_for_column[col_header].append(region)
            elif col_header == 'Compartment Name':
                values_for_column[col_header].append(volume_comp)
            elif col_header == 'Source Kind':
                values_for_column[col_header].append(source_kind)
            elif col_header == "Source Log Group Names" and source_kind == "logging":
                log_source_list = [*set(log_source_list)]
                values_for_column[col_header].append(",".join(log_source_list))
            elif col_header == 'Target Kind':
                values_for_column[col_header].append(target_kind)
            elif col_header == 'Target Log Group Name' and target_kind == "loggingAnalytics":
                values_for_column[col_header].append(target_la_string)
            elif col_header == 'Target Log Source Identifier' and target_kind == "loggingAnalytics":
                values_for_column[col_header].append(target_log_source_identifier)
            elif col_header == 'Source Stream Name' and source_kind == "streaming":
                values_for_column[col_header].append(source_stream_string)
            elif col_header == 'Target Stream Name' and target_kind == "streaming":
                values_for_column[col_header].append(target_stream_string)
            elif col_header == 'Source Monitoring Details' and source_kind == "monitoring":
                values_for_column[col_header].append(mon_ns_string)
            elif col_header == 'Target Monitoring Details' and target_kind == "monitoring":
                values_for_column[col_header].append(target_mon_ns_string)
            elif col_header == 'Target Topic Name' and target_kind == "notifications":
                values_for_column[col_header].append(target_topic_string)
            elif col_header == 'Target Function Details' and target_kind == "functions":
                values_for_column[col_header].append(target_func_string)
            elif col_header == 'Target Bucket Name' and target_kind == "objectStorage":
                values_for_column[col_header].append(target_bucket_name)
            elif col_header == 'Target Object Name Prefix' and target_kind == "objectStorage":
                values_for_column[col_header].append(target_object_name_prefix)

            # elif col_header == 'Stream Partitions' and target_kind == "streaming":
            #     stream_partitions = getattr(target_data, 'stream_partitions')
            #     values_for_column[col_header].append(stream_partitions)
            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(schs, col_header, values_for_column)
            else:
                oci_objs = [schs]
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict,
                                                                     values_for_column)


def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export Service Connectors  on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export Service Connectors objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument('service_dir', help='Structured out directory for creation of TF files')
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--export-compartments", nargs='*', required=False,
                        help="comma seperated Compartments for which to export Service Connector Objects")
    parser.add_argument("--export-regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                        required=False)

    return parser.parse_args()


def export_service_connectors(inputfile, _outdir, service_dir, _config, ct, export_compartments=[],export_regions=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global cd3file
    global reg
    global outdir
    global valuesforcolumn

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    outdir = _outdir
    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    sheetName = "ServiceConnectors"
    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab- ServiceConnectors  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Service Connector Hub Details
    print("\nFetching details of Service Connectors...")

    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for Service Connectors #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()
        sch_client = oci.sch.ServiceConnectorClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        log_client = oci.logging.LoggingManagementClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        la_client = oci.log_analytics.LogAnalyticsClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        identity_client = oci.identity.IdentityClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        stream_client = oci.streaming.StreamAdminClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        notification_client = oci.ons.NotificationControlPlaneClient(config,
                                                                     retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        func_client = oci.functions.FunctionsManagementClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        for ntk_compartment_name in export_compartments:
            SCH_LIST = oci.pagination.list_call_get_all_results(sch_client.list_service_connectors,
                                                                compartment_id=ct.ntk_compartment_ids[
                                                                    ntk_compartment_name], lifecycle_state="ACTIVE",
                                                                sort_by="timeCreated")
            get_service_connectors(region, SCH_LIST, sch_client, log_client, la_client, identity_client,
                                   stream_client, notification_client, func_client, ct, values_for_column, ntk_compartment_name)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("Service Connectors exported to CD3\n")

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_service_connectors(args.inputfile, args.outdir, args.service_dir, args.config, args.export_compartments,args.export_regions)
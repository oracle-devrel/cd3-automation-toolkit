#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Service Connector Hub resources.
#
# Author: Ulaganathan N
# Oracle Consulting
#
import json
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

# Execution of the code begins here
def create_service_connectors(inputfile, outdir, service_dir, prefix, ct):
    tfStr = {}

    filename = inputfile

    sheetName = "ServiceConnectors"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('service-connectors-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
        tfStr[eachregion] = ''

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        display_name = str(df.loc[i, 'Display Name'])

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(
                df.loc[i, 'Display Name']).lower() == 'nan' or str(
            df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
            df.loc[i, 'Source Kind']).lower() == 'nan' or str(
            df.loc[i, 'Target Kind']).lower() == 'nan'):
            print(
                "\nColumn Region, Compartment Name, Display Name, "
                "Source Kind, Target Kind cannot be left empty in ServiceConnectors sheet of "
                "CD3..exiting...")
            exit(1)

        if (str(df.loc[i, 'Source Kind']).lower() == "streaming" and str(
                df.loc[i, 'Source Kind']).lower() == "logginganalytics" and str(
            df.loc[i, 'Target Log Source Identifier']).lower() == 'nan' or
                str(df.loc[i, 'Target Log Source Identifier']).lower() == ""):
            print(
                "\n Target Log Source Identifier field cannot be left empty when source is streaming "
                "and target is logginganalytics in ServiceConnectors sheet of "
                "CD3..exiting...")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Display Name':
                # columnvalue = columnvalue.strip()
                display_name = columnvalue
                display_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'serviceconnector_tf_name': display_tf_name, 'serviceconnector_name': display_name}

            # if columnname == 'Description':
            #    tempdict = {'description': description}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            # if columnname == 'Logs Compartment Name':
            #     logs_compartment_var_name = columnvalue.strip()
            #     logs_compartment_var_name = commonTools.check_tf_variable(logs_compartment_var_name)
            #     tempdict = {'logs_compartment_tf_name': logs_compartment_var_name}

            if columnname == 'Source Kind':
                source_kind = columnvalue.strip()
                source_kind = commonTools.check_tf_variable(source_kind)
                tempdict = {'source_kind': source_kind}

            if columnname == 'target kind':
                target_kind = columnvalue.strip()
                target_kind = commonTools.check_tf_variable(target_kind)
                tempdict = {'target_kind': target_kind}

            if columnname == 'Target Stream Name':
                target_stream_name = columnvalue.strip().split()
                target_stream_name = dict(subString.split("@") for subString in target_stream_name)
                target_stream_name = dict((commonTools.check_tf_variable(k), v) for k, v in target_stream_name.items())
                target_stream_name = json.dumps(target_stream_name)
                tempdict = {'target_stream_name': target_stream_name}

            if columnname == 'Source Stream Name':
                source_stream_name = columnvalue.strip().split()
                source_stream_name = dict(subString.split("@") for subString in source_stream_name)
                source_stream_name = dict((commonTools.check_tf_variable(k), v) for k, v in source_stream_name.items())
                source_stream_name = json.dumps(source_stream_name)
                tempdict = {'source_stream_name': source_stream_name}

            if columnname == 'Stream Partitions':
                stream_partitions = columnvalue.strip()
                # stream_partitions = commonTools.check_tf_variable(stream_partitions)
                tempdict = {'stream_partitions': stream_partitions}

            if columnname == 'Target Log Group Name':
                target_log_group_name = columnvalue.strip().split()
                target_log_group_name = dict(subString.split("@") for subString in target_log_group_name)
                target_log_group_name = dict(
                    (commonTools.check_tf_variable(k), v) for k, v in target_log_group_name.items())
                target_log_group_name = json.dumps(target_log_group_name)
                tempdict = {'target_log_group_name': target_log_group_name}

            if columnname == 'Target Log Source Identifier':
                target_log_source_identifier = columnvalue.strip()
                tempdict = {'target_log_source_identifier': target_log_source_identifier}

            if columnname == 'Source Log Group Names':
                source_log_group_names = columnvalue.strip()
                source_log_group_list = source_log_group_names.replace(" ", "").replace("::", "--").split(",")
                for index, item in enumerate(source_log_group_list):
                    if len(item.split("@")) == 2:
                        source_log_group_list[index] = f"{item}@all"

                source_log_group_list = json.dumps(source_log_group_list)
                tempdict = {'source_log_group_names': source_log_group_list}

            if columnname == 'Target Topic Name':
                target_topic_name = columnvalue.strip().split()
                target_topic_name = dict(subString.split("@") for subString in target_topic_name)
                target_topic_name = dict((commonTools.check_tf_variable(k), v) for k, v in target_topic_name.items())
                target_topic_name = json.dumps(target_topic_name)
                tempdict = {'target_topic_name': target_topic_name}

            if columnname == 'Target Bucket Name':
                target_bucket_name = columnvalue.strip()
                tempdict = {'target_bucket_name': target_bucket_name}

            if columnname == 'Target Object Name Prefix':
                target_object_name_prefix = columnvalue.strip()
                tempdict = {'target_object_name_prefix': target_object_name_prefix}

            if columnname == 'Target Function Details':
                target_function_details = columnvalue.strip()
                target_function_details = target_function_details.replace(" ", "").replace("::", "--").split(",")

                target_function_details = json.dumps(target_function_details)
                tempdict = {'target_function_details': target_function_details}

            if columnname == 'Target Monitoring Details' and columnvalue != "":
                target_monitoring_details = columnvalue.strip().replace(" ", "")
                target_monitoring_details = dict(item.split("@") for item in target_monitoring_details.split(";"))
                target_monitoring_details = {
                    json.dumps(key): '[' + ','.join(['"' + x + '"' for x in val[1:-1].split(',')]) + ']' for
                    key, val in target_monitoring_details.items()}

                target_monitoring_details = "{" + ", ".join(
                    ["{}:{}".format(k, v) for k, v in target_monitoring_details.items()]) + "}"
                target_monitoring_details = str(target_monitoring_details).replace(', ', ',\n').replace("::", "--")
                tempdict = {'target_monitoring_details': target_monitoring_details}

            if columnname == 'Source Monitoring Details' and columnvalue != "":
                # loop through the columnvalue
                monitoring_details = columnvalue.strip().replace(" ", "")
                monitoring_details = dict(item.split("@") for item in monitoring_details.split(";"))
                # monitoring_details = dict((commonTools.check_tf_variable(k), v) for k, v in monitoring_details.items())
                monitoring_details = {
                    json.dumps(key): '[' + ','.join(['"' + x + '"' for x in val[1:-1].split(',')]) + ']' for
                    key, val in monitoring_details.items()}

                monitoring_details = "{" + ", ".join(
                    ["{}:{}".format(k, v) for k, v in monitoring_details.items()]) + "}"
                monitoring_details = str(monitoring_details).replace(', ', ',\n').replace('::', "--")
                tempdict = {'source_monitoring_details': monitoring_details}

                # split compartment_name and metric namespaces by separator
                # form the below format for each entry and append to source_monitoring_details dict
                #   "comp_name" = ["oci_computeagent","oci_blockstorage"]
                # if repeated entry check for membership and modify the previous one or create a new key/value pair.

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:

        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if tfStr[reg] != '':
            # Generate SCH String
            src = "##Add New SCH for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            resource = sheetName.lower()
            commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

            # Write to TF file
            outfile = reg_out_dir + "/" + auto_tfvars_filename
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print(outfile + " has been created for region " + reg)
            oname.write(tfStr[reg])
            oname.close()

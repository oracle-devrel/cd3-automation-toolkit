#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Instances
#
# Author: Suruchi
# Oracle Consulting

#

import argparse
import os
import datetime
from commonTools import *
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader



def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates TF files for Alarms")
    parser.add_argument('inputfile', help='Full Path of input CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


#If input is CD3 excel file
def create_terraform_alarms(inputfile, outdir, prefix, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config
    sheetName="Alarms"
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    x = datetime.datetime.now()
    date = x.strftime("%f").strip()
    tempStr={}
    tfStr={}
    outfile = {}
    oname = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    alarms_template = env.get_template('alarm-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()


    # Take backup of files
    for eachregion in ct.all_regions:
        resource=sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, sheetName.lower()+".tf")
        tfStr[eachregion] = ''

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region=region.strip().lower()
        
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempdict = {}
        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Alarm Name']).lower() == 'nan' or str(df.loc[i, 'Destination Topic Name']).lower() == 'nan' or str(df.loc[i, 'Is Enabled']).lower() == 'nan' or str(df.loc[i, 'Metric Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Namespace']).lower() == 'nan' or str(df.loc[i, 'Severity']).lower() == 'nan' or str(df.loc[i, 'Query']).lower() == 'nan':
            print("\nThe values for Region, Compartment, Alarm Name, Destination Topic Name, Is Enabled, Metric Compartment Name, Namespace, Severity and Query cannot be left empty. Please enter a value and try again !!")
            exit()

        #metric = str(df.loc[i, 'Metric Name']).strip()
        #interval = str(df.loc[i, 'Interval']).strip()
        #statistic = str(df.loc[i, 'Statistic']).strip().lower()
        #operator = str(df.loc[i, 'Operator']).strip()
        #value = str(df.loc[i, 'Value']).strip()
        #query=metric[interval].statistic() operator value
        #if(operator.lower()=="absent"):
        #    query = metric+"["+interval+"].absent()"
        #else:
        #    query = metric+"["+interval+"]."+statistic+"() < "+value
        #tempdict = {"query": query}

        skip_row=0
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()
            
            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivXalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = commonTools.check_tf_variable(columnvalue)
                columnvalue = str(compartmentVarName)
                tempdict = {"compartment_tf_name": columnvalue}
            if columnname == "Severity":
                columnvalue = str(columnvalue).upper()


            if columnname == "Metric Compartment Name":
                if columnvalue == 'Not_Found':
                    skip_row = 1
                    continue

                compartmentVarName = commonTools.check_tf_variable(columnvalue)
                columnvalue = str(compartmentVarName)
                tempdict = {"metric_compartment_tf_name": columnvalue}

            if columnname == "Alarm Name":
                alarm_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'alarm_tf_name': alarm_tf_name}


            if columnname == "Destination Topic Name":
                if columnvalue == 'Not_Found':
                    skip_row = 1
                    continue

                topic_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'destination_topic_tf_name': topic_tf_name}
                tempStr.update(tempdict)

            if columnname == "Is Enabled":
                is_enabled = commonTools.check_columnvalue(columnvalue)
                tempdict = {'is_enabled': is_enabled}
                tempStr.update(tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if skip_row == 1:
            continue

        # Write all info to TF string
        tfStr[region]=tfStr[region]+alarms_template.render(tempStr)+"\n"

    # Write to output
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg
        if(tfStr[reg]!=''):
            outfile[reg] = reg_out_dir + "/"+prefix+"_"+sheetName.lower()+".tf"
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for Alarms has been created for region "+reg)



if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_terraform_alarms(args.inputfile, args.outdir, args.prefix, args.config)

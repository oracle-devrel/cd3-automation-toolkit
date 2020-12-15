#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI solutions components
# Notifications & Subscriptions
#
#Author: Shravanthi Lingam
#Oracle Consulting
#shravanthi.lingam@oracle.com
# Modified (TF Upgrade): Shravanthi Lingam
#

import sys
import argparse
import os
import datetime
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd()+"/../..")
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######

#If input is cd3 file
def main():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Creates TF files for Notifications")
    parser.add_argument("inputfile",help="Full Path to the CSV file for creating fss or CD3 excel file. eg fss.csv or CD3-template.xlsx in example folder")
    parser.add_argument("outdir",help="directory path for output tf files ")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv)<3:
            parser.print_help()
            sys.exit(1)

    # Declare variables
    args = parser.parse_args()
    filename = args.inputfile
    outdir = args.outdir
    all_regions = os.listdir(outdir)
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""
    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    x = datetime.datetime.now()
    date = x.strftime("%f").strip()
    tempStr={}
    tfStr={}
    Notifications_names={}
    Subscriptions_names={}

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    notifications_template = env.get_template('notifications-template')
    subscriptions_template = env.get_template('subscriptions-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Notifications")

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for reg in ct.all_regions:
        tfStr[reg] = ''
        Notifications_names[reg]=[]
        Subscriptions_names[reg]=[]
    reg = df['Region'].unique()
    
    # Take backup of Notification files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()
        resource='Notifications'
        if (eachregion in commonTools.endNames)or ('nan' in str(eachregion).lower() ):
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-notification.tf")
        commonTools.backup_file(srcdir, resource, "-subscription.tf")
    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()
        region=region.strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)
        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Protocol']).lower() == 'nan' or str(df.loc[i, 'Endpoint']).lower() == 'nan' or str(df.loc[i, 'Topic']).lower() == 'nan' :
            print("\nThe values for Region, Compartment, Topic, Protocol and Endpoint cannot be left empty. Please enter a value and try again !!")
            exit()
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
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {columnname: columnvalue}

            if columnname == "Topic":
                columnvalue = columnvalue.strip()
                topic = columnvalue
                tf_name_topic = commonTools.check_tf_variable(columnvalue)
                tempdict = {'topic_tf_name': tf_name_topic}

            if columnname == "Description":
                if columnvalue == "" or columnvalue == 'nan':
                    topic_desc = ""
                topic_desc = columnvalue.strip()
                tempdict = {'topic_description': topic_desc}   

            if columnname == "Protocol":
                columnvalue = columnvalue.strip()
                protocol = commonTools.check_tf_variable(columnvalue)
                protocol = protocol.upper()
                tempdict = {'protocol': protocol}

            if columnname == "Endpoint":
                endpoint = columnvalue.strip()
                tempdict = {'endpoint': endpoint}
          
            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
           
        count = 1 
        if(topic in Notifications_names[region]):
                count = count +  1
        if(topic not in Notifications_names[region]):
                Notifications_names[region].append(topic)             
                # Write all info to TF string
                tfStr[region]=tfStr[region] + notifications_template.render(tempStr)
                # Write to output
                file = outdir + "/" + region + "/" + tf_name_topic + "-notification.tf"
                oname = open(file, "w+")
                print("Writing to " + file)
                oname.write(tfStr[region])
                oname.close()
                tfStr[region]= ""
        subscription = tf_name_topic + "_sub" + str(count)
        tempdict = {'subscription_tf_name': subscription}
        tempStr.update(tempdict)
        if(subscription.strip() not in Subscriptions_names[region]):
                Subscriptions_names[region].append(subscription.strip())
                if ( protocol in "ORACLE_FUNCTIONS" ):
                    endpoint = endpoint.split("::")
                    endpoint = endpoint[1]
                    tempdict = {'endpoint': endpoint}
                    tempStr.update(tempdict)
                tfStr[region]=tfStr[region] + subscriptions_template.render(tempStr)
                # Write to output
                file = outdir + "/" + region + "/" + subscription + "-subscription.tf"
                oname = open(file, "w+")
                print("Writing to " + file)
                oname.write(tfStr[region])
                oname.close()
                tfStr[region]=""

if __name__ == '__main__':

    # Execution of the code begins here
    main()
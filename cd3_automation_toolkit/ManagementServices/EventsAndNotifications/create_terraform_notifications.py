#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Management components
# Notifications & Subscriptions
#
#Author: Shravanthi Lingam
#Oracle Consulting
#shravanthi.lingam@oracle.com
# Modified (TF Upgrade): Shravanthi Lingam
#
import datetime
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######

# Execution of the code begins here
def create_terraform_notifications(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile
    outdir = outdir
    sheetName="Notifications"
    topics_auto_tfvars_filename = '_' + sheetName.lower() + '-topics.auto.tfvars'
    subs_auto_tfvars_filename = '_' + sheetName.lower() + '-subscriptions.auto.tfvars'

    x = datetime.datetime.now()
    date = x.strftime("%f").strip()
    tempStr={}
    tfStr={}
    tfStr1 = {}
    outfile={}
    oname={}
    Notifications_names={}
    Subscriptions_names={}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    notifications_template = env.get_template('notifications-topics-template')
    subscriptions_template = env.get_template('notifications-subscriptions-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    regions_done = []

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for eachregion in ct.all_regions:
        tfStr[eachregion] = ''
        tfStr1[eachregion] = ''
        Notifications_names[eachregion]=[]
        Subscriptions_names[eachregion]=[]

        # Take backup of files
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, topics_auto_tfvars_filename)
        commonTools.backup_file(srcdir, resource, subs_auto_tfvars_filename)

    # Iterate over rows
    count = 1
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
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Topic']).lower() == 'nan' :
            print("\nThe values for Region, Compartment, Topic cannot be left empty. Please enter a value and try again !!")
            exit(1)
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i])

            # Dont strip for Description
            if columnname == "Description":
                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

            else:
                columnvalue = columnvalue.strip()
                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
            
            if columnname == "Compartment Name":
                compartmentVarName = commonTools.check_tf_variable(columnvalue)
                columnvalue = str(compartmentVarName)
                tempdict = {"compartment_tf_name": columnvalue}

            if columnname == "Topic":
                columnvalue = columnvalue.strip()
                topic = columnvalue
                tf_name_topic = commonTools.check_tf_variable(columnvalue)
                tempdict = {'topic_tf_name': tf_name_topic}

            if columnname == "Description":
                tempdict = {'description': columnvalue}

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

        if(topic in Notifications_names[region]):
                count = count +  1
        if(topic not in Notifications_names[region]):
                count = 1
                Notifications_names[region].append(topic)             
                # Write all info to TF string
                tfStr[region]=tfStr[region][:-1]  + notifications_template.render(tempStr)

        #Empty Topic
        if(str(df.loc[i, 'Protocol']).lower() == 'nan' and str(df.loc[i, 'Endpoint']).lower() == 'nan'):
            continue

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
                tfStr1[region]=tfStr1[region][:-1]  + subscriptions_template.render(tempStr)

    # Write to output
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if (tfStr[reg] != ''):
            outfile[reg] = reg_out_dir + "/" + prefix + topics_auto_tfvars_filename
            srcStr = "##Add New Topics for "+str(reg).lower()+" here##"
            tfStr[reg] = notifications_template.render(skeleton=True, region=reg).replace(srcStr, tfStr[reg] + "\n" + srcStr)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg] = open(outfile[reg], 'w+')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for Notifications_Topics has been created for region " + reg)

        if (tfStr1[reg] != ''):
            outfile[reg] = reg_out_dir + "/" + prefix + subs_auto_tfvars_filename
            srcStr = "##Add New Subscriptions for "+str(reg).lower()+" here##"
            tfStr1[reg] = subscriptions_template.render(skeleton=True, region=reg).replace(srcStr,tfStr1[reg] + "\n" + srcStr)
            tfStr1[reg] = "".join([s for s in tfStr1[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg] = open(outfile[reg], 'w+')
            oname[reg].write(tfStr1[reg])
            oname[reg].close()
            print(outfile[reg] + " for Notifications_Subscriptions has been created for region " + reg)


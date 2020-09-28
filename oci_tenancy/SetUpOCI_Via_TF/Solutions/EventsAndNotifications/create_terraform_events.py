#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Instances
#
# Author: Shravanthi Lingam
# Oracle Consulting
# Modified (TF Upgrade): Shravanthi Lingam
#

import json
import sys
import argparse
import os
import shutil
import datetime
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

#Method to extend conditions with resources
def extend_event(service_name, resources, listeventid):
            event = [ "com.oraclecloud." + service_name + "." + resources ]
            listeventid['eventType'].extend(event)
            listeventid['eventType'] = list(dict.fromkeys(listeventid['eventType']))
            condition = json.dumps(listeventid)
            condition = condition.replace("\"" , "\\\"")
            condition = condition.replace(" " , "")
            return (condition)


#If input is CD3 excel file
def main():

    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates TF files for Events")
    parser.add_argument("inputfile",help="Full Path to the CSV file for creating fss or CD3 excel file. eg fss.csv or CD3-template.xlsx in example folder")
    parser.add_argument("outdir",help="directory path for output tf files ")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv)<2:
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
    #tempStr2={}
    Events_names={}
    tfStr={}
    NaNstr = 'NaN'

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    events_template = env.get_template('events-template')
    actions_template = env.get_template('actions-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Events")

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for reg in ct.all_regions:
        tfStr[reg] = '' 
        Events_names[reg]=[]
    reg = df['Region'].unique()
    
    # Take backup of files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()
        resource='Events'
        if (eachregion in commonTools.endNames):
            break
        if eachregion == 'nan':
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-event.tf")

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
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Event Name']).lower() == 'nan' or str(df.loc[i, 'Action Type']).lower() == 'nan' or str(df.loc[i, 'Action is Enabled']).lower() == 'nan' or str(df.loc[i, 'Service Name']).lower() == 'nan' or str(df.loc[i, 'Resource']).lower() == 'nan' or str(df.loc[i, 'Event is Enabled']).lower() == 'nan'or str(df.loc[i, 'Topic']).lower() == 'nan' :
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

            if columnname == "Event Description":
                if columnvalue == "" or columnvalue == 'nan':
                    event_desc = ''
                event_desc = columnvalue.strip()
                event_desc = event_desc.replace("\"" , "\\\"")
                tempdict = {'event_description': event_desc}   

            if columnname == "Action Description":
                if columnvalue == "" or columnvalue == 'nan':
                    action_desc = ''
                action_desc = columnvalue.strip()
                tempdict = {'action_description': action_desc} 
                tempStr.update(tempdict)

            if columnname == "Event Name":
                event_name = columnvalue.strip()
                tf_name = commonTools.check_tf_variable(event_name)
                tempdict = {'event_tf_name': tf_name}

            if columnname == "Action Type":
                action_type = columnvalue.strip()
                tempdict = {'action_type': action_type}
                tempStr.update(tempdict)
            
            if columnname == "Topic":
               topic_name = columnvalue.strip()
               if ( action_type.lower() in "faas"):
                topic_id = topic_name.split("::")
                topic_id = "\"" + topic_id[1] + "\""
                tempdict = {'action_id': topic_id}
                tempStr.update(tempdict)
                name = "function_id"
                tempdict = {'label' : name}
                tempStr.update(tempdict)
               if ( action_type.lower() == "ons"):
                topic_id = "oci_ons_notification_topic." + topic_name + ".id"
                tempdict = {'action_id': topic_id}
                tempStr.update(tempdict)
                name = "topic_id"
                tempdict = {'label' : name}
                tempStr.update(tempdict)

            if columnname == "Action is Enabled":
                columnvalue = columnvalue.strip()
                action_is_enabled = commonTools.check_columnvalue(columnvalue)
                tempdict = {'action_is_enabled': action_is_enabled}
                tempStr.update(tempdict)

            if columnname == "Event is Enabled":
                columnvalue = columnvalue.strip()
                event_is_enabled = commonTools.check_columnvalue(columnvalue)
                tempdict = {'event_is_enabled': event_is_enabled}

            if columnname == "Service Name": 
                service_name = columnvalue.strip()

            if columnname == "Resource":
                resources = columnvalue.strip()
            
            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if(event_name not in Events_names[region]):
            tfStr[region] = ""
            Events_names[region].append(event_name)
            listevent = '{"eventType":[],"data":{}}'
            listeventid = json.loads(listevent)
            temp_topic = topic_name
            temp_action = action_is_enabled
            if(str(service_name).lower()==NaNstr.lower() and str(resources).lower()==NaNstr.lower()): 
                tempdict = {'condition' : "{}"}
                temp = "{}"
            if (str(service_name).lower()!=NaNstr.lower() and str(resources).lower()!=NaNstr.lower()):
                condition = extend_event(service_name, resources, listeventid)
                temp = condition
                tempdict = {'condition' : condition}
            tempStr.update(tempdict)
      
            # Write all info to TF string
            tfStr[region]=tfStr[region] + events_template.render(tempStr)
            actions =  actions_template.render(tempStr)
            tfStr[region] = tfStr[region].replace("#ADD_Actions", actions)

            # Write to output
            file = outdir + "/" + region + "/" + tf_name + "-event.tf"
            oname = open(file, "w+")
            print("Writing to " + file)
            oname.write(tfStr[region])
            oname.close()

        elif(event_name in Events_names[region]):
            tfStr[region]=''
            if( topic_name == temp_topic):
             if( temp_action != action_is_enabled ):
              temp_action = action_is_enabled
              actions =  actions + actions_template.render(tempStr)
            if( topic_name != temp_topic ):
             temp_topic = topic_name
             temp_action = action_is_enabled
             actions =  actions + actions_template.render(tempStr)
             
            if(str(service_name).lower()==NaNstr.lower() and str(resources).lower()==NaNstr.lower()):
                condition = "{}"
            if (str(service_name).lower()!=NaNstr.lower() and str(resources).lower()!=NaNstr.lower()):
                condition = extend_event(service_name, resources, listeventid)
            tempdict = {'condition' : condition}
            tempStr.update(tempdict)
            tfStr[region]=tfStr[region] + events_template.render(tempStr)
            tfStr[region] = tfStr[region].replace("#ADD_Actions", actions)

            # Write to output
            file = outdir + "/" + region + "/" + tf_name + "-event.tf"
            oname = open(file, "w+")
            oname.write(tfStr[region])
            oname.close()

if __name__ == '__main__':

    # Execution of the code begins here
    main()

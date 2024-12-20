#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Management components
# Events
#
# Author: Shravanthi Lingam
# Oracle Consulting
# Modified (TF Upgrade): Shravanthi Lingam
#

import json
from commonTools import *
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

#Method to extend conditions with resources
def extend_event(service_name, resources, listeventid):
    event = [ "com.oraclecloud." + service_name + "." + resources ]
    listeventid['eventType'].extend(event)
    listeventid['eventType'] = list(dict.fromkeys(listeventid['eventType']))
    condition = json.dumps(listeventid,separators=(',', ':'))
    condition = condition.replace("\"" , "\\\"")
    #condition = condition.replace(" " , "")
    return (condition)


# Execution of the code begins here
def create_terraform_events(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile

    sheetName = "Events"
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    tempStr={}
    event_data = ""
    Events_names={}
    outfile = {}
    oname = {}
    tfStr={}
    NaNstr = 'NaN'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    events_template = env.get_template('events-template')
    actions_template = env.get_template('actions-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    region_list = df['Region'].tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        resource=sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

        tfStr[eachregion] = ''
        Events_names[eachregion] = []

    regions_done_count =[]
    region = None
    # Iterate over rows
    i=0
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
            exit(1)

        data = "{}"
        for columnname in dfcolumns:
            # Column value

            # Dont strip for Description
            columnvalue = str(df[columnname][i])
            if columnname in ["Event Description","Additional Data"]:

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

            else:
                columnvalue = columnvalue.strip()
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
                tempdict = {'event_description': columnvalue}

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
                topic_id = topic_id[1]
                tempdict = {'action_id': topic_id}
                tempStr.update(tempdict)
                name = "function_id"
                tempdict = {'label' : name}
                tempStr.update(tempdict)
               if ( action_type.lower() == "ons"):
                topic_id = topic_name
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
            if columnname == "Additional Data" or columnname == "AdditionalData":
                data = columnvalue

            if columnname == "Service Name": 
                service_name = columnvalue.strip()

            if columnname == "Resource":
                resources = columnvalue.strip()
            
            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)


        if(event_name not in Events_names[region]):
            prev_row_region = str(region_list[i-1]).strip().lower()
            if (i!=0 and region != prev_row_region):
                tfStr[prev_row_region] = tfStr[prev_row_region][:-1] + event_data
            else:
                tfStr[region] =tfStr[region][:-1] + event_data

            if (region not in regions_done_count):
                tempdict = {"count": 0}
                regions_done_count.append(region)
            else:
                tempdict = {"count": i}
            tempStr.update(tempdict)

            Events_names[region].append(event_name)
            listevent = '{"eventType":[]}'
            #listevent = '{"data":{},"eventType":[]}'
            listeventid = json.loads(listevent)
            temp_topic = topic_name
            temp_action = action_is_enabled
            if(str(service_name).lower()==NaNstr.lower() and str(resources).lower()==NaNstr.lower()): 
                tempdict = {'condition' : "{}"}
                temp = "{}"
            if (str(service_name).lower()!=NaNstr.lower() and str(resources).lower()!=NaNstr.lower()):
                condition = extend_event(service_name, resources, listeventid)
                temp = condition
                json_acceptable_string = condition.replace("\\", "")
                d = json.loads(json_acceptable_string)
                if data != "{}":
                    d["data"] = json.loads(data.replace("'", "\""))
                else:
                    d["data"] = json.loads(data)
                condition = json.dumps(d,separators=(',', ':'))

                condition = condition.replace("\"" , "\\\"").replace("'", "\\\"")
                tempdict = {'condition' : condition}
            tempStr.update(tempdict)
      
            event_data = events_template.render(tempStr)
            actions = actions_template.render(tempStr)
            event_data = event_data.replace("#ADD_Actions", actions)

        elif(event_name in Events_names[region]):
            prev_row_region = str(region_list[i - 1]).strip().lower()
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

            json_acceptable_string = condition.replace("\\", "")
            d = json.loads(json_acceptable_string)
            if data != "{}":
                d["data"] = json.loads(data.replace("'", "\""))
            else:
                d["data"] = json.loads(data)
            condition = json.dumps(d,separators=(',', ':'))
            condition = condition.replace("\"", "\\\"").replace("'", "\\\"")

            tempdict = {'condition' : condition}
            tempStr.update(tempdict)

            event_data = events_template.render(tempStr)
            event_data = event_data.replace("#ADD_Actions", actions)

    if(i!=0 and region in commonTools.endNames):
        tfStr[prev_row_region] = tfStr[prev_row_region][:-1] + event_data
    if(region!=None and region not in commonTools.endNames):
        tfStr[region] = tfStr[region][:-1] + event_data
    # Write to output
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if (tfStr[reg] != ''):
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for Events has been created for region " + reg)


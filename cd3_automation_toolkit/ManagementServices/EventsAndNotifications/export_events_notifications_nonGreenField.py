#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Management components
# Events, Notifications & Subscriptions
#
#Author: Shravanthi Lingam
#Oracle Consulting
#
import sys
import oci
import json
from oci.ons import NotificationControlPlaneClient
from oci.events import EventsClient
from oci.ons import NotificationDataPlaneClient
from oci.functions import FunctionsManagementClient
from oci.config import DEFAULT_LOCATION
import os
sys.path.append(os.getcwd() + "/..")
from commonTools import *

compartment_ids={}
importCommands={}

def  print_notifications(values_for_column_notifications,region, ntk_compartment_name, sbpn, nftn_info, i, fun):

    tf_name_nftn = commonTools.check_tf_variable(str(nftn_info.name))
    sbpn_name = nftn_info.name + "_" + "sub" + str(i)
    tf_name_sbpn = commonTools.check_tf_variable(str(sbpn_name))

    for col_header in values_for_column_notifications.keys():
        if (col_header == "Region"):
            values_for_column_notifications[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_notifications[col_header].append(ntk_compartment_name)
        elif (col_header == "Topic"):
            values_for_column_notifications[col_header].append(nftn_info.name)
        elif (col_header == "Topic Description"):
            values_for_column_notifications[col_header].append(nftn_info.description)
        elif (col_header == "Protocol"):
            if (i==0):
                values_for_column_notifications[col_header].append('')
            else:
                values_for_column_notifications[col_header].append(sbpn.protocol)
        elif (col_header == "Endpoint"):
            if (i==0):
                values_for_column_notifications[col_header].append('')
            else:
                endpoint = sbpn.endpoint
                if ("ORACLE_FUNCTIONS" in sbpn.protocol):
                    endpointname = fun.get_function(endpoint).data
                    endpoint = endpointname.display_name + "::" + endpoint
                values_for_column_notifications[col_header].append(endpoint)
        elif col_header.lower() in ['subscription defined tags','subscription_defined_tags','subscription freeform tags', 'subscription_freeform_tags']:
            if (sbpn == None):
                values_for_column_notifications[col_header].append("")
            else:
                values_for_column_notifications = commonTools.export_tags(sbpn, col_header, values_for_column_notifications)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_notifications = commonTools.export_tags(nftn_info, col_header, values_for_column_notifications)
        else:
            oci_objs = [nftn_info,sbpn]
            values_for_column_notifications = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_notifications,values_for_column_notifications)

    if (i ==0 or i == 1):
       importCommands[region.lower()].write("\nterraform import \"module.notifications-topics[\\\"" + str(tf_name_nftn) + "\\\"].oci_ons_notification_topic.topic\" " + str(nftn_info.topic_id))

    if(i!=0):
        importCommands[region.lower()].write("\nterraform import \"module.notifications-subscriptions[\\\"" + str(tf_name_sbpn) + "\\\"].oci_ons_subscription.subscription\" " + str(sbpn.id))



def print_events(values_for_column_events, region, ntk_compartment_name, event, event_info, ncpc, fun):
    tf_name = commonTools.check_tf_variable(str(event.display_name))
    event_name = event.display_name
    action_type = ""
    action_is_enabled = ""
    action_description = ""
    action_id = ""
    event_is_enabled = event.is_enabled
    event_prod =  ""
    event_res = ""
    data = ""
    event_desc = ""
    event_desc = event.description
    actions = event_info.actions.actions
    condition = json.loads(event.condition)
    if ( actions is not None ):
        i = 0
        for action in actions:
          action_type = action.action_type
          action_is_enabled = str(action.is_enabled)
          if (action_type == "OSS"):
              print("Ignoring Event "+event_name +" because action is OSS")
              action_name = ""
              continue
          if ( action_type == "FAAS" ):
             action_id = action.function_id
             try:
                 action_info = fun.get_function(action_id).data
                 action_name = action_info.display_name + "::" + action_id
             except Exception as e:
                 action_name = "" #+ ":" +  action_id
                 continue 
          if ( action_type == "ONS" ):
             action_id = action.topic_id
             try:
                 action_info = ncpc.get_topic(action_id).data
                 action_name = action_info.name
             except Exception as e:
                 action_name = ""
                 continue 
          action_description = action.description  
          if ( i == 0 ): 
            if condition is not None:
               #print(condition)
               if "data" in condition:
                   data = str(condition["data"])
               else:
                   data = "{}"
               for val in condition["eventType"]:
                 if "oraclecloud" in val:
                   service = val.split("com.oraclecloud.")[1]
                 elif "oracle" in val:
                   service = val.split("com.oracle.")[1]
                 event_prod = service.split('.', 1)[0]
                 event_res = service.split('.', 1)[1]
                 if ( action_name != "" ):
                     events_rows(values_for_column_events, region, ntk_compartment_name, event_name, event_desc, action_type, action_is_enabled, action_description, event_prod, event_res,data,  event_is_enabled, action_name, event, event_info)
          if ( i > 0 and action_name != ""):
             events_rows(values_for_column_events, region, ntk_compartment_name, event_name, event_desc, action_type, action_is_enabled, action_description, event_prod, event_res,data,  event_is_enabled, action_name, event, event_info)
          i = i + 1
    if ( action_name != "" ):
       #importCommands[region.lower()].write("\nterraform import oci_events_rule." + tf_name + " " + str(event.id))
       importCommands[region.lower()].write("\nterraform import \"module.events[\\\"" + str(tf_name) + "\\\"].oci_events_rule.event\" " + str(event.id))

def events_rows(values_for_column_events, region, ntk_compartment_name, event_name, event_desc, action_type, action_is_enabled, action_description, event_prod, event_res,data,  event_is_enabled, action_name, event, event_info):
    for col_header in values_for_column_events.keys():
        if (col_header == "Region"):
            values_for_column_events[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_events[col_header].append(ntk_compartment_name)
        elif (col_header == "Event Name"):
            values_for_column_events[col_header].append(event_name)
        elif (col_header == "Event Description"):
            values_for_column_events[col_header].append(event_desc)
        elif (col_header == "Action Type"):
            values_for_column_events[col_header].append(action_type)
        elif (col_header == "Action is Enabled"):
            values_for_column_events[col_header].append(action_is_enabled)
        elif (col_header == "Action Description"):
            values_for_column_events[col_header].append(action_description)
        elif (col_header == "Service Name"):
            values_for_column_events[col_header].append(event_prod)
        elif (col_header == "Resource"):
            values_for_column_events[col_header].append(event_res)
        elif (col_header == "Additional Data") or (col_header == "AdditionalData"):
            values_for_column_events[col_header].append(data)
        elif (col_header == "Event is Enabled"):
            values_for_column_events[col_header].append(event_is_enabled)
        elif (col_header == "Topic"):
            values_for_column_events[col_header].append(action_name)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_events = commonTools.export_tags(event, col_header, values_for_column_events)
        else:
            oci_objs = [event,event_info]
            values_for_column_events = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_events,values_for_column_events)

# Execution for Events export starts here
def export_events(inputfile, outdir, service_dir, config, signer, ct,export_compartments=[], export_regions=[]):
    global rows
    global tf_import_cmd
    global values_for_column_events
    global values_for_column_notifications
    global sheet_dict_events
    global sheet_dict_notifications
    global importCommands

    sheetName = "Events"

    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_events = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict_events = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Events would be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
                commonTools.backup_file(outdir + "/" + reg +"/" + service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Events
    print("\nFetching Events...")
    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for Events #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        # comp_ocid_done = []
        ncpc = NotificationControlPlaneClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        fun = FunctionsManagementClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        evt = EventsClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        region = reg.capitalize()
        for ntk_compartment_name in export_compartments:
            evts = oci.pagination.list_call_get_all_results(evt.list_rules, compartment_id=ct.ntk_compartment_ids[
                ntk_compartment_name], lifecycle_state="ACTIVE")
            for event in evts.data:
                event_info = evt.get_rule(event.id).data
                print_events(values_for_column_events, region, ntk_compartment_name, event, event_info, ncpc, fun)
            ievts = oci.pagination.list_call_get_all_results(evt.list_rules, compartment_id=ct.ntk_compartment_ids[
                ntk_compartment_name], lifecycle_state="INACTIVE")
            for event in ievts.data:
                event_info = evt.get_rule(event.id).data
                print_events(values_for_column_events, region, ntk_compartment_name, event, event_info, ncpc, fun)

    commonTools.write_to_cd3(values_for_column_events, cd3file, sheetName)
    print("{0} Events exported into CD3.\n".format(len(values_for_column_events["Region"])))

    for reg in export_regions:
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')

# Execution for Notifications export starts here
def export_notifications(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[]):
    global rows
    global tf_import_cmd
    global values_for_column_events
    global values_for_column_notifications
    global sheet_dict_events
    global sheet_dict_notifications
    global importCommands

    sheetName = "Notifications"

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_notifications = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict_notifications = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Notifications would be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
                commonTools.backup_file(outdir + "/" + reg +"/" + service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Notifications & Subscriptions
    print("\nFetching Notifications - Topics & Subscriptions...")
    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for Notifications #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        ncpc = NotificationControlPlaneClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        ndpc = NotificationDataPlaneClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        fun = FunctionsManagementClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        region = reg.capitalize()
        for ntk_compartment_name in export_compartments:
                topics = oci.pagination.list_call_get_all_results(ncpc.list_topics,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])

                #sbpns = oci.pagination.list_call_get_all_results(ndpc.list_subscriptions,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
                for topic in topics.data:
                    #subscriptions get created in same comp as topic
                    sbpns = oci.pagination.list_call_get_all_results(ndpc.list_subscriptions,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],topic_id = topic.topic_id)
                    i=0
                    sbpn = None
                    for sbpn in sbpns.data:
                        i=i+1
                        print_notifications(values_for_column_notifications, region, ntk_compartment_name, sbpn,topic, i, fun)
                    # Empty Topic - No Subscription in the same compartment as Topic's
                    if(i==0):
                        print_notifications(values_for_column_notifications, region, ntk_compartment_name, sbpn, topic,i, fun)


                '''
                list_nftn = []
                i = 0
                for sbpn in sbpns.data:
                  try:
                   nftn_info = ncpc.get_topic(sbpn.topic_id).data
                  except:
                   continue
                  if( nftn_info.topic_id  not in list_nftn):
                     i = 1
                     list_nftn.append(nftn_info.topic_id)
                  else:
                     i = i + 1
                print_notifications(values_for_column_notifications,region, ntk_compartment_name, sbpn, nftn_info, i, fun)
                '''


    commonTools.write_to_cd3(values_for_column_notifications, cd3file, sheetName)
    print("{0} Notifications exported into CD3.\n".format(len(values_for_column_notifications["Region"])))


    for reg in export_regions:
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')

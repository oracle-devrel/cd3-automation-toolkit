#!/usr/bin/python3


import argparse
import sys
import oci
import re
from oci.identity import IdentityClient
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *


compartment_ids={}
importCommands={}

parser = argparse.ArgumentParser(description="Export Route Table on OCI to CD3")
parser.add_argument("cd3file", help="path of CD3 excel file to export network objects to")
parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Identity Objects", required=False)
parser.add_argument("--configFileName", help="Config file name" , required=False)

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
cd3file=args.cd3file
outdir=args.outdir
input_config_file=args.configFileName
input_compartment_list = args.networkCompartment
if(input_compartment_list is not None):
    input_compartment_names = input_compartment_list.split(",")
    input_compartment_names = [x.strip() for x in input_compartment_names]
else:
    input_compartment_names = None

if('.xls' not in cd3file):
    print("\nAcceptable cd3 format: .xlsx")
    exit()


if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

ct = commonTools()
ct.get_subscribedregions(configFileName)
ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

#Check Compartments
"""remove_comps=[]
if(input_compartment_names is not None):
    for x in range(0,len(input_compartment_names)):
        if(input_compartment_names[x] not in ntk_compartment_ids.keys()):
            print("Input compartment: "+ input_compartment_names[x]+" doesn't exist in OCI")
            remove_comps.append(input_compartment_names[x])

    input_compartment_names = [x for x in input_compartment_names if x not in remove_comps]
    if(len(input_compartment_names)==0):
        print("None of the input compartments specified exist in OCI..Exiting!!!")
        exit(1)
    else:
        print("Fetching for Compartments... "+str(input_compartment_names))
else:
    print("Fetching for all Compartments...")
"""
print("Fetching for all Compartments...")
print("\nCD3 excel file should not be opened during export process!!!")
print("Tabs- Compartments, Groups, Policies would be overwritten during export process!!!\n")

# Create backup
if(os.path.exists(outdir + "/" + ct.home_region+"/tf_import_commands_identity_nonGF.sh")):
    commonTools.backup_file(outdir + "/" + ct.home_region,"tf_import_commands_identity_nonGF.sh")
importCommands[ct.home_region] = open(outdir + "/" + ct.home_region+"/tf_import_commands_identity_nonGF.sh", "w")
importCommands[ct.home_region].write("#!/bin/bash")
importCommands[ct.home_region].write("\n")
importCommands[ct.home_region].write("terraform init")

config.__setitem__("region", ct.region_dict[ct.home_region])
idc=IdentityClient(config)

#Fetch Compartments
print("\nFetching Compartments...")
rows=[]
importCommands[ct.home_region].write("\n######### Writing import for Compartments #########\n")
"""if (input_compartment_names is not None):
    for input_comp_name in input_compartment_names:
        if(input_comp_name=='root'):
            continue
        parent_input_comp_name=""
    
        while parent_input_comp_name!="root":
            input_comp_id = ntk_compartment_ids[input_comp_name]
            input_comp_info = idc.get_compartment(compartment_id=input_comp_id).data

            for k, v in ntk_compartment_ids.items():
                if (v == input_comp_info.compartment_id):
                        parent_input_comp_name = k
                        
            if(parent_input_comp_name!="root"):
                tf_name = parent_input_comp_name+"::"+input_comp_info.name
            else:
                tf_name=input_comp_info.name
            tf_name= commonTools.check_tf_variable(tf_name)
            importCommands[ct.home_region].write("\nterraform import oci_identity_compartment." + tf_name + " " + input_comp_id)
            new_row = (ct.home_region.capitalize(), input_comp_name, input_comp_info.description, parent_input_comp_name)
            rows.append(new_row)
            if(parent_input_comp_name=='root'):
                break
            else:
                input_comp_name=parent_input_comp_name


else:
"""
comps = oci.pagination.list_call_get_all_results(idc.list_compartments,compartment_id=config['tenancy'],compartment_id_in_subtree=True)
for comp in comps.data:
    comp_info = comp
    if (comp_info.lifecycle_state == "ACTIVE"):
        comp_display_name = comp_info.name
        comp_desc = comp_info.description
        parent_comp_id = comp_info.compartment_id

        keys = []
        for k,v in ct.ntk_compartment_ids.items():
            if(v==parent_comp_id):
                keys.append(k)
        if(len(keys)>1):
            for key in keys:
                if("::" in key):
                    parent_comp_name=key
        else:
            parent_comp_name=keys[0]

        if (parent_comp_name != "root"):
            tf_name=parent_comp_name+"::"+comp_display_name
        else:
            tf_name=comp_display_name

        tf_name = commonTools.check_tf_variable(tf_name)
        importCommands[ct.home_region].write("\nterraform import oci_identity_compartment." + tf_name + " " + comp_info.id)
        new_row = (ct.home_region.capitalize(), comp_display_name, comp_desc, parent_comp_name)
        rows.append(new_row)

commonTools.write_to_cd3(rows,cd3file,"Compartments")
print("Compartments exported to CD3\n")

#Fetch Groups
print("\nFetchig Groups...")
rows=[]
importCommands[ct.home_region].write("\n######### Writing import for Groups #########\n")
groups = oci.pagination.list_call_get_all_results(idc.list_groups,compartment_id=config['tenancy'])
for group in groups.data:
    grp_info=group
    if(grp_info.lifecycle_state == "ACTIVE"):
        grp_display_name=grp_info.name
        grp_desc=grp_info.description
        tf_name=commonTools.check_tf_variable(grp_display_name)
        importCommands[ct.home_region].write("\nterraform import oci_identity_group."+ tf_name+" "+grp_info.id)
        new_row = (ct.home_region.capitalize(), grp_display_name, grp_desc)
        rows.append(new_row)

commonTools.write_to_cd3(rows,cd3file,"Groups")
print("Groups exported to CD3\n")

# Fetch Policies
rows=[]
print("\nFetchig Policies...")
importCommands[ct.home_region].write("\n\n######### Writing import for Policies #########\n\n")
comp_ocid_done = []
for ntk_compartment_name in ct.ntk_compartment_ids:
    if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
        comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
    #if(input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
    #    continue
        policies = oci.pagination.list_call_get_all_results(idc.list_policies, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
        for policy in policies.data:
            policy_name=policy.name
            policy_desc=policy.description
            policy_comp_id=policy.compartment_id
            if (policy_comp_id == config['tenancy']):
                policy_comp = 'root'
            else:
                keys = []
                for k, v in ct.ntk_compartment_ids.items():
                    if (v == policy_comp_id):
                        keys.append(k)

                if (len(keys) > 1):
                    for key in keys:
                        if ("::" in key):
                            policy_comp = key
                else:
                    policy_comp = keys[0]

            if (policy_comp != "root"):
                tf_name = policy_comp+"_"+policy_name
            else:
                tf_name = policy_name

                #policy_comp=idc.get_compartment(policy.compartment_id).data.name


            tf_name = commonTools.check_tf_variable(tf_name)
            importCommands[ct.home_region].write("\nterraform import oci_identity_policy." + tf_name + " " + policy.id)

            count=1
            policy_statements = policy.statements
            for stmt in policy_statements:
                #Commented as statement case was changing
                """if(" compartment " in stmt.lower()):
                    policy_compartment_name=stmt.lower().split(" compartment ")[1].split()[0]
                    stmt=re.sub(r'%s([\s]|$)'%policy_compartment_name, r'* ', stmt.lower())
                elif(" tenancy" in stmt.lower()):
                    policy_compartment_name=''
    
                if(" group " in stmt.lower()):
                    policy_grp_name=stmt.lower().split(" group ")[1].split()[0]
                    stmt=re.sub(r'%s([\s]|$)'%policy_grp_name, r'$ ', stmt.lower())
                else:
                    policy_grp_name=""
                """
                if(count==1):
                    #new_row = (ct.home_region.capitalize(), policy_name, policy_comp,policy_desc,stmt,policy_grp_name,policy_compartment_name)
                    new_row = (ct.home_region.capitalize(), policy_name, policy_comp, policy_desc, stmt, '','')
                else:
                    #new_row = ('', '','', '', stmt, policy_grp_name, policy_compartment_name)
                    new_row = ('', '', '', '', stmt, '', '')
                count=count+1
                rows.append(new_row)

commonTools.write_to_cd3(rows,cd3file,"Policies")
print("Policies exported to CD3\n")

importCommands[ct.home_region] = open(outdir + "/" + ct.home_region + "/tf_import_commands_identity_nonGF.sh", "a")
importCommands[ct.home_region].write("\n\nterraform plan")
importCommands[ct.home_region].write("\n")
importCommands[ct.home_region].close()

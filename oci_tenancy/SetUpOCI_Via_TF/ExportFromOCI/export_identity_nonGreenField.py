#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script is to export Identity Objects from OCI
#put them into CD3 Excel and create TF files

#Author: Suruchi
#Oracle Consulting
#

import argparse
import sys
import oci
import re
from oci.identity import IdentityClient
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *

def main():
    parser = argparse.ArgumentParser(description="Export Route Table on OCI to CD3")
    parser.add_argument("cd3file", help="path of CD3 excel file to export network objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Identity Objects", required=False)
    parser.add_argument("--configFileName", help="Config file name" , required=False)

    global values_for_column_comps
    global values_for_column_groups
    global values_for_column_policies
    global sheet_dict_comps
    global sheet_dict_groups
    global sheet_dict_policies
    global config
    global cd3file

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    cd3file=args.cd3file
    outdir=args.outdir
    input_compartment_list = args.networkCompartment

    if('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()


    if args.configFileName is not None:
        configFileName = args.configFileName
        config = oci.config.from_file(file_location=configFileName)
    else:
        configFileName=""
        config = oci.config.from_file()

    importCommands={}

    # Read CD3 Identity Sheets
    df, values_for_column_comps = commonTools.read_cd3(cd3file, "Compartments")
    df, values_for_column_groups = commonTools.read_cd3(cd3file, "Groups")
    df, values_for_column_policies = commonTools.read_cd3(cd3file, "Policies")

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Get dict for columns from Excel_Columns
    sheet_dict_comps = ct.sheet_dict["Compartments"]
    sheet_dict_groups = ct.sheet_dict["Groups"]
    sheet_dict_policies = ct.sheet_dict["Policies"]

    print("Fetching for all Compartments...")
    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Compartments, Groups, Policies would be overwritten during export process!!!\n")

    # Create backup
    if(os.path.exists(outdir + "/" + ct.home_region+"/tf_import_commands_identity_nonGF.sh")):
        commonTools.backup_file(outdir + "/" + ct.home_region,"tf_import_identity","tf_import_commands_identity_nonGF.sh")
    importCommands[ct.home_region] = open(outdir + "/" + ct.home_region+"/tf_import_commands_identity_nonGF.sh", "w")
    importCommands[ct.home_region].write("#!/bin/bash")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].write("terraform init")

    config.__setitem__("region", ct.region_dict[ct.home_region])
    idc=IdentityClient(config)

    #Fetch Compartments
    print("\nFetching Compartments...")
    importCommands[ct.home_region].write("\n######### Writing import for Compartments #########\n")

    comp_ocids_done=[]
    for c_name, c_id in ct.ntk_compartment_ids.items():
        c_details=idc.get_compartment(c_id).data

        #write child comps info
        if("::" in c_name):
            c_names=c_name.rsplit("::", 1)
            comp_display_name = c_names[1]
            comp_parent_name = c_names[0]
            tf_name = commonTools.check_tf_variable(c_name)
            importCommands[ct.home_region].write("\nterraform import oci_identity_compartment." + tf_name + " " + c_id)

        #write parent comp info(at root)
        else:
            parent_c_id = c_details.compartment_id
            # if it root compartment
            if(parent_c_id==ct.ntk_compartment_ids["root"]):
                comp_display_name=c_name
                comp_parent_name = "root"
                tf_name = commonTools.check_tf_variable(c_name)
                importCommands[ct.home_region].write("\nterraform import oci_identity_compartment." + tf_name + " " + c_id)
            else:
                continue
        if(c_id not in comp_ocids_done):
            comp_ocids_done.append(c_id)
            for col_header in values_for_column_comps.keys():
                if(col_header == "Region"):
                    values_for_column_comps[col_header].append(ct.home_region.capitalize())
                elif(col_header == "Name"):
                    values_for_column_comps[col_header].append(comp_display_name)
                elif(col_header == "Parent Compartment"):
                    values_for_column_comps[col_header].append(comp_parent_name)
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_comps = commonTools.export_tags(c_details, col_header, values_for_column_comps)
                else:
                    oci_objs=[c_details]
                    values_for_column_comps=commonTools.export_extra_columns(oci_objs,col_header,sheet_dict_comps,values_for_column_comps)

    commonTools.write_to_cd3(values_for_column_comps,cd3file,"Compartments")
    print("Compartments exported to CD3\n")

    #Fetch Groups
    print("\nFetchig Groups...")
    importCommands[ct.home_region].write("\n######### Writing import for Groups #########\n")
    groups = oci.pagination.list_call_get_all_results(idc.list_groups,compartment_id=config['tenancy'])
    for group in groups.data:
        grp_info=group
        if(grp_info.lifecycle_state == "ACTIVE"):
            grp_display_name=grp_info.name
            tf_name=commonTools.check_tf_variable(grp_display_name)
            importCommands[ct.home_region].write("\nterraform import oci_identity_group."+ tf_name+" "+grp_info.id)
            for col_header in values_for_column_groups.keys():
                if (col_header == "Region"):
                    values_for_column_groups[col_header].append(ct.home_region.capitalize())
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_groups = commonTools.export_tags(grp_info, col_header, values_for_column_groups)
                else:
                    oci_objs=[grp_info]
                    values_for_column_groups = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_groups,values_for_column_groups)

    commonTools.write_to_cd3(values_for_column_groups,cd3file,"Groups")
    print("Groups exported to CD3\n")

    # Fetch Policies
    print("\nFetchig Policies...")
    importCommands[ct.home_region].write("\n\n######### Writing import for Policies #########\n\n")
    comp_ocid_done = []
    for ntk_compartment_name in ct.ntk_compartment_ids:
        if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
            policies = oci.pagination.list_call_get_all_results(idc.list_policies, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
            for policy in policies.data:
                policy_name=policy.name
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
                        for col_header in values_for_column_policies.keys():
                            if (col_header == "Region"):
                                values_for_column_policies[col_header].append(ct.home_region.capitalize())
                            elif (col_header == "Compartment Name"):
                                values_for_column_policies[col_header].append(policy_comp)
                            elif (col_header == "Policy Statement Compartment"):
                                values_for_column_policies[col_header].append("")
                            elif (col_header == "Policy Statement Groups"):
                                values_for_column_policies[col_header].append("")
                            elif(col_header == "Policy Statements"):
                                values_for_column_policies[col_header].append(stmt)
                            elif col_header.lower() in commonTools.tagColumns:
                                values_for_column_policies = commonTools.export_tags(policy, col_header,values_for_column_policies)
                            else:
                                oci_objs=[policy]
                                values_for_column_policies = commonTools.export_extra_columns(oci_objs, col_header,sheet_dict_policies,values_for_column_policies)
                    else:
                        for col_header in values_for_column_policies.keys():
                            if (col_header == "Policy Statements"):
                                values_for_column_policies[col_header].append(stmt)
                            else:
                                values_for_column_policies[col_header].append("")

                    count=count+1

    commonTools.write_to_cd3(values_for_column_policies,cd3file,"Policies")
    print("Policies exported to CD3\n")

    importCommands[ct.home_region] = open(outdir + "/" + ct.home_region + "/tf_import_commands_identity_nonGF.sh", "a")
    importCommands[ct.home_region].write("\n\nterraform plan")
    importCommands[ct.home_region].write("\n")
    importCommands[ct.home_region].close()
    if ("linux" in sys.platform):
        dir = os.getcwd()
        os.chdir(outdir + "/" + ct.home_region)
        os.system("chmod +x tf_import_commands_identity_nonGF.sh")
        os.chdir(dir)


if __name__=="__main__":
    main()

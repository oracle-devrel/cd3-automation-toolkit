#!/usr/bin/python3
# Copyright (c) 2024 Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export budgets
#
#Author: Bhanu P. Lohumi
#Oracle Consulting
#
import sys
import oci
import os
import subprocess as sp

from commonTools import *

sys.path.append(os.getcwd()+"/..")

compartment_ids={}
importCommands={}
tf_name_namespace_list = []

def print_budgets(values_for_columns, region, budget,budget_name,budget_alert_rule,ct):

    comp_id_list = list(ct.ntk_compartment_ids.values())
    comp_name_list = list(ct.ntk_compartment_ids.keys())
    for col_header in values_for_columns.keys():
        if (col_header == "Region"):
            value = region if budget else ""
            values_for_columns[col_header].append(value)

        elif (col_header == "Name"):
            value = budget_name if budget else ""
            values_for_columns[col_header].append(value)

        if (col_header == "Description"):
            value = budget.description if budget else ""
            values_for_columns[col_header].append(value)
        elif (col_header == "Scope"):
            value = budget.target_type if budget else ""
            values_for_columns[col_header].append(value)

        elif col_header == "Target":
            targets = ""
            if budget:
                for target in budget.targets :
                    if budget.target_type == "COMPARTMENT":
                        target = comp_name_list[comp_id_list.index(target)] if target in comp_id_list else target
                    targets+= "," + target

            values_for_columns[col_header].append(targets[1:])
        elif (col_header == "Schedule"):
            value = budget.processing_period_type if budget else ""
            values_for_columns[col_header].append(value)

        elif (col_header == "Amount"):
            value = budget.amount if budget else ""
            values_for_columns[col_header].append(value)

        elif (col_header == "Start Day"):
            start_day = ""
            if budget and budget.processing_period_type == "MONTH":
                start_day = str(budget.budget_processing_period_start_offset)
            values_for_columns[col_header].append(start_day)

        elif (col_header == "Budget Start Date"):
            budget_start_date = ""
            if budget and budget.processing_period_type == "SINGLE_USE":
                budget_start_date = (budget.start_date).strftime("%Y-%m-%d")
            values_for_columns[col_header].append(budget_start_date)


        elif (col_header == "Budget End Date"):
            budget_end_date = ""
            if budget and budget.processing_period_type == "SINGLE_USE":
                budget_end_date = (budget.end_date).strftime("%Y-%m-%d")
            values_for_columns[col_header].append(budget_end_date)


        elif col_header.lower() in commonTools.tagColumns:
            if budget:
                values_for_columns = commonTools.export_tags(budget, col_header, values_for_columns)
            else:
                values_for_columns[col_header].append("")


        if (col_header == "Alert Rules"):
            alert_rule = ""
            if budget_alert_rule:
                alert_rule = str(budget_alert_rule.type)+"::"+str(budget_alert_rule.threshold)
                if budget_alert_rule.threshold_type == "PERCENTAGE":
                    alert_rule += "%"
            values_for_columns[col_header].append(alert_rule)
        elif (col_header == "Alert Recipients"):
            recipients = ""
            if budget_alert_rule:
                recipients = str(budget_alert_rule.recipients) if budget_alert_rule.recipients else ""
            values_for_columns[col_header].append(recipients)
        elif col_header == "Alert Message":
            message = ""
            if budget_alert_rule:
                message = str(budget_alert_rule.message) if budget_alert_rule.message else ""
            values_for_columns[col_header].append(message)



# Execution of the code begins here
def export_budgets_nongreenfield(inputfile, outdir, service_dir, config, signer, ct,export_regions=[],export_tags=[]):
    global importCommands
    global values_for_column_budgets
    global sheet_dict_budgets,tf_or_tofu

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    cd3file = inputfile
    total_resources = 0
    budget_done = []

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_budgets = commonTools.read_cd3(cd3file, "Budgets")

    # Get dict for columns from Excel_Columns
    sheet_dict_budgets = ct.sheet_dict["Budgets"]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- budgets would be overwritten during export process!!!\n")

    # Fetch budgets
    print("\nFetching budgets...")

    for reg in [ct.home_region]:
        importCommands = ""
        region = reg.lower()
        script_file = f'{outdir}/{region}/{service_dir}/import_commands_budgets.sh'
        # Create backups
        if os.path.exists(script_file):
            commonTools.backup_file(os.path.dirname(script_file), "import_budgets", os.path.basename(script_file))

        config.__setitem__("region", ct.region_dict[region])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        tenancy_id = config["tenancy"]
        budgets_client = oci.budget.BudgetClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)


        budgets_list = oci.pagination.list_call_get_all_results(budgets_client.list_budgets,compartment_id=tenancy_id,lifecycle_state="ACTIVE",target_type="ALL")
        if budgets_list.data != []:
            for budget in budgets_list.data:

                # Tags filter
                defined_tags = budget.defined_tags
                tags_list = []
                for tkey, tval in defined_tags.items():
                    for kk, vv in tval.items():
                        tag = tkey + "." + kk + "=" + vv
                        tags_list.append(tag)

                if export_tags == []:
                    check = True
                else:
                    check = any(e in tags_list for e in export_tags)
                # None of Tags from export_tags exist on this instance; Dont export this instance
                if check == False:
                    continue

                budget_name = str(budget.display_name)
                budget_id = str(budget.id)
                budget_tf_name = commonTools.check_tf_variable(budget_name)
                budget_alert_rules = budgets_client.list_alert_rules(budget_id=budget.id)
                if budget_alert_rules.data:
                    for budget_alert_rule in budget_alert_rules.data:
                        total_resources += 1
                        alert_tf_name = budget_tf_name+"_"+commonTools.check_tf_variable(str(budget_alert_rule.type) + "_"+str(budget_alert_rule.threshold_type) +"_"+  str(budget_alert_rule.threshold))
                        alert_id = "budgets/"+budget_id+"/alertRules/"+str(budget_alert_rule.id)
                        if budget_tf_name in budget_done :
                            budget = []
                        print_budgets(values_for_column_budgets, region, budget,budget_name,budget_alert_rule,ct)
                        budget_done.append(budget_tf_name)
                        tf_resource = f'module.budget-alert-rules[\\"{alert_tf_name}\\"].oci_budget_alert_rule.alert_rule'
                        if tf_resource not in state["resources"]:
                            importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {alert_id}'

                else:
                    print_budgets(values_for_column_budgets, region, budget,budget.display_name, budget_alert_rules.data, ct)
                    total_resources += 1

                tf_resource = f'module.budgets[\\"{budget_tf_name}\\"].oci_budget_budget.budget'
                if tf_resource not in state["resources"]:
                    importCommands += f'\n{tf_or_tofu} import "{tf_resource}" {budget_id}'


        init_commands = f'\n######### Writing import for Budgets #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands != "":
            importCommands += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands)


    commonTools.write_to_cd3(values_for_column_budgets, cd3file, "Budgets")
    print("{0} rows exported into CD3 for Budgets and Budget alert-rules.\n".format(total_resources))

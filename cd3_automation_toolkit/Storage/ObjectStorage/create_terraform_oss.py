#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Object Storage Bucket
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade):Ranjini Rajendran
#
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######

# Execution of the code begins here
def create_terraform_oss(inputfile, outdir, service_dir, prefix, ct):

    # Declare variables
    filename = inputfile
    prefix = prefix
    outdir = outdir

    #Get subscribed regions and home region

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader = file_loader, keep_trailing_newline = True, trim_blocks = True, lstrip_blocks = True)
    oss_template = env.get_template('oss-template')

    #define the excel sheet details
    sheetName = "Buckets"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how = 'all')
    df = df.reset_index(drop = True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    #Declare dictionaries
    outfile = {}
    oname = {}
    tfStr = {}

    # Initialise empty TF string for each region to take backup of files
    for eachregion in ct.all_regions:
        tfStr[eachregion] = ''
        srcdir = outdir + "/" + eachregion + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(srcdir + "/", resource, auto_tfvars_filename)

    #Declaration
    bucket_lifecycle_policy = {}
    bucket_done = []
    lf_list = []
    prev_region = ""

    # loop for lifecycle policy
    for r in df.index:
        lifecycle_rule = {}
        bucket_var_name = str(df.loc[r, 'Bucket Name']).strip()
        region = (str(df.loc[r, 'Region']).strip()).lower()
        l_key = region + '_' + bucket_var_name

        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if l_key not in bucket_done:
            lf_list = []

        # Lifecycle Policy details
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df.loc[r, columnname]).strip()

            # Check for boolean/null in column values
            if (columnname == 'exclusion_patterns') or (columnname == 'inclusion_patterns') or (columnname == 'inclusion_prefixes'):
                columnvalue = columnvalue.replace("nan", "")
            else:
                columnvalue = commonTools.check_columnvalue(columnvalue)

            if columnname == 'Lifecycle Policy Name':
                if columnvalue != "":
                    lifecycle_policy_name = columnvalue
                    lifecycle_rule['name'] = lifecycle_policy_name
                else:
                    lifecycle_rule['name'] = ""

            if columnname == 'Lifecycle Target and Action':
                    tgt_action_map = columnvalue
                    tgt_map = tgt_action_map.split("::")
                    if len(tgt_map) == 2:
                        target = tgt_map[0].lower()
                        action = tgt_map[1].upper()
                        lifecycle_rule['target'] = target
                        lifecycle_rule['action'] = action

            if columnname == 'Lifecycle Policy Enabled':
                    is_enabled = columnvalue.lower()
                    lifecycle_rule['is_enabled'] = is_enabled

            if columnname == 'Lifecycle Rule Period':
                    columnvalue = columnvalue.upper()
                    columnvalue = columnvalue.split("::")
                    if len(columnvalue) == 2:
                        time_amount = columnvalue[0]
                        time_unit = columnvalue[1].lower()
                        # Check that time_unit is an integer
                        if not time_amount.isdigit():
                            print("\nERROR!!! Invalid time unit. Must be an integer value. Lifecycle policy will not be processed")

                        # Check that time_amount is either "days" or "years"
                        if time_unit not in ["days", "years"]:
                            print("\nERROR!!! Invalid time amount. Must be 'days' or 'years'.Lifecycle policy will not be processed")

                        lifecycle_rule['time_amount'] = time_amount
                        lifecycle_rule['time_unit'] = time_unit.upper()

            if columnname == 'Lifecyle Exclusion Patterns' and columnvalue != "":
                exclusion_patterns = columnvalue.lower()
                lifecycle_rule['exclusion_patterns'] = exclusion_patterns

            if columnname == 'Lifecyle Inclusion Patterns' and columnvalue != "":
                inclusion_patterns = columnvalue.lower()
                lifecycle_rule['inclusion_patterns'] = inclusion_patterns

            if columnname == 'Lifecyle Inclusion Prefixes' and columnvalue != "":
                inclusion_prefixes = columnvalue.lower()
                lifecycle_rule['inclusion_prefixes'] = inclusion_prefixes


        lf_list.append(lifecycle_rule)
        if l_key not in bucket_done:
            bucket_done.append(l_key)
            bucket_lifecycle_policy[l_key] = lf_list
        else:
            bucket_lifecycle_policy[l_key].append(lf_list)

    # loop for bucket

    for i in df.index:

        region = (str(df.loc[i, 'Region']).strip()).lower()
        compartment_var_name = str(df.loc[i, 'Compartment Name']).strip()
        bucket_var_name = str(df.loc[i, 'Bucket Name']).strip()
        bucket_key = region + "_" + bucket_var_name

        if region != prev_region:
            bucket_done =[]
        prev_region = region

        # Encountered <End>
        if region in commonTools.endNames:
            break

        # If some invalid region is specified
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields

        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Bucket Name']).lower() == 'nan':
            print("\nThe values for Region, Compartment Name and Bucket Name cannot be left empty. Please enter a value and try again !!")
            exit(1)

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df.loc[i, columnname]).strip()

            # Check for boolean/null in column values
            if (columnname == 'exclusion_patterns') or (columnname == 'inclusion_patterns') or (columnname == 'inclusion_prefixes'):
                columnvalue = columnvalue.replace("nan", "")
            else:
                columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            #Compartment name
            if columnname == "Compartment Name":
                compartmentname = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentname = commonTools.check_tf_variable(compartmentname)
                columnvalue = str(compartmentname)
                tempdict = {'compartment_tf_name': columnvalue}

            if columnname == "Bucket Name":
                bucket_name = columnvalue.strip()
                bucket_name = commonTools.check_tf_variable(str(bucket_name))
                tempdict = {'bucket_tf_name': bucket_name, 'bucket_name' : columnvalue.strip()}

            if columnname == "Storage Tier":
                storage_tier = columnvalue.strip()
                storage_tier = str(storage_tier)
                tempdict = {'storage_tier': storage_tier}

            if columnname == "Auto Tiering":
                auto_tiering = columnvalue.strip()
                if auto_tiering == "Enabled":
                    auto_tiering = "InfrequentAccess"
                tempdict = {'auto_tiering': auto_tiering}

            if columnname == "Object Versioning":
                versioning = columnvalue.strip()
                versioning = str(versioning)
                tempdict = {'versioning': versioning}

            if columnname == "Emit Object Events":
                object_events_enabled = columnvalue.strip()
                if object_events_enabled == "Enabled":
                    object_events_enabled = "true"
                else:
                    object_events_enabled = "false"
                tempdict = {'object_events_enabled': object_events_enabled}

            if columnname == "Visibility":
                access_type = columnvalue.strip()
                if access_type == "Private":
                    access_type = "NoPublicAccess"
                else:
                    access_type = "ObjectRead"
                tempdict = {'access_type': access_type}

            # Retention Rule details
            if columnname == 'Retention Rules' and columnvalue != "":
                columnvalue = str(df[columnname][i])
                rule_values = columnvalue.split("\n")
                retention_rules = []
                for rule in rule_values:
                    rule_components = rule.split("::")
                    if len(rule_components) >= 1:
                        retention_rule_display_name = rule_components[0]
                        time_unit = None
                        time_amount = None
                        time_rule_locked = None

                        if len(rule_components) >= 2:
                            if rule_components[1].lower() == 'indefinite':
                                time_amount = None
                            else:
                                time_amount = rule_components[1]
                                if not time_amount.isdigit():
                                    print(
                                        f"'{time_amount}' is not a valid time amount. It should be an integer or 'indefinite'. The retention rules will not be processed.")
                                    continue
                                else:
                                    time_amount = int(time_amount)

                        if len(rule_components) >= 3:
                            time_unit = rule_components[2].upper()
                            if time_unit not in ('DAYS', 'YEARS'):
                                print(
                                    f"'{time_unit}' is not a valid time unit. It should be either 'DAYS' or 'YEARS'. The retention rules will not be processed.")
                                continue

                        if len(rule_components) == 4:
                            time_rule_locked = rule_components[3]
                            if time_rule_locked.endswith(".000Z"):
                                time_rule_locked = time_rule_locked[:-5] + "Z"
                            elif not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*Z",time_rule_locked):
                                # Convert from "dd-mm-yyyy" to "YYYY-MM-DDThh:mm:ssZ" format
                                if re.match(r"\d{2}-\d{2}-\d{4}", time_rule_locked):
                                    try:
                                        datetime_obj = datetime.datetime.strptime(time_rule_locked, "%d-%m-%Y")
                                        time_rule_locked = datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                                    except ValueError:
                                        print(
                                            f"'{time_rule_locked}' is not in the correct format. It should be in the format 'dd-mm-yyyy'. The retention rules will not be processed.")
                                        continue
                                '''
                                else:
                                    print(
                                        f"'{time_rule_locked}' is not in the correct format. It should be in the format of 'YYYY-MM-DDThh:mm:ssZ' or 'YYYY-MM-DDThh:mm:ss.fffZ'. The retention rules will not be processed.")
                                    continue
                                '''

                        tempdict = {'retention_rule_display_name': retention_rule_display_name,
                                    'time_unit': time_unit,
                                    'time_amount': time_amount,
                                    'time_rule_locked': time_rule_locked}
                        retention_rules.append(tempdict)
                    else:
                        print(
                            f"'{rule}' is not a valid Retention Rule. It should be in the format of 'rulename::timeunit::timeamount::time_rule_locked'.")
                tempdict = {'retention_rules': retention_rules}

            #Replication Policy details
            if columnname == 'Replication Policy' and columnvalue !="":
                columnvalue = str(df[columnname][i])
                columnvalue= columnvalue.split("::")
                if len(columnvalue) == 3 and all(columnvalue):
                 replication_policy_name = columnvalue[0]
                 destination_region = columnvalue[1].lower()
                 if destination_region in ct.region_dict:
                     destination_region = ct.region_dict[destination_region]
                 else:
                     raise ValueError(f"{destination_region} is not a valid destination region.")

                 destination_bucket = columnvalue[2]
                 tempdict = {'replication_policy_name':replication_policy_name,'destination_region':destination_region , 'destination_bucket' : destination_bucket}

            if bucket_lifecycle_policy[bucket_key] != []:
                LF_Rule = bucket_lifecycle_policy[bucket_key]
                tempdict['lifecycle_rules'] = LF_Rule

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        #Write all info to TF string

        if bucket_var_name not in bucket_done:
          tfStr[region] = tfStr[region] + oss_template.render(tempStr)
          bucket_done.append(bucket_var_name)

    for reg in ct.all_regions:
        srcdir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(srcdir):
            os.makedirs(srcdir)
        outfile[reg] = srcdir + "/" + auto_tfvars_filename

        if(tfStr[reg]!=''):
            src = "##Add New OSS Buckets for " + reg.lower() + " here##"
            tfStr[reg] = oss_template.render(count = 0, region = reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])


            oname[reg]=open(outfile[reg],'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " for Buckets has been created for region "+reg)

    print("\nEnsure that for the creation of replication policy, the destination bucket already exists in OCI tenancy")

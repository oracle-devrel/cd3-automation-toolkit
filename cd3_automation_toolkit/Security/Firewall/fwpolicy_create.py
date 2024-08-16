#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# policy, Listeners
#
# Author: Suruchi Singla
# Oracle Consulting
#
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader
import os

######
# Required Inputs-CD3 excel file, Config file AND outdir
######

# Execution of the code begins here
def firewallpolicy_create(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    policy = env.get_template('firewall-policies-template')


    sheetName = "Firewall-Policy"
    policy_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile


    policy_str = {}
    outfile = {}
    oname = {}
    policy_tf_name = ''
    policy_name = ''
    policy_names = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        policy_str[reg] = ''
        policy_names[reg] = []
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, policy_auto_tfvars_filename)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    region_seen_so_far = []
    region_list = []
    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()
        if region.lower() != 'nan' and region in ct.all_regions:
            region = region.strip().lower()
            if region not in region_seen_so_far:
                region_list.append(region)
                region_seen_so_far.append(region)
        if region in commonTools.endNames:
            break
        if region != 'nan' and region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the regions tenancy is subscribed to...Exiting!!")
            exit()
        # temporary dictionaries
        tempStr= {}
        tempdict= {}

        # Fetch data; loop through columns
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Compartment Name":
                columnname = "compartment_tf_name"
                columnvalue = commonTools.check_tf_variable(columnvalue)


            if columnname == "Policy Name":
                policy_tf_name = commonTools.check_tf_variable(columnvalue)
                policy_name = columnvalue
                tempdict = {'policy_tf_name': policy_tf_name}


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if (region != 'nan' and policy_name not in policy_names[region]):
            policy_names[region].append(policy_name)
            policy_str[region] = policy_str[region] + policy.render(tempStr)

    for reg in region_list:

        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + policy_auto_tfvars_filename

        if policy_str[reg] != '':
            # Generate Final String
            src = "##Add New firewall policy for " + reg.lower() + " here##"
            policy_str[reg] = policy.render(count=0, region=reg).replace(src, policy_str[reg] + "\n" + src)
            policy_str[reg] = "".join([s for s in policy_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            policy_str[reg] = "\n\n" + policy_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(policy_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall policy has been updated for region " + reg)

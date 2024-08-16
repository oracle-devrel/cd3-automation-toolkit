#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# firewall, Listeners
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
def fwpolicy_create_applicationlist(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print(inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    applicationlist = env.get_template('policy-applicationlists-template')


    sheetName = "Firewall-Policy-ApplicationList"
    applicationlist_auto_tfvars_filename = prefix + "_firewall-policy-applicationlist.auto.tfvars"
    filename = inputfile


    outfile = {}
    oname = {}
    applicationlist_tf_name = ''
    applicationlist_str = {}
    applicationlist_names = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        applicationlist_str[reg] = ''
        applicationlist_names[reg] = []
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, applicationlist_auto_tfvars_filename)


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
        port_ranges = ''
        ip_id = ''

        # Fetch data; loop through columns
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)


            if columnname == "Firewall Policy":
                policy_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'policy_tf_name': policy_tf_name}

            if columnname == "Application List":
                applicationlist_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'applicationlist_tf_name': applicationlist_tf_name,'applicationlist_name':columnvalue}

            data = ""
            if columnname == 'Applications':
                if columnvalue != '':

                    apps = columnvalue.strip().split("\n")
                    if len(apps) == 1:
                        for app in apps:
                            app = app.split("::")
                            applicationlist_name =  app[0]
                            data = "\"" + applicationlist_name.strip() + "\""
                            tempdict = {'apps_tf_name': data}


                    elif len(apps) >= 2:
                        c = 1

                        apps1 = ''
                        for app in apps:
                            if c <= len(apps):
                                app = app.split("::")
                                applicationlist_name = app[0]

                                #applicationlist.append(service_name)
                                data = "\"" + applicationlist_name.strip() + "\""
                                if c == len(apps):
                                    apps1 = apps1 + data
                                else:
                                    apps1 = apps1 + data + ","
                            tempdict = {'apps_tf_name': apps1}
                            c += 1

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        applicationlist_str[region] = applicationlist_str[region] + applicationlist.render(tempStr)

    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + applicationlist_auto_tfvars_filename

        if applicationlist_str[reg] != '':
            # Generate Final String
            src = "##Add New application list for " + reg.lower() + " here##"
            applicationlist_str[reg] = applicationlist.render(count=0, region=reg).replace(src, applicationlist_str[reg] + "\n" + src)
            applicationlist_str[reg] = "".join([s for s in applicationlist_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            applicationlist_str[reg] = "\n\n" + applicationlist_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(applicationlist_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall policy application lists has been updated for region " + reg)


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
def fwpolicy_create_apps(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    applications = env.get_template('policy-apps-template')


    sheetName = "Firewall-Policy-ApplicationList"
    apps_auto_tfvars_filename = prefix + "_firewall-policy-application.auto.tfvars"

    filename = inputfile

    apps_seen_so_far = set()
    outfile = {}
    oname = {}
    apps_tf_name = ''
    service_name = ''
    policy_name = ''
    apps_str = {}
    apps_names = {}
    apps_str_02 = {}
    policy_names = {}
    ip_id = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        apps_str[reg] = ''
        apps_names[reg] = []
        apps_str_02[reg] = ''
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, apps_auto_tfvars_filename)


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
                tempdict = {'applicationlist_tf_name': applicationlist_tf_name}

            port = []
            box1 = '[{\n    minimum_port ="'
            box11 = '  \n  {\n    minimum_port ="'
            box2 = '"\n    maximum_port ="'
            box3 = '"\n  },'
            box33 = '"\n  }]'
            app_name = ''
            icmp_type = ''
            icmp_code = ''
            app_type = ''
            if columnname == 'Applications':
                if columnvalue != '':
                    apps_str[region] = ''
                    apps = columnvalue.strip().split("\n")
                    if len(apps) == 1:
                        #print("you are here")
                        for app in apps:
                            region_app = app + "--" + region + "--" + policy_tf_name
                            if region_app not in apps_seen_so_far:
                                apps_seen_so_far.add(region_app)
                                app = app.split("::")
                                app_name = app[0]
                                app_type = app[1]
                                icmp_type = app[2]
                                if len(app) == 4:
                                    icmp_code = app[3]
                                else:
                                    icmp_code = ''
                                tempdict = {'app_name': app_name, 'app_tf_name': commonTools.check_tf_variable(app_name),'app_type': app_type, 'icmp_type': icmp_type, 'icmp_code': icmp_code, 'policy_tf_name': policy_tf_name}
                                columnname = commonTools.check_column_headers(columnname)
                                tempStr[columnname] = str(columnvalue).strip()
                                tempStr.update(tempdict)
                            apps_str[region] = apps_str[region] + applications.render(tempStr)

                    elif len(apps) >= 2:
                        c = 1
                        for app in apps:
                            region_app = app + "--" + region + "--" + policy_tf_name
                            if region_app not in apps_seen_so_far:
                                apps_seen_so_far.add(region_app)
                                if c <= len(apps):
                                    app = app.split("::")
                                    app_name = app[0]
                                    app_type = app[1]
                                    icmp_type = app[2]
                                    if len(app) == 4:
                                        icmp_code = app[3]
                                    else:
                                        icmp_code = ''
                                tempdict = {'app_name': app_name, 'app_tf_name': commonTools.check_tf_variable(app_name),'app_type': app_type, 'icmp_type': icmp_type, 'icmp_code': icmp_code, 'policy_tf_name': policy_tf_name}
                                columnname = commonTools.check_column_headers(columnname)
                                tempStr[columnname] = str(columnvalue).strip()
                                tempStr.update(tempdict)
                                apps_str[region] = apps_str[region] + applications.render(tempStr)
                            c += 1
        apps_str_02[region] = apps_str_02[region] + apps_str[region]

    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + apps_auto_tfvars_filename

        if apps_str_02[reg] != '':
            # Generate Final String
            src = "##Add New apps for " + reg.lower() + " here##"
            apps_str_02[reg] = applications.render(count=0, region=reg).replace(src, apps_str_02[reg] + "\n" + src)
            apps_str_02[reg] = "".join([s for s in apps_str_02[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            apps_str_02[reg] = "\n\n" + apps_str_02[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(apps_str_02[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for firewall policy services has been updated for region " + reg)
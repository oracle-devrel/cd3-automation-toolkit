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
def fwpolicy_create_secrules(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    secrules = env.get_template('policy-secrules-template')


    sheetName = "Firewall-Policy-SecRule"
    secrules_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile

    outfile = {}
    oname = {}
    secrules_str = {}
    secrules_names = {}


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        secrules_str[reg] = ''
        secrules_names[reg] = []
        resource = sheetName.lower()
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        commonTools.backup_file(reg_out_dir, resource, secrules_auto_tfvars_filename)


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
        dst_id = ''
        src_id = ''
        ser_id = ''
        app_id = ''
        url_id = ''


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

            if columnname == "Rule Name":
                rule_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'rule_tf_name': rule_tf_name,'rule_name':columnvalue}

            if columnname == "Source Address":
                if columnvalue != '':
                    srcaddrs = str(columnvalue).strip().split(",")
                    if len(srcaddrs) == 1:
                        for src in srcaddrs:
                            src_id = "\"" + src.strip() + "\""

                    elif len(srcaddrs) >= 2:
                        c = 1
                        for src in srcaddrs:
                            data = "\"" + src.strip() + "\""

                            if c == len(srcaddrs):
                                src_id = src_id + data
                            else:
                                src_id = src_id + data + ","
                            c += 1
                    columnvalue = src_id
                    tempdict = {'src_address': src_id}

            if columnname == "Destination Address":
                if columnvalue != '':
                    dstaddrs = str(columnvalue).strip().split(",")
                    if len(dstaddrs) == 1:
                        for dst in dstaddrs:
                            dst_id = "\"" + dst.strip() + "\""

                    elif len(dstaddrs) >= 2:
                        c = 1
                        for dst in dstaddrs:
                            data = "\"" + dst.strip() + "\""

                            if c == len(dstaddrs):
                                dst_id = dst_id + data
                            else:
                                dst_id = dst_id + data + ","
                            c += 1
                    columnvalue = dst_id
                    tempdict = {'dst_address': dst_id}

            if columnname == "Service List":
                if columnvalue != '':
                    services = str(columnvalue).strip().split(",")
                    if len(services) == 1:
                        for ser in services:
                            ser_id = "\"" + ser.strip() + "\""

                    elif len(services) >= 2:
                        c = 1
                        for ser in services:
                            data = "\"" + ser.strip() + "\""

                            if c == len(services):
                                ser_id = ser_id + data
                            else:
                                ser_id = ser_id + data + ","
                            c += 1
                    columnvalue = ser_id
                    tempdict = {'service_list': ser_id}

            if columnname == "Application List":
                if columnvalue != '':
                    apps = str(columnvalue).strip().split(",")
                    if len(apps) == 1:
                        for app in apps:
                            app_id = "\"" + app.strip() + "\""

                    elif len(apps) >= 2:
                        c = 1
                        for app in apps:
                            data = "\"" + app.strip() + "\""

                            if c == len(apps):
                                app_id = app_id + data
                            else:
                                app_id = app_id + data + ","
                            c += 1
                    columnvalue = app_id
                    tempdict = {'apps_list': app_id}

            if columnname == "Url List":
                if columnvalue != '':
                    urls = str(columnvalue).strip().split(",")
                    if len(urls) == 1:
                        for url in urls:
                            url_id = "\"" + url.strip() + "\""

                    elif len(urls) >= 2:
                        c = 1
                        for url in urls:
                            data = "\"" + url.strip() + "\""

                            if c == len(urls):
                                url_id = url_id + data
                            else:
                                url_id = url_id + data + ","
                            c += 1
                    columnvalue = url_id
                    tempdict = {'urls_list': url_id}

            if columnname == "Action":
                if columnvalue != '':
                    action = str(columnvalue).strip().split("::")
                    if len(action) == 1:
                        action1 = action[0].upper()
                        inspect = ''
                        tempdict = {'rule_action': action1, 'rule_ins': inspect}
                    else:
                        action1 = action[0].upper()
                        inspect = action[1].upper()
                        tempdict = {'rule_action': action1, 'rule_ins': inspect}

            if columnname == "Position":
                if columnvalue != '':
                    position = str(columnvalue).strip().split(",")
                    if len(position) == 1:
                        for post in position:
                            post = post.strip().split("::")
                            place1 = post[0].lower()
                            rule_place1 = post[1]
                            place2 = None
                            rule_place2 = None
                    if len(position) == 2:
                        for post in position:
                            post = post.strip().split("::")
                            place = post[0].lower()
                            if place == "before_rule":
                                place1 = post[0].lower()
                                rule_place1 = post[1]
                            if place == "after_rule":
                                place2 = post[0].lower()
                                rule_place2 = post[1]

                    tempdict = {'placement1': place1, 'rule_place1': rule_place1, 'placement2': place2, 'rule_place2': rule_place2}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)


        secrules_str[region] = secrules_str[region] + secrules.render(tempStr)


    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + secrules_auto_tfvars_filename

        if secrules_str[reg] != '':
            # Generate Final String
            src = "##Add New Security rules for " + reg.lower() + " here##"
            secrules_str[reg] = secrules.render(count=0, region=reg).replace(src, secrules_str[reg] + "\n" + src)
            secrules_str[reg] = "".join([s for s in secrules_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            secrules_str[reg] = "\n\n" + secrules_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(secrules_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall Policy Security Rules has been updated for region " + reg)

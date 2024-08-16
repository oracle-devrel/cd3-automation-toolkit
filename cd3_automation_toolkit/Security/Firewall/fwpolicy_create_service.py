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
def fwpolicy_create_service(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    service = env.get_template('policy-services-template')


    sheetName = "Firewall-Policy-ServiceList"
    service_auto_tfvars_filename = prefix + "_firewall-policy-service.auto.tfvars"

    filename = inputfile


    service_seen_so_far = set()
    outfile = {}
    oname = {}
    service_tf_name = ''
    service_name = ''
    policy_name = ''
    service_str = {}
    service_names = {}
    service_str_02 = {}
    policy_names = {}
    ip_id = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        service_str[reg] = ''
        service_names[reg] = []
        service_str_02[reg] = ''
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = "firewall-policy-services"
        commonTools.backup_file(reg_out_dir, resource, service_auto_tfvars_filename)
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

            if columnname == "Service List":
                servicelist_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'servicelist_tf_name': servicelist_tf_name}

            port = []
            box1 = '[{\n    minimum_port ="'
            box11 = '  \n  {\n    minimum_port ="'
            box2 = '"\n    maximum_port ="'
            box3 = '"\n  },'
            box33 = '"\n  }]'
            service_name = ''
            service_type = ''

            if columnname == 'Services':
                if columnvalue != '':
                    service_str[region] = ''
                    services = columnvalue.strip().split("\n")
                    if len(services) == 1:
                        for ser in services:
                            region_ser = ser + "--" + region + "--" + policy_tf_name
                            if region_ser not in service_seen_so_far:
                                service_seen_so_far.add(region_ser)
                                ser = ser.split("::")
                                service_name = ser[0]
                                service_type = ser[1]
                                port_range = ser[2]
                                if port_range != '':

                                    port_range = port_range.split(",")
                                    i = 1
                                    for port in port_range:

                                        port = port.split("-")
                                        if len(port_range) == 1:
                                            port_ranges = box1 + port[0] + box2 + port[1] + box33
                                        elif i == len(port_range) and i > 1:
                                            port_ranges = port_ranges + box11 + port[0] + box2 + port[1] + box33
                                        elif i == 1:
                                            port_ranges = box1 + port[0] + box2 + port[1] + box3
                                        else:
                                            port_ranges = port_ranges + box11 + port[0] + box2 + port[1] + box3
                                        i += 1
                            tempdict = {'port_ranges': port_ranges, 'service_name': service_name, 'service_tf_name': commonTools.check_tf_variable(service_name), 'service_type': service_type, 'policy_tf_name': policy_tf_name}
                            columnname = commonTools.check_column_headers(columnname)
                            tempStr[columnname] = str(columnvalue).strip()
                            tempStr.update(tempdict)
                            service_str[region] = service_str[region] + service.render(tempStr)


                    elif len(services) >= 2:
                        c = 1
                        service_str[region] = ''
                        for ser in services:
                            region_ser = ser + "--" + region + "--" + policy_tf_name
                            if region_ser not in service_seen_so_far:
                                service_seen_so_far.add(region_ser)
                                if c <= len(services):
                                    ser = ser.split("::")
                                    service_name = ser[0]
                                    service_type = ser[1]
                                    port_range = ser[2]
                                    if port_range != '':

                                        port_range = port_range.split(",")
                                        i = 0
                                        for port in port_range:
                                            i = i + 1
                                            port = port.split("-")
                                            if len(port_range) == 1:
                                                port_ranges = box1 + port[0] + box2 + port[1] + box33
                                            elif i == len(port_range) and i > 1:
                                                port_ranges = port_ranges + box11 + port[0] + box2 + port[1] + box33
                                            elif i == 1:
                                                port_ranges = box1 + port[0] + box2 + port[1] + box3
                                            else:
                                                port_ranges = port_ranges + box11 + port[0] + box2 + port[1] + box3

                                tempdict = {'port_ranges': port_ranges, 'service_name': service_name, 'service_tf_name': commonTools.check_tf_variable(service_name), 'service_type': service_type, 'policy_tf_name': policy_tf_name}
                                columnname = commonTools.check_column_headers(columnname)
                                tempStr[columnname] = str(columnvalue).strip()
                                tempStr.update(tempdict)
                                service_str[region] = service_str[region] + service.render(tempStr)
                            c += 1
        service_str_02[region] = service_str_02[region] + service_str[region]
        #print(service_str_02[region])

    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + service_auto_tfvars_filename

        if service_str_02[reg] != '':
            # Generate Final String
            src = "##Add New service policy for " + reg.lower() + " here##"
            service_str_02[reg] = service.render(count=0, region=reg).replace(src, service_str_02[reg] + "\n" + src)
            service_str_02[reg] = "".join([s for s in service_str_02[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            service_str_02[reg] = "\n\n" + service_str_02[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(service_str_02[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for firewall policy services has been updated for region " + reg)
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
def fwpolicy_create_servicelist(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    servicelist = env.get_template('policy-servicelists-template')


    sheetName = "Firewall-Policy-ServiceList"
    servicelist_auto_tfvars_filename = prefix + "_firewall-policy-servicelist.auto.tfvars"
    filename = inputfile


    outfile = {}
    oname = {}
    service_tf_name = ''
    servicelist_tf_name = ''
    service_name = ''
    policy_name = ''
    service_str = {}
    service_names = {}
    servicelist_str = {}
    servicelist_names = {}
    servicelist_name = ''
    policy_names = {}
    services = {}
    ip_id = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        servicelist_str[reg] = ''
        servicelist_names[reg] = []
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, servicelist_auto_tfvars_filename)
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

            if columnname == "Service List":
                servicelist_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'servicelist_tf_name': servicelist_tf_name,'servicelist_name':columnvalue}

            data = ""
            if columnname == 'Services':
                if columnvalue != '':

                    services = columnvalue.strip().split("\n")
                    if len(services) == 1:
                        for ser in services:
                            ser = ser.split("::")
                            service_name = ser[0]
                            service_type = ser[1]
                            port_range = ser[2]
                            #servicelist.append(service_name)
                            #print(service_name, service_type, port_range)
                            service_name = "\"" + service_name.strip() + "\""
                            tempdict = {'services_tf_name': service_name}


                    elif len(services) >= 2:
                        c = 1

                        service1 = ''
                        for ser in services:
                            if c <= len(services):
                                ser = ser.split("::")
                                service_name = ser[0]
                                service_type = ser[1]
                                port_range = ser[2]
                                #servicelist.append(service_name)
                                data = "\"" + service_name.strip() + "\""
                                if c == len(services):
                                    service1 = service1 + data
                                else:
                                    service1 = service1 + data + ","
                            tempdict = {'services_tf_name': service1}
                            c += 1





            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)


        servicelist_str[region] = servicelist_str[region] + servicelist.render(tempStr)

    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + servicelist_auto_tfvars_filename

        if servicelist_str[reg] != '':
            # Generate Final String
            src = "##Add New service list for " + reg.lower() + " here##"
            servicelist_str[reg] = servicelist.render(count=0, region=reg).replace(src, servicelist_str[reg] + "\n" + src)
            servicelist_str[reg] = "".join([s for s in servicelist_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            servicelist_str[reg] = "\n\n" + servicelist_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(servicelist_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall policy service lists has been updated for region " + reg)


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
def fwpolicy_create_urllist(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    urllist = env.get_template('policy-urllists-template')


    sheetName = "Firewall-Policy-UrlList"
    urllist_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile

    outfile = {}
    oname = {}
    urllist_tf_name = ''
    urllist_name = ''
    policy_name = ''
    urllist_str = {}
    urllist_names = {}
    policy_names = {}
    ip_id = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        urllist_str[reg] = ''
        urllist_names[reg] = []
        resource = sheetName.lower()
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        commonTools.backup_file(reg_out_dir, resource, urllist_auto_tfvars_filename)

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

            if columnname == "List Name":
                urllist_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'urllist_tf_name': urllist_tf_name,'urllist_name':columnvalue}


            cover1 = '[{\n    pattern = "'
            cover11 = '  {\n    pattern = "'
            cover2 = '"\n    type = "SIMPLE"\n  },\n  ]'
            cover22 = '"\n    type = "SIMPLE"\n  },\n'
            if columnname == "URL List":
                if columnvalue != '':
                    urls = str(columnvalue).strip().split("\n")

                    if len(urls) == 1:
                        for url in urls:
                            url = cover1 + url + cover2
                            tempdict = {'url_list': url}
                    elif len(urls) >= 2:
                        c = 1
                        for url in urls:
                            if c == len(urls):
                                url1 = url1 + cover11 + url + cover2
                            elif c == 1:
                                url1 = cover1 + url + cover22
                            else:
                                url1 = url1 + cover11 + url + cover22
                            tempdict = {'url_list': url1}
                            c += 1

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        urllist_str[region] = urllist_str[region] + urllist.render(tempStr)



    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + urllist_auto_tfvars_filename

        if urllist_str[reg] != '':
            # Generate Final String
            src = "##Add New urllist for " + reg.lower() + " here##"
            urllist_str[reg] = urllist.render(count=0, region=reg).replace(src, urllist_str[reg] + "\n" + src)
            urllist_str[reg] = "".join([s for s in urllist_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            urllist_str[reg] = "\n\n" + urllist_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(urllist_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall Policy url lists has been updated for region " + reg)

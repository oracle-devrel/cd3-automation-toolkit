#!/usr/bin/python3
# Copyright (c) 2019, 2023, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Identity components
# Network Sources
#
# Author: Gaurav Goyal
# Oracle Consulting
#
import os
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_networkSources(inputfile, outdir, service_dir, prefix, ct):
    # Read the arguments
    filename = inputfile

    sheetName = 'NetworkSources'
    auto_tfvars_filename = '_' + sheetName.lower() + '.auto.tfvars'

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    users_template = env.get_template('network-sources-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    tfStr[ct.home_region] = ''

    # Take backup of files
    srcdir = outdir + "/" + ct.home_region + "/" + service_dir + "/"
    resource = sheetName.lower()
    commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region=region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)


        # temporary dictionary1 and dictionary2
        tempStr = { "count" : i }
        tempdict = {}
        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Name']).lower() == 'nan' or str(df.loc[i, 'Description']).lower() == 'nan' :
            print("\nThe values for Region, Name and Description cannot be left empty. Please enter a value and try again !!")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            if 'name' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'tf_name': tf_name}
                tempdict['name'] = columnvalue

            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df[columnname][i]).strip()

            if columnname == 'Public Networks':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    public_source_str = ""
                    public_source = ""
                    publicSources = columnvalue.split(",")
                    k = 0
                    while k < len(publicSources):
                        public_source = "\"" + commonTools.check_columnvalue(publicSources[k].strip()) + "\""

                        public_source_str = public_source_str + str(public_source)
                        if (k != len(publicSources) - 1):
                            public_source_str = public_source_str + ","
                        k += 1
                    tempdict = {'public_source_list': public_source_str}
                    tempStr.update(tempdict)
                continue

            IPList = []
            if columnname == 'OCI Networks':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    IPRanges = columnvalue.split(";")

                    k = 0
                    while k < len(IPRanges):
                        IP = IPRanges[k].strip()
                        IPs = IP.split(",")
                        j = 0
                        strIPs = ""
                        while j < len(IPs):
                            if(strIPs == ""):
                                    strIPs = "\"" + IPs[j].strip() + "\""
                            else:
                                strIPs = strIPs + ",\"" + IPs[j].strip() + "\""
                            j += 1
                        IPList.append(strIPs)
                        k += 1

                tempdict = {'virtual_source_list': IPList}
                tempStr.update(tempdict)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)


            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()


            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region]= tfStr[region][:-1] + users_template.render(tempStr)
    # Write TF string to the file in respective region directory
    reg=ct.home_region

    reg_out_dir = outdir + "/" + reg + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

    if(tfStr[reg]!=''):
        tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " for Network Sources has been created for region "+reg)


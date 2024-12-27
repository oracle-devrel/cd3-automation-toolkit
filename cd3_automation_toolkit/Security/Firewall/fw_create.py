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
def fw_create(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    firewall = env.get_template('firewalls-template')
    ADS = ["AD1", "AD2", "AD3"]

    sheetName = "Firewall"
    firewall_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile


    firewall_str = {}
    outfile = {}
    oname = {}
    firewall_tf_name = ''
    firewall_name = ''
    firewall_names = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        firewall_str[reg] = ''
        firewall_names[reg] = []
        resource = sheetName.lower()
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        commonTools.backup_file(reg_out_dir, resource, firewall_auto_tfvars_filename)

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
        nsg_id = ''

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
                tempdict = {'compartment_tf_name': columnvalue}

            if columnname == "Firewall Name":
                firewall_tf_name = commonTools.check_tf_variable(columnvalue)
                firewall_name = columnvalue
                tempdict = {'firewall_tf_name': firewall_tf_name}

            if columnname == "Firewall Policy":
                policy_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'policy_tf_name': policy_tf_name}

            if columnname == "Network Compartment Name":
                columnname = "subnet_compartment_tf_name"
                columnvalue = commonTools.check_tf_variable(columnvalue)
                tempdict = {'subnet_compartment_tf_name': columnvalue}

            if columnname == 'Subnet Name':
                subnet_tf_name = str(columnvalue).strip()
                if subnet_tf_name == 'nan' or subnet_tf_name == '':
                    continue
                if ("ocid1.subnet.oc" in subnet_tf_name):
                    vcn_name = ""
                    subnet_id = subnet_tf_name
                else:
                    subnet_tf_name = subnet_tf_name.split("::")
                    vcn_name = subnet_tf_name[0]
                    subnet_id = subnet_tf_name[1]
                tempdict = {'vcn_name': vcn_name, 'subnet_id': subnet_id}

            if columnname == "NSGs":
                if columnvalue != '':
                    fw_nsgs = str(columnvalue).strip().split(",")
                    if len(fw_nsgs) == 1:
                        for nsgs in fw_nsgs:
                            nsg_id = "\"" + nsgs.strip() + "\""

                    elif len(fw_nsgs) >= 2:
                        c = 1
                        for nsgs in fw_nsgs:
                            data = "\"" + nsgs.strip() + "\""

                            if c == len(fw_nsgs):
                                nsg_id = nsg_id + data
                            else:
                                nsg_id = nsg_id + data + ","
                            c += 1
                columnvalue = nsg_id

            if columnname == 'Availability Domain(AD1|AD2|AD3|Regional)':
                if columnvalue != '':
                    columnname = 'availability_domain'

                    if (columnvalue.strip().lower() != 'regional'):
                        AD = columnvalue.upper()
                        ad = ADS.index(AD)
                        adString = str(ad)
                    else:
                        adString = ""

                tempdict = {'availability_domain': adString}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if (region != 'nan' and firewall_name not in firewall_names[region]):
            firewall_names[region].append(firewall_name)
            firewall_str[region] = firewall_str[region] + firewall.render(tempStr)

    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + firewall_auto_tfvars_filename
        if firewall_str[reg] != '':
            # Generate Final String
            src = "##Add New firewall for " + reg.lower() + " here##"
            firewall_str[reg] = firewall.render(count=0, region=reg).replace(src, firewall_str[reg] + "\n" + src)
            firewall_str[reg] = "".join([s for s in firewall_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            firewall_str[reg] = "\n\n" + firewall_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(firewall_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall has been updated for region " + reg)

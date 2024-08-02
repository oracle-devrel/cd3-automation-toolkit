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
def fwpolicy_create_decryptionprofile(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    decryptionprofile = env.get_template('policy-decryptionprofiles-template')


    sheetName = "Firewall-Policy-DecryptProfile"
    decryptionprofile_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile

    decryptionprofile_str = {}
    outfile = {}
    oname = {}


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        decryptionprofile_str[reg] = ''
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, decryptionprofile_auto_tfvars_filename)

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



            if columnname == "Firewall Policy":
                policy_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'policy_tf_name': policy_tf_name}

            if columnname == "Decryption Profile Name":
                decryptionprofile_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'decryptionprofile_tf_name': decryptionprofile_tf_name,'decryptionprofile_name':columnvalue}

            if columnname == "Decryption Profile Type":
                tempdict = {'decryptionprofile_type': columnvalue}


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        decryptionprofile_str[region] = decryptionprofile_str[region] + decryptionprofile.render(tempStr)


    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + decryptionprofile_auto_tfvars_filename

        if decryptionprofile_str[reg] != '':
            # Generate Final String
            src = "##Add New Decryption Profile for " + reg.lower() + " here##"
            decryptionprofile_str[reg] = decryptionprofile.render(count=0, region=reg).replace(src, decryptionprofile_str[reg] + "\n" + src)
            decryptionprofile_str[reg] = "".join([s for s in decryptionprofile_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            decryptionprofile_str[reg] = "\n\n" + decryptionprofile_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(decryptionprofile_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall firewall has been updated for region " + reg)

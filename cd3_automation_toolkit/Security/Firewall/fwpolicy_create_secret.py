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
def fwpolicy_create_secret(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    #print (inputfile, outdir, prefix, config, service_dir)
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    secret = env.get_template('policy-secrets-template')


    sheetName = "Firewall-Policy-Secret"
    secret_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile


    secret_str = {}
    outfile = {}
    oname = {}


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        secret_str[reg] = ''
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, secret_auto_tfvars_filename)

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

            if columnname == "Vault Compartment Name":
                compartment_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartment_tf_name}

            if columnname == "Firewall Policy":
                policy_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'policy_tf_name': policy_tf_name}

            if columnname == "Secret Name":
                secret_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'secret_tf_name': secret_tf_name,'secret_name':columnvalue}


            if columnname == "Vault Secret Id":
                if columnvalue != '':
                    secret_id = str(columnvalue).strip().split("::")
                    vault_secret_name = secret_id[1]
                    vault_name = secret_id[0]
                tempdict = {'vault_secret_name': vault_secret_name, 'vault_name': vault_name}

            if columnname == "Version Number":
                version_number = columnvalue
                tempdict = {'version_number': version_number}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        secret_str[region] = secret_str[region] + secret.render(tempStr)



    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + secret_auto_tfvars_filename

        if secret_str[reg] != '':
            # Generate Final String
            src = "##Add New Secrets for " + reg.lower() + " here##"
            secret_str[reg] = secret.render(count=0, region=reg).replace(src, secret_str[reg] + "\n" + src)
            secret_str[reg] = "".join([s for s in secret_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            secret_str[reg] = "\n\n" + secret_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(secret_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall firewall has been updated for region " + reg)

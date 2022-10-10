#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# NLB, Listeners
#
# Author: Suruchi Singla
# Oracle Consulting
#
import re
import json
import shutil
import argparse
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######
def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates TF files for NLB")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-CIS-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


# If input file is CD3
def create_terraform_nlb_listener(inputfile, outdir, prefix, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    nlb = env.get_template('nlb-template')
    reserved_ips_template = env.get_template('nlb-reserved-ips-template')
    nlb_listener = env.get_template('nlb-listener-template')

    sheetName = "NLB-Listeners"
    nlb_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    nlb_str = {}
    reserved_ips_str = {}
    nlb_listener_str = {}
    nlb_tf_name = ''
    nlb_name = ''
    nlb_names = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in ct.all_regions:
        nlb_str[reg] = ''
        reserved_ips_str[reg] = ''
        nlb_listener_str[reg] = ''
        nlb_names[reg] = []

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    subnets = parseSubnets(filename)
    prevreg = ''

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if region.lower() != 'nan':
            region = region.strip().lower()
            prevreg = region

        if region in commonTools.endNames:
            break

        if region != 'nan' and region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the regions tenancy is subscribed to...Exiting!!")
            exit()

        # Check for empty values
        empty_nlb = 0

        #empty NLB without Listener/BS
        if (str(df.loc[i, 'Listener Name']).lower() == 'nan') and (str(df.loc[i, 'Listener Protocol(UDP|TCP|UDP/TCP|Any)']).lower() == 'nan') and (str(df.loc[i, 'Listener Port']).lower() == 'nan') and (str(df.loc[i, 'Backend Set Name']).lower() == 'nan'):
            empty_nlb = 1

        #NLB having multiple Listeners can't have null values for listener properties
        elif (str(df.loc[i, 'Region']).lower() == 'nan') and (str(df.loc[i, 'Compartment Name']).lower() == 'nan') and (str(df.loc[i, 'NLB Name']).lower() == 'nan') and (str(df.loc[i, 'Subnet Name']).lower() == 'nan'):
            if (str(df.loc[i, 'Listener Name']).lower() == 'nan') or (str(df.loc[i, 'Listener Protocol(UDP|TCP|UDP/TCP|Any)']).lower() == 'nan') or (str(df.loc[i, 'Listener Port']).lower() == 'nan') or (str(df.loc[i, 'Backend Set Name']).lower() == 'nan'):
                print("\nColumns Backend Set Name, Listener Name, Listener Protocol and Listener Port cannot be left empty.....Exiting! Check Row No "+(str(i+3)))
                exit(1)
        elif (str(df.loc[i, 'Region']).lower() != 'nan') and (str(df.loc[i, 'Compartment Name']).lower() != 'nan') and (str(df.loc[i, 'NLB Name']).lower() != 'nan') and (str(df.loc[i, 'Subnet Name']).lower() != 'nan'):
            if (str(df.loc[i, 'Listener Name']).lower() == 'nan') or (str(df.loc[i, 'Listener Protocol(UDP|TCP|UDP/TCP|Any)']).lower() == 'nan') or (str(df.loc[i, 'Listener Port']).lower() == 'nan') or (str(df.loc[i, 'Backend Set Name']).lower() == 'nan'):
                print("\nColumns Backend Set Name, Listener Name, Listener Protocol and Listener Port cannot be left empty.....Exiting! Check Row No " + (str(i + 3)))
                exit(1)

        elif (str(df.loc[i, 'Listener Name']).lower() != 'nan') and (str(df.loc[i, 'Listener Protocol(UDP|TCP|UDP/TCP|Any)']).lower() != 'nan') and (str(df.loc[i, 'Listener Port']).lower() != 'nan') and (str(df.loc[i, 'Backend Set Name']).lower() != 'nan'):
            if (str(df.loc[i, 'Region']).lower() == 'nan') or (str(df.loc[i, 'Compartment Name']).lower() == 'nan') or (str(df.loc[i, 'NLB Name']).lower() == 'nan') or (str(df.loc[i, 'Subnet Name']).lower() == 'nan'):
                print("\nColumns Region, Compartment Name, NLB Name and Subnet Name cannot be left empty.....Exiting! Check Row No "+(str(i+3)))
                exit(1)

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

            if columnname == "Reserved IP(Y|N|OCID)":
                columnname = "reserved_ips_id"
                if columnvalue != "":
                    if "," in columnvalue:
                        columnvalue = columnvalue.split(",")

            if columnname == "NLB Name":
                if columnvalue != '' and columnvalue != 'nan':
                    nlb_name = columnvalue
                    nlb_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'nlb_tf_name': nlb_tf_name, 'nlb_name': nlb_name}

            network_compartment_id = ''
            vcn_name = ''
            if columnname == 'Subnet Name':
                nlb_subnet = str(columnvalue).strip()
                if(nlb_subnet != "" and nlb_subnet != 'nan'):
                    if ("ocid1.subnet.oc1" in nlb_subnet):
                        pass
                    else:
                        subnet_tf_name = commonTools.check_tf_variable(nlb_subnet)
                        try:
                            key = region, subnet_tf_name
                            network_compartment_id = subnets.vcn_subnet_map[key][0]
                            vcn_name = subnets.vcn_subnet_map[key][1]
                            nlb_subnet = subnets.vcn_subnet_map[key][2]
                        except Exception as e:
                                print("Invalid Subnet Name specified for row " + str(i + 3) + ". It Doesnt exist in Subnets sheet. Exiting!!!")
                                exit()
                        tempdict = {'network_compartment_tf_name': commonTools.check_tf_variable(network_compartment_id), 'vcn_tf_name': vcn_name,'nlb_subnet': nlb_subnet}

            if columnname == "NSGs":
                if columnvalue != '' and columnvalue != 'nan':
                    nlb_nsgs = str(columnvalue).strip().split(",")
                    if len(nlb_nsgs) == 1:
                        for nsgs in nlb_nsgs:
                            if "ocid" in nsgs.strip():
                                nsg_id = "\"" + nsgs.strip() + "\""
                            else:
                                nsg_id = "\"" + commonTools.check_tf_variable(str(nsgs).strip()) + "\""

                    elif len(nlb_nsgs) >=2 :
                        c = 1
                        for nsgs in nlb_nsgs:
                            if "ocid" in nsgs.strip():
                                data = "\"" + nsgs.strip() + "\""
                            else:
                                data = "\""+ commonTools.check_tf_variable(str(nsgs).strip()) + "\""

                            if c == len(nlb_nsgs):
                                nsg_id = nsg_id + data
                            else:
                                nsg_id = nsg_id + data +","
                            c += 1
                columnvalue = nsg_id

            if columnname == "Backend Set Name":
                backend_set_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'backend_set_tf_name': backend_set_tf_name}

            if columnname == "Listener Name":
                listener_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'listener_tf_name': listener_tf_name}

            if columnname == 'Listener Protocol(UDP|TCP|UDP/TCP|Any)':
                columnname = 'protocol'
                if columnvalue == "UDP/TCP":
                    columnvalue = "TCP_AND_UDP"

            if columnname == 'Is Preserve Source Destination(True|False)':
                columnname = 'is_preserve_source_destination'

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if(region != 'nan' and nlb_name not in nlb_names[region]):
            nlb_names[region].append(nlb_name)
            nlb_str[region] = nlb_str[region] + nlb.render(tempStr)
            if empty_nlb !=1 :
                nlb_listener_str[region] = nlb_listener_str[region] + nlb_listener.render(tempStr)
        else:
            nlb_listener_str[prevreg] = nlb_listener_str[prevreg] + nlb_listener.render(tempStr)

        if tempStr['reserved_ips_id'].lower() == 'y':
            reserved_ips_str[region] = reserved_ips_str[region] + reserved_ips_template.render(tempStr)

    for reg in ct.all_regions:
        if nlb_str[reg] != '':
            # Generate Final String
            src = "##Add New Network Load Balancers for "+reg.lower()+" here##"
            nlb_str[reg] = nlb.render(skeleton=True, count=0, region=reg).replace(src,nlb_str[reg]+"\n"+src)

        if nlb_listener_str[reg] != '':
            # Generate Final String
            src = "##Add New Listeners for " + reg.lower() + " here##"
            nlb_listener_str[reg] = nlb_listener.render(skeleton=True, count=0, region=reg).replace(src, nlb_listener_str[reg]+"\n"+src)

        if reserved_ips_str[reg] != '':
            # Generate Final String
            src = "##Add New Network Load Balancer Reserved IPs for "+ reg.lower() +" here##"
            reserved_ips_str[reg] = reserved_ips_template.render(skeleton=True, count = 0, region=reg).replace(src, reserved_ips_str[reg]+"\n"+src)

        finalstring =  nlb_str[reg] + nlb_listener_str[reg] + reserved_ips_str[reg]
        finalstring = "".join([s for s in finalstring.strip().splitlines(True) if s.strip("\r\n").strip()])

        if finalstring != "":
            resource = sheetName.lower()
            srcdir = outdir + "/" + reg + "/"
            commonTools.backup_file(srcdir, resource, nlb_auto_tfvars_filename)

            # Write to TF file
            outfile = outdir + "/" + reg + "/" + nlb_auto_tfvars_filename
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(finalstring)
            oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_terraform_nlb_listener(args.inputfile, args.outdir, args.prefix, args.config)

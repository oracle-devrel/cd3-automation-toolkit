#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create Listener
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import os
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
    parser = argparse.ArgumentParser(description="Creates Listener TF files for LBR")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


# If input file is CD3
def create_listener(inputfile, outdir, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    listener = env.get_template('listener-template')
    filename = inputfile
    outdir = outdir
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "LB-Listener")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    #DF with just the load balancer names and the Region details

    # fill the empty values with that in previous row.
    dffill = df[['Region','LBR Name']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','LBR Name']]
    dfdrop = df.drop(dfdrop, axis=1)

    #dfcert with required details
    df = pd.concat([dffill, dfdrop], axis=1)

    unique_region = df['Region'].unique()

    # Take backup of files
    for eachregion in unique_region:
        eachregion = str(eachregion).strip().lower()
        if (eachregion in commonTools.endNames):
            continue
        if eachregion == 'nan':
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        resource='Listener'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_listener-lb.tf")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if region.lower() == 'nan':
            continue

        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the values mentioned in VCN Info tab...Exiting!!")
            exit()

        # temporary dictionaries
        tempStr= {}
        tempdict= {}
        lbr_hostname = ''
        rule_set_names = ''
        listener_tf_name = ''
        lbr_tf_name = ''

        #Check if mandatory field is empty
        if (str(df.loc[i,'Listener Name']).lower() == 'nan') or (str(df.loc[i,'Listener Protocol (HTTP|TCP)']).lower() == 'nan') or (str(df.loc[i,'Listener Port']).lower() == 'nan') or (str
            (df.loc[i,'Backend Set Name']).lower() == 'nan') :
            print("\nColumns Backend Set Name, Listener Name, Listerner Protocol and Listener Port cannot be left empty.....Exiting!")
            exit(1)


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

            if columnname == "LBR Name":
                lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == "Certificate Name":
                certificate_tf_name = commonTools.check_tf_variable(columnvalue)+"_cert"
                tempdict = {'certificate_tf_name': certificate_tf_name}

            if columnname == "Backend Set Name":
                backend_set_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'backend_set_tf_name': backend_set_tf_name}

            if columnname == "Listener Name":
                listener_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'listener_tf_name': listener_tf_name}

            if columnname == "UseSSL (y|n)":
                columnname = "usessl"

            if columnname == 'Listener Protocol (HTTP|TCP)':
                columnname = 'protocol'

            if columnname == 'Idle Time Out (in Seconds)':
                columnname = 'idle_timeout_in_seconds'

            if columnname == 'Path Route Set Name':
                if columnvalue == '':
                    path_route_set_tf_name = "\"\""
                else:
                    columnvalue = commonTools.check_tf_variable(str(columnvalue).strip())
                    path_route_set_tf_name = 'oci_load_balancer_path_route_set.'+lbr_tf_name +"_"+ columnvalue+'.name'
                tempdict = {'path_route_set_tf_name' : path_route_set_tf_name}

            if columnname == "LBR Hostnames (Name)":
                columnname = 'lbr_hostnames'
                if columnvalue != '':
                    lbr_hostnames =  str(columnvalue).strip().split(',')
                    if len(lbr_hostnames) == 1:
                        for hostname in lbr_hostnames:
                            hostname = commonTools.check_tf_variable(hostname)
                            lbr_hostname = 'oci_load_balancer_hostname.'+lbr_tf_name+"_"+hostname+'_hostname.name'
                    elif len(lbr_hostnames) >= 2:
                        c = 1
                        for hostname in lbr_hostnames:
                            hostname = commonTools.check_tf_variable(hostname)
                            if c == len(lbr_hostnames):
                                lbr_hostname = lbr_hostname+'oci_load_balancer_hostname.'+lbr_tf_name+"_" + hostname + '_hostname.name'
                            else:
                                lbr_hostname = lbr_hostname+'oci_load_balancer_hostname.'+lbr_tf_name+"_"+hostname+'_hostname.name,'
                            c += 1
                columnvalue = lbr_hostname

            if columnname == 'Rule Set Names':
                if columnvalue != '':
                    rule_sets = str(columnvalue).strip().split(',')
                    if len(rule_sets) == 1:
                        for rule in rule_sets:
                            rule = commonTools.check_tf_variable(str(rule))
                            rule_set_names = 'oci_load_balancer_rule_set.'+lbr_tf_name+"_"+rule+'.name'
                    elif len(rule_sets) >=2 :
                        c=1
                        for rule in rule_sets:
                            if c == len(rule_sets):
                                rule = commonTools.check_tf_variable(str(rule))
                                rule_set_names = rule_set_names+'oci_load_balancer_rule_set.'+lbr_tf_name+"_"+rule+'.name'
                            else:
                                rule = commonTools.check_tf_variable(str(rule))
                                rule_set_names = rule_set_names+'oci_load_balancer_rule_set.'+lbr_tf_name+"_"+ rule + '.name,'
                            c += 1
                columnvalue = rule_set_names

            if columnname == 'Verify Peer Certificate':
                if str(columnvalue).lower() == 'true':
                    if str(df.loc[i,'Verify Depth']) == '' or str(df.loc[i,'Verify Depth']) == 'nan':
                        print("\nVerify Depth cannot be left empty when Verify Peer Certificate has a value... Exiting!!!")
                        exit()

            if columnname == 'SSL Protocols':
                tls_versions_list = ''
                if columnvalue != '' and str(df.loc[i,'Cipher Suite Name']) != 'nan':
                    tls_versions = str(columnvalue).strip().split(',')
                    for tls in tls_versions:
                        tls_versions_list = tls_versions_list + "\""+tls+"\","

                    if (tls_versions_list != "" and tls_versions_list[0] == ','):
                        tls_versions_list = tls_versions_list.lstrip(',')
                    columnvalue = tls_versions_list

                elif columnvalue == '' and str(df.loc[i,'Cipher Suite Name']) != 'nan':
                    print("\nSSL Protocols are mandatory when custom CipherSuiteName is provided..... Exiting !!")
                    exit()

                elif columnvalue != '' and str(df.loc[i,'Cipher Suite Name']) == 'nan':
                    print("\nNOTE: Cipher Suite Name is not specified for Listener -> "+str(df.loc[i,'Listener Name'])+", default value - 'oci-default-ssl-cipher-suite-v1' will be considered.\n")

                else:
                    pass

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Render Backend Set
        listener_str = listener.render(tempStr)

        # Write to TF file
        outfile = outdir + "/" + region + "/"+lbr_tf_name+"_"+listener_tf_name+"_listener-lb.tf"
        oname = open(outfile, "w+")
        print("Writing to " + outfile)
        oname.write(listener_str)
        oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_listener(args.inputfile, args.outdir, args.config)

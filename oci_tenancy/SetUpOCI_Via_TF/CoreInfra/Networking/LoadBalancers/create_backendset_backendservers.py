#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Backend Set and Backend Server
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import os
import pandas as pd
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######

# If input file is CD3
def main():

    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates Backend Set and Backend Server TF files for LBR")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    beset = env.get_template('backend-set-template')
    beserver = env.get_template('backend-server-template')

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.inputfile
    outdir = args.outdir
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "BackendSet-BackendServer")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    #DF with just the load balancer names and the Cert details

    # fill the empty values with that in previous row.
    dffill = df[['Region','Compartment Name','LBR Name']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','Compartment Name','LBR Name']]
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
        resource='BackendSet-BackendServer'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_backends-lb.tf")

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
        lbr_tf_name =''
        backend_set_tf_name = ''

        #Check if mandatory field is empty
        if (str(df.loc[i,'Backend Set Name']).lower() == 'nan'):
            print("\nColumn Backend Set Name cannot be left empty.....Exiting!")
            exit(1)

        if (str(df.loc[i,'UseSSL(y|n)']).lower() == 'y') and (str(df.loc[i,'Certificate Name']).lower() == 'y'):
            print("\n Certificate Name cannot be empty if Use SSL is set to 'y'.....Exiting!")
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

            if columnname == "Compartment Name":
                columnname = "compartment_tf_name"
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == "LBR Name":
                lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == "Certificate Name":
                if columnvalue != "":
                    certificate_tf_name = commonTools.check_tf_variable(columnvalue)+"_cert"
                else:
                    certificate_tf_name = ""
                tempdict = {'certificate_tf_name': certificate_tf_name}

            if columnname == "Backend Set Name":
                backend_set_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'backend_set_tf_name': backend_set_tf_name}

            if columnname == "Backend Policy(LEAST_CONNECTIONS|ROUND_ROBIN|IP_HASH)":
                columnname = 'backend_policy'

            if columnname == "Cookie Session(n|LB|Backend Server)":
                columnname = "session"

            if columnname == "Disable Fallback(TRUE|FALSE)":
                columnname = "disable_fallback"
                if columnvalue == '':
                    columnvalue = 'false'

            if columnname == "Backend HealthCheck Protocol(HTTP|TCP)":
                columnname = "backend_healthcheck_protocol"

            if columnname == "Backend HealthCheck Interval In Millis":
                columnname = 'interval_in_millis'

            if columnname == "UseSSL(y|n)":
                columnname = "usessl"

            if columnname == "Backup <Backend Server Name>":
                columnname = "backup"

            if columnname == 'Verify Peer Certificate':
                if str(columnvalue).lower() == 'true':
                    if str(df.loc[i,'Verify Depth']) == '' or str(df.loc[i,'Verify Depth']) == 'nan':
                        print("\nVerify Depth cannot be left empty when Verify Peer Certificate has a value... Exiting!!!")
                        exit()

            if columnname == 'SSL Protocols':
                tls_versions_list = ''
                if columnvalue != '' and str(df.loc[i, 'Cipher Suite Name']) != 'nan':
                    tls_versions = str(columnvalue).strip().split(',')
                    for tls in tls_versions:
                        tls_versions_list = tls_versions_list + "\"" + tls + "\","

                    if (tls_versions_list != "" and tls_versions_list[0] == ','):
                        tls_versions_list = tls_versions_list.lstrip(',')
                    columnvalue = tls_versions_list

                elif columnvalue == '' and str(df.loc[i, 'Cipher Suite Name']) != 'nan':
                    print("\nSSL Protocols are mandatory when custom CipherSuiteName is provided..... Exiting !!")
                    exit()

                elif columnvalue != '' and str(df.loc[i, 'Cipher Suite Name']) == 'nan':
                    print("\nNOTE: Cipher Suite Name is not specified for Listener -> " + str(df.loc[i, 'Listener Name']) + ", default value - 'oci-default-ssl-cipher-suite-v1' will be considered.\n")
                else:
                    pass

            if columnname == "Backend ServerName:Port":
                columnname = "backend_server"

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Render Backend Set
        beset_str= beset.render(tempStr)

        cnt = 0

        beserver_str = ''
        columnvalue = str(df.loc[i,'Backend ServerName:Port']).strip().split(',')
        for lbr_be_server in columnvalue:
            if (lbr_be_server != "" and lbr_be_server != "nan"):
                bserver_list = str(df.loc[i, 'Backup <Backend Server Name>']).strip().split(',')
                cnt = cnt + 1
                serverinfo = lbr_be_server.strip().split(":")
                servername = serverinfo[0].strip()
                if servername in bserver_list:
                    backup = "true"
                else:
                    backup = "false"

                tempback = {'backup': backup }
                tempStr.update(tempback)

                backend_server_tf_name = commonTools.check_tf_variable(servername)
                serverport = serverinfo[1].strip()
                e = servername.count(".")
                if (e == 3):
                    backend_server_ip_address = "\""+servername+"\""
                else:
                    backend_server_ip_address = "oci_core_instance." + servername + ".private_ip"

                tempback = {'backend_server_tf_name': backend_set_tf_name+"_"+backend_server_tf_name,'serverport':serverport,'backend_server_ip_address':backend_server_ip_address}
                tempStr.update(tempback)

                # Render Backend Server
                beserver_str = beserver_str + beserver.render(tempStr)

        # Write to TF file
        outfile = outdir + "/" + region + "/"+ lbr_tf_name+"_"+ backend_set_tf_name+"_backends-lb.tf"
        oname = open(outfile, "w+")
        print("Writing to " + outfile)
        oname.write(beset_str + beserver_str)
        oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    main()
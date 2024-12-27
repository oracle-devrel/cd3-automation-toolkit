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
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######
# Execution of the code begins here
def create_listener(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    listener = env.get_template('listener-template')
    filename = inputfile
    outdir = outdir
    sheetName = "LB-Listener"
    lb_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    listener_str = {}

    #DF with just the load balancer names and the Region details

    # fill the empty values with that in previous row.
    dffill = df[['Region','LBR Name']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','LBR Name']]
    dfdrop = df.drop(dfdrop, axis=1)

    #dfcert with required details
    df = pd.concat([dffill, dfdrop], axis=1)

    # Take backup of files
    for reg in ct.all_regions:
        listener_str[reg] = ""
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, lb_auto_tfvars_filename)

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
            exit(1)

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

            if columnname == "Certificate Name or OCID":
                if columnvalue != '':
                    if 'ocid1.certificate.oc' not in columnvalue:
                        certificate_tf_name = commonTools.check_tf_variable(columnvalue)+"_cert"
                        tempdict = {'certificate_tf_name': certificate_tf_name}
                    else:
                        tempdict = {'certificate_ids': columnvalue}

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
                if columnvalue != '':
                    columnvalue = commonTools.check_tf_variable(str(columnvalue).strip())
                    path_route_set_tf_name = lbr_tf_name +"_"+ columnvalue
                    tempdict = {'path_route_set_tf_name' : path_route_set_tf_name}

            if columnname == "LBR Hostnames (Name)":
                columnname = 'lbr_hostnames'
                if columnvalue != '':
                    lbr_hostnames =  str(columnvalue).strip().split(',')
                    if len(lbr_hostnames) == 1:
                        for hostname in lbr_hostnames:
                            hostname = commonTools.check_tf_variable(hostname)
                            lbr_hostname = "\""+lbr_tf_name+"_"+hostname+'_hostname\"'
                    elif len(lbr_hostnames) >= 2:
                        c = 1
                        for hostname in lbr_hostnames:
                            hostname = commonTools.check_tf_variable(hostname)
                            if c == len(lbr_hostnames):
                                lbr_hostname = lbr_hostname+"\""+lbr_tf_name+"_" + hostname + '_hostname\"'
                            else:
                                lbr_hostname = lbr_hostname+"\""+lbr_tf_name+"_"+hostname+'_hostname\",'
                            c += 1
                columnvalue = lbr_hostname

            if columnname == 'Rule Set Names':
                if columnvalue != '':
                    rule_sets = str(columnvalue).strip().split(',')
                    if len(rule_sets) == 1:
                        for rule in rule_sets:
                            rule = commonTools.check_tf_variable(str(rule))
                            rule_set_names = "\""+lbr_tf_name+"_"+rule+"\""
                    elif len(rule_sets) >=2 :
                        c=1
                        for rule in rule_sets:
                            if c == len(rule_sets):
                                rule = commonTools.check_tf_variable(str(rule))
                                rule_set_names = rule_set_names+"\""+lbr_tf_name+"_"+rule+"\""
                            else:
                                rule = commonTools.check_tf_variable(str(rule))
                                rule_set_names = rule_set_names+"\""+lbr_tf_name+"_"+ rule + '\",'
                            c += 1
                columnvalue = rule_set_names

            if columnname == 'Verify Peer Certificate':
                if str(columnvalue).lower() == 'true':
                    if str(df.loc[i,'Verify Depth']) == '' or str(df.loc[i,'Verify Depth']) == 'nan':
                        print("\nVerify Depth cannot be left empty when Verify Peer Certificate has a value... Exiting!!!")
                        exit(1)

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
                    exit(1)

                elif columnvalue != '' and str(df.loc[i,'Cipher Suite Name']) == 'nan':
                    print("NOTE: Cipher Suite Name is not specified for Listener -> "+str(df.loc[i,'Listener Name'])+", default value - 'oci-default-ssl-cipher-suite-v1' will be considered.")

                else:
                    pass

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Render Backend Set
        listener_str[region] = listener_str[region] + listener.render(tempStr)

    for reg in ct.all_regions:

        if listener_str[reg] != '':

            # Generate Final String
            src = "##Add New Listeners for "+reg.lower()+" here##"
            listener_str[reg] = listener.render(skeleton=True, count=0, region=reg).replace(src,listener_str[reg]+"\n"+src)
            finalstring = "".join([s for s in listener_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            srcdir = outdir + "/" + reg + "/" + service_dir + "/"

            # Write to TF file
            outfile = srcdir + lb_auto_tfvars_filename
            oname = open(outfile, "w+")
            print("Writing to " + outfile)
            oname.write(finalstring)
            oname.close()

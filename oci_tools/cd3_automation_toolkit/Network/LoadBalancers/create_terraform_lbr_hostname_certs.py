#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# LBR,Hostname,Certificates
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#
import re
import shutil
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
    parser = argparse.ArgumentParser(description="Creates TF files for LBR")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


# If input file is CD3
def create_terraform_lbr_hostname_certs(inputfile, outdir, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    lbr = env.get_template('lbr-template')
    hostname = env.get_template('hostname-template')
    certficate = env.get_template('certificate-template')
    ciphersuite =  env.get_template('cipher-suite-template')

    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    lbr_str = {}
    hostname_str = {}
    certificate_str = {}
    cipher_suites = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "LB-Hostname-Certs")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    #DF with just the load balancer names and the Cert details

    # fill the empty values with that in previous row.
    dffill = df[['Region','LBR Name']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','LBR Name']]
    dfdrop = df.drop(dfdrop, axis=1)

    #dfcert with required details
    dfcert = pd.concat([dffill, dfdrop], axis=1)


    oracle_cipher_suites = ['oci-default-ssl-cipher-suite-v1', 'oci-modern-ssl-cipher-suite-v1',
                            'oci-compatible-ssl-cipher-suite-v1', 'oci-wider-compatible-ssl-cipher-suite-v1',
                            'oci-customized-ssl-cipher-suite']

    # Take backup of files
    for reg in ct.all_regions:
        resource='LB-Hostname-Certs'
        srcdir = outdir + "/" + reg + "/"
        commonTools.backup_file(srcdir, resource, "_certificate-lb.tf")
        commonTools.backup_file(srcdir, resource, "_lbr-hostname-lb.tf")
        commonTools.backup_file(srcdir, resource,"_cipher-suite-lb.tf")

        lbr_str[reg] = ''
        hostname_str[reg] = ''
        certificate_str[reg] = ''
        cipher_suites[reg] = ''

    def certificate_templates(dfcert):

        # List of the column headers
        dfcolumns = dfcert.columns.values.tolist()
        tempdict = {}
        tempStr = {}


        for i in dfcert.index:

            region = str(dfcert.loc[i, 'Region']).strip().lower()
            certificate_tf_name = ''
            ciphers_list = ''
            cipher_tf_name = ''
            lbr_tf_name=''

            if region in commonTools.endNames:
                break

            # Fetch data; loop through columns
            for columnname in dfcolumns:

                # Column value
                columnvalue = str(dfcert[columnname][i]).strip()

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

                if columnname == "CA Cert" or columnname == "Public Cert" or columnname == "Private Key":
                    columnname = commonTools.check_column_headers(columnname)
                    if columnvalue != '':
                        cert_name = re.split('/|\\\\', columnvalue)[-1]
                        if columnvalue != outdir + '/' +region+'/'+ cert_name :
                            try:
                                shutil.copy(columnvalue, outdir + '/' +region+'/'+ cert_name)
                            except shutil.SameFileError:
                                pass
                        tempdict = { columnname : cert_name }

                if columnname == "Certificate Name":
                    if columnvalue != '':
                        columnvalue = str(columnvalue).strip()
                        certificate_tf_name = commonTools.check_tf_variable(columnvalue)
                        tempdict = {'certificate_tf_name': certificate_tf_name}

                    else:
                        certificate_tf_name = ''
                        tempdict = {'certificate_tf_name': certificate_tf_name}

                if columnname == 'Cipher Suite Name':
                    if str(columnvalue).strip() != '':
                        cipher_tf_name = commonTools.check_tf_variable(columnvalue)
                        tempdict = { 'cipher_tf_name' : cipher_tf_name }
                        tempStr.update(tempdict)

                        if columnvalue.strip().lower() in oracle_cipher_suites:
                            print("User-defined cipher suite must not be the same as any of Oracle's predefined or reserved SSL cipher suite names... Exiting!!")
                            exit()

                        if str(df.loc[i,'Ciphers']).strip() == '':
                            print("Ciphers Column cannot be left blank when Cipher Suite Name has a value.....Exiting!!")
                            exit()
                    else:
                            columnvalue = ""

                if columnname == 'Ciphers':
                    columnvalue = columnvalue.strip()
                    if columnvalue != '':
                        columnvalue = columnvalue.split(',')
                        for ciphers in columnvalue:
                            ciphers_list = "\""+ciphers+"\","+ciphers_list

                        if (ciphers_list != "" and ciphers_list[-1] == ','):
                            ciphers_list = ciphers_list[:-1]

                        tempdict = {'ciphers' : ciphers_list}
                        tempStr.update(tempdict)

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = str(columnvalue).strip()
                tempStr.update(tempdict)


            if cipher_tf_name != '' and cipher_tf_name.lower() != 'nan':
                cipher_suites[region] = ciphersuite.render(tempStr)

                outfile = outdir + "/" + region + "/"+lbr_tf_name+"_"+cipher_tf_name+"_cipher-suite-lb.tf"
                oname = open(outfile, "w+")
                print("Writing to " + outfile)
                oname.write(cipher_suites[region])
                oname.close()

            if certificate_tf_name != '' and certificate_tf_name.lower() != 'nan':
                certificate_str[region] =  certficate.render(tempStr)

                # Write to TF file
                outfile = outdir + "/" + region + "/"+lbr_tf_name+"_"+certificate_tf_name+"_certificate-lb.tf"
                oname = open(outfile, "w+")
                print("Writing to " + outfile)
                oname.write(certificate_str[region])
                oname.close()


    #create Certificates
    certificate_templates(dfcert)

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
        nsg_id = ''
        lbr_tf_name= ''
        host_list =[]

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

            if columnname == "Is Private(True|False)":
                columnname = 'is_private'

            if columnname == "Compartment Name":
                columnname = "compartment_tf_name"
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == "LBR Name":
                if columnvalue != '':
                    lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == "Shape(100Mbps|400Mbps|8000Mbps|flexible)":
                columnname = 'lbr_shape'
                if str(columnvalue).lower() == 'flexible':
                    columnvalue = 'flexible'

            if columnname == "Minimum Bandwidth In Mbps (Flexible shapes only)":
                columnname = "min_bandwidth"

            if columnname == "Maximum Bandwidth In Mbps (Flexible shapes only)":
                columnname = "max_bandwidth"

            if columnname == "LBR Hostname(Name:Hostname)":
                columnname = "lbr_hostname"

            if columnname == 'LBR Subnets':
                lbr_subnets = str(columnvalue).strip().split(",")
                if len(lbr_subnets) == 1:
                    columnvalue = "merge(module.subnets.*...)[\"" + commonTools.check_tf_variable(str(lbr_subnets[0]).strip()) + "\"][\"subnet_tf_id\"]"

                elif len(lbr_subnets) == 2:
                    columnvalue = "merge(module.subnets.*...)[\"" + commonTools.check_tf_variable(str(lbr_subnets[0]).strip()) + "\"][\"subnet_tf_id\"], merge(module.subnets.*...)[\"" + commonTools.check_tf_variable(str(lbr_subnets[0]).strip()) + "\"][\"subnet_tf_id\"]"

            if columnname == "NSGs":
                if columnvalue != '':
                    lbr_nsgs = str(columnvalue).strip().split(",")
                    if len(lbr_nsgs) == 1:
                        for nsgs in lbr_nsgs:
                            if "ocid" in nsgs.strip():
                                nsg_id = "\"" + nsgs.strip() + "\""
                            else:
                                nsg_id = "merge(module.nsgs.*...)[\""+commonTools.check_tf_variable(str(nsgs).strip())+"\"][\"nsg_tf_id\"]"

                    elif len(lbr_nsgs) >=2 :
                        c = 1
                        for nsgs in lbr_nsgs:
                            if "ocid" in nsgs.strip():
                                data = "\"" + nsgs.strip() + "\""
                            else:
                                data = "merge(module.nsgs.*...)[\""+commonTools.check_tf_variable(str(nsgs).strip())+"\"][\"nsg_tf_id\"]"

                            if c == len(lbr_nsgs):
                                nsg_id = nsg_id + data
                            else:
                                nsg_id = nsg_id + data +","
                            c += 1
                columnvalue = nsg_id

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

            if columnname == "lbr_hostname":
                if columnvalue != '':
                    hostname_str[region] = ''
                    lbr_hostnames = columnvalue.strip().split(",")
                    if len(lbr_hostnames) == 1:
                        for hostnames in lbr_hostnames:
                            hostnames = hostnames.split(":")
                            name = hostnames[0]
                            hostname_value = hostnames[1]

                            lbr_host_tf_name = lbr_tf_name+"_"+commonTools.check_tf_variable(name)
                            lbr_hosname = hostname_value
                            host_list.append(lbr_host_tf_name)
                            tempdict = {'host_tf_name': lbr_host_tf_name,'hostname' : lbr_hosname,'name' : name}

                            columnname = commonTools.check_column_headers(columnname)
                            tempStr[columnname] = str(columnvalue).strip()
                            tempStr.update(tempdict)

                            hostname_str[region] = hostname.render(tempStr)

                    elif len(lbr_hostnames) >=2 :
                        c = 1
                        hostname_str[region] = ''
                        for hostnames in lbr_hostnames:
                            if c <= len(lbr_hostnames):
                                hostnames = hostnames.split(":")
                                name = hostnames[0]
                                hostname_value = hostnames[1]

                                lbr_host_tf_name = lbr_tf_name + "_" + commonTools.check_tf_variable(name)
                                lbr_hosname = hostname_value
                                host_list.append(lbr_host_tf_name)
                                tempdict = {'host_tf_name': lbr_host_tf_name, 'hostname': lbr_hosname,'name':name}

                                columnname = commonTools.check_column_headers(columnname)
                                tempStr[columnname] = str(columnvalue).strip()
                                tempStr.update(tempdict)

                            hostname_str[region] = hostname_str[region] + hostname.render(tempStr)
                            c += 1
                else:
                    hostname_str[region] = ''

        if lbr_tf_name != '':
            lbr_str[region] = lbr.render(tempStr)
            finalstring = hostname_str[region] + lbr_str[region]

            # Write to TF file
            outfile = outdir + "/" + region + "/"+lbr_tf_name+"_lbr-hostname-lb.tf"
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(finalstring)
            oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_terraform_lbr_hostname_certs(args.inputfile, args.outdir, args.config)
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
    parser = argparse.ArgumentParser(description="Creates TF files for LBR")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    lbr = env.get_template('lbr-template')
    hostname = env.get_template('hostname-template')
    certficate = env.get_template('certificate-template')

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

    lbr_str = {}
    hostname_str = {}
    certificate_str = {}

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

    unique_region = df['Region'].unique()

    # Take backup of files
    for eachregion in unique_region:
        eachregion = str(eachregion).strip().lower()
        if (eachregion in commonTools.endNames):
            break
        if eachregion == 'nan':
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        resource='LB-Hostname-Certs'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-lb.tf")

    for reg in ct.all_regions:
        if reg not in commonTools.endNames and  reg != 'nan':
            lbr_str[reg] = ''
            hostname_str[reg] = ''
            certificate_str[reg] = ''

    def certificate_templates(dfcert):

        # List of the column headers
        dfcolumns = dfcert.columns.values.tolist()
        tempdict = {}
        tempStr = {}
        certificate_tf_name = ''

        for i in dfcert.index:

            region = str(dfcert.loc[i, 'Region']).strip().lower()

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

                if columnname == "Certificate Name":
                    if columnvalue != '':
                        columnvalue = str(columnvalue).strip()
                        certificate_tf_name = commonTools.check_tf_variable(columnvalue)

                    else:
                        certificate_tf_name = ''
                    tempdict = {'certificate_tf_name': certificate_tf_name}

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = str(columnvalue).strip()
                tempStr.update(tempdict)

            if certificate_tf_name != '' and certificate_tf_name.lower() != 'nan':
                certificate_str[region] =  certficate.render(tempStr)

            # Write to TF file
            outfile = outdir + "/" + region + "/"+certificate_tf_name+"-certificate-lb.tf"
            oname = open(outfile, "w+")
            print("Writing to ..." + outfile)
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
                lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == "Shape(100Mbps|400Mbps|8000Mbps)":
                columnname = 'lbr_shape'

            if columnname == "LBR Hostname\n(Name:Hostname)":
                columnname = "lbr_hostname"

            if columnname == 'LBR Subnets':
                lbr_subnets = str(columnvalue).strip().split(",")
                if len(lbr_subnets) == 1:
                    columnvalue = "oci_core_subnet." + commonTools.check_tf_variable(str(lbr_subnets[0]).strip()) + ".id"

                elif len(lbr_subnets) == 2:
                    columnvalue = "oci_core_subnet." + commonTools.check_tf_variable(str(lbr_subnets[0]).strip()) + ".id, oci_core_subnet." + commonTools.check_tf_variable(str(lbr_subnets[1]).strip()) + ".id"

            if columnname == "NSGs":
                if columnvalue != '':
                    lbr_nsgs = str(columnvalue).strip().split(",")
                    if len(lbr_nsgs) == 1:
                        for nsgs in lbr_nsgs:
                            nsg_id = "oci_core_network_security_group." + nsgs + ".id"
                    elif len(lbr_nsgs) >=2 :
                        c = 1
                        for nsgs in lbr_nsgs:
                            if c == len(lbr_nsgs):
                                nsg_id = nsg_id + "oci_core_network_security_group."+nsgs+".id"
                            else:
                                nsg_id = nsg_id + "oci_core_network_security_group."+nsgs+".id,"
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

        lbr_str[region] = lbr.render(tempStr)
        finalstring = hostname_str[region] + lbr_str[region]

        # Write to TF file
        outfile = outdir + "/" + region + "/"+lbr_tf_name+"-lbr-hostname-lb.tf"
        oname = open(outfile, "w+")
        print("Writing to ..."+outfile)
        oname.write(finalstring)
        oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    main()
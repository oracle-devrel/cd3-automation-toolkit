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
import json
import shutil
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######
# Execution of the code begins here
def create_terraform_lbr_hostname_certs(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    lbr = env.get_template('lbr-template')
    hostname = env.get_template('hostname-template')
    certficate = env.get_template('certificate-template')
    ciphersuite =  env.get_template('cipher-suite-template')
    reserved_ips_template = env.get_template('lbr-reserved-ips-template')
    sheetName = "LB-Hostname-Certs"
    lb_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile

    lbr_str = {}
    reserved_ips_str = {}
    hostname_str = {}
    hostname_str_02 = {}
    certificate_str = {}
    cipher_suites = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

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
        lbr_str[reg] = ''
        hostname_str[reg] = ''
        reserved_ips_str[reg] = ''
        certificate_str[reg] = ''
        cipher_suites[reg] = ''
        hostname_str_02[reg] = ''
        resource = sheetName.lower()
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, lb_auto_tfvars_filename)

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
                        if columnvalue != outdir + '/' +region+ "/"+ service_dir+ '/'+ cert_name :
                            try:
                                shutil.copy(columnvalue, outdir + '/' +region+'/'+ service_dir+ "/"+ cert_name)
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
                            exit(1)

                        if str(df.loc[i,'Ciphers']).strip() == '':
                            print("Ciphers Column cannot be left blank when Cipher Suite Name has a value.....Exiting!!")
                            exit(1)
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
                cipher_suites[region] = cipher_suites[region] + ciphersuite.render(tempStr)

            if certificate_tf_name != '' and certificate_tf_name.lower() != 'nan':
                certificate_str[region] =  certificate_str[region] + certficate.render(tempStr)

    #create Certificates
    certificate_templates(dfcert)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    #subnets = parseSubnets(filename)

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if region.lower() == 'nan':
            continue

        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region != 'nan' and region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the regions tenancy is subscribed to...Exiting!!")
            exit(1)

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
                tempdict = {'compartment_tf_name': columnvalue}

            if columnname == "LBR Name":
                if columnvalue != '':
                    lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == "Shape(10Mbps|100Mbps|400Mbps|8000Mbps|flexible)":
                columnname = 'lbr_shape'
                if str(columnvalue).lower() == 'flexible':
                    columnvalue = 'flexible'

            if columnname == "Minimum Bandwidth In Mbps (Flexible shapes only)":
                columnname = "min_bandwidth"

            if columnname == "Maximum Bandwidth In Mbps (Flexible shapes only)":
                columnname = "max_bandwidth"

            if columnname == "LBR Hostname(Name:Hostname)":
                columnname = "lbr_hostname"

            if columnname == "Reserved IP (Y|N|OCID)":
                columnname = "reserved_ips_id"

            lbr_subnets_list = []
            network_compartment_id = ''
            vcn_name = ''
            if columnname == 'Network Details':
                lbr_subnets = str(columnvalue).strip().split(",")
                if len(lbr_subnets) == 1:
                    columnvalue=str(lbr_subnets[0]).strip()
                    if ("ocid1.subnet.oc" in columnvalue):
                        network_compartment_id = "root"
                        vcn_name = ""
                        subnet_id = columnvalue
                    elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                        if len(columnvalue.split("@")) == 2:
                            network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                            vcn_subnet_name = columnvalue.split("@")[1].strip()
                        else:
                            network_compartment_id = commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip())
                            vcn_subnet_name = columnvalue
                        if ("::" not in vcn_subnet_name):
                            print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                            exit(1)
                        else:
                            vcn_name = vcn_subnet_name.split("::")[0].strip()
                            subnet_id = vcn_subnet_name.split("::")[1].strip()

                    lbr_subnets_list.append(subnet_id)
                    tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,'lbr_subnets': json.dumps(lbr_subnets_list)}
                elif len(lbr_subnets) == 2:
                    for subnet in lbr_subnets:
                        columnvalue=subnet
                        if ("ocid1.subnet.oc" in columnvalue):
                            network_compartment_id = "root"
                            vcn_name = ""
                            subnet_id = columnvalue
                        elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                            if len(columnvalue.split("@")) == 2:
                                network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                                vcn_subnet_name = columnvalue.split("@")[1].strip()
                            else:
                                network_compartment_id = commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip())
                                vcn_subnet_name = columnvalue
                            if ("::" not in vcn_subnet_name):
                                print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                                exit(1)
                            else:
                                vcn_name = vcn_subnet_name.split("::")[0].strip()
                                subnet_id = vcn_subnet_name.split("::")[1].strip()
                        lbr_subnets_list.append(subnet_id)
                        tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,'lbr_subnets': json.dumps(lbr_subnets_list)}

            if columnname == "NSGs":
                if columnvalue != '':
                    lbr_nsgs = str(columnvalue).strip().split(",")
                    if len(lbr_nsgs) == 1:
                        for nsgs in lbr_nsgs:
                            nsg_id = "\"" + nsgs.strip() + "\""

                    elif len(lbr_nsgs) >=2 :
                        c = 1
                        for nsgs in lbr_nsgs:
                            data = "\"" + nsgs.strip() + "\""

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

                            hostname_str[region] = hostname_str[region] +  hostname.render(tempStr)

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

        lbr_str[region] = lbr_str[region] + lbr.render(tempStr)
        hostname_str_02[region] = hostname_str_02[region] + hostname_str[region]
        if tempStr['reserved_ips_id'].lower() == 'y':
            reserved_ips_str[region] = reserved_ips_str[region] + reserved_ips_template.render(tempStr)

    for reg in ct.all_regions:
        if lbr_str[reg] != '':
            # Generate Final String
            src = "##Add New Load Balancers for "+reg.lower()+" here##"
            lbr_str[reg] = lbr.render(skeleton=True, count=0, region=reg).replace(src,lbr_str[reg]+"\n"+src)

        if hostname_str_02[reg] != '':
            # Generate Final String
            src = "##Add New Hostnames for " + reg.lower() + " here##"
            hostname_str_02[reg] = hostname.render(skeleton=True, count=0, region=reg).replace(src, hostname_str_02[reg]+"\n"+src)

        if certificate_str[reg] != '':
            # Generate Final String
            src = "##Add New Certificates for " + reg.lower() + " here##"
            certificate_str[reg] = certficate.render(skeleton=True, count = 0, region=reg).replace(src, certificate_str[reg]+"\n"+src)

        if cipher_suites[reg] != '':
            # Generate Final String
            src = "##Add New Ciphers for " + reg.lower() + " here##"
            cipher_suites[reg] = ciphersuite.render(skeleton=True, count = 0, region=reg).replace(src, cipher_suites[reg]+"\n"+src)

        if reserved_ips_str[reg] != '':
            # Generate Final String
            src = "##Add New Load Balancer Reserved IPs for "+ reg.lower() +" here##"
            reserved_ips_str[reg] = reserved_ips_template.render(skeleton=True, count = 0, region=reg).replace(src, reserved_ips_str[reg]+"\n"+src)

        finalstring =  lbr_str[reg] + hostname_str_02[reg] + certificate_str[reg] + cipher_suites[reg] + reserved_ips_str[reg]
        finalstring = "".join([s for s in finalstring.strip().splitlines(True) if s.strip("\r\n").strip()])

        if finalstring != "":
            srcdir = outdir + "/" + reg + "/" + service_dir + "/"

            # Write to TF file
            outfile = srcdir + lb_auto_tfvars_filename
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(finalstring)
            oname.close()

#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Network Load Balancer Backend Set and Backend Server
#
# Author: Suruchi Singla
# Oracle Consulting
#
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######
# Execution of the code begins here
def create_nlb_backendset_backendservers(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    beset = env.get_template('nlb-backend-set-template')
    beserver = env.get_template('nlb-backends-template')
    filename = inputfile
    sheetName = "NLB-BackendSets-BackendServers"
    lb_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    beset_str = {}
    beserver_str = {}
    nlb_tf_name = ''
    nlb_name = ''
    nlb_names = {}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # Take backup of files
    for reg in ct.all_regions:
        beset_str[reg] = ''
        beserver_str[reg] = ''
        nlb_names[reg] = []
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, lb_auto_tfvars_filename)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    prevreg = ''
    prevcomp=''

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if region.lower() != 'nan':
            region = region.strip().lower()
            prevreg = region

        region = region.strip().lower()

        if region in commonTools.endNames:
            break


        if region != 'nan' and region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the values mentioned in VCN Info tab...Exiting!!")
            exit(1)
        compname = str(df.loc[i, 'Compartment Name'])

        if compname.lower() != 'nan':
            compname = compname.strip()
            prevcomp = compname


        # temporary dictionaries
        tempStr= {}
        tempdict= {}
        backend_set_tf_name = ''

        #Check if mandatory field is empty
        if (str(df.loc[i,'Backend Set Name']).lower() == 'nan' or str(df.loc[i,'Backend HealthCheck Port']).lower() == 'nan'):
            print("\nColumn Backend Set Name or Backend HealthCheck Port cannot be left empty.....Exiting!")
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

            if columnname == "NLB Name":
                if columnvalue != '' and columnvalue != 'nan':
                    nlb_name = columnvalue
                    nlb_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'nlb_tf_name': nlb_tf_name, 'nlb_name': nlb_name}

            if columnname == "Backend Set Name":
                backend_set_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'backend_set_tf_name': backend_set_tf_name, 'backend_set_name': columnvalue}

            if columnname == "Backend Policy(FIVE_TUPLE|THREE_TUPLE|TWO_TUPLE)":
                columnname = 'backend_policy'
                if columnvalue == '':
                    columnvalue = "FIVE_TUPLE"

            if columnname == "Backend HealthCheck Protocol(HTTP|HTTPS|TCP|UDP|DNS)":
                columnname = "backend_healthcheck_protocol"
                if columnvalue == '':
                    columnvalue = "HTTP"

            if columnname == "Is Preserve Source(True|False)":
                columnname = "is_preserve_source"

            if columnname == "Backend HealthCheck Interval In Millis":
                columnname = 'interval_in_millis'

            if columnname == "Backend ServerComp@ServerName:Port":
                columnname = "backend_server"

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Render Backend Set
        if(region == 'nan' and str(df.loc[i,'Compartment Name']).lower() == 'nan' and str(df.loc[i,'NLB Name']).lower() == 'nan'):
            region=prevreg
        beset_str[region] = beset_str[region] + beset.render(tempStr)

        cnt = 0

        #beserver_str = ''
        columnvalue = str(df.loc[i,'Backend ServerComp@ServerName:Port']).strip().split(',')
        for nlb_be_server in columnvalue:

            nlb_be_server = nlb_be_server.strip()

            if (nlb_be_server != "" and nlb_be_server != "nan"):
                cnt = cnt + 1

                inst_compartment_tf_name = commonTools.check_tf_variable(prevcomp).strip()
                #inst_compartment_tf_name = tempStr['compartment_tf_name']
                if len(nlb_be_server.split("@")) == 2:
                    if (len(nlb_be_server.split("@")[0].strip()) != 0):
                        inst_compartment_tf_name = commonTools.check_tf_variable(nlb_be_server.split("@")[0].strip())
                    serverinfo = nlb_be_server.split("@")[1]
                else:
                    serverinfo = nlb_be_server
                if (":" not in serverinfo):
                    print("Invalid Backend ServerComp@ServerName:Port format specified for row " + str(
                        i + 3) + ". Exiting!!!")
                    exit(1)
                else:
                    servername = serverinfo.split(":")[0].strip()
                    serverport = serverinfo.split(":")[1].strip()

                backend_server_tf_name = commonTools.check_tf_variable(servername + "-" + serverport)
                e = servername.count(".")
                if (e == 3):
                    backend_server_ip_address = "IP:" + servername
                    servername = ""
                else:
                    backend_server_ip_address = "NAME:" + servername

                tempback = {'backend_server_tf_name': backend_set_tf_name+"_"+backend_server_tf_name,'serverport':serverport,'backend_server_ip_address':backend_server_ip_address, 'instance_tf_compartment': inst_compartment_tf_name, 'servername': servername }
                tempStr.update(tempback)

                # Render Backend Server
                beserver_str[region] = beserver_str[region] + beserver.render(tempStr)


    for reg in ct.all_regions:
        if beset_str[reg] != '':
            # Generate Final String
            src = "##Add New Backend Sets for "+reg.lower()+" here##"
            beset_str[reg] = beset.render(skeleton=True, count=0, region=reg).replace(src,beset_str[reg]+"\n"+src)
        if beserver_str[reg] != '':
            # Generate Final String
            src = "##Add New Backends for "+reg.lower()+" here##"
            beserver_str[reg] = beserver.render(skeleton=True, count=0, region=reg).replace(src,beserver_str[reg]+"\n"+src)

        finalstring = beset_str[reg] + beserver_str[reg]
        finalstring = "".join([s for s in finalstring.strip().splitlines(True) if s.strip("\r\n").strip()])

        if finalstring != "":

            srcdir = outdir + "/" + reg + "/" + service_dir + "/"

            # Write to TF file
            outfile = srcdir + lb_auto_tfvars_filename
            oname = open(outfile, "w+")
            print("Writing to " + outfile)
            oname.write(finalstring)
            oname.close()

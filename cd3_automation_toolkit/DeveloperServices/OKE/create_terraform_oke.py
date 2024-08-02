#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# OKE cluster and nodepools
#
# Author: Divya Das
# Oracle Consulting
#
import os
import json
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
import commonTools
from commonTools import *
from jinja2 import Environment, FileSystemLoader


######
# Required Inputs-CD3 excel file, Config file AND outdir
######
# Execution of the code begins here
def create_terraform_oke(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    cluster = env.get_template('cluster-template')
    node = env.get_template('nodepool-template')
    virtual_node = env.get_template('virtual-nodepool-template')
    sheetName = "OKE"
    cluster_auto_tfvars_filename = prefix + "_" "oke_clusters.auto.tfvars"
    nodepool_auto_tfvars_filename = prefix + "_" "oke_nodepools.auto.tfvars"
    virtual_nodepool_auto_tfvars_filename = prefix + "_" "oke_virtual-nodepools.auto.tfvars"
    ADS = ["AD1", "AD2", "AD3"]

    filename = inputfile
    cluster_str = {}
    node_str = {}
    virtual_node_str ={}

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # fill the empty values with that in previous row.
    dffill = df[
        ['Region', 'Compartment Name', 'Cluster Name', 'Cluster Kubernetes Version','Network Type', 'Pod Security Policies Enforced',
         'Load Balancer Network Details', 'API Endpoint Network Details']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[
        ['Region', 'Compartment Name', 'Cluster Name', 'Cluster Kubernetes Version','Network Type', 'Pod Security Policies Enforced',
         'Load Balancer Network Details', 'API Endpoint Network Details']]
    dfdrop = df.drop(dfdrop, axis=1)
    df = pd.concat([dffill, dfdrop], axis=1)

    # Take backup of files
    for reg in ct.all_regions:
        cluster_str[reg] = ''
        node_str[reg] = ''
        virtual_node_str[reg] = ''
        resource = sheetName.lower()
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, cluster_auto_tfvars_filename)
        commonTools.backup_file(srcdir, resource, nodepool_auto_tfvars_filename)
        commonTools.backup_file(srcdir, resource, virtual_nodepool_auto_tfvars_filename)

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

        if region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the values mentioned in VCN Info tab...Exiting!!")
            exit(1)


        # temporary dictionaries
        tempStr= {}
        tempdict= {}
        nsg_id = ''

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'Cluster Name']).lower() == 'nan' or \
                str(df.loc[i, 'Network Type']).lower() == 'nan' or \
                str(df.loc[i, 'Cluster Kubernetes Version']).lower() == 'nan' or \
                str(df.loc[i, 'Pod Security Policies Enforced']).lower() == 'nan' or \
                str(df.loc[i, 'Load Balancer Network Details']).lower() == 'nan' or \
                str(df.loc[i, 'API Endpoint Network Details']).lower() == 'nan':
            print(
                "\nRegion, Compartment Name, Cluster Name, Network Type, Cluster Kubernetes Version, Pod Security Policies, Load Balancer Network Details, API Endpoint Network Details fields are mandatory. Please enter a value and try again !!\n\nPlease fix it for row : {}".format(
                    i + 3))
            print("\n** Exiting **")
            exit(1)
        if str(df.loc[i, 'CompartmentName@Node Pool Name:Node Pool Type']).lower() != 'nan':
            nodepool_tf_name_type = str(df.loc[i, 'CompartmentName@Node Pool Name:Node Pool Type']).strip().split("@")[1]
            if (":" in nodepool_tf_name_type):
                nodepool_type = nodepool_tf_name_type.split(":")[1]
                nodepool_type = nodepool_type.lower()
            else:
                nodepool_type = 'managed'

            if str(df.loc[i, 'Worker Node Network Details']).lower() == 'nan' or \
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan':
                print("\nCompartmentName@Node Pool Name:Node Pool Type, Worker Node Network Details and Availability Domain(AD1|AD2|AD3) fields are mandatory. \n\nPlease fix it for row : {} and try again.".format(i+3))
                print("\n** Exiting **")
                exit(1)
            if (nodepool_type == "managed"):
                if  str(df.loc[i, 'Nodepool Kubernetes Version']).lower() == 'nan' or \
                    str(df.loc[i, 'Shape']).lower() == 'nan' or \
                    str(df.loc[i, 'Source Details']).lower() == 'nan' or \
                    str(df.loc[i, 'Number of Nodes']).lower() == 'nan' or \
                    str(df.loc[i, 'Worker Node Network Details']).lower() == 'nan' or \
                    str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan':
                    print("\nCompartmentName@Node Pool Name:Node Pool Type, Nodepool Kubernetes Version, Shape, Source Details, Number of Nodes, Worker Node Network Details and Availability Domain(AD1|AD2|AD3) fields are mandatory. \n\nPlease fix it for row : {} and try again.".format(i+3))
                    print("\n** Exiting **")
                    exit(1)


            shapeField = str(df.loc[i, 'Shape'])
            shapeField = shapeField.strip()

            if nodepool_type == 'virtual':
                if (shapeField.lower() != 'nan' and "pod" not in shapeField.lower()):
                    print("\nERROR!!! Virtual Nodepool in row " + str(i + 3) + " is having incorrect shape....Exiting!")
                    exit(1)
            elif nodepool_type == 'managed':
                if (shapeField.lower() != "nan"):
                    if ".Micro" in shapeField or ".Flex" in shapeField:
                        if ("::" not in shapeField):
                            print("\nERROR!!! Nodepool in row " + str(
                                i + 3) + " is missing ocpus for Flex/Micro shape....Exiting!")
                            exit(1)
                        else:
                            shapeField = shapeField.split("::")
                            if (shapeField[1].strip() == ""):
                                print("\nERROR!!! Nodepool in row " + str(
                                    i + 3) + " is missing ocpus for Flex/Micro shape....Exiting!")
                                exit(1)

        '''
        if str(df.loc[i, 'Network Type']).lower() == 'oci_vcn_ip_native':
            if str(df.loc[i, 'Pod Communication Network Details']).lower() == 'nan':
                print("\nPod Communication Network Details required for cluster with networking type:OCI_VCN_IP_NATIVE")
                print("\n** Exiting **")
                exit(1)
        '''
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

            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                if columnvalue != "":
                    AD = columnvalue.upper()
                    ad = ADS.index(AD)
                    columnvalue = str(ad)
                    availability_domain = columnvalue
                else:
                    availability_domain = ""
                tempdict = {'availability_domain': availability_domain}

            if columnname == "Fault Domains":
                if columnvalue != "":
                    columnvalue =  ','.join(['"' + x.upper() + '"' for x in columnvalue.split(',')])

            if columnname == "Compartment Name":
                columnname = "compartment_tf_name"
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == "Cluster Name":
                if columnvalue != '':
                    cluster_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'cluster_tf_name': cluster_tf_name, 'cluster_display_name': columnvalue}

            if columnname == "CompartmentName@Node Pool Name:Node Pool Type":
                if columnvalue != '':
                    try:
                        node_compartment = columnvalue.split("@")[0]
                        node_compartment = commonTools.check_tf_variable(node_compartment)
                        nodepool_tf_name_type = columnvalue.split("@")[1]
                        nodepool_tf_name = nodepool_tf_name_type.split(":")[0]
                        nodepool_tf_name = commonTools.check_tf_variable(nodepool_tf_name)
                        nodepool_display_name = nodepool_tf_name
                        if (":" in nodepool_tf_name_type):
                            nodepool_type = nodepool_tf_name_type.split(":")[1]
                            nodepool_type = nodepool_type.lower()
                        else:
                            nodepool_type = "managed"

                        tempdict = {'nodepool_tf_name': nodepool_tf_name, 'node_compartment': node_compartment, 'nodepool_display_name' : nodepool_display_name, 'nodepool_type' : nodepool_type}
                    except:
                        print("Error in row {} for column '{}'. Check if the value is in correct format.".format(i+3,columnname))
                        exit(0)

            if columnname == 'Shape':
                if ".Flex" not in columnvalue and ".Micro" not in columnvalue:
                    columnvalue = columnvalue.strip()
                    tempdict = {'shape': [columnvalue]}

            if columnname == "SSH Key Var Name":
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    if "ssh-rsa" in columnvalue.strip():
                        ssh_key_var_name = "\"" + columnvalue.strip() + "\""
                    else:
                        ssh_key_var_name = columnvalue.strip()
                    tempdict = {'ssh_key_var_name': ssh_key_var_name}

            if columnname.lower() == "taints key,value,effect":
                columnvalue = columnvalue.strip()
                if columnvalue != '' and columnvalue.lower() != 'nan':
                    taints = columnvalue.split("\n")
                else:
                    taints='nan'
                tempdict = {'taints': taints}

            oke_lb_subnets_list = []
            if columnname == 'Load Balancer Network Details':
                if columnvalue!='':
                    oke_lb_subnets = str(columnvalue).strip().split(",")
                    if len(oke_lb_subnets) == 1:
                        columnvalue = str(oke_lb_subnets[0]).strip()
                        if ("ocid1.subnet.oc" in columnvalue):
                            subnet_id = columnvalue
                            oke_lb_subnets_list.append(subnet_id)
                            tempdict = {'oke_lb_subnets': json.dumps(oke_lb_subnets_list)}

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
                            oke_lb_subnets_list.append(subnet_id)
                            tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,'oke_lb_subnets': json.dumps(oke_lb_subnets_list)}
                elif len(oke_lb_subnets) > 1:
                    for subnet in oke_lb_subnets:
                        columnvalue = subnet
                        if ("ocid1.subnet.oc" in columnvalue):
                            subnet_id = columnvalue
                            oke_lb_subnets_list.append(subnet_id)
                            tempdict = {'oke_lb_subnets': json.dumps(oke_lb_subnets_list)}
                        elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                            if len(columnvalue.split("@")) == 2:
                                network_compartment_id = commonTools.check_tf_variable(
                                    columnvalue.split("@")[0].strip())
                                vcn_subnet_name = columnvalue.split("@")[1].strip()
                            else:
                                network_compartment_id = commonTools.check_tf_variable(
                                    str(df.loc[i, 'Compartment Name']).strip())
                                vcn_subnet_name = columnvalue
                            if ("::" not in vcn_subnet_name):
                                print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                                exit(1)
                            else:
                                vcn_name = vcn_subnet_name.split("::")[0].strip()
                                subnet_id = vcn_subnet_name.split("::")[1].strip()
                            oke_lb_subnets_list.append(subnet_id)
                            tempdict = {'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                                    'oke_lb_subnets': json.dumps(oke_lb_subnets_list)}

            if columnname == 'API Endpoint Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    network_compartment_id="root"
                    vcn_name=""
                    subnet_id = columnvalue
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(
                            str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,
                            'api_endpoint_subnet': subnet_id}

            if columnname == 'Worker Node Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    subnet_id = columnvalue
                    tempdict = {'worker_node_subnet': subnet_id}
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(
                            str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                    tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,
                            'worker_node_subnet': subnet_id}

            if columnname == 'Pod Communication Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    subnet_id = columnvalue
                    tempdict = {'pod_communication_subnet': subnet_id}
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(
                            str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                    tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,
                            'pod_communication_subnet': subnet_id}

            if columnname == "API Endpoint NSGs":
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg_str = ""
                    nsg = ""
                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg = "\"" + NSGs[k].strip() + "\""

                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    columnvalue = nsg_str

            if columnname == "Nodepool NSGs":
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg_str = ""
                    nsg = ""
                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg = "\"" + NSGs[k].strip() + "\""

                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    columnvalue = nsg_str

            if columnname == 'Pod NSGs':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg_str = ""
                    nsg = ""
                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg = "\"" + NSGs[k].strip() + "\""

                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    columnvalue = nsg_str

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        if tempStr['compartmentname_node_pool_name_node_pool_type'] != "":
            if nodepool_type=='managed':
                node_str[region] = node_str[region] + node.render(tempStr)
            elif nodepool_type=='virtual':
                virtual_node_str[region] = virtual_node_str[region] + virtual_node.render(tempStr)

        if i!=0 and (df.loc[i, 'Cluster Name'] == df.loc[i-1, 'Cluster Name']) and (df.loc[i, 'Region'] == df.loc[i-1, 'Region']):
            continue
        cluster_str[region] = cluster_str[region] + cluster.render(tempStr)

    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if cluster_str[reg] != '':
            # Generate Final String
            src = "##Add New Cluster for "+reg.lower()+" here##"
            cluster_str[reg] = cluster.render(skeleton=True, count=0, region=reg).replace(src,cluster_str[reg]+"\n"+src)
            cluster_str[reg] = "".join([s for s in cluster_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            resource = sheetName.lower()

            # Write to TF file
            outfile = reg_out_dir + "/" + cluster_auto_tfvars_filename
            cluster_str[reg] = "".join([s for s in cluster_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(cluster_str[reg])
            oname.close()

        if node_str[reg] != '':
            # Generate Final String
            src = "##Add New Nodepool for "+reg.lower()+" here##"
            node_str[reg] = node.render(skeleton=True, count=0, region=reg).replace(src,node_str[reg]+"\n"+src)
            node_str[reg] = "".join([s for s in node_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            resource = sheetName.lower()


            # Write to TF file
            outfile = reg_out_dir + "/" + nodepool_auto_tfvars_filename
            node_str[reg] = "".join([s for s in node_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(node_str[reg])
            oname.close()

        if virtual_node_str[reg] != '':
            # Generate Final String
            src = "##Add New Virtual Nodepool for "+reg.lower()+" here##"
            virtual_node_str[reg] = virtual_node.render(skeleton=True, count=0, region=reg).replace(src,virtual_node_str[reg]+"\n"+src)
            virtual_node_str[reg] = "".join([s for s in virtual_node_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            resource = sheetName.lower()

            # Write to TF file
            outfile = reg_out_dir + "/" + virtual_nodepool_auto_tfvars_filename
            virtual_node_str[reg] = "".join([s for s in virtual_node_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(virtual_node_str[reg])
            oname.close()

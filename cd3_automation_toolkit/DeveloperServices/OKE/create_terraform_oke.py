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
import pprint
import re
import json
import shutil
import argparse
import pandas as pd
from oci.config import DEFAULT_LOCATION
from pathlib import Path
import commonTools
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
    parser.add_argument("service_dir",help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


# If input file is CD3
def create_terraform_oke(inputfile, outdir, service_dir, prefix, config=DEFAULT_LOCATION):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    cluster = env.get_template('cluster-template')
    node = env.get_template('nodepool-template')
    sheetName = "OKE"
    cluster_auto_tfvars_filename = prefix + "_" "oke_clusters.auto.tfvars"
    nodepool_auto_tfvars_filename = prefix + "_" "oke_nodepools.auto.tfvars"
    ADS = ["AD1", "AD2", "AD3"]

    filename = inputfile
    configFileName = config
    cluster_str = {}
    node_str = {}

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # fill the empty values with that in previous row.
    dffill = df[
        ['Region', 'Compartment Name', 'Cluster Name', 'Cluster Kubernetes Version','Network Type', 'Pod Security Policies Enforced',
         'Load Balancer Subnets', 'API Endpoint Subnet']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[
        ['Region', 'Compartment Name', 'Cluster Name', 'Cluster Kubernetes Version','Network Type', 'Pod Security Policies Enforced',
         'Load Balancer Subnets', 'API Endpoint Subnet']]
    dfdrop = df.drop(dfdrop, axis=1)
    df = pd.concat([dffill, dfdrop], axis=1)

    # Take backup of files
    for reg in ct.all_regions:
        cluster_str[reg] = ''
        node_str[reg] = ''

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    subnets = parseSubnets(filename)

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

        display_name = str(df.loc[i, 'CompartmentName&Node Pool Name'])
        shapeField = str(df.loc[i, 'Shape'])
        shapeField = shapeField.strip()
        shape_error = 0

        if (shapeField.lower() != "nan"):
            if ".Micro" in shapeField or ".Flex" in shapeField:
                if ("::" not in shapeField):
                    shape_error = 1
                else:
                    shapeField = shapeField.split("::")
                    if (shapeField[1].strip() == ""):
                        shape_error = 1

        if (shape_error == 1):
            print("\nERROR!!! " + display_name + "nodepool is missing ocpus for Flex/Micro shape....Exiting!")
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
                str(df.loc[i, 'Load Balancer Subnets']).lower() == 'nan' or \
                str(df.loc[i, 'API Endpoint Subnet']).lower() == 'nan':
            print(
                "\nRegion, Compartment Name, Cluster Name, Network Type, Cluster Kubernetes Version, Pod Security Policies, Load Balancer Subnets, API Endpoint Subnet fields are mandatory. Please enter a value and try again !!\n\nPlease fix it for row : {}".format(
                    i + 3))
            print("\n** Exiting **")
            exit()
        if str(df.loc[i, 'CompartmentName&Node Pool Name']).lower() != 'nan':
            if  str(df.loc[i, 'Nodepool Kubernetes Version']).lower() == 'nan' or \
                    str(df.loc[i, 'Shape']).lower() == 'nan' or \
                    str(df.loc[i, 'Source Details']).lower() == 'nan' or \
                    str(df.loc[i, 'Number of Nodes']).lower() == 'nan' or \
                    str(df.loc[i, 'Worker Node Subnet']).lower() == 'nan' or \
                    str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan':
                print(
                    "\nCompartmentName&Node Pool Name, Nodepool Kubernetes Version, Shape, Source Details, Number of Nodes, Worker Node Subnet and Availability Domain(AD1|AD2|AD3) fields are mandatory. \n\nPlease fix it for row : {} and try again.".format(i+3))
                print("\n** Exiting **")
                exit()
        '''
        if str(df.loc[i, 'Network Type']).lower() == 'oci_vcn_ip_native':
            if str(df.loc[i, 'Pod Communication Subnet']).lower() == 'nan':
                print("\nPod Communication Subnet required for cluster with networking type:OCI_VCN_IP_NATIVE")
                print("\n** Exiting **")
                exit()
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

            if columnname == "Compartment Name":
                columnname = "compartment_tf_name"
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == "Cluster Name":
                if columnvalue != '':
                    cluster_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'cluster_tf_name': cluster_tf_name, 'cluster_display_name': columnvalue}

            if columnname == "CompartmentName&Node Pool Name":
                if columnvalue != '':
                    try:
                        nodepool_tf_name = columnvalue.split("&")[1]
                        nodepool_display_name = nodepool_tf_name
                        node_compartment = columnvalue.split("&")[0]
                        nodepool_tf_name = commonTools.check_tf_variable(nodepool_tf_name)
                        node_compartment = commonTools.check_tf_variable(node_compartment)
                        tempdict = {'nodepool_tf_name': nodepool_tf_name, 'node_compartment': node_compartment, 'nodepool_display_name' : nodepool_display_name}
                    except:
                        print("Error in row {} for column '{}'. Check if the value is in correct format.".format(i+3,columnname))
                        exit(0)

            if columnname == 'Shape':
                if ".Flex" not in columnvalue and ".Micro" not in columnvalue:
                    columnvalue = columnvalue.strip()
                    tempdict = {'shape': [columnvalue]}

            oke_lb_subnets_list = []
            network_compartment_id = ''
            vcn_name = ''

            if columnname == "SSH Key Var Name":
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    if "ssh-rsa" in columnvalue.strip():
                        ssh_key_var_name = "\"" + columnvalue.strip() + "\""
                    else:
                        ssh_key_var_name = columnvalue.strip()
                    tempdict = {'ssh_key_var_name': ssh_key_var_name}

            if columnname == 'Load Balancer Subnets':
                oke_lb_subnets = str(columnvalue).strip().split(",")
                if len(oke_lb_subnets) == 1:
                    if len(oke_lb_subnets[0]) == 0:
                        pass
                    elif ("ocid1.subnet.oc1" in str(oke_lb_subnets[0]).strip()):
                        oke_lb_subnets_list.append(str(oke_lb_subnets[0]).strip())
                    else:
                        subnet_tf_name = commonTools.check_tf_variable(str(oke_lb_subnets[0]).strip())
                        try:
                            key = region, subnet_tf_name
                            network_compartment_id = commonTools.check_tf_variable(subnets.vcn_subnet_map[key][0])
                            vcn_name = subnets.vcn_subnet_map[key][1]
                            oke_lb_subnets_list.append(subnets.vcn_subnet_map[key][2])
                        except Exception as e:
                            print("Invalid Subnet Name specified for row {} and column \"{}\". It Doesnt exist in Subnets sheet. Exiting!!!".format(i+3,columnname))
                            exit()
                    tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_name': vcn_name,'oke_lb_subnets': json.dumps(oke_lb_subnets_list)}
                elif len(oke_lb_subnets) > 1:
                    for subnet in oke_lb_subnets:
                        if "ocid1.subnet.oc1" in subnet:
                            oke_lb_subnets_list.append(str(subnet).strip())
                        else:
                            subnet_tf_name = commonTools.check_tf_variable(str(subnet).strip())
                            try:
                                key = region, subnet_tf_name
                                network_compartment_id = commonTools.check_tf_variable(subnets.vcn_subnet_map[key][0])
                                vcn_name = subnets.vcn_subnet_map[key][1]
                                oke_lb_subnets_list.append(subnets.vcn_subnet_map[key][2])
                            except Exception as e:
                                print("Invalid Subnet Name specified for row {} and column \"{}\". It Doesnt exist in Subnets sheet. Exiting!!!".format(i+3,columnname))
                                exit()
                    tempdict = {'network_compartment_tf_name': network_compartment_id, 'vcn_tf_name': vcn_name,'oke_lb_subnets': json.dumps(oke_lb_subnets_list) }

            if columnname == 'API Endpoint Subnet':
                subnet_tf_name = str(columnvalue).strip().split()
                if len(subnet_tf_name) == 1:
                    if len(subnet_tf_name[0]) == 0:
                        pass
                    elif ("ocid1.subnet.oc1" in str(subnet_tf_name[0]).strip()):
                        api_endpoint_subnet = str(subnet_tf_name[0]).strip()
                    else:
                        try:
                            key = region, str(subnet_tf_name[0]).strip()
                            api_endpoint_subnet = subnets.vcn_subnet_map[key][2]
                        except Exception as e:
                            print("Invalid Subnet Name specified for row {} and column \"{}\". It Doesnt exist in Subnets sheet. Exiting!!!".format(i+3,columnname))
                            exit()
                    tempdict = {'api_endpoint_subnet': api_endpoint_subnet}
                elif len(subnet_tf_name) > 1:
                    print("Invalid Subnet Values for row {} and column \"{}\". Only one subnet allowed".format(i+3,columnname))
                    exit()

            if columnname == 'Worker Node Subnet':
                subnet_tf_name = str(columnvalue).strip().split()
                if len(subnet_tf_name) == 1:
                    if len(subnet_tf_name[0]) == 0:
                        pass
                    elif subnet_tf_name != "":
                        if ("ocid1.subnet.oc1" in str(subnet_tf_name[0]).strip()):
                            worker_node_subnet = str(subnet_tf_name[0]).strip()
                        else:
                            try:
                                key = region, str(subnet_tf_name[0]).strip()
                                worker_node_subnet = subnets.vcn_subnet_map[key][2]
                            except Exception as e:
                                print("Invalid Subnet Name specified for row {} and column \"{}\". It Doesnt exist in Subnets sheet. Exiting!!!".format(i+3,columnname))
                                exit()
                    else:
                        worker_node_subnet = ""
                    tempdict = {'worker_node_subnet': worker_node_subnet}
                elif len(subnet_tf_name) > 1:
                    print("Invalid Subnet Values for row {} and column \"{}\". Only one subnet allowed".format(i+3,columnname))
                    exit()

            if columnname == 'Pod Communication Subnet':
                subnet_tf_name = columnvalue.strip()
                if subnet_tf_name != "":
                    if ("ocid1.subnet.oc1" in subnet_tf_name):
                        pod_communication_subnet = subnet_tf_name
                    else:
                        try:
                            key = region, subnet_tf_name
                            pod_communication_subnet = subnets.vcn_subnet_map[key][2]
                        except Exception as e:
                            print("Invalid Subnet Name specified for row {} and column \"{}\". It Doesnt exist in Subnets sheet. Exiting!!!".format(i+3,columnname))
                            exit()
                else:
                    pod_communication_subnet = ""
                tempdict = {'pod_communication_subnet': pod_communication_subnet}

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

        if tempStr['compartmentname_node_pool_name'] != "":
            node_str[region] = node_str[region] + node.render(tempStr)
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
            commonTools.backup_file(reg_out_dir, resource, cluster_auto_tfvars_filename)

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
            commonTools.backup_file(reg_out_dir, resource, nodepool_auto_tfvars_filename)

            # Write to TF file
            outfile = reg_out_dir + "/" + nodepool_auto_tfvars_filename
            node_str[reg] = "".join([s for s in node_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print("Writing to ..."+outfile)
            oname.write(node_str[reg])
            oname.close()


if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    create_terraform_oke(args.inputfile, args.outdir, args.service_dir, args.prefix, args.config)

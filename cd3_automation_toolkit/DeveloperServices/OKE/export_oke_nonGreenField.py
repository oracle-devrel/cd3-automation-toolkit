#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export OKE Components
#
# Author: Divya Das
# Oracle Consulting
#

import argparse
import sys
import oci
import os
import re
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.container_engine import ContainerEngineClient
from oci.config import DEFAULT_LOCATION
from commonTools import *
sys.path.append(os.getcwd() + "/..")


def print_oke(values_for_column_oke, reg, compartment_name, compartment_name_nodepool,nodepool_count, nodepool_info,cluster_info,network):
    for col_header in values_for_column_oke.keys():
        if (col_header == "Region"):
            if(nodepool_count <= 1):
                values_for_column_oke[col_header].append(reg.capitalize())
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Compartment Name':
            if (nodepool_count <= 1):
                values_for_column_oke[col_header].append(compartment_name)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Cluster Name':
            if (nodepool_count <= 1):
                values_for_column_oke[col_header].append(cluster_info.name)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Cluster Kubernetes Version':
            if(nodepool_count <= 1):
                values_for_column_oke[col_header].append(cluster_info.kubernetes_version)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Network Type':
            if nodepool_count <= 1:
                if cluster_info.cluster_pod_network_options != []:
                    values_for_column_oke[col_header].append(cluster_info.cluster_pod_network_options[0].cni_type)
                else:
                    # For Old OKE clusters which only supported single Network Type
                    values_for_column_oke[col_header].append("FLANNEL_OVERLAY")
            else:
                    values_for_column_oke[col_header].append(None)
        elif col_header == 'Pod Security Policies Enforced':
            if nodepool_count <= 1:
                values_for_column_oke[col_header].append(
                cluster_info.options.admission_controller_options.is_pod_security_policy_enabled)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Load Balancer Subnets':
            if nodepool_count <=1:
                subnets = []
                for id in cluster_info.options.service_lb_subnet_ids:
                    vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=id).data.vcn_id)).data.display_name
                    subnet = network.get_subnet(subnet_id=id).data.display_name
                    combined = vcn + "_" + subnet
                    subnets.append(combined)
                values_for_column_oke[col_header].append(','.join(subnets))
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'API Endpoint Subnet':
            if nodepool_count <= 1:
                vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=cluster_info.endpoint_config.subnet_id).data.vcn_id)).data.display_name
                subnet = network.get_subnet(subnet_id=cluster_info.endpoint_config.subnet_id).data.display_name
                combined = vcn + "_" + subnet
                values_for_column_oke[col_header].append(combined)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'API Endpoint Pub Address':
            if nodepool_count <=1:
                if cluster_info.endpoints.public_endpoint != None:
                    values_for_column_oke[col_header].append("true")
                else:
                    values_for_column_oke[col_header].append("false")
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Service CIDR Block':
            if nodepool_count <= 1:
                values_for_column_oke[col_header].append(cluster_info.options.kubernetes_network_config.services_cidr)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'Pod CIDR Block':
            if nodepool_count <=1:
                values_for_column_oke[col_header].append(cluster_info.options.kubernetes_network_config.pods_cidr)
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'API Endpoint NSGs':
            if nodepool_count <= 1:
                if cluster_info.endpoint_config.nsg_ids == None:
                    values_for_column_oke[col_header].append(None)
                else:
                    nsgs = []
                    for nsg_id in cluster_info.endpoint_config.nsg_ids:
                        nsgs.append(network.get_network_security_group(network_security_group_id=nsg_id).data.display_name)
                    values_for_column_oke[col_header].append(','.join(nsgs))
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "CompartmentName&Node Pool Name"):
            if (nodepool_info != None):
                comp_np_value = compartment_name_nodepool + "&" + nodepool_info.name
                values_for_column_oke[col_header].append(comp_np_value)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Nodepool Kubernetes Version"):
            if (nodepool_info != None):
                values_for_column_oke[col_header].append(nodepool_info.kubernetes_version)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Shape"):
            if (nodepool_info != None):
                if (".Flex" in nodepool_info.node_shape or ".Micro" in nodepool_info.node_shape):
                    shape = nodepool_info.node_shape + "::" + str(int(nodepool_info.node_shape_config.ocpus))
                    values_for_column_oke[col_header].append(shape)
                else:
                    values_for_column_oke[col_header].append(nodepool_info.node_shape)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Memory In GBs"):
            if (nodepool_info != None):
                if (".Flex" in nodepool_info.node_shape or ".Micro" in nodepool_info.node_shape):
                    values_for_column_oke[col_header].append(nodepool_info.node_shape_config.memory_in_gbs)
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Source Details"):
            if (nodepool_info != None):
                source_details = nodepool_info.node_source.source_type + "::" + commonTools.check_tf_variable(nodepool_info.node_source.source_name)
                values_for_column_oke[col_header].append(source_details)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Number of Nodes"):
            if (nodepool_info != None):
                values_for_column_oke[col_header].append(nodepool_info.node_config_details.size)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Boot Volume Size In GBs"):
            if (nodepool_info != None):
                values_for_column_oke[col_header].append(nodepool_info.node_source_details.boot_volume_size_in_gbs)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Nodepool NSGs"):
            if (nodepool_info != None):
                if (nodepool_info.node_config_details.nsg_ids == None ):
                    values_for_column_oke[col_header].append(None)
                else:
                    nsgs = []
                    for nsg_id in nodepool_info.node_config_details.nsg_ids:
                        nsgs.append(network.get_network_security_group(network_security_group_id=nsg_id).data.display_name)
                    values_for_column_oke[col_header].append(','.join(nsgs))
            else:
                values_for_column_oke[col_header].append(None)

        elif (col_header == "Worker Node Subnet"):
            if (nodepool_info != None):
                vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=nodepool_info.node_config_details.placement_configs[0].subnet_id).data.vcn_id)).data.display_name
                subnet = network.get_subnet(subnet_id=nodepool_info.node_config_details.placement_configs[0].subnet_id).data.display_name
                combined = vcn + "_" + subnet
                values_for_column_oke[col_header].append(combined)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Availability Domain(AD1|AD2|AD3)"):
            if (nodepool_info != None):
                ad = nodepool_info.node_config_details.placement_configs[0].availability_domain
                AD = lambda ad: "AD1" if ("AD-1" in ad or "ad-1" in ad) else (
                    "AD2" if ("AD-2" in ad or "ad-2" in ad) else (
                        "AD3" if ("AD-3" in ad or "ad-3" in ad) else " NULL"))  # Get shortend AD
                values_for_column_oke[col_header].append(AD(ad))
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Max Pods Per Node"):
            if (nodepool_info != None):
                if nodepool_info.node_config_details.node_pool_pod_network_option_details.cni_type == "OCI_VCN_IP_NATIVE":
                    values_for_column_oke[col_header].append(nodepool_info.node_config_details.node_pool_pod_network_option_details.max_pods_per_node)
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Pod NSGs"):
            if (nodepool_info != None):
                if nodepool_info.node_config_details.node_pool_pod_network_option_details.cni_type != "OCI_VCN_IP_NATIVE" \
                        or nodepool_info.node_config_details.node_pool_pod_network_option_details.pod_nsg_ids == None:
                    values_for_column_oke[col_header].append(None)
                else:
                    nsgs = []
                    for nsg_id in nodepool_info.node_config_details.node_pool_pod_network_option_details.pod_nsg_ids:
                        nsgs.append(
                            network.get_network_security_group(
                                network_security_group_id=nsg_id).data.display_name)
                    values_for_column_oke[col_header].append(','.join(nsgs))
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Pod Communication Subnet"):
            if (nodepool_info != None):
                if nodepool_info.node_config_details.node_pool_pod_network_option_details.cni_type == "OCI_VCN_IP_NATIVE":
                    subnets = []
                    for id in nodepool_info.node_config_details.node_pool_pod_network_option_details.pod_subnet_ids:
                        vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=id).data.vcn_id)).data.display_name
                        subnet = network.get_subnet(subnet_id=id).data.display_name
                        combined = vcn + "_" + subnet
                        subnets.append(combined)
                    values_for_column_oke[col_header].append(','.join(subnets))
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "SSH Key Var Name"):
            if (nodepool_info != None):
                if nodepool_info.ssh_public_key == None or nodepool_info.ssh_public_key == '':
                    values_for_column_oke[col_header].append(None)
                else:
                    values_for_column_oke[col_header].append(commonTools.check_tf_variable(cluster_info.name + "_" + nodepool_info.name) + "_" + nodepool_info.id[-6:])
            else:
                values_for_column_oke[col_header].append(None)
            # Process the Node Label Columns
        elif 'oke labels' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                values_for_column_oke = commonTools.export_tags(nodepool_info, col_header,values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'nodepool defined tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                values_for_column_oke = commonTools.export_tags(nodepool_info, col_header,values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'node defined tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                values_for_column_oke = commonTools.export_tags(nodepool_info.node_config_details, col_header,values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'nodepool freeform tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                values_for_column_oke = commonTools.export_tags(nodepool_info, col_header,values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'node freeform tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                values_for_column_oke = commonTools.export_tags(nodepool_info.node_config_details, col_header,values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        # Process tag columns
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_oke = commonTools.export_tags(cluster_info, col_header, values_for_column_oke)
        else:
            oci_objs = [cluster_info,nodepool_info]
            values_for_column_oke = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_oke,values_for_column_oke)


def export_oke(inputfile, outdir,service_dir, ct, _config=DEFAULT_LOCATION, export_compartments=[], export_regions=[]):
    global importCommands
    global tf_import_cmd
    global values_for_column_oke
    global sheet_dict_oke
    global config

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    sheetName = "OKE"
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'

    importCommands={}

    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    df, values_for_column_oke = commonTools.read_cd3(cd3file, "OKE")

    # Get dict for columns from Excel_Columns
    sheet_dict_oke = ct.sheet_dict["OKE"]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab - OKE will be overwritten during export process!!!\n")

    # Create backups
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + reg+"/"+service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch OKE Details
    print("\nFetching details of OKE...")

    tempImageDict = {}
    tempsshDict = {}
    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for OKE Objects #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        oke = ContainerEngineClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        network = VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        for compartment_name in export_compartments:
            clusterList = []
            clusterResponse = oci.pagination.list_call_get_all_results(oke.list_clusters,
                                                                       compartment_id=ct.ntk_compartment_ids[
                                                                           compartment_name],
                                                                       lifecycle_state=["ACTIVE"],sort_by="TIME_CREATED")
            clusterList.extend(clusterResponse.data)
            for cluster_info in clusterList:
                empty_cluter = True
                nodepool_count = 0
                nodepool_info = None

                importCommands[reg] = open(script_file, "a")
                cluster_display_name = cluster_info.name
                cluster_tf_name = commonTools.check_tf_variable(cluster_display_name)
                importCommands[reg].write("\nterraform import \"module.clusters[\\\"" + str(cluster_tf_name) + "\\\"].oci_containerengine_cluster.cluster\" " + cluster_info.id)

                for compartment_name_nodepool in export_compartments:
                    nodepoolList = []
                    nodepoolResponse = oci.pagination.list_call_get_all_results(oke.list_node_pools,cluster_id=cluster_info.id,compartment_id=ct.ntk_compartment_ids[compartment_name_nodepool],sort_by="TIME_CREATED")
                    nodepoolList.extend(nodepoolResponse.data)
                    for nodepool_info in nodepoolList:
                        empty_cluter = False
                        nodepool_count=nodepool_count+1

                        importCommands[reg] = open(script_file, "a")
                        nodepool_display_name = nodepool_info.name
                        np_tf_name = commonTools.check_tf_variable(nodepool_display_name)
                        importCommands[reg].write("\nterraform import \"module.nodepools[\\\"" + str(cluster_tf_name) + "_" + str(np_tf_name) + "\\\"].oci_containerengine_node_pool.nodepool\" " + nodepool_info.id)

                        # Extract the image details
                        tempImageDict[reg + "::" + commonTools.check_tf_variable(nodepool_info.node_source.source_name)] = nodepool_info.node_source.image_id
                        # Extract the ssh details
                        if nodepool_info.ssh_public_key == None:
                            pass
                        elif nodepool_info.ssh_public_key:
                            tempsshDict[reg + "::" + commonTools.check_tf_variable(cluster_display_name + "_" + nodepool_info.name) + "_" + nodepool_info.id[-6:]] = nodepool_info.ssh_public_key

                        print_oke(values_for_column_oke,reg, compartment_name, compartment_name_nodepool,nodepool_count,nodepool_info,cluster_info,network)

                if(empty_cluter==True):
                    print_oke(values_for_column_oke, reg, compartment_name, compartment_name_nodepool,nodepool_count, nodepool_info,cluster_info,network)


    # write oke image ocids and ssh keys
    var_data = {}
    for reg in export_regions:
        myocids = {}
        for keys, values in tempImageDict.items():
            reg_name = keys.split("::")[0]
            if (reg == reg_name):
                os_name = keys[len(reg_name) + 2:]
                myocids[os_name] = values

        mykeys = {}
        for keys, values in tempsshDict.items():
            reg_name = keys.split("::")[0]
            if (reg == reg_name):
                key_name = "\"" + keys[len(reg_name) + 2:] + "\""
                mykeys[key_name] = values

        file = f'{outdir}/{reg}/{service_dir}/variables_{reg}.tf'
        # Read variables file data
        with open(file, 'r') as f:
            var_data[reg] = f.read()

        tempStrOcids = ""
        for k, v in myocids.items():
            v = "\"" + v + "\""
            k = "\"" + k + "\""
            tempStrOcids = "\t" + k + " = " + v + "\n" + tempStrOcids

        tempStrOcids = "\n" + tempStrOcids
        tempStrOcids = "#START_oke_source_ocids#" + tempStrOcids + "\t#oke_source_ocids_END#"
        var_data[reg] = re.sub('#START_oke_source_ocids#.*?#oke_source_ocids_END#', tempStrOcids,
                               var_data[reg],
                               flags=re.DOTALL)

        tempStrKeys = ""
        for k, v in mykeys.items():
            v = "\"" + v + "\""
            tempStrKeys = "\t" + k + " = " + v + "\n" + tempStrKeys

        tempStrKeys = "\n" + tempStrKeys
        tempStrKeys = "#START_oke_ssh_keys#" + tempStrKeys + "\t#oke_ssh_keys_END#"
        if ("\\n" in tempStrKeys):
            tempStrKeys = tempStrKeys.replace("\\n", "\\\\n")

        var_data[reg] = re.sub('#START_oke_ssh_keys#.*?#oke_ssh_keys_END#', tempStrKeys,
                               var_data[reg], flags=re.DOTALL)

        # Write variables file data
        with open(file, "w") as f:
            f.write(var_data[reg])
        f.close()

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/tf_import_commands_oke_nonGF.sh'
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')

    commonTools.write_to_cd3(values_for_column_oke, cd3file, "OKE")
    print("OKE exported to CD3\n")

def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export OKE to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export OKE to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("service_dir",help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument("--network-compartments", nargs='*',
                        help="comma seperated Compartments for which to export OKE Objects", required=False)
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                        required=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_oke(args.inputfile, args.outdir, args.service_dir,args.export_compartments, args.config, args.export_regions)


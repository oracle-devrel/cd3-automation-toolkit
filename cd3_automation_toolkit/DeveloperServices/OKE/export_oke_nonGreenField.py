#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export OKE Components
#
# Author: Divya Das
# Oracle Consulting
#
import sys
import oci
import os
import re
import subprocess as sp
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.container_engine import ContainerEngineClient
from oci.config import DEFAULT_LOCATION
from commonTools import *
sys.path.append(os.getcwd() + "/..")


def print_oke(values_for_column_oke, reg, compartment_name, compartment_name_nodepool,nodepool_count, nodepool_info,cluster_info,network,nodepool_type,ct):
    image_policy_config = cluster_info.image_policy_config
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
        elif col_header == 'Cluster Type':
            if (nodepool_count <= 1):
                values_for_column_oke[col_header].append(cluster_info.type.capitalize())
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
        elif col_header == 'Load Balancer Network Details':
            if nodepool_count <=1:
                subnets = []
                for id in cluster_info.options.service_lb_subnet_ids:
                    try:
                        vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=id).data.vcn_id)).data.display_name
                        subnet = network.get_subnet(subnet_id=id).data.display_name

                        ntk_compartment_id = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=id).data.vcn_id)).data.compartment_id  # compartment-id
                        network_compartment_name = compartment_name
                        for comp_name, comp_id in ct.ntk_compartment_ids.items():
                            if comp_id == ntk_compartment_id:
                                network_compartment_name = comp_name

                        combined = network_compartment_name + "@" + vcn + "::" + subnet
                    except Exception as e:
                        combined = id
                    subnets.append(combined)
                values_for_column_oke[col_header].append(','.join(subnets))
            else:
                values_for_column_oke[col_header].append(None)
        elif col_header == 'API Endpoint Network Details':
            if nodepool_count <= 1:
                try:
                    vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=cluster_info.endpoint_config.subnet_id).data.vcn_id)).data.display_name
                    subnet = network.get_subnet(subnet_id=cluster_info.endpoint_config.subnet_id).data.display_name
                    ntk_compartment_id = network.get_vcn(
                        vcn_id=(network.get_subnet(subnet_id=cluster_info.endpoint_config.subnet_id).data.vcn_id)).data.compartment_id  # compartment-id
                    network_compartment_name = compartment_name
                    for comp_name, comp_id in ct.ntk_compartment_ids.items():
                        if comp_id == ntk_compartment_id:
                            network_compartment_name = comp_name

                    combined = network_compartment_name + "@" + vcn + "::" + subnet
                except Exception as e:
                    combined = id
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
        elif (col_header == "CompartmentName@Node Pool Name:Node Pool Type"):
            if (nodepool_info != None):
                if nodepool_type=="managed":
                    comp_np_value = compartment_name_nodepool + "@" + nodepool_info.name+":Managed"
                    values_for_column_oke[col_header].append(comp_np_value)
                elif nodepool_type == "virtual":
                    comp_np_value = compartment_name_nodepool + "@" + nodepool_info.display_name + ":Virtual"
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
                if nodepool_type=="managed":
                    if (".Flex" in nodepool_info.node_shape or ".Micro" in nodepool_info.node_shape):
                        shape = nodepool_info.node_shape + "::" + str(int(nodepool_info.node_shape_config.ocpus))
                        values_for_column_oke[col_header].append(shape)
                    else:
                        values_for_column_oke[col_header].append(nodepool_info.node_shape)
                if nodepool_type=="virtual":
                    shape = nodepool_info.pod_configuration.shape
                    values_for_column_oke[col_header].append(shape)
            else:
                values_for_column_oke[col_header].append(None)

        elif (col_header == "Memory In GBs"):
            if (nodepool_info != None and nodepool_type=="managed"):
                if (".Flex" in nodepool_info.node_shape or ".Micro" in nodepool_info.node_shape):
                    values_for_column_oke[col_header].append(nodepool_info.node_shape_config.memory_in_gbs)
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Source Details" and nodepool_type=="managed"):
            if (nodepool_info != None):
                source_details = nodepool_info.node_source.source_type + "::" + commonTools.check_tf_variable(nodepool_info.node_source.source_name)
                values_for_column_oke[col_header].append(source_details)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Number of Nodes"):
            if (nodepool_info != None):
                if (nodepool_type=='managed'):
                    values_for_column_oke[col_header].append(nodepool_info.node_config_details.size)
                elif (nodepool_type=='virtual'):
                    values_for_column_oke[col_header].append(nodepool_info.size)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Boot Volume Size In GBs" and nodepool_type=="managed"):
            if (nodepool_info != None):
                values_for_column_oke[col_header].append(nodepool_info.node_source_details.boot_volume_size_in_gbs)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Nodepool NSGs"):
            if (nodepool_info != None):
                if nodepool_type == 'managed':
                    if (nodepool_info.node_config_details.nsg_ids == None ):
                        values_for_column_oke[col_header].append(None)
                    else:
                        nsgs = []
                        for nsg_id in nodepool_info.node_config_details.nsg_ids:
                            nsgs.append(network.get_network_security_group(network_security_group_id=nsg_id).data.display_name)
                        values_for_column_oke[col_header].append(','.join(nsgs))
                elif (nodepool_type == 'virtual'):
                    if (nodepool_info.nsg_ids == None ):
                        values_for_column_oke[col_header].append(None)
                    else:
                        nsgs = []
                        for nsg_id in nodepool_info.nsg_ids:
                            nsgs.append(network.get_network_security_group(network_security_group_id=nsg_id).data.display_name)
                        values_for_column_oke[col_header].append(','.join(nsgs))
            else:
                values_for_column_oke[col_header].append(None)

        elif (col_header == "Worker Node Network Details"):
            if (nodepool_info != None):
                subnet_id = ""
                if (nodepool_type=='managed'):
                    subnet_id = nodepool_info.node_config_details.placement_configs[0].subnet_id
                elif (nodepool_type == 'virtual'):
                    subnet_id = nodepool_info.placement_configurations[0].subnet_id
                try:
                    vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=subnet_id).data.vcn_id)).data.display_name
                    subnet = network.get_subnet(subnet_id=subnet_id).data.display_name
                    ntk_compartment_id = network.get_vcn(
                        vcn_id=(network.get_subnet(subnet_id=subnet_id).data.vcn_id)).data.compartment_id  # compartment-id
                    network_compartment_name = compartment_name
                    for comp_name, comp_id in ct.ntk_compartment_ids.items():
                        if comp_id == ntk_compartment_id:
                            network_compartment_name = comp_name

                    combined = network_compartment_name + "@" + vcn + "::" + subnet
                except Exception as e:
                    combined = id
                values_for_column_oke[col_header].append(combined)

            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Availability Domain(AD1|AD2|AD3)"):
            if (nodepool_info != None):
                ad=""
                if (nodepool_type=='managed'):
                    okead = nodepool_info.node_config_details.placement_configs[0].availability_domain
                elif (nodepool_type=='virtual'):
                    okead = nodepool_info.placement_configurations[0].availability_domain

                AD = lambda ad: "AD1" if ("AD-1" in okead or "ad-1" in okead) else (
                    "AD2" if ("AD-2" in okead or "ad-2" in okead) else (
                        "AD3" if ("AD-3" in okead or "ad-3" in okead) else "NULL"))  # Get shortend AD
                values_for_column_oke[col_header].append(AD(ad))
            else:
                values_for_column_oke[col_header].append(None)

        elif (col_header == "Fault Domains"):
            if (nodepool_info != None):
                fd=""
                if (nodepool_type=='managed'):
                    fd = nodepool_info.node_config_details.placement_configs[0].fault_domains
                elif (nodepool_type=='virtual'):
                    fd = nodepool_info.placement_configurations[0].fault_domain

                if fd !=None:
                    fd_s = ','.join(str(x) for x in fd)
                    values_for_column_oke[col_header].append(fd_s)
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)

        elif (col_header == "Max Pods Per Node"):
            if (nodepool_info != None and nodepool_type=='managed'):
                if nodepool_info.node_config_details.node_pool_pod_network_option_details.cni_type == "OCI_VCN_IP_NATIVE":
                    values_for_column_oke[col_header].append(nodepool_info.node_config_details.node_pool_pod_network_option_details.max_pods_per_node)
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Pod NSGs"):
            if (nodepool_info != None):
                if nodepool_type=="managed":
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
                elif nodepool_type=='virtual':
                    nsgs = []
                    if(nodepool_info.pod_configuration.nsg_ids!=None):
                        for nsg_id in nodepool_info.pod_configuration.nsg_ids:
                            nsgs.append(network.get_network_security_group(
                                    network_security_group_id=nsg_id).data.display_name)

                    values_for_column_oke[col_header].append(','.join(nsgs))
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "Pod Communication Network Details"):
            if (nodepool_info != None):
                if nodepool_type == "managed":
                    if nodepool_info.node_config_details.node_pool_pod_network_option_details.cni_type == "OCI_VCN_IP_NATIVE":
                        subnets = []
                        for id in nodepool_info.node_config_details.node_pool_pod_network_option_details.pod_subnet_ids:
                            try:
                                vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=id).data.vcn_id)).data.display_name
                                subnet = network.get_subnet(subnet_id=id).data.display_name
                                ntk_compartment_id = network.get_vcn(vcn_id=(
                                    network.get_subnet(subnet_id=id).data.vcn_id)).data.compartment_id  # compartment-id
                                network_compartment_name = compartment_name
                                for comp_name, comp_id in ct.ntk_compartment_ids.items():
                                    if comp_id == ntk_compartment_id:
                                        network_compartment_name = comp_name

                                combined = network_compartment_name + "@" + vcn + "::" + subnet
                            except Exception as e:
                                combined = id
                            subnets.append(combined)
                        values_for_column_oke[col_header].append(','.join(subnets))
                    else:
                        values_for_column_oke[col_header].append(None)
                elif nodepool_type == 'virtual':
                    pod_subnet_id=nodepool_info.pod_configuration.subnet_id
                    try:
                        vcn = network.get_vcn(vcn_id=(network.get_subnet(subnet_id=pod_subnet_id).data.vcn_id)).data.display_name
                        subnet = network.get_subnet(subnet_id=pod_subnet_id).data.display_name
                        ntk_compartment_id = network.get_vcn(
                            vcn_id=(network.get_subnet(subnet_id=pod_subnet_id).data.vcn_id)).data.compartment_id  # compartment-id
                        network_compartment_name = compartment_name
                        for comp_name, comp_id in ct.ntk_compartment_ids.items():
                            if comp_id == ntk_compartment_id:
                                network_compartment_name = comp_name

                        combined = network_compartment_name + "@" + vcn + "::" + subnet
                    except Exception as e:
                        combined = id
                    values_for_column_oke[col_header].append(combined)
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header == "SSH Key Var Name"):
            if (nodepool_info != None and nodepool_type == "managed"):
                if nodepool_info.ssh_public_key == None or nodepool_info.ssh_public_key == '':
                    values_for_column_oke[col_header].append(None)
                else:
                    values_for_column_oke[col_header].append(commonTools.check_tf_variable(cluster_info.name + "_" + nodepool_info.name) + "_" + nodepool_info.id[-6:])
            else:
                values_for_column_oke[col_header].append(None)
        elif (col_header.lower() == "taints key,value,effect"):
            val=''
            if (nodepool_info != None and nodepool_type == "virtual"):
                taints = nodepool_info.taints
                for taint in taints:
                    val=val+taint.key+","+taint.value+","+taint.effect
                    val=val+"\n"
                val = val[:-1]
            values_for_column_oke[col_header].append(val)

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
        elif 'nodepool freeform tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                values_for_column_oke = commonTools.export_tags(nodepool_info, col_header,values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'node defined tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                if nodepool_type=='managed':
                    values_for_column_oke = commonTools.export_tags(nodepool_info.node_config_details, col_header,values_for_column_oke)
                elif (nodepool_type=='virtual' and nodepool_info.virtual_node_tags!=None):
                    values_for_column_oke = commonTools.export_tags(nodepool_info.virtual_node_tags , col_header,
                                                                    values_for_column_oke)
                else:
                    values_for_column_oke[col_header].append(None)
            else:
                values_for_column_oke[col_header].append(None)


        elif 'node freeform tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_info != None):
                if nodepool_type == 'managed':
                    values_for_column_oke = commonTools.export_tags(nodepool_info.node_config_details, col_header,values_for_column_oke)
                elif (nodepool_type == 'virtual' and nodepool_info.virtual_node_tags!=None):
                    values_for_column_oke = commonTools.export_tags(nodepool_info.virtual_node_tags, col_header,
                                                                    values_for_column_oke)
                else:
                    values_for_column_oke[col_header].append(None)

            else:
                values_for_column_oke[col_header].append(None)

        elif 'lb defined tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_count <= 1):
                values_for_column_oke = commonTools.export_tags(cluster_info.options.service_lb_config, col_header,
                                                                values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'lb freeform tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_count <= 1):
                values_for_column_oke = commonTools.export_tags(cluster_info.options.service_lb_config, col_header,
                                                                values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        elif 'volume defined tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_count <= 1):
                values_for_column_oke = commonTools.export_tags(cluster_info.options.persistent_volume_config,
                                                                col_header, values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)


        elif 'volume freeform tags' in col_header.lower() and col_header.lower() in commonTools.tagColumns:
            if (nodepool_count <= 1):
                values_for_column_oke = commonTools.export_tags(cluster_info.options.persistent_volume_config,
                                                                col_header, values_for_column_oke)
            else:
                values_for_column_oke[col_header].append(None)

        # Process tag columns
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_oke = commonTools.export_tags(cluster_info, col_header, values_for_column_oke)
        else:
             oci_objs = [cluster_info,image_policy_config, nodepool_info]
             values_for_column_oke = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_oke,values_for_column_oke)

# Execution of the code begins here
def export_oke(inputfile, outdir,service_dir, config, signer, ct, export_compartments=[], export_regions=[],export_tags=[]):
    global importCommands
    global tf_import_cmd
    global values_for_column_oke
    global sheet_dict_oke,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "OKE"
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    importCommands={}

    df, values_for_column_oke = commonTools.read_cd3(cd3file, "OKE")

    # Get dict for columns from Excel_Columns
    sheet_dict_oke = ct.sheet_dict["OKE"]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tab - OKE will be overwritten during export process!!!\n")

    # Create backups
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch OKE Details
    print("\nFetching details of OKE...")

    tempImageDict = {}
    tempsshDict = {}
    total_resources = 0
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        oke = ContainerEngineClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        network = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        for compartment_name in export_compartments:
            clusterList = []
            clusterResponse = oci.pagination.list_call_get_all_results(oke.list_clusters,
                                                                       compartment_id=ct.ntk_compartment_ids[
                                                                           compartment_name],
                                                                       lifecycle_state=["ACTIVE"],sort_by="TIME_CREATED")
            clusterList.extend(clusterResponse.data)
            #total_resources +=len(clusterList)
            for cluster_info in clusterList:
                empty_cluter = True
                nodepool_count = 0
                nodepool_info = None
                nodepool_type=""

                # Tags filter
                defined_tags = cluster_info.defined_tags
                tags_list = []
                for tkey, tval in defined_tags.items():
                    for kk, vv in tval.items():
                        tag = tkey + "." + kk + "=" + vv
                        tags_list.append(tag)

                if export_tags == []:
                    check = True
                else:
                    check = any(e in tags_list for e in export_tags)
                # None of Tags from export_tags exist on this instance; Dont export this instance
                if check == False:
                    continue

                total_resources = total_resources + 1
                cluster_display_name = cluster_info.name
                cluster_tf_name = commonTools.check_tf_variable(cluster_display_name)
                tf_resource = f'module.clusters[\\"{str(cluster_tf_name)}\\"].oci_containerengine_cluster.cluster'
                if tf_resource not in state["resources"]:
                    importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {cluster_info.id}'

                for compartment_name_nodepool in export_compartments:
                    nodepoolList = []
                    #virtual_nodepoolList = []
                    nodepoolResponse = oci.pagination.list_call_get_all_results(oke.list_node_pools,cluster_id=cluster_info.id,compartment_id=ct.ntk_compartment_ids[compartment_name_nodepool],sort_by="TIME_CREATED")
                    nodepoolList.extend(nodepoolResponse.data)

                    virtual_nodepoolResponse = oci.pagination.list_call_get_all_results(oke.list_virtual_node_pools,
                                                                                cluster_id=cluster_info.id,
                                                                                compartment_id=ct.ntk_compartment_ids[
                                                                                    compartment_name_nodepool],
                                                                                sort_by="TIME_CREATED")
                    nodepoolList.extend(virtual_nodepoolResponse.data)


                    for nodepool_info in nodepoolList:
                        if nodepool_info.lifecycle_state!="ACTIVE":
                            continue

                        # Tags filter
                        defined_tags = nodepool_info.defined_tags
                        tags_list = []
                        for tkey, tval in defined_tags.items():
                            for kk, vv in tval.items():
                                tag = tkey + "." + kk + "=" + vv
                                tags_list.append(tag)

                        if export_tags == []:
                            check = True
                        else:
                            check = any(e in tags_list for e in export_tags)
                        # None of Tags from export_tags exist on this instance; Dont export this instance
                        if check == False:
                            continue

                        empty_cluter = False
                        nodepool_count=nodepool_count+1


                        #Virtual NodePool
                        if ("ocid1.virtualnodepool.oc" in nodepool_info.id):
                            nodepool_display_name = nodepool_info.display_name
                            np_tf_name = commonTools.check_tf_variable(nodepool_display_name)
                            tf_resource = f'module.virtual-nodepools[\\"{cluster_tf_name}_{np_tf_name}\\"].oci_containerengine_virtual_node_pool.virtual_nodepool'
                            if tf_resource not in state["resources"]:
                                importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {nodepool_info.id}'
                            nodepool_type = "virtual"

                        # Managed NodePool
                        if ("ocid1.nodepool.oc" in nodepool_info.id):
                            nodepool_display_name = nodepool_info.name
                            np_tf_name = commonTools.check_tf_variable(nodepool_display_name)
                            nodepool_type = "managed"
                            tf_resource = f'module.nodepools[\\"{cluster_tf_name}_{np_tf_name}\\"].oci_containerengine_node_pool.nodepool'
                            if tf_resource not in state["resources"]:
                                importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {nodepool_info.id}'

                            # Extract the image details
                            tempImageDict[reg + "::" + commonTools.check_tf_variable(nodepool_info.node_source.source_name)] = nodepool_info.node_source.image_id
                            # Extract the ssh details
                            if nodepool_info.ssh_public_key == None:
                                pass
                            elif nodepool_info.ssh_public_key:
                                tempsshDict[reg + "::" + commonTools.check_tf_variable(cluster_display_name + "_" + nodepool_info.name) + "_" + nodepool_info.id[-6:]] = nodepool_info.ssh_public_key

                        print_oke(values_for_column_oke,reg, compartment_name, compartment_name_nodepool,nodepool_count,nodepool_info,cluster_info,network,nodepool_type,ct)


                if(empty_cluter==True):
                    print_oke(values_for_column_oke, reg, compartment_name, compartment_name_nodepool,nodepool_count, nodepool_info,cluster_info,network,nodepool_type,ct)


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
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for OKE #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])

    commonTools.write_to_cd3(values_for_column_oke, cd3file, "OKE")
    print("{0} OKE clusters exported into CD3.\n".format(total_resources))


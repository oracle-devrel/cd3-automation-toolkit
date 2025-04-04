#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export NLB Components
#
# Author: Suruchi Singla
# Oracle Consulting
#
import sys
import oci
import os
import subprocess as sp

from oci.core.virtual_network_client import VirtualNetworkClient
from oci.network_load_balancer import NetworkLoadBalancerClient
from oci.core.compute_client import ComputeClient
sys.path.append(os.getcwd()+"/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}

def print_nlb_backendset_backendserver(region, values_for_column_bss,NLBs, nlb_compartment_name,cmpt,vcn,nlb,export_tags, state, ct):

    for eachnlb in NLBs.data:
        cnt_bss = 0
        nlb_display_name = eachnlb.display_name
        tf_name = commonTools.check_tf_variable(nlb_display_name)

        # Tags filter
        defined_tags = eachnlb.defined_tags
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

        # Filter out the NLBs provisioned by oke
        eachnlb_defined_tags = eachnlb.defined_tags
        if 'Oracle-Tags' in eachnlb_defined_tags.keys():
            if 'CreatedBy' in eachnlb_defined_tags['Oracle-Tags'].keys():
                created_by = eachnlb_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Loop through Backend Sets
        for backendsets in eachnlb.__getattribute__('backend_sets'):
            cnt_bss = cnt_bss + 1

            backendsets_tf_name = commonTools.check_tf_variable(backendsets)
            tf_resource = f'module.nlb-backend-sets[\\"{tf_name}_{backendsets_tf_name}\\"].oci_network_load_balancer_backend_set.backend_set'
            if tf_resource not in state["resources"]:
                importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkLoadBalancers/{eachnlb.id}/backendSets/{backendsets}'

            backend_list = ""
            backendset_details = nlb.get_backend_set(eachnlb.__getattribute__('id'), backendsets).data
            hc = nlb.get_health_checker(eachnlb.__getattribute__('id'), backendsets).data
            dns=hc.__getattribute__('dns')

            # Process the Backend Server
            cnt_bes = 0
            for backends in backendset_details.__getattribute__('backends'):
                cnt_bes = cnt_bes+1

                if str(backends.__getattribute__('name')).lower() != "none":
                    backend_value = str(backends.__getattribute__('name'))
                    port = str(backends.__getattribute__('port'))

                    if "ocid1.privateip" in backend_value:
                        private_ip_ocid = backend_value.split(":")[0]
                        #port = backend_value.split(":")[1]
                        try:
                            private_ip = vcn.get_private_ip(private_ip_ocid).data
                        except Exception as e:
                            print("Some issue with  Backend "+backend_value+ " for NLB "+nlb_display_name+". Skipping it...")
                            continue

                        vnic_ocid = private_ip.vnic_id
                        vnic = vcn.get_vnic(vnic_ocid).data
                        vnic_found = 0
                        instance_comp_name = None
                        for k,v in ct.ntk_compartment_ids.items():
                            vnic_attachments = oci.pagination.list_call_get_all_results(cmpt.list_vnic_attachments, compartment_id = v,vnic_id=vnic_ocid)
                            for vnic_attachment in vnic_attachments.data:
                                instance_ocid = vnic_attachment.instance_id
                                instance = cmpt.get_instance(instance_ocid).data
                                instance_display_name = instance.display_name
                                instance_comp_name = k
                                vnic_found = 1
                            if vnic_found==1:
                                break

                        backend = instance_comp_name+"@"+instance_display_name+":"+port
                        backend_list = backend_list + "," + backend

                        backendservers_name = instance_display_name +"-"+port
                        backendservers_tf_name = commonTools.check_tf_variable(backendservers_name)
                    else:
                        backend = backend_value
                        backend_list= backend_list+","+backend

                        backendservers_name = backend.split(":")[0] +"-"+port
                        backendservers_tf_name = commonTools.check_tf_variable(backendservers_name)
                    tf_resource = f'module.nlb-backends[\\"{tf_name}_{backendsets_tf_name}_{backendservers_tf_name}\\"].oci_network_load_balancer_backend.backend'
                    if tf_resource not in state["resources"]:
                        importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkLoadBalancers/{eachnlb.id}/backendSets/{backendsets}/backends/{backend_value}'

                if (backend_list != "" and backend_list[0] == ','):
                    backend_list = backend_list.lstrip(',')

            for col_header in values_for_column_bss.keys():
                if col_header == 'Region':
                    if cnt_bss == 1:
                        values_for_column_bss[col_header].append(str(region))
                    else:
                        values_for_column_bss[col_header].append('')
                elif col_header == 'Compartment Name':
                    if cnt_bss == 1:
                        values_for_column_bss[col_header].append(nlb_compartment_name)
                    else:
                        values_for_column_bss[col_header].append('')
                elif col_header == 'NLB Name':
                    if cnt_bss == 1:
                        values_for_column_bss[col_header].append(eachnlb.display_name)
                    else:
                        values_for_column_bss[col_header].append('')

                # Process the Tag  Columns
                elif col_header.lower() in commonTools.tagColumns:
                    if cnt_bss == 1:
                        values_for_column_bss = commonTools.export_tags(eachnlb, col_header, values_for_column_bss)
                    else:
                        values_for_column_bss[col_header].append('')

                elif col_header == "Backend Policy(FIVE_TUPLE|THREE_TUPLE|TWO_TUPLE)":
                    policy = backendset_details.__getattribute__(sheet_dict_bss[col_header])
                    values_for_column_bss[col_header].append(str(policy))

                elif 'Backend HealthCheck' in col_header:
                    values_for_column_bss[col_header].append(hc.__getattribute__(sheet_dict_bss[col_header]))

                elif col_header == "Backend ServerComp@ServerName:Port":
                    values_for_column_bss[col_header].append(backend_list)

                elif col_header == "Backend Set Name":
                    values_for_column_bss[col_header].append(backendsets)
                else:
                    oci_objs = [eachnlb,backendset_details,hc,dns]
                    values_for_column_bss = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_bss,values_for_column_bss)

    return values_for_column_bss


def print_nlb_listener(region, outdir, values_for_column_lis, NLBs, nlb_compartment_name,vcn,export_tags,ct,state):

    for eachnlb in NLBs.data:

        # Tags filter
        defined_tags = eachnlb.defined_tags
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


        # Filter out the NLBs provisioned by oke
        eachnlb_defined_tags = eachnlb.defined_tags
        if 'Oracle-Tags' in eachnlb_defined_tags.keys():
            if 'CreatedBy' in eachnlb_defined_tags['Oracle-Tags'].keys():
                created_by = eachnlb_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        nlb_display_name = eachnlb.display_name
        tf_name = commonTools.check_tf_variable(nlb_display_name)
        tf_resource = f'module.network-load-balancers[\\"{tf_name}\\"].oci_network_load_balancer_network_load_balancer.network_load_balancer'
        if tf_resource not in state["resources"]:
            importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {eachnlb.id}'

        cnt_lsnr = 0

        #Fetch subnet
        subnet_ocid = eachnlb.subnet_id
        subnet_info = vcn.get_subnet(subnet_ocid).data
        subnet_name = subnet_info.display_name
        vcn_id = subnet_info.vcn_id
        vcn_info = vcn.get_vcn(vcn_id).data
        vcn_name = vcn_info.display_name
        ntk_compartment_id = vcn.get_vcn(vcn_id).data.compartment_id  # compartment-id
        network_compartment_name = nlb_compartment_name
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if comp_id == ntk_compartment_id:
                network_compartment_name = comp_name

        subnet_detail = network_compartment_name + "@" + vcn_name + "::" + subnet_name

        #Fetch NSGs
        nsg_detail = ""
        for nsg_id in eachnlb.network_security_group_ids:
            nsg_info = vcn.get_network_security_group(nsg_id).data
            nsg_name = nsg_info.display_name
            nsg_detail = nsg_name + "," +nsg_detail
        if(nsg_detail!=""):
            nsg_detail = nsg_detail[:-1]

        # Fetch reserved IP address
        reserved_ip = ""
        is_public=False
        if eachnlb.ip_addresses != []:
            for ips in eachnlb.ip_addresses:
                if(ips.is_public == True):
                    is_public=ips.is_public
                    if str(ips.reserved_ip) == "null" or str(ips.reserved_ip) == "None":
                        reserved_ip = "N"
                    else:
                        reserved_ip = ips.reserved_ip.id

        # Loop through listeners
        for listeners, values in eachnlb.__getattribute__('listeners').items():
            cnt_lsnr = cnt_lsnr + 1

            listener_tf_name = commonTools.check_tf_variable(listeners)
            tf_resource = f'module.nlb-listeners[\\"{tf_name}_{listener_tf_name}\\"].oci_network_load_balancer_listener.listener'
            if tf_resource not in state["resources"]:
                importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkLoadBalancers/{eachnlb.id}/listeners/{listeners}'

            for col_header in values_for_column_lis.keys():
                if col_header == 'Region':
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(str(region))
                    else:
                        values_for_column_lis[col_header].append("")
                elif col_header == 'Compartment Name':
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(nlb_compartment_name)
                    else:
                        values_for_column_lis[col_header].append("")
                elif col_header == 'NLB Name':
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(eachnlb.display_name)
                    else:
                        values_for_column_lis[col_header].append("")
                elif col_header == "Network Details":
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(subnet_detail)
                    else:
                        values_for_column_lis[col_header].append("")
                elif (col_header == "NSGs"):
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(nsg_detail)
                    else:
                        values_for_column_lis[col_header].append("")

                elif (col_header == "Is Private(True|False)"):
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(not(is_public))
                    else:
                        values_for_column_lis[col_header].append("")

                elif (col_header == "Reserved IP(Y|N|OCID)"):
                    if cnt_lsnr == 1:
                        values_for_column_lis[col_header].append(reserved_ip)
                    else:
                        values_for_column_lis[col_header].append("")

                # Process the Tag Columns
                elif col_header.lower() in commonTools.tagColumns:
                    if cnt_lsnr == 1:
                        values_for_column_lis = commonTools.export_tags(eachnlb, col_header, values_for_column_lis)
                    else:
                        values_for_column_lis[col_header].append("")
                else:
                    oci_objs = [values,eachnlb,ips]
                    values_for_column_lis = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_lis, values_for_column_lis)

        if cnt_lsnr == 0:
            for col_header in values_for_column_lis.keys():
                if col_header == 'Region':
                    values_for_column_lis[col_header].append(str(region))
                elif col_header == 'Compartment Name':
                    values_for_column_lis[col_header].append(nlb_compartment_name)
                elif col_header == 'NLB Name':
                    values_for_column_lis[col_header].append(eachnlb.display_name)
                elif col_header == "Network Details":
                    values_for_column_lis[col_header].append(subnet_detail)
                elif (col_header == "NSGs"):
                    values_for_column_lis[col_header].append(nsg_detail)
                elif (col_header == "Reserved IP(Y|N|OCID)"):
                    values_for_column_lis[col_header].append(reserved_ip)
                elif (col_header == "Is Private(True|False)"):
                    values_for_column_lis[col_header].append(not(is_public))
                # Process the Tag Columns
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_lis = commonTools.export_tags(eachnlb, col_header, values_for_column_lis)
                else:
                    oci_objs = [eachnlb,ips]
                    values_for_column_lis = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_lis,values_for_column_lis)

    return values_for_column_lis

# Execution of the code begins here
def export_nlb(inputfile, outdir, service_dir, config,signer, ct, export_compartments, export_regions,export_tags):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global values_for_column_bss
    global values_for_column_lis
    global sheet_dict_bss
    global sheet_dict_lis
    global listener_to_cd3,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    total_resources = 0

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_bss = commonTools.read_cd3(cd3file, "NLB-BackendSets-BackendServers")
    df, values_for_column_lis = commonTools.read_cd3(cd3file, "NLB-Listeners")


    # Get dict for columns from Excel_Columns
    sheet_dict_bss = ct.sheet_dict["NLB-BackendSets-BackendServers"]
    sheet_dict_lis = ct.sheet_dict["NLB-Listeners"]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- NLB-Listeners, NLB-BackendSets-BackendServers will be overwritten during export process!!!\n")

    # Fetch NLB Details
    print("\nFetching details of Network Load Balancer...")

    file_name = 'import_commands_nlb.sh'
    resource = 'import_nlb'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name

        # Create backups
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)

        importCommands[reg] = ''

        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        nlb = NetworkLoadBalancerClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        vcn = VirtualNetworkClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        cmpt = ComputeClient(config=config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        region = reg.capitalize()

        for compartment_name in export_compartments:
                NLBs = oci.pagination.list_call_get_all_results(nlb.list_network_load_balancers,compartment_id=ct.ntk_compartment_ids[compartment_name],
                                                                lifecycle_state="ACTIVE")
                if NLBs.data != [] and importCommands[reg] == '':
                    for eachnlb in NLBs.data:

                        # Tags filter
                        defined_tags = eachnlb.defined_tags
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
                        total_resources +=1

                values_for_column_lis = print_nlb_listener(region, outdir, values_for_column_lis,NLBs,compartment_name,vcn,export_tags,ct,state)
                values_for_column_bss = print_nlb_backendset_backendserver(region, values_for_column_bss,NLBs,compartment_name,cmpt,vcn,nlb,export_tags, state,ct)

    commonTools.write_to_cd3(values_for_column_lis, cd3file, "NLB-Listeners")
    commonTools.write_to_cd3(values_for_column_bss, cd3file, "NLB-BackendSets-BackendServers")

    print("{0} NLBs exported into CD3.\n".format(total_resources))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if importCommands[reg] != "":
            init_commands = f'\n######### Writing import for Network Load Balancer Objects #########\n\n#!/bin/bash\n{tf_or_tofu} init'
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])


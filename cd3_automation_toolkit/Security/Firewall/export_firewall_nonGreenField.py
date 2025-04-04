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

from oci.network_firewall import NetworkFirewallClient
from oci.core.virtual_network_client import VirtualNetworkClient

sys.path.append(os.getcwd() + "/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}
AD = lambda ad: "AD1" if ("AD-1" in ad or "ad-1" in ad) else ("AD2" if ("AD-2" in ad or "ad-2" in ad) else ("AD3" if ("AD-3" in ad or "ad-3" in ad) else " NULL"))

def print_firewall(region, export_tags, ct, values_for_column_fw, fws, fw_compartment_name, vcn, fw,state):
    for eachfw in fws.data:

        # Tags filter
        defined_tags = eachfw.defined_tags
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

        fw_display_name = eachfw.display_name
        tf_name = commonTools.check_tf_variable(fw_display_name)
        tf_resource = f'module.firewalls[\\"{str(tf_name)}\\"].oci_network_firewall_network_firewall.network_firewall'
        if tf_resource not in state["resources"]:
            importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {eachfw.id}'
        # Fetch subnet and Compartment name
        comp_done_ids = []
        subnet_ocid = eachfw.subnet_id
        subnet_info = vcn.get_subnet(subnet_ocid).data
        subnet_name = subnet_info.display_name
        vcn_id = subnet_info.vcn_id
        vcn_info = vcn.get_vcn(vcn_id).data
        vcn_name = vcn_info.display_name
        net_cmp_id = vcn_info.compartment_id
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if net_cmp_id == comp_id and net_cmp_id not in comp_done_ids:
                net_cmp_name = comp_name
                comp_done_ids.append(net_cmp_id)
        subnet_detail = vcn_name + "::" + subnet_name

        # Fetch policy
        policy_ocid = eachfw.network_firewall_policy_id
        policy_info = fw.get_network_firewall_policy(policy_ocid).data
        policy_name = policy_info.display_name
        policy_detail = policy_name

        # Fetch NSGs
        nsg_detail = ""
        firewall_ocid = eachfw.id
        nsg_ids = fw.get_network_firewall(firewall_ocid).data.network_security_group_ids
        if(nsg_ids is not None and len(nsg_ids)):
            for nsg_id in nsg_ids:
                nsg_info = vcn.get_network_security_group(nsg_id).data
                nsg_name = nsg_info.display_name
                nsg_detail = nsg_name + "," + nsg_detail
        if (nsg_detail != ""):
            nsg_detail = nsg_detail[:-1]



        for col_header in values_for_column_fw:
            if col_header == 'Region':
                values_for_column_fw[col_header].append(region)
            elif col_header == 'Compartment Name':
                values_for_column_fw[col_header].append(fw_compartment_name)

            elif col_header == 'Firewall Name':
                values_for_column_fw[col_header].append(fw_display_name)

            elif col_header == 'Network Compartment Name':
                values_for_column_fw[col_header].append(net_cmp_name)

            elif col_header == 'Subnet Name':
                values_for_column_fw[col_header].append(subnet_detail)

            elif col_header == 'IPv4 Address':
                values_for_column_fw[col_header].append(eachfw.ipv4_address)

            elif col_header == 'Firewall Policy':
                values_for_column_fw[col_header].append(policy_detail)

            elif col_header == 'NSGs':
                values_for_column_fw[col_header].append(nsg_detail)

            elif col_header == 'Availability Domain(AD1|AD2|AD3|Regional)':
                if (eachfw.availability_domain == None):
                    value_of_ad = "Regional"
                else:
                    value_of_ad = AD(eachfw.availability_domain)
                values_for_column_fw[col_header].append(value_of_ad)

            elif col_header.lower() in commonTools.tagColumns:
                values_for_column_fw = commonTools.export_tags(eachfw, col_header, values_for_column_fw)

    return values_for_column_fw


# Execution of the code begins here
def export_firewall(inputfile, _outdir, service_dir, config, signer, ct, export_compartments, export_regions, export_tags):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global outdir
    global values_for_column_fwpolicy
    global sheet_dict_fwpolicy
    global sheet_dict_fwaddress
    global listener_to_cd3,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()
    sheetName = "Firewall"
    outdir = _outdir

    # Read CD3
    df, values_for_column_fw= commonTools.read_cd3(cd3file, sheetName)

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Firewall will be overwritten during export process!!!\n")

    # Create backups
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    # Create backups
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)
        importCommands[reg] = ''

    # Fetch Network firewall Policy Details
    print("\nFetching details of Network Firewall...")

    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        fw = NetworkFirewallClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        vcn = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        #cmpt = ComputeClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        region = reg.capitalize()

        for compartment_name in export_compartments:
            fws = oci.pagination.list_call_get_all_results(fw.list_network_firewalls, compartment_id=ct.ntk_compartment_ids[compartment_name], lifecycle_state="ACTIVE")
            # fwpolicies = oci.pagination.list_call_get_all_results(fwpolicy.list_network_firewall_policies,compartment_id=ct.ntk_compartment_ids[compartment_name],lifecycle_state = "ACTIVE")

            values_for_column_fw = print_firewall(region, export_tags, ct, values_for_column_fw, fws, compartment_name, vcn, fw,state)

    # writing data
    init_commands = f'\n######### Writing import for Network Firewall Objects #########\n\n#!/bin/bash\n{tf_or_tofu} init'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])

    commonTools.write_to_cd3(values_for_column_fw, cd3file, sheetName)
    print("{0} Firewalls exported into CD3.\n".format(len(values_for_column_fw["Region"])))


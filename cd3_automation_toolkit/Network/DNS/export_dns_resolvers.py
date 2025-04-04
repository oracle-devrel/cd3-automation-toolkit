#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export DNS Resolvers
#
import oci
import os
import subprocess as sp
from commonTools import *
importCommands = {}
oci_obj_names = {}




# Create map for each endpoint
def get_e_map(region, dns_client, vnc_client, ct, resolver, ntk_compartment_name):
    vcn_name = vnc_client.get_vcn(resolver.attached_vcn_id).data.display_name
    views = ""
    e_map = {}
    for view in resolver.attached_views:
        view_data = dns_client.get_view(view.view_id).data
        view_comp_id = view_data.compartment_id
        comp_list = list(ct.ntk_compartment_ids.values())
        view_comp_name = list(ct.ntk_compartment_ids.keys())[comp_list.index(view_comp_id)]
        view_name = view_data.display_name
        views = views + "\n" + str(view_comp_name) + '@' + str(view_name)
    endpoints = resolver.endpoints
    if endpoints:
        for endpoint in endpoints:
            e_tmpstr = {}
            e_key = vcn_name + '_' + endpoint.name
            e_tmpstr['region'] = region
            e_tmpstr['res_ntk_compartment'] = ntk_compartment_name
            #e_tmpstr['res_ntk_compartment'] = comp_name_list[resolver.compartment_id]
            e_tmpstr['res_vcn_name'] = vcn_name
            e_tmpstr['res_display_name'] = resolver.display_name
            e_tmpstr['res_views'] = views.lstrip('\n')
            e_tmpstr['res_id'] = resolver.id
            e_tmpstr['e_name'] = endpoint.name
            e_tmpstr['e_subnet'] = vnc_client.get_subnet(endpoint.subnet_id).data.display_name

            if endpoint.is_forwarding:
                e_type = 'Forwarding'
                ip = endpoint.forwarding_address
                type_and_ip = e_type + ':' + ip
            else:
                e_type = 'Listening'
                ip = endpoint.listening_address
                type_and_ip = e_type + ':' + ip
            e_tmpstr['e_type_ip'] = type_and_ip

            endpoint_data = (dns_client.get_resolver_endpoint(resolver_id=resolver.id, resolver_endpoint_name=endpoint.name)).data
            e_nsgs = ""
            for nsg_id in endpoint_data.nsg_ids:
                nsg_name = vnc_client.get_network_security_group(nsg_id).data.display_name
                e_nsgs = e_nsgs + "," + nsg_name
            e_tmpstr['e_nsgs'] = e_nsgs.lstrip(',')

            res_rules = ""
            r_index = 1
            for res_rule in resolver.rules:
                #rule_index = "rule"+str(r_index)
                if len(res_rule.qname_cover_conditions) != 0:
                    rule_condition = "Domains"
                    clients = ""
                    for client in res_rule.qname_cover_conditions:
                        clients = clients + "," + client

                elif len(res_rule.client_address_conditions) != 0:
                    rule_condition = "CIDRs"
                    clients = ""
                    for client in res_rule.client_address_conditions:
                        clients = clients + "," + client
                else:
                    rule_condition = "None"
                    clients = "Match all"
                rule_dest = res_rule.destination_addresses[0]
                #res_rule_item = rule_index + "::" + rule_condition + "::" + clients.lstrip(',') + "::" + rule_dest
                res_rule_item = rule_condition + "::" + clients.lstrip(',') + "::" + rule_dest
                if res_rule.source_endpoint_name == endpoint.name:
                    res_rules = res_rules + "\n" + res_rule_item
                #r_index += 1
            e_tmpstr['res_rule_detail'] = res_rules.lstrip('\n')

            e_map[e_key] = e_tmpstr
    else:
        e_tmpstr = {}
        e_key = vcn_name + '_'
        tmp_keys = ['res_rule_detail', 'e_nsgs', 'e_type_ip', 'e_subnet', 'e_name']
        for keys in tmp_keys:
            e_tmpstr[keys] = ""
        e_tmpstr['region'] = region
        e_tmpstr['res_ntk_compartment'] = ntk_compartment_name
        e_tmpstr['res_vcn_name'] = vcn_name
        e_tmpstr['res_display_name'] = resolver.display_name
        e_tmpstr['res_id'] = resolver.id
        e_tmpstr['res_views'] = views.lstrip('\n')
        e_map[e_key] = e_tmpstr

    return e_map


# Write values to columns map - values_for_column
def print_resolvers(resolver_tf_name, resolver, values_for_column,state, **value):
    endpoint_value = value
    region = endpoint_value['region']
    res_id = endpoint_value['res_id']
    e_name = endpoint_value['e_name']
    tf_resource = f'module.dns-resolvers[\\"{resolver_tf_name}\\"].oci_dns_resolver_endpoint.resolver_endpoint[\\"{e_name}\\"]'
    if e_name and tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" resolverId/{str(res_id)}/name/{str(e_name)}'

    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(endpoint_value['res_ntk_compartment'])
        elif col_header == 'VCN Name':
            values_for_column[col_header].append(endpoint_value['res_vcn_name'])
        elif col_header == 'Display Name':
            values_for_column[col_header].append(endpoint_value['res_display_name'])
        elif col_header == 'Associated Private Views':
            values_for_column[col_header].append(endpoint_value['res_views'])
        elif col_header == 'Endpoint Display Name':
            values_for_column[col_header].append(endpoint_value['e_name'])
        elif col_header == 'Endpoint Subnet Name':
            values_for_column[col_header].append(endpoint_value['e_subnet'])
        elif col_header == 'Endpoint Type:IP Address':
            values_for_column[col_header].append(endpoint_value['e_type_ip'])
        elif col_header == 'Endpoint NSGs':
            values_for_column[col_header].append(endpoint_value['e_nsgs'])
        elif col_header == 'Rules':
            values_for_column[col_header].append(endpoint_value['res_rule_detail'])
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(resolver, col_header, values_for_column)

# Execution of the code begins here
def export_dns_resolvers(inputfile, outdir, service_dir, config, signer, ct, export_compartments=[], export_regions=[],export_tags=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global values_for_column
    global serv_dir,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    serv_dir = service_dir
    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "DNS-Resolvers"
    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- DNS-Resolvers will be overwritten during export process!!!\n")

    # Fetch Resolver Details
    print("\nFetching details of DNS Resolvers ...")

    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{serv_dir}/' + file_name
        resource = 'import_' + sheetName.lower()
        # Create backups
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + reg + "/" + serv_dir, resource, file_name)

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
        region = reg.capitalize()
        dns_client = oci.dns.DnsClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        vnc_client = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        for ntk_compartment_name in export_compartments:
            vcns = oci.pagination.list_call_get_all_results(vnc_client.list_vcns, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="AVAILABLE")

            for vcn in vcns.data:
                resolver_id = vnc_client.get_vcn_dns_resolver_association(vcn.id).data.dns_resolver_id
                resolver = dns_client.get_resolver(resolver_id).data

                # Tags filter
                defined_tags = resolver.defined_tags
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

                endpoint_map = get_e_map(region, dns_client, vnc_client, ct, resolver, ntk_compartment_name)
                vcn_name = vnc_client.get_vcn(resolver.attached_vcn_id).data.display_name
                resolver_tf_name = vcn_name
                tf_resource = f'module.dns-resolvers[\\"{resolver_tf_name}\\"].oci_dns_resolver.resolver'
                if tf_resource not in state["resources"]:
                    importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(resolver.id)}'
                for key, value in endpoint_map.items():
                    print_resolvers(resolver_tf_name, resolver, values_for_column,state,**value)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("{0} DNS Resolvers and Endpoints exported into CD3.\n".format(len(values_for_column["Region"])))


    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if importCommands[reg] != "":
            init_commands = f'\n######### Writing import for DNS Resolvers #########\n\n#!/bin/bash\n{tf_or_tofu} init'
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])


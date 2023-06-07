#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export DNS Resolvers
#


import argparse
import oci
import os
from oci.config import DEFAULT_LOCATION
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
def print_resolvers(resolver_tf_name, resolver, values_for_column, **value):
    endpoint_value = value
    region = endpoint_value['region']
    res_id = endpoint_value['res_id']
    e_name = endpoint_value['e_name']
    importCommands[region.lower()].write("\nterraform import \"module.dns-resolvers[\\\"" + resolver_tf_name + "\\\"].oci_dns_resolver_endpoint.resolver_endpoint[\\\"" + e_name + "\\\"]\" resolverId/"+ str(res_id)+"/name/" + str(e_name))

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


# Argument parser
def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Export DNS resolvers on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export DNS resolvers objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument('service_dir', help='Structured out directory for creation of TF files')
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--export-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export Block Volume Objects")
    parser.add_argument("--export-regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                        required=False)
    return parser.parse_args()


# main methode for this script
def export_dns_resolvers(inputfile, _outdir, service_dir, _config, ct, export_compartments=[], export_regions=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global values_for_vcninfo
    global cd3file
    global reg
    global outdir
    global values_for_column
    global serv_dir

    serv_dir = service_dir
    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    outdir = _outdir
    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    sheetName = "DNS-Resolvers"
    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)
    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file, sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- DNS-Resolvers will be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{serv_dir}/' + file_name
        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + reg + "/" + serv_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Resolver Details
    print("\nFetching details of DNS Resolvers ...")

    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for DNS Resolvers #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()
        dns_client = oci.dns.DnsClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        vnc_client = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        for ntk_compartment_name in export_compartments:
            vcns = oci.pagination.list_call_get_all_results(vnc_client.list_vcns, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="AVAILABLE")
            for vcn in vcns.data:
                resolver_id = vnc_client.get_vcn_dns_resolver_association(vcn.id).data.dns_resolver_id
                resolver = dns_client.get_resolver(resolver_id).data
                endpoint_map = get_e_map(region, dns_client, vnc_client, ct, resolver, ntk_compartment_name)
                vcn_name = vnc_client.get_vcn(resolver.attached_vcn_id).data.display_name
                resolver_tf_name = vcn_name
                importCommands[region.lower()].write(
                    "\nterraform import \"module.dns-resolvers[\\\"" + resolver_tf_name + "\\\"].oci_dns_resolver.resolver\" " + str(
                        resolver.id))
                for key, value in endpoint_map.items():
                    print_resolvers(resolver_tf_name, resolver, values_for_column, **value)

    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("DNS Resolvers and Endpoints exported to CD3\n")

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{serv_dir}/' + file_name
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    export_dns_resolvers(args.inputfile, args.outdir, args.config, args.service_dir, args.network_compartments,args.regions)

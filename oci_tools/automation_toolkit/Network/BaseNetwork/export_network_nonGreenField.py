#!/usr/bin/python3


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.config import DEFAULT_LOCATION
import os
from .exportRoutetable import export_routetable
from .exportRoutetable import export_drg_routetable
from .exportSeclist import export_seclist

sys.path.append(os.getcwd() + "/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}

def print_nsgsl(values_for_column_nsgs,vnc,region, comp_name, vcn_name, nsg, nsgsl,i):
    tf_name = commonTools.check_tf_variable(str(nsg.display_name))
    sportmin = ""
    sportmax = ""
    dportmin = ""
    dportmax = ""
    icmptype = ""
    icmpcode = ""
    nsgname = ""
    is_stateless = ""
    nsgsourcetype = nsgsl.source_type
    nsgdestinationtype = nsgsl.destination_type
    nsgdestination = nsgsl.destination
    nsgsource = nsgsl.source

    if (nsgsl.destination_type == "CIDR_BLOCK"):
        nsgdestinationtype = "cidr"
    if (nsgsl.source_type == "CIDR_BLOCK"):
        nsgsourcetype = "cidr"
    if (nsgsl.source_type == None):
        nsgsourcetype = ""
    if (nsgsl.destination_type == None):
        nsgdestinationtype = ""

    if (nsgsl.destination_type == "SERVICE_CIDR_BLOCK"):
        nsgdestinationtype = "service"
    if (nsgsl.source_type == "SERVICE_CIDR_BLOCK"):
        nsgsourcetype = "service"
    if (nsgsl.destination is not None):
        if ("networksecuritygroup" in nsgsl.destination):
            nsgdestinationtype = "nsg"
            nsgname = vnc.get_network_security_group(nsgsl.destination).data
            nsgdestination = nsgname.display_name
    else:
        nsgdestination=""
    if (nsgsl.source is not None):
        if ("networksecuritygroup" in nsgsl.source):
            nsgsourcetype = "nsg"
            nsgname = vnc.get_network_security_group(nsgsl.source).data
            nsgsource = nsgname.display_name
    else:
        nsgsource=""
    if (nsgsl.tcp_options is not None):
        if (nsgsl.tcp_options.source_port_range is not None):
            sportmin = nsgsl.tcp_options.source_port_range.min
            sportmax = nsgsl.tcp_options.source_port_range.max
        if (nsgsl.tcp_options.destination_port_range is not None):
            dportmin = nsgsl.tcp_options.destination_port_range.min
            dportmax = nsgsl.tcp_options.destination_port_range.max
    if (nsgsl.udp_options is not None):
        if (nsgsl.udp_options.source_port_range is not None):
            sportmin = nsgsl.udp_options.source_port_range.min
            sportmax = nsgsl.udp_options.source_port_range.max
        if (nsgsl.udp_options.destination_port_range is not None):
            dportmin = nsgsl.udp_options.destination_port_range.min
            dportmax = nsgsl.udp_options.destination_port_range.max
    if (nsgsl.icmp_options is not None):
        if (nsgsl.icmp_options.type is not None):
            icmptype = nsgsl.icmp_options.type
        if (nsgsl.icmp_options.code is not None):
            icmpcode = nsgsl.icmp_options.code

    if nsgsl.protocol.lower()!="all":
        protocol = str(commonTools().protocol_dict[nsgsl.protocol].lower())
    else:
        protocol="all"
    for col_header in values_for_column_nsgs.keys():
        if (col_header == "Region"):
            values_for_column_nsgs[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_nsgs[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column_nsgs[col_header].append(vcn_name)
        elif(col_header == "Protocol"):
            values_for_column_nsgs[col_header].append(protocol)
        elif(col_header == "Soure Type"):
            values_for_column_nsgs[col_header].append(nsgsourcetype)
        elif(col_header == "Source"):
            values_for_column_nsgs[col_header].append(nsgsource)
        elif (col_header == "Destination Type"):
            values_for_column_nsgs[col_header].append(nsgdestinationtype)
        elif (col_header == "Destination"):
            values_for_column_nsgs[col_header].append(nsgdestination)
        elif (col_header == "SPortMin"):
            values_for_column_nsgs[col_header].append(sportmin)
        elif (col_header == "SPortMax"):
            values_for_column_nsgs[col_header].append(sportmax)
        elif (col_header == "DPortMin"):
            values_for_column_nsgs[col_header].append(dportmin)
        elif (col_header == "DPortMax"):
            values_for_column_nsgs[col_header].append(dportmax)
        elif (col_header == "ICMPType"):
            values_for_column_nsgs[col_header].append(icmptype)
        elif (col_header == "ICMPCode"):
            values_for_column_nsgs[col_header].append(icmpcode)
        elif(col_header == 'isStateless'):
            is_stateless = nsgsl.is_stateless
            if str(is_stateless).lower() == 'none':
                is_stateless = "false"
            values_for_column_nsgs[col_header].append(str(is_stateless))
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_nsgs = commonTools.export_tags(nsg, col_header, values_for_column_nsgs)
        else:
            oci_objs = [nsg,nsgsl]
            values_for_column_nsgs = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_nsgs,values_for_column_nsgs)


    importCommands[region.lower()].write("\nterraform import oci_core_network_security_group_security_rule." + tf_name + "_security_rule" + str(i) + " " + "networkSecurityGroups/" + str(nsg.id) + "/securityRules/" + str(nsgsl.id))


def print_nsg(values_for_column_nsgs,region, comp_name, vcn_name, nsg):
    tf_name = commonTools.check_tf_variable(str(nsg.display_name))

    for col_header in values_for_column_nsgs.keys():
        if (col_header == "Region"):
            values_for_column_nsgs[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_nsgs[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column_nsgs[col_header].append(vcn_name)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_nsgs = commonTools.export_tags(nsg, col_header, values_for_column_nsgs)
        else:
            oci_objs = [nsg]
            values_for_column_nsgs = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_nsgs,values_for_column_nsgs)

    importCommands[region.lower()].write("\nterraform import oci_core_network_security_group." + tf_name + " "+str(nsg.id))

def print_drgv2(values_for_column_drgv2,region, comp_name, vcn_info,drg_info,drg_attachment_info, drg_rt_info, import_drg_route_distribution_info,drg_route_distribution_statements):
    for col_header in values_for_column_drgv2.keys():
        if (col_header == "Region"):
            values_for_column_drgv2[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_drgv2[col_header].append(comp_name)
        elif (col_header == "DRG Name"):
            values_for_column_drgv2[col_header].append(drg_info.display_name)
        elif(col_header == "Attached To"):
            if(drg_attachment_info is None):
                values_for_column_drgv2[col_header].append('')
            else:
                if (drg_attachment_info.network_details is not None):
                    attach_type = drg_attachment_info.network_details.type
                    attach_id = drg_attachment_info.network_details.id
                # DRG v1
                else:
                    attach_type = "VCN"
                    attach_id = drg_attachment_info.vcn_id

                if(attach_type.upper()=="VCN"):
                    columnval = attach_type+"::"+vcn_info.display_name
                    values_for_column_drgv2[col_header].append(columnval)
                else:
                    columnval = attach_type + "::" + attach_id
                    values_for_column_drgv2[col_header].append(columnval)

        elif (col_header == "DRG RT Name"):
            if(drg_rt_info == None):
                values_for_column_drgv2[col_header].append("")
            else:
                values_for_column_drgv2[col_header].append(drg_rt_info.display_name)
        elif(col_header == 'Import DRG Route Distribution Name'):
            if import_drg_route_distribution_info == None:
                values_for_column_drgv2[col_header].append("")
            else:
                values_for_column_drgv2[col_header].append(import_drg_route_distribution_info.display_name)
        elif(col_header == "Import DRG Route Distribution Statements"):
            statement_val = ''
            if (drg_route_distribution_statements == None):
                statement_val=''
            else:
                for stmt in drg_route_distribution_statements.data:
                    priority=stmt.priority
                    if(len(stmt.match_criteria))!=0:
                        match_type=stmt.match_criteria[0].match_type
                        if(match_type=="DRG_ATTACHMENT_TYPE"):
                            attachment_type=stmt.match_criteria[0].attachment_type
                            statement_val=statement_val+"\n"+ match_type+"::"+attachment_type+"::"+str(priority)
                        elif(match_type=="DRG_ATTACHMENT_ID"):
                            drg_attachment_id=stmt.match_criteria[0].drg_attachment_id

                            statement_val = statement_val+"\n"+ match_type + "::" + drg_attachment_id + "::" + str(priority)
                    else:
                        statement_val = statement_val+"\n"+ "ALL::::"+str(priority)+ "\n"
            values_for_column_drgv2[col_header].append(statement_val)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_drgv2 = commonTools.export_tags(drg_info, col_header, values_for_column_drgv2)
        else:
            oci_objs = [drg_info,drg_attachment_info, drg_rt_info, import_drg_route_distribution_info]
            values_for_column_drgv2 = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_drgv2,values_for_column_drgv2)



def print_vcns(values_for_column_vcns,region, comp_name, vcn_info, drg_info, igw_info, ngw_info, sgw_info,lpg_display_names):
    for col_header in values_for_column_vcns.keys():
        if (col_header == "Region"):
            values_for_column_vcns[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_vcns[col_header].append(comp_name)
        elif (col_header == "DRG Required"):
            if(drg_info==None):
                values_for_column_vcns[col_header].append("n")
            else:
                values_for_column_vcns[col_header].append(drg_info.display_name)

        elif (col_header == "IGW Required"):
            if(igw_info==None):
                values_for_column_vcns[col_header].append("n")
            else:
                values_for_column_vcns[col_header].append(igw_info.display_name)
        elif (col_header == "NGW Required"):
            if(ngw_info==None):
                values_for_column_vcns[col_header].append("n")
            else:
                values_for_column_vcns[col_header].append(ngw_info.display_name)
        elif (col_header == "SGW Required"):
            if(sgw_info==None):
                values_for_column_vcns[col_header].append("n")
            else:
                values_for_column_vcns[col_header].append(sgw_info.display_name)
        elif (col_header == "LPG Required"):
            values_for_column_vcns[col_header].append(lpg_display_names)
        elif (col_header == "DNS Label"):
            value=vcn_info.dns_label
            if value is None:
                values_for_column_vcns[col_header].append("n")
            else:
                values_for_column_vcns[col_header].append(value)
        elif (col_header == "Hub/Spoke/Peer/None"):
            values_for_column_vcns[col_header].append("exported")
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_vcns = commonTools.export_tags(vcn_info, col_header, values_for_column_vcns)
        else:
            oci_objs = [vcn_info,drg_info,igw_info,ngw_info,sgw_info]
            values_for_column_vcns = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_vcns,values_for_column_vcns)

    tf_name = commonTools.check_tf_variable(vcn_info.display_name)
    importCommands[region.lower()].write("\nterraform import \"module.vcns[\\\"" + tf_name + "\\\"].oci_core_vcn.vcn[0]\" " + str(vcn_info.id))


def print_dhcp(values_for_column_dhcp,region, comp_name, vcn_name, dhcp_info):
    tf_name=vcn_name+"_"+str(dhcp_info.display_name)
    tf_name = commonTools.check_tf_variable(tf_name)

    options = dhcp_info.options
    server_type = ""
    custom_dns_servers_str = ""
    search_domain_names_str = ""
    oci_objs=[dhcp_info]
    for option in options:
        oci_objs.append(option)
        if (option.type == "DomainNameServer"):
            server_type = option.server_type
            custom_dns_servers = option.custom_dns_servers
            for custom_dns_server in custom_dns_servers:
                custom_dns_servers_str = custom_dns_servers_str + "," + custom_dns_server
            if (custom_dns_servers_str != "" and custom_dns_servers_str[0] == ','):
                custom_dns_servers_str = custom_dns_servers_str[1:]
        if (option.type == "SearchDomain"):
            search_domain_names = option.search_domain_names
            search_domain_names_str = search_domain_names[0]

    for col_header in values_for_column_dhcp.keys():
        if (col_header == "Region"):
            values_for_column_dhcp[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_dhcp[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column_dhcp[col_header].append(vcn_name)
        elif(col_header == "Server Type(VcnLocalPlusInternet|CustomDnsServer)"):
            values_for_column_dhcp[col_header].append(server_type)
        elif (col_header == "Search Domain"):
            values_for_column_dhcp[col_header].append(search_domain_names_str)
        elif (col_header == "Custom DNS Server"):
            values_for_column_dhcp[col_header].append(custom_dns_servers_str)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_dhcp = commonTools.export_tags(dhcp_info, col_header, values_for_column_dhcp)
        else:
            values_for_column_dhcp = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_dhcp, values_for_column_dhcp)
    if ("Default DHCP Options for " in dhcp_info.display_name):
        importCommands[region.lower()].write(
            "\nterraform import \"module.default-dhcps[\\\""+ tf_name + "\\\"].oci_core_default_dhcp_options.default_dhcp_option[0]\" " + str(dhcp_info.id))
    else:
        importCommands[region.lower()].write("\nterraform import \"module.custom-dhcps[\\\""+ tf_name + "\\\"].oci_core_dhcp_options.custom_dhcp_option[0]\" " + str(dhcp_info.id))


def print_subnets(values_for_column_subnets,region, comp_name, vcn_name, subnet_info, dhcp_name, rt_name, sl_names, add_def_seclist):
    tf_name = vcn_name + "_" + str(subnet_info.display_name)
    tf_name = commonTools.check_tf_variable(tf_name)
    importCommands[region.lower()].write("\nterraform import oci_core_subnet." + tf_name + " " + str(subnet_info.id))

    for col_header in values_for_column_subnets.keys():
        if (col_header == "Region"):
            values_for_column_subnets[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_subnets[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column_subnets[col_header].append(vcn_name)
        elif (col_header == "DHCP Option Name"):
            values_for_column_subnets[col_header].append(dhcp_name)
        elif (col_header == "Route Table Name"):
            values_for_column_subnets[col_header].append(rt_name)
        elif (col_header == "Seclist Names"):
            values_for_column_subnets[col_header].append(sl_names)
        elif (col_header == "Add Default Seclist"):
            values_for_column_subnets[col_header].append(add_def_seclist)
        elif (col_header == "Configure SGW Route(n|object_storage|all_services)"):
            values_for_column_subnets[col_header].append("-")
        elif (col_header == "Configure NGW Route(y|n)"):
            values_for_column_subnets[col_header].append("-")
        elif (col_header == "Configure IGW Route(y|n)"):
            values_for_column_subnets[col_header].append("-")
        elif (col_header == "Configure OnPrem Route(y|n)"):
            values_for_column_subnets[col_header].append("-")
        elif (col_header == "Configure VCNPeering Route(y|n)"):
            values_for_column_subnets[col_header].append("-")
        elif ("Availability Domain" in col_header):
            value = subnet_info.__getattribute__(sheet_dict_subnets[col_header])
            ad = ""
            if (value == None):
                ad = "Regional"
            elif ("AD-1" in value):
                ad = "AD1"
            elif ("AD-2" in value):
                ad = "AD2"
            elif ("AD-3" in value):
                ad = "AD3"
            values_for_column_subnets[col_header].append(ad)
            # Get public or private
        elif (col_header == "Type(private|public)"):
            value = subnet_info.__getattribute__(sheet_dict_subnets[col_header])
            if (value == True):
                access = "private"
            elif (value == False):
                access = "public"
            values_for_column_subnets[col_header].append(access)

        elif (col_header == "DNS Label"):
            value = subnet_info.dns_label
            if value is None:
                values_for_column_subnets[col_header].append("n")
            else:
                values_for_column_subnets[col_header].append(value)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_subnets = commonTools.export_tags(subnet_info, col_header, values_for_column_subnets)
        else:
            oci_objs = [subnet_info]
            values_for_column_subnets = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_subnets,values_for_column_subnets)

def parse_args():
    parser = argparse.ArgumentParser(description="Export Network Objects in OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export network objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--configFileName", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", nargs='*', help="comma seperated Compartments for which to export Networking Objects", required=False)
    return parser.parse_args()


def export_networking(inputfile, outdir, _config, network_compartments=[]):
    global tf_import_cmd
    global values_for_column_vcns
    global values_for_column_drgv2
    global values_for_column_dhcp
    global values_for_column_subnets
    global values_for_column_nsgs
    global sheet_dict_vcns
    global sheet_dict_drgv2
    global sheet_dict_dhcp
    global sheet_dict_subnets
    global sheet_dict_nsgs
    global importCommands
    global config

    cd3file = inputfile
    input_config_file = _config
    input_compartment_names = network_compartments


    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    configFileName = _config
    config = oci.config.from_file(file_location=configFileName)

    # Read CD3
    df,values_for_column_vcns=commonTools.read_cd3(cd3file,"VCNs")
    df, values_for_column_drgv2 = commonTools.read_cd3(cd3file, "DRGs")
    df, values_for_column_dhcp = commonTools.read_cd3(cd3file, "DHCP")
    df, values_for_column_subnets = commonTools.read_cd3(cd3file, "Subnets")
    df, values_for_column_nsgs = commonTools.read_cd3(cd3file, "NSGs")

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Get dict for columns from Excel_Columns
    sheet_dict_vcns=ct.sheet_dict["VCNs"]
    sheet_dict_drgv2 = ct.sheet_dict["DRGs"]
    sheet_dict_dhcp = ct.sheet_dict["DHCP"]
    sheet_dict_subnets = ct.sheet_dict["Subnets"]
    sheet_dict_nsgs = ct.sheet_dict["NSGs"]

    # Check Compartments
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments, ct.ntk_compartment_ids)


    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- VCNs, VCN Info, Subnets, DHCP, SecRulesinOCI and RouteRulesinOCI DRGRouteRulesinOCI would be overwritten during export process!!!\n")

    # Create backups
    for reg in ct.all_regions:
        if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh")):
            commonTools.backup_file(outdir + "/" + reg, "tf_import_network","tf_import_commands_network_nonGF.sh")
        if (os.path.exists(outdir + "/" + reg + "/obj_names.safe")):
            commonTools.backup_file(outdir + "/" + reg, "obj_names","obj_names.safe")
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")
        oci_obj_names[reg] = open(outdir + "/" + reg + "/obj_names.safe", "w")

    # Fetch VCNs
    print("\nFetching VCNs...")
    for reg in ct.all_regions:
        importCommands[reg].write("\n######### Writing import for VCNs #########\n")
        config.__setitem__("region", ct.region_dict[reg])
        vnc = VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        region = reg.capitalize()
        comp_ocid_done=[]
        for ntk_compartment_name in comp_list_fetch:
            #if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                #if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                #    continue
                #comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                for vcn in vcns.data:
                    vcn_info = vcn
                    # Fetch VCN components assuming components are in same comp as VCN

                    #DRG attachemnt is in same compartment as VCN by default
                    DRG_Attachments = oci.pagination.list_call_get_all_results(vnc.list_drg_attachments,
                                                                               compartment_id=ct.ntk_compartment_ids[
                                                                                   ntk_compartment_name], vcn_id=vcn.id)
                    drg_info=None
                    igw_info = None
                    ngw_info = None
                    sgw_info = None

                    for drg_attachment_info in DRG_Attachments.data:
                        drg_id = drg_attachment_info.drg_id
                        drg_info = vnc.get_drg(drg_id).data


                    #igw_display_name = "n"
                    IGWs = oci.pagination.list_call_get_all_results(vnc.list_internet_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                    for igw in IGWs.data:
                        igw_info = igw
                        igw_display_name = igw_info.display_name
                        tf_name = vcn_info.display_name + "_" + igw_display_name
                        tf_name=commonTools.check_tf_variable(tf_name)
                        importCommands[reg].write("\nterraform import \"module.igws[\\\"" + tf_name + "\\\"].oci_core_internet_gateway.internet_gateway[0]\" " + igw_info.id)

                    #ngw_display_name = "n"
                    NGWs = oci.pagination.list_call_get_all_results(vnc.list_nat_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                    for ngw in NGWs.data:
                        ngw_info = ngw
                        ngw_display_name = ngw_info.display_name
                        tf_name = vcn_info.display_name + "_" + ngw_display_name
                        tf_name = commonTools.check_tf_variable(tf_name)

                        importCommands[reg].write("\nterraform import \"module.ngws[\\\"" + tf_name + "\\\"].oci_core_nat_gateway.nat_gateway[0]\" " + ngw_info.id)

                    #sgw_display_name = "n"
                    SGWs = oci.pagination.list_call_get_all_results(vnc.list_service_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                    for sgw in SGWs.data:
                        sgw_info = sgw
                        sgw_display_name = sgw_info.display_name
                        tf_name = vcn_info.display_name + "_" + sgw_display_name
                        tf_name = commonTools.check_tf_variable(tf_name)
                        importCommands[reg].write("\nterraform import \"module.sgws[\\\"" + tf_name + "\\\"].oci_core_service_gateway.service_gateway[0]\" " + sgw_info.id)

                    lpg_display_names = ""
                    LPGs = oci.pagination.list_call_get_all_results(vnc.list_local_peering_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id)
                    for lpg in LPGs.data:
                        if (lpg.lifecycle_state != "AVAILABLE"):
                            continue
                        lpg_info = lpg
                        lpg_display_names = lpg_info.display_name + "," + lpg_display_names

                        lpg_route_table_id = lpg_info.route_table_id
                        if (lpg_route_table_id is not None):
                            oci_obj_names[region.lower()].write(
                                "\nlpginfo::::" + vcn_info.display_name + "::::" + lpg_info.display_name + "::::" + vnc.get_route_table(
                                    lpg_route_table_id).data.display_name)

                        tf_name = vcn_info.display_name + "_" + lpg_info.display_name
                        tf_name = commonTools.check_tf_variable(tf_name)
                        importCommands[reg].write(
                            "\nterraform import \"module.exported-lpgs[\\\"" + tf_name + "\\\"].oci_core_local_peering_gateway.local_peering_gateway[0]\" " + lpg_info.id)

                    if (lpg_display_names == ""):
                        lpg_display_names = "n"
                    elif (lpg_display_names[-1] == ','):
                        lpg_display_names = lpg_display_names[:-1]

                    # Fill VCNs Tab
                    print_vcns(values_for_column_vcns,region,ntk_compartment_name, vcn_info, drg_info,igw_info,ngw_info, sgw_info, lpg_display_names)

    commonTools.write_to_cd3(values_for_column_vcns, cd3file, "VCNs")
    print("VCNs exported to CD3\n")

    # Fetch DRGs
    print("\nFetching DRGs...")
    for reg in ct.all_regions:
        importCommands[reg].write("\n######### Writing import for DRGs #########\n")
        config.__setitem__("region", ct.region_dict[reg])
        vnc = VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        region = reg.capitalize()
        drg_ocid=[]
        drg_rt_ocid=[]
        drg_comp_name=''
        drg_version="DRGv2"
        for ntk_compartment_name in comp_list_fetch:
              #drgs = oci.pagination.list_call_get_all_results(vnc.list_drgs,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
                #for drg in drgs.data:
                            DRG_Attachments = oci.pagination.list_call_get_all_results(vnc.list_drg_attachments,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])#,lifecycle_state ="ATTACHED")#,attachment_type="ALL")

                            for drg_attachment_info in DRG_Attachments.data:
                                if (drg_attachment_info.lifecycle_state != "ATTACHED"):
                                    continue
                                drg_attachment_name = drg_attachment_info.display_name
                                drg_id = drg_attachment_info.drg_id
                                drg_info = vnc.get_drg(drg_id).data

                                # Attachment Data
                                drg_display_name = drg_info.display_name
                                drg_comp_id=drg_info.compartment_id
                                for key, val in ct.ntk_compartment_ids.items():
                                    if val == drg_comp_id:
                                        if("::" in key):
                                            drg_comp_name = key
                                            continue
                                        else:
                                            drg_comp_name = key
                                            break

                                tf_name = commonTools.check_tf_variable(drg_display_name)

                                #Get Attachment Details
                                # DRG v2
                                if(drg_attachment_info.network_details is not None):
                                    attach_type = drg_attachment_info.network_details.type
                                    attach_id = drg_attachment_info.network_details.id
                                #DRG v1
                                else:
                                    drg_version = "DRGv1"
                                    attach_type = "VCN"
                                    attach_id = drg_attachment_info.vcn_id

                                oci_obj_names[ct.home_region].write("\nDRG Version::::" + drg_version+"::::None::::None")

                                if (attach_type.upper() == "VCN"):
                                    vcn_drgattach_route_table_id = drg_attachment_info.route_table_id
                                    vcn_info = vnc.get_vcn(attach_id).data
                                    if (vcn_drgattach_route_table_id is not None):
                                        oci_obj_names[reg].write("\ndrginfo::::" + vcn_info.display_name + "::::" + drg_info.display_name + "::::" + vnc.get_route_table(
                                        vcn_drgattach_route_table_id).data.display_name)
                                    else:
                                        oci_obj_names[reg].write("\ndrginfo::::" + vcn_info.display_name + "::::" + drg_info.display_name + "::::None")


                                if (drg_id not in drg_ocid):
                                    importCommands[reg].write("\nterraform import oci_core_drg." + tf_name + " " + drg_info.id)
                                    drg_ocid.append(drg_id)

                                #tf_name = vcn_info.display_name + "_" + drg_attachment_name
                                tf_name = commonTools.check_tf_variable(drg_attachment_name)

                                importCommands[reg].write("\nterraform import oci_core_drg_attachment." + tf_name + " " + drg_attachment_info.id)
                                oci_obj_names[reg].write("\ndrgattachinfo::::" + vcn_info.display_name + "::::" + drg_display_name + "::::" + drg_attachment_name)

                                drg_route_table_id = drg_attachment_info.drg_route_table_id

                                ##DRG v2
                                drg_route_table_info =None
                                import_drg_route_distribution_info = None
                                drg_route_distribution_statements = None

                                if(drg_route_table_id is not None):
                                    drg_rt_ocid.append(drg_route_table_id)
                                    drg_route_table_info = vnc.get_drg_route_table(drg_route_table_id).data

                                    import_drg_route_distribution_id = drg_route_table_info.import_drg_route_distribution_id
                                    if(import_drg_route_distribution_id!=None):
                                        import_drg_route_distribution_info = vnc.get_drg_route_distribution(import_drg_route_distribution_id).data
                                        drg_route_distribution_statements = vnc.list_drg_route_distribution_statements(import_drg_route_distribution_info.id)

                                        tf_name = commonTools.check_tf_variable(drg_display_name+"_"+import_drg_route_distribution_info.display_name)
                                        if(import_drg_route_distribution_info.display_name not in commonTools.drg_auto_RDs):
                                            importCommands[reg].write("\nterraform import oci_core_drg_route_distribution." + tf_name + " " + import_drg_route_distribution_info.id)

                                            k = 1
                                            for stmt in drg_route_distribution_statements.data:
                                                importCommands[reg].write("\nterraform import oci_core_drg_route_distribution_statement." + tf_name + "_statement" + str(k) + " drgRouteDistributions/" + import_drg_route_distribution_info.id + "/statements/" + stmt.id)
                                                k=k+1

                                print_drgv2(values_for_column_drgv2, region, drg_comp_name, vcn_info,drg_info, drg_attachment_info, drg_route_table_info, import_drg_route_distribution_info,drg_route_distribution_statements)

                            # Get All Other RTs for this DRG only if it is DRGv2
                            # DRG v2
                            for drg_id in drg_ocid:
                                drg_attachment_info = None
                                vcn_info=None
                                drg_info = vnc.get_drg(drg_id).data

                                if drg_info.default_drg_route_tables is not None:
                                    DRG_RTs = oci.pagination.list_call_get_all_results(vnc.list_drg_route_tables,
                                                                                       drg_id=drg_id)
                                    for drg_route_table_info in DRG_RTs.data:
                                        drg_rt_id = drg_route_table_info.id
                                        #RT associated with attachment already processed above
                                        if (drg_rt_id in drg_rt_ocid):
                                            continue

                                        #Process other RTs of this DRG
                                        drg_rt_ocid.append(drg_rt_id)
                                        import_drg_route_distribution_info = None
                                        drg_route_distribution_statements = None

                                        import_drg_route_distribution_id = drg_route_table_info.import_drg_route_distribution_id
                                        if (import_drg_route_distribution_id != None):
                                            import_drg_route_distribution_info = vnc.get_drg_route_distribution(
                                                import_drg_route_distribution_id).data
                                            drg_route_distribution_statements = vnc.list_drg_route_distribution_statements(
                                                import_drg_route_distribution_info.id)

                                            tf_name = commonTools.check_tf_variable(
                                                drg_display_name + "_" + import_drg_route_distribution_info.display_name)
                                            if (import_drg_route_distribution_info.display_name not in commonTools.drg_auto_RDs):
                                                importCommands[reg].write(
                                                    "\nterraform import oci_core_drg_route_distribution." + tf_name + " " + import_drg_route_distribution_info.id)

                                                k = 1
                                                for stmt in drg_route_distribution_statements.data:
                                                    importCommands[reg].write(
                                                        "\nterraform import oci_core_drg_route_distribution_statement." + tf_name + "_statement" + str(
                                                            k) + " drgRouteDistributions/" + import_drg_route_distribution_info.id + "/statements/" + stmt.id)
                                                    k = k + 1
                                        print_drgv2(values_for_column_drgv2, region, drg_comp_name, vcn_info, drg_info,
                                                    drg_attachment_info, drg_route_table_info,
                                                    import_drg_route_distribution_info,
                                                    drg_route_distribution_statements)


    commonTools.write_to_cd3(values_for_column_drgv2, cd3file, "DRGs")
    print("DRGs exported to CD3\n")

    # Fetch NSGs
    rows = []
    print("\nFetching NSGs...")
    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for NSG #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        vnc = VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        region = reg.capitalize()
        #comp_ocid_done = []
        for ntk_compartment_name in comp_list_fetch:
            #if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                #if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                #    continue
                #comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")

                for vcn in vcns.data:
                    vcn_info = vnc.get_vcn(vcn.id).data
                    #comp_ocid_done_again = []
                    for ntk_compartment_name_again in comp_list_fetch:
                    #    if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                    #        if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                    #            continue
                    #        comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
                            NSGs = oci.pagination.list_call_get_all_results(vnc.list_network_security_groups,
                                                                            compartment_id=ct.ntk_compartment_ids[
                                                                                ntk_compartment_name_again], vcn_id=vcn.id,
                                                                            lifecycle_state="AVAILABLE")
                            nsglist = [""]
                            for nsg in NSGs.data:
                                NSGSLs = vnc.list_network_security_group_security_rules(nsg.id)
                                i = 1
                                for nsgsl in NSGSLs.data:
                                    nsglist.append(nsg.id)
                                    print_nsgsl(values_for_column_nsgs,vnc,region, ntk_compartment_name_again, vcn_info.display_name, nsg, nsgsl, i)
                                    i = i + 1
                                if (nsg.id not in nsglist):
                                    print_nsg(values_for_column_nsgs,region, ntk_compartment_name_again, vcn_info.display_name, nsg)
                                else:
                                    tf_name = commonTools.check_tf_variable(str(nsg.display_name))
                                    importCommands[region.lower()].write("\nterraform import oci_core_network_security_group." + tf_name + " " + str(nsg.id))

    commonTools.write_to_cd3(values_for_column_nsgs, cd3file, "NSGs")
    print("NSGs exported to CD3\n")

    # Fetch DHCP
    print("\nFetching DHCP...")
    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for DHCP #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        vnc = VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        region = reg.capitalize()
        #comp_ocid_done = []
        for ntk_compartment_name in comp_list_fetch:
        #    if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
        #        if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
        #            continue
        #        comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                for vcn in vcns.data:
                    vcn_info = vnc.get_vcn(vcn.id).data
        #            comp_ocid_done_again = []
                    for ntk_compartment_name_again in comp_list_fetch:
        #                if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
        #                    if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
        #                        continue
        #                    comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
                            DHCPs = oci.pagination.list_call_get_all_results(vnc.list_dhcp_options,
                                                                             compartment_id=ct.ntk_compartment_ids[
                                                                                 ntk_compartment_name_again], vcn_id=vcn.id,
                                                                             lifecycle_state="AVAILABLE")
                            for dhcp in DHCPs.data:
                                dhcp_info = dhcp
                                print_dhcp(values_for_column_dhcp,region, ntk_compartment_name_again, vcn_info.display_name, dhcp_info)
    commonTools.write_to_cd3(values_for_column_dhcp, cd3file, "DHCP")
    print("DHCP exported to CD3\n")

    # Fetch Subnets
    print("\nFetching Subnets...")
    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for Subnets #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        vnc = VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        region = reg.capitalize()
        #comp_ocid_done = []
        for ntk_compartment_name in comp_list_fetch:
        #    if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
        #        if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
        #            continue
        #        comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                for vcn in vcns.data:
                    vcn_info = vnc.get_vcn(vcn.id).data
        #            comp_ocid_done_again = []
                    for ntk_compartment_name_again in comp_list_fetch:
        #                if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
        #                    if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
        #                        continue
        #                    comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
                            Subnets = oci.pagination.list_call_get_all_results(vnc.list_subnets, compartment_id=ct.ntk_compartment_ids[
                                ntk_compartment_name_again], vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                            for subnet in Subnets.data:
                                subnet_info = subnet
                                dhcp_id = subnet_info.dhcp_options_id
                                dhcp_name = vnc.get_dhcp_options(dhcp_id).data.display_name
                                if ("Default DHCP Options for " in dhcp_name):
                                    dhcp_name = ""

                                rt_id = subnet_info.route_table_id
                                rt_name = vnc.get_route_table(rt_id).data.display_name
                                if ("Default Route Table for " in rt_name):
                                    rt_name = "n"

                                sl_ids = subnet_info.security_list_ids
                                sl_names = ""
                                add_def_seclist = 'n'
                                for sl_id in sl_ids:
                                    sl_name = vnc.get_security_list(sl_id).data.display_name
                                    if ("Default Security List for " in sl_name):
                                        add_def_seclist = 'y'
                                        continue
                                    sl_names = sl_name + "," + sl_names
                                if (sl_names == ""):
                                    sl_names = "n"
                                elif (sl_names != "" and sl_names[-1] == ','):
                                    sl_names = sl_names[:-1]
                                # Fill Subnets tab
                                print_subnets(values_for_column_subnets,region, ntk_compartment_name_again, vcn_info.display_name, subnet_info, dhcp_name,
                                              rt_name, sl_names, add_def_seclist)
    commonTools.write_to_cd3(values_for_column_subnets, cd3file, "Subnets")
    print("Subnets exported to CD3\n")

    for reg in ct.all_regions:
        importCommands[reg].close()
        oci_obj_names[reg].close()

    # Fetch RouteRules and SecRules
    export_seclist(inputfile, network_compartments=network_compartments, _config=input_config_file, _tf_import_cmd=True, outdir=outdir )
    print("SecRules exported to CD3\n")

    export_routetable(inputfile, network_compartments=network_compartments, _config=input_config_file, _tf_import_cmd=True, outdir=outdir )
    print("RouteRules exported to CD3\n")

    export_drg_routetable(inputfile, network_compartments=network_compartments, _config=input_config_file, _tf_import_cmd=True, outdir=outdir )
    print("DRG RouteRules exported to CD3\n")

    for reg in ct.all_regions:
        script_file = f'{outdir}/{reg}/tf_import_commands_network_nonGF.sh'
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')
        if "linux" in sys.platform:
            os.chmod(script_file, 0o755)


if __name__=="__main__":
    args = parse_args()
    export_networking(args.inputfile, args.outdir, args.config, args.network_compartments)

#!/usr/bin/python3


import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
import os

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
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_nsgs = commonTools.export_tags(nsg, col_header, values_for_column_nsgs)
        else:
            oci_objs = [nsg,nsgsl]
            values_for_column_nsgs = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_nsgs,values_for_column_nsgs)

        """elif(col_header in sheet_dict_nsgs.keys()):
            # Check if property exists for nsg
            try:
                value = nsg.__getattribute__(sheet_dict_nsgs[col_header])
                value = commonTools.check_exported_value(value)
                values_for_column_nsgs[col_header].append(value)
            #Check if property exists for nsgsl
            except AttributeError as e:
                try:
                    value = nsgsl.__getattribute__(sheet_dict_nsgs[col_header])
                    value = commonTools.check_exported_value(value)
                    values_for_column_nsgs[col_header].append(value)
                except AttributeError as e:
                    value = ""
                    values_for_column_nsgs[col_header].append(value)
        else:
            # Check if property exists for nsg
            try:
                value = nsg.__getattribute__(commonTools.check_column_headers(col_header))
                value = commonTools.check_exported_value(value)
                values_for_column_nsgs[col_header].append(value)
            # Check if property exists for nsgsl
            except AttributeError as e:
                try:
                    value = nsgsl.__getattribute__(commonTools.check_column_headers(col_header))
                    value = commonTools.check_exported_value(value)
                    values_for_column_nsgs[col_header].append(value)
                except AttributeError as e:
                    value = ""
                    values_for_column_nsgs[col_header].append(value)
        """

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

        """elif (col_header in sheet_dict_nsgs.keys()):
            # Check if property exists for nsg
            try:
                value = nsg.__getattribute__(sheet_dict_nsgs[col_header])
                value = commonTools.check_exported_value(value)
                values_for_column_nsgs[col_header].append(value)
            # Check if property exists for nsgsl
            except AttributeError as e:
                value = ""
                values_for_column_nsgs[col_header].append(value)
        else:
            # Check if property exists for nsg
            try:
                value = nsg.__getattribute__(commonTools.check_column_headers(col_header))
                value = commonTools.check_exported_value(value)
                values_for_column_nsgs[col_header].append(value)
            # Check if property exists for nsgsl
            except AttributeError as e:
                value = ""
                values_for_column_nsgs[col_header].append(value)
            """
    importCommands[region.lower()].write("\nterraform import oci_core_network_security_group." + tf_name + " "+str(nsg.id))

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

        """elif (col_header in sheet_dict_vcns.keys()):
            # Check if property exists for vcn
            try:
                value = vcn_info.__getattribute__(sheet_dict_vcns[col_header])
                value = commonTools.check_exported_value(value)
                values_for_column_vcns[col_header].append(value)
            except AttributeError as e:
                found = 0
                if(drg_info!=None):
                    try:
                        value = drg_info.__getattribute__(sheet_dict_vcns[col_header])
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if (igw_info != None):
                    try:
                        value = igw_info.__getattribute__(sheet_dict_vcns[col_header])
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if (ngw_info != None):
                    try:
                        value = ngw_info.__getattribute__(sheet_dict_vcns[col_header])
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if (sgw_info != None):
                    try:
                        value = sgw_info.__getattribute__(sheet_dict_vcns[col_header])
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if(found == 0):
                    value=""
                    values_for_column_vcns[col_header].append(value)
        else:
            # Check if property exists for vcn
            try:
                value = vcn_info.__getattribute__(commonTools.check_column_headers(col_header))
                value = commonTools.check_exported_value(value)
                values_for_column_vcns[col_header].append(value)
            except AttributeError as e:
                found = 0
                if (drg_info != None):
                    try:
                        value = drg_info.__getattribute__(commonTools.check_column_headers(col_header))
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if (igw_info != None):
                    try:
                        value = igw_info.__getattribute__(commonTools.check_column_headers(col_header))
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if (ngw_info != None):
                    try:
                        value = ngw_info.__getattribute__(commonTools.check_column_headers(col_header))
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if (sgw_info != None):
                    try:
                        value = sgw_info.__getattribute__(commonTools.check_column_headers(col_header))
                        value = commonTools.check_exported_value(value)
                        values_for_column_vcns[col_header].append(value)
                        found = 1
                    except AttributeError as e:
                        pass
                if(found == 0):
                    value = ""
                    values_for_column_vcns[col_header].append(value)
            """
    tf_name = commonTools.check_tf_variable(vcn_info.display_name)
    importCommands[region.lower()].write("\nterraform import oci_core_vcn." + tf_name + " " + str(vcn_info.id))


def print_dhcp(values_for_column_dhcp,region, comp_name, vcn_name, dhcp_info):
    tf_name=vcn_name+"_"+str(dhcp_info.display_name)
    tf_name = commonTools.check_tf_variable(tf_name)
    # Dont write Default DHCP option to cd3, jst write TF import command

    options = dhcp_info.options
    for col_header in values_for_column_dhcp.keys():
        if (col_header == "Region"):
            values_for_column_dhcp[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_dhcp[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column_dhcp[col_header].append(vcn_name)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_dhcp = commonTools.export_tags(dhcp_info, col_header, values_for_column_dhcp)
        elif (col_header in sheet_dict_dhcp.keys()):
            # Check if property exists for dhcp_info
            try:
                value = dhcp_info.__getattribute__(sheet_dict_dhcp[col_header])
                value = commonTools.check_exported_value(value)
                values_for_column_dhcp[col_header].append(value)
            except AttributeError as e:
                # Check if property exists for option
                for option in options:
                    try:
                        value = option.__getattribute__(sheet_dict_dhcp[col_header])
                        value = commonTools.check_exported_value(value)
                        values_for_column_dhcp[col_header].append(value)
                    except AttributeError as e:
                        pass
        else:
            # Check if property exists for dhcp_info
            try:
                value = dhcp_info.__getattribute__(commonTools.check_column_headers(col_header))
                value = commonTools.check_exported_value(value)
                values_for_column_dhcp[col_header].append(value)
            except AttributeError as e:
                # Check if property exists for option
                for option in options:
                    try:
                        value = option.__getattribute__(commonTools.check_column_headers(col_header))
                        value = commonTools.check_exported_value(value)
                        values_for_column_dhcp[col_header].append(value)
                    except AttributeError as e:
                        value=""
                        values_for_column_dhcp[col_header].append(value)
                        break
    if ("Default DHCP Options for " in dhcp_info.display_name):
        importCommands[region.lower()].write(
            "\nterraform import oci_core_default_dhcp_options." + tf_name + " " + str(dhcp_info.id))
    else:
        importCommands[region.lower()].write("\nterraform import oci_core_dhcp_options." + tf_name + " " + str(dhcp_info.id))


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

        """elif (col_header in sheet_dict_subnets.keys()):
            # Check if property exists for subnet_info
            try:
                value = subnet_info.__getattribute__(sheet_dict_subnets[col_header])
                value = commonTools.check_exported_value(value)
                values_for_column_subnets[col_header].append(value)
            except AttributeError as e:
                value = ""
                values_for_column_subnets[col_header].append(value)
        else:
            # Check if property exists for subnet_info
            try:
                value = subnet_info.__getattribute__(commonTools.check_column_headers(col_header))
                value = commonTools.check_exported_value(value)
                values_for_column_subnets[col_header].append(value)
            except AttributeError as e:
                value = ""
                values_for_column_subnets[col_header].append(value)
        """

def main():
    parser = argparse.ArgumentParser(description="Export Route Table on OCI to CD3")
    parser.add_argument("cd3file", help="path of CD3 excel file to export network objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export Networking Objects",
                        required=False)
    parser.add_argument("--configFileName", help="Config file name", required=False)

    global tf_import_cmd
    global values_for_column_vcns
    global values_for_column_dhcp
    global values_for_column_subnets
    global values_for_column_nsgs
    global sheet_dict_vcns
    global sheet_dict_dhcp
    global sheet_dict_subnets
    global sheet_dict_nsgs
    global importCommands
    global config

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    cd3file = args.cd3file
    outdir = args.outdir
    input_config_file = args.configFileName
    input_compartment_list = args.networkCompartment
    if (input_compartment_list is not None):
        input_compartment_names = input_compartment_list.split(",")
        input_compartment_names = [x.strip() for x in input_compartment_names]
    else:
        input_compartment_names = None


    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    if args.configFileName is not None:
        configFileName = args.configFileName
        config = oci.config.from_file(file_location=configFileName)
    else:
        configFileName=""
        config = oci.config.from_file()

    # Read CD3
    df,values_for_column_vcns=commonTools.read_cd3(cd3file,"VCNs")
    df, values_for_column_dhcp = commonTools.read_cd3(cd3file, "DHCP")
    df, values_for_column_subnets = commonTools.read_cd3(cd3file, "Subnets")
    df, values_for_column_nsgs = commonTools.read_cd3(cd3file, "NSGs")

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Get dict for columns from Excel_Columns
    sheet_dict_vcns=ct.sheet_dict["VCNs"]
    sheet_dict_dhcp = ct.sheet_dict["DHCP"]
    sheet_dict_subnets = ct.sheet_dict["Subnets"]
    sheet_dict_nsgs = ct.sheet_dict["NSGs"]


    # Check Compartments
    remove_comps = []
    if (input_compartment_names is not None):
        for x in range(0, len(input_compartment_names)):
            if (input_compartment_names[x] not in ct.ntk_compartment_ids.keys()):
                print("Input compartment: " + input_compartment_names[x] + " doesn't exist in OCI")
                remove_comps.append(input_compartment_names[x])

        input_compartment_names = [x for x in input_compartment_names if x not in remove_comps]
        if (len(input_compartment_names) == 0):
            print("None of the input compartments specified exist in OCI..Exiting!!!")
            exit(1)
        else:
            print("Fetching for Compartments... " + str(input_compartment_names))
    else:
        print("Fetching for all Compartments...")
    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- VCNs, VCN Info, Subnets, DHCP, SecRulesinOCI and RouteRulesinOCI would be overwritten during export process!!!\n")


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
        vnc = VirtualNetworkClient(config)
        region = reg.capitalize()
        comp_ocid_done=[]
        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                for vcn in vcns.data:
                    vcn_info = vcn
                    # Fetch VCN components assuming components are in same comp as VCN
                    #drg_display_name = "n"
                    DRG_Attachments = oci.pagination.list_call_get_all_results(vnc.list_drg_attachments,
                                                                               compartment_id=ct.ntk_compartment_ids[
                                                                                   ntk_compartment_name], vcn_id=vcn.id)
                    drg_info=None
                    igw_info=None
                    ngw_info = None
                    sgw_info = None

                    for drg_attachment in DRG_Attachments.data:
                        drg_attachment_info = drg_attachment
                        drg_attachment_name = drg_attachment_info.display_name
                        drg_id = drg_attachment_info.drg_id

                        drg_info = vnc.get_drg(drg_id).data
                        drg_display_name = drg_info.display_name

                        drgattach_route_table_id = drg_attachment_info.route_table_id
                        if (drgattach_route_table_id is not None):
                            oci_obj_names[reg].write(
                                "\ndrginfo::::" + vcn_info.display_name + "::::" + drg_display_name + "::::" + vnc.get_route_table(
                                    drgattach_route_table_id).data.display_name)
                        tf_name = commonTools.check_tf_variable(drg_display_name)
                        importCommands[reg].write("\nterraform import oci_core_drg." + tf_name + " " + drg_info.id)

                        tf_name = vcn_info.display_name + "_" + drg_attachment_name
                        tf_name=commonTools.check_tf_variable(tf_name)

                        importCommands[reg].write("\nterraform import oci_core_drg_attachment." + tf_name + " " + drg_attachment_info.id)
                        oci_obj_names[reg].write("\ndrgattachinfo::::" + vcn_info.display_name + "::::" + drg_display_name + "::::" + drg_attachment_name)

                    #igw_display_name = "n"
                    IGWs = oci.pagination.list_call_get_all_results(vnc.list_internet_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                    for igw in IGWs.data:
                        igw_info = igw
                        igw_display_name = igw_info.display_name
                        tf_name = vcn_info.display_name + "_" + igw_display_name
                        tf_name=commonTools.check_tf_variable(tf_name)
                        importCommands[reg].write("\nterraform import oci_core_internet_gateway." + tf_name + " " + igw_info.id)

                    #ngw_display_name = "n"
                    NGWs = oci.pagination.list_call_get_all_results(vnc.list_nat_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                    for ngw in NGWs.data:
                        ngw_info = ngw
                        ngw_display_name = ngw_info.display_name
                        tf_name = vcn_info.display_name + "_" + ngw_display_name
                        tf_name = commonTools.check_tf_variable(tf_name)

                        importCommands[reg].write("\nterraform import oci_core_nat_gateway." + tf_name + " " + ngw_info.id)

                    #sgw_display_name = "n"
                    SGWs = oci.pagination.list_call_get_all_results(vnc.list_service_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                    vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                    for sgw in SGWs.data:
                        sgw_info = sgw
                        sgw_display_name = sgw_info.display_name
                        tf_name = vcn_info.display_name + "_" + sgw_display_name
                        tf_name = commonTools.check_tf_variable(tf_name)
                        importCommands[reg].write("\nterraform import oci_core_service_gateway." + tf_name + " " + sgw_info.id)

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
                            "\nterraform import oci_core_local_peering_gateway." + tf_name + " " + lpg_info.id)

                    if (lpg_display_names == ""):
                        lpg_display_names = "n"
                    elif (lpg_display_names[-1] == ','):
                        lpg_display_names = lpg_display_names[:-1]

                    # Fill VCNs Tab
                    #print_vcns(region, ntk_compartment_name, vcn_info, drg_display_name, igw_display_name, ngw_display_name,sgw_display_name, lpg_display_names)
                    print_vcns(values_for_column_vcns,region,ntk_compartment_name, vcn_info, drg_info,igw_info,ngw_info, sgw_info, lpg_display_names)

    commonTools.write_to_cd3(values_for_column_vcns, cd3file, "VCNs")
    print("VCNs exported to CD3\n")
    # Fetch NSGs
    rows = []
    print("\nFetching NSGs...")
    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for NSG #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        vnc = VirtualNetworkClient(config)
        region = reg.capitalize()
        comp_ocid_done = []
        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")

                for vcn in vcns.data:
                    vcn_info = vnc.get_vcn(vcn.id).data
                    comp_ocid_done_again = []
                    for ntk_compartment_name_again in ct.ntk_compartment_ids:
                        if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                            if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                                continue
                            comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
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
        vnc = VirtualNetworkClient(config)
        region = reg.capitalize()
        comp_ocid_done = []
        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                for vcn in vcns.data:
                    vcn_info = vnc.get_vcn(vcn.id).data
                    comp_ocid_done_again = []
                    for ntk_compartment_name_again in ct.ntk_compartment_ids:
                        if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                            if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                                continue
                            comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
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
        vnc = VirtualNetworkClient(config)
        region = reg.capitalize()
        comp_ocid_done = []
        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                for vcn in vcns.data:
                    vcn_info = vnc.get_vcn(vcn.id).data
                    comp_ocid_done_again = []
                    for ntk_compartment_name_again in ct.ntk_compartment_ids:
                        if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                            if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                                continue
                            comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
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
    os.chdir('../CoreInfra/Networking/BaseNetwork')
    if (input_compartment_list is None):
        if (input_config_file is None):
            command_sl = 'python exportSeclist.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir
            command_rt = 'python exportRoutetable.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir
        else:
            command_sl = 'python exportSeclist.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file
            command_rt = 'python exportRoutetable.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file
    else:
        if (input_config_file is None):
            command_sl = 'python exportSeclist.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir + " --networkCompartment " + input_compartment_list
            command_rt = 'python exportRoutetable.py ' + cd3file + " --tf_import_cmd true --outdir " + outdir + " --networkCompartment " + input_compartment_list
        else:
            command_sl = 'python exportSeclist.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file + " --networkCompartment " + input_compartment_list
            command_rt = 'python exportRoutetable.py ' + cd3file + ' --tf_import_cmd true --outdir ' + outdir + ' --configFileName ' + input_config_file + " --networkCompartment " + input_compartment_list

    os.system(command_sl)
    print("SecRules exported to CD3\n")

    os.system(command_rt)
    print("RouteRules exported to CD3\n")

    os.chdir("../../..")

    for reg in ct.all_regions:
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "a")
        importCommands[reg].write("\n\nterraform plan")
        importCommands[reg].write("\n")
        importCommands[reg].close()
        if ("linux" in sys.platform):
            dir = os.getcwd()
            os.chdir(outdir + "/" + reg)
            os.system("chmod +x tf_import_commands_network_nonGF.sh")
            os.chdir(dir)


if __name__=="__main__":
    main()

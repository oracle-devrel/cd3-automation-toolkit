#!/usr/bin/python3


import argparse
import sys
import oci
from oci.config import DEFAULT_LOCATION
from oci.core.virtual_network_client import VirtualNetworkClient
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)
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
            try:
                nsgname = vnc.get_network_security_group(nsgsl.destination).data
                nsgdestination = nsgname.display_name
            except Exception as e:
                print("invalid rule for NSG - "+str(nsg.display_name))
                nsgdestination = "Invalid"
                return


    else:
        nsgdestination=""
    if (nsgsl.source is not None):
        if ("networksecuritygroup" in nsgsl.source):
            nsgsourcetype = "nsg"
            try:
                nsgname = vnc.get_network_security_group(nsgsl.source).data
                nsgsource = nsgname.display_name
            except Exception as e:
                print("invalid rule for NSG - "+str(nsg.display_name))
                nsgsource = "Invalid"
                return

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
        elif(col_header == "Source Type"):
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

    nsg_rule_tf_name = tf_name + "_security_rule" + str(i)
    if tf_import_cmd:
        importCommands[region.lower()].write("\nterraform import \"module.nsg-rules[\\\""+nsg_rule_tf_name+"\\\"].oci_core_network_security_group_security_rule.nsg_rule\" " + "networkSecurityGroups/" + str(nsg.id) + "/securityRules/" + str(nsgsl.id))

    # importCommands[region.lower()].write("\nterraform import oci_core_network_security_group_security_rule." + tf_name + "_security_rule" + str(i) + " " + "networkSecurityGroups/" + str(nsg.id) + "/securityRules/" + str(nsgsl.id))


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
    if tf_import_cmd:
        importCommands[region.lower()].write("\nterraform import \"module.nsgs[\\\"" + tf_name +  "\\\"].oci_core_network_security_group.network_security_group\" " + str(nsg.id))

def parse_args():
    parser = argparse.ArgumentParser(description='Export Security list on OCI to CD3')
    parser.add_argument('inputfile', help='path of CD3 excel file to export rules to')
    parser.add_argument('--network-compartments', nargs='*', help='comma seperated Compartments for which to export Networking Objects')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    parser.add_argument('--tf-import-cmd', default=False, action='store_action', help='write tf import commands')
    parser.add_argument('--outdir', default=None, required=False, help='outdir for TF import commands script')
    return parser.parse_args()


def export_nsg(inputfile, network_compartments, _config, _tf_import_cmd, outdir):
    global tf_import_cmd
    global values_for_column_nsgs
    global sheet_dict_nsgs
    global importCommands
    global config

    cd3file = inputfile

    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    tf_import_cmd = _tf_import_cmd
    if tf_import_cmd and not outdir:
        exit_menu('out directory is a mandatory argument to write tf import commands')

    # Read CD3
    df, values_for_column_nsgs = commonTools.read_cd3(cd3file,"NSGs")

    ct = commonTools()
    ct.get_subscribedregions(_config)
    config = oci.config.from_file(_config)
    ct.get_network_compartment_ids(config['tenancy'],"root", _config)

    print("\nFetching NSGs...")

    # Check Compartments
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments, ct.ntk_compartment_ids)

    # Get dict for columns from Excel_Columns
    sheet_dict_nsgs=ct.sheet_dict["NSGs"]

    if tf_import_cmd:
        importCommands={}
        for reg in ct.all_regions:
            if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_network_nsg_nonGF.sh")):
                commonTools.backup_file(outdir + "/" + reg, "tf_import_network",
                                        "tf_import_commands_network_nsg_nonGF.sh")
            importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nsg_nonGF.sh", "w")
            importCommands[reg].write("#!/bin/bash")
            importCommands[reg].write("\n\n######### Writing import for NSG #########\n\n")


    for reg in ct.all_regions:
        config.__setitem__("region", commonTools().region_dict[reg])
        vnc = VirtualNetworkClient(config)
        region = reg.capitalize()
        #comp_ocid_done = []
        for ntk_compartment_name in comp_list_fetch:
            vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                            compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                            lifecycle_state="AVAILABLE")

            for vcn in vcns.data:
                vcn_info = vnc.get_vcn(vcn.id).data
                for ntk_compartment_name_again in comp_list_fetch:
                    NSGs = oci.pagination.list_call_get_all_results(vnc.list_network_security_groups,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name_again], vcn_id=vcn.id,
                                                                    lifecycle_state="AVAILABLE")
                    nsglist = [""]
                    for nsg in NSGs.data:
                        NSGSLs = vnc.list_network_security_group_security_rules(nsg.id, sort_by="TIMECREATED")
                        i = 1
                        for nsgsl in NSGSLs.data:
                            nsglist.append(nsg.id)
                            print_nsgsl(values_for_column_nsgs, vnc, region, ntk_compartment_name_again,
                                        vcn_info.display_name, nsg, nsgsl, i)
                            i = i + 1
                        if (nsg.id not in nsglist):
                            print_nsg(values_for_column_nsgs, region, ntk_compartment_name_again, vcn_info.display_name,
                                      nsg)
                        else:
                            tf_name = commonTools.check_tf_variable(str(nsg.display_name))

                            if tf_import_cmd:
                                importCommands[region.lower()].write("\nterraform import \"module.nsgs[\\\"" + tf_name + "\\\"].oci_core_network_security_group.network_security_group\" " + str(
                                    nsg.id))

    commonTools.write_to_cd3(values_for_column_nsgs, cd3file, "NSGs")
    print("NSGs exported to CD3\n")

    if tf_import_cmd:
        for reg in ct.all_regions:
            importCommands[reg].write('\n\nterraform plan\n')
            importCommands[reg].close()


if __name__=="__main__":
    args = parse_args()
    export_nsg(args.inputfile, args.network_compartments, args.config, args.tf_import_cmd, args.outdir)

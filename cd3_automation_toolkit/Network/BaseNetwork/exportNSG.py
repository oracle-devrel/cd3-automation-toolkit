#!/usr/bin/python3

import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
import os
import subprocess as sp
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

def convertNullToNothing(input):
    EMPTY_STRING = ""
    if input is None:
        return EMPTY_STRING
    else:
        return str(input)
def print_nsgsl(values_for_column_nsgs,vnc,region, comp_name, vcn_name, nsg, nsgsl,i,state):
    tf_name = commonTools.check_tf_variable(str(vcn_name)+"_"+str(nsg.display_name))
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
    tf_resource = f'module.nsg-rules[\\"{nsg_rule_tf_name}\\"].oci_core_network_security_group_security_rule.nsg_rule'
    if tf_import_cmd and tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" networkSecurityGroups/{str(nsg.id)}/securityRules/{str(nsgsl.id)}'

    # importCommands[region.lower()].write("\nterraform import oci_core_network_security_group_security_rule." + tf_name + "_security_rule" + str(i) + " " + "networkSecurityGroups/" + str(nsg.id) + "/securityRules/" + str(nsgsl.id))


def print_nsg(values_for_column_nsgs,region, comp_name, vcn_name, nsg,state):
    tf_name = commonTools.check_tf_variable(str(vcn_name)+"_"+str(nsg.display_name))

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
    tf_resource = f'module.nsgs[\\"{tf_name}\\"].oci_core_network_security_group.network_security_group'
    if tf_import_cmd and tf_resource not in state["resources"]:
        importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(nsg.id)}'

# Execution of the code begins here
def export_nsg(inputfile, outdir, service_dir,config,signer, ct, export_compartments,export_regions,export_tags,_tf_import_cmd):
    global tf_import_cmd
    global values_for_column_nsgs
    global sheet_dict_nsgs
    global importCommands,tf_or_tofu
    cd3file = inputfile

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    tf_import_cmd = _tf_import_cmd
    if tf_import_cmd and not outdir:
        exit_menu('out directory is a mandatory argument to write tf import commands')

    # Read CD3
    df, values_for_column_nsgs = commonTools.read_cd3(cd3file,"NSGs")

    print("\nFetching NSGs...")

    # Get dict for columns from Excel_Columns
    sheet_dict_nsgs=ct.sheet_dict["NSGs"]

    if tf_import_cmd:
        importCommands={}
        for reg in export_regions:
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir + "/import_commands_network_nsg.sh")):
                commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, "import_network",
                                        "import_commands_network_nsg.sh")
            importCommands[reg] = ""


    for reg in export_regions:
        config.__setitem__("region", commonTools().region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"],stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        vnc = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        region = reg.capitalize()
        nsglist = [""]
        for ntk_compartment_name in export_compartments:
            vcns = oci.pagination.list_call_get_all_results(vnc.list_vcns,
                                                            compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                            lifecycle_state="AVAILABLE")

            for vcn in vcns.data:
                # Tags filter
                defined_tags = vcn.defined_tags
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

                vcn_info = vnc.get_vcn(vcn.id).data
                for ntk_compartment_name_again in export_compartments:
                    NSGs = oci.pagination.list_call_get_all_results(vnc.list_network_security_groups,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name_again], vcn_id=vcn.id,
                                                                    lifecycle_state="AVAILABLE")

                    for nsg in NSGs.data:
                        # Tags filter
                        defined_tags = nsg.defined_tags
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
                        NSGSLs = oci.pagination.list_call_get_all_results(vnc.list_network_security_group_security_rules, network_security_group_id= nsg.id, sort_by="TIMECREATED")
                        i = 1
                        for nsgsl in NSGSLs.data:
                            nsglist.append(nsg.id)
                            print_nsgsl(values_for_column_nsgs, vnc, region, ntk_compartment_name_again,
                                        vcn_info.display_name, nsg, nsgsl, i,state)
                            i = i + 1
                        if (nsg.id not in nsglist):
                            print_nsg(values_for_column_nsgs, region, ntk_compartment_name_again, vcn_info.display_name,
                                      nsg,state)
                        else:
                            tf_name = commonTools.check_tf_variable(str(vcn_info.display_name)+"_"+str(nsg.display_name))

                            tf_resource = f'module.nsgs[\\"{tf_name}\\"].oci_core_network_security_group.network_security_group'
                            if tf_import_cmd and tf_resource not in state["resources"]:
                                importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(nsg.id)}'


    commonTools.write_to_cd3(values_for_column_nsgs, cd3file, "NSGs")
    print("NSGs exported to CD3\n")

    if tf_import_cmd:
        for reg in export_regions:
            script_file = f'{outdir}/{reg}/{service_dir}/import_commands_network_nsg.sh'
            init_commands = f'\n#!/bin/bash\n{tf_or_tofu} init\n######### Writing import for NSGs #########\n'
            if importCommands[reg] != "":
                importCommands[reg] += f'\n{tf_or_tofu} plan\n'
                with open(script_file, 'a') as importCommandsfile:
                    importCommandsfile.write(init_commands + importCommands[reg])



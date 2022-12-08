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

def insert_values(values_for_column,oci_objs, region, comp_name, vcn_name, ruletype, protocol, sportmin, sportmax, dportmin, dportmax, icmptype, icmpcode):
    for col_header in values_for_column.keys():
        if (col_header == "Region"):
            values_for_column[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column[col_header].append(vcn_name)
        elif (col_header == "Rule Type"):
            values_for_column[col_header].append(ruletype)
        elif (col_header == "Protocol"):
            values_for_column[col_header].append(protocol)
        elif (col_header == "SPortMin"):
            values_for_column[col_header].append(sportmin)
        elif (col_header == "SPortMax"):
            values_for_column[col_header].append(sportmax)
        elif (col_header == "DPortMin"):
            values_for_column[col_header].append(dportmin)
        elif (col_header == "DPortMax"):
            values_for_column[col_header].append(dportmax)
        elif (col_header == "ICMPType"):
            values_for_column[col_header].append(icmptype)
        elif (col_header == "ICMPCode"):
            values_for_column[col_header].append(icmpcode)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(oci_objs[0], col_header, values_for_column)
        else:
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict,values_for_column)


def print_secrules(seclists,region,vcn_name,comp_name):
    for seclist in seclists.data:
        isec_rules = seclist.ingress_security_rules
        esec_rules = seclist.egress_security_rules
        display_name = seclist.display_name
        dn=display_name

        if tf_import_cmd:
            tf_name = vcn_name + "_" + dn
            tf_name=commonTools.check_tf_variable(tf_name)
            if("Default Security List for " in dn):
                importCommands[region.lower()].write("\nterraform import \"module.default-security-lists[\\\"" + tf_name + "\\\"].oci_core_default_security_list.default_security_list\" " + str(seclist.id))
            else:
                importCommands[region.lower()].write("\nterraform import \"module.security-lists[\\\"" + tf_name + "\\\"].oci_core_security_list.security_list\" " + str(seclist.id))


        if(len(isec_rules)==0 and len(esec_rules)==0):
            oci_objs=[seclist]
            insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, '', '', '', '', '', '', '', '')
            #new_row=(region,comp_name,vcn_name,dn,'','','','','','','','','','','','')
            #rows.append(new_row)

        for rule in esec_rules:
            oci_objs=[seclist,rule]
            desc = str(rule.description)
            if (desc == "None"):
                desc = ""

            if rule.protocol == "all":
                printstr = (dn + ",egress,all," + str(rule.is_stateless) + "," + rule.destination + ",,,,,,,,"+desc)
                insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'all', '', '','', '', '', '')
            elif rule.protocol == "1":
                if rule.icmp_options is None:
                    printstr = (dn + ",egress,icmp," + str(rule.is_stateless) + "," + rule.destination + ",,,,,,,."+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'icmp', '', '','', '', '', '')
                else:
                    code = convertNullToNothing(rule.icmp_options.code)
                    type = convertNullToNothing(rule.icmp_options.type)
                    printstr = (dn + ",egress,icmp," + str(rule.is_stateless) + "," + rule.destination + ",,,,,"+type+","+code+","+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name,'egress', 'icmp','', '', '','', type, code)
            elif rule.protocol == "6":
                if rule.tcp_options is None:
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination+",,,,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'tcp','', '', '','', '', '')
                elif rule.tcp_options.source_port_range is not None and rule.tcp_options.destination_port_range is None:
                    min = convertNullToNothing(rule.tcp_options.source_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.source_port_range.max)
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'tcp',min, max,'', '', '', '')
                elif rule.tcp_options.destination_port_range is not None and rule.tcp_options.source_port_range is None:
                    min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'tcp','', '', min, max, '', '')
                elif rule.tcp_options.destination_port_range is not None and rule.tcp_options.source_port_range is not None:
                    smin = convertNullToNothing(rule.tcp_options.source_port_range.min)
                    smax = convertNullToNothing(rule.tcp_options.source_port_range.max)
                    dmin = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    dmax = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    printstr = (dn + ",egress,tcp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + smin + "," + smax + "," + dmin + "," + dmax + ",,," + desc)
                    insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, 'egress', 'tcp', smin, smax,dmin, dmax, '', '')

            elif rule.protocol == "17":
                if rule.udp_options is None:
                    printstr = (dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination+",,,,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'udp', '', '', '', '', '', '')
                elif rule.udp_options.source_port_range is not None and rule.udp_options.destination_port_range is None :
                    min = convertNullToNothing(rule.udp_options.source_port_range.min)
                    max = convertNullToNothing(rule.udp_options.source_port_range.max)
                    printstr = (dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'udp', min, max,'', '', '', '')
                elif rule.udp_options.destination_port_range is not None and rule.udp_options.source_port_range is None:
                    min = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    printstr=(dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + min + "," + max + ",,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', 'udp', '', '', min, max, '', '')
                elif rule.udp_options.destination_port_range is not None and rule.udp_options.source_port_range is not None:
                    smin = convertNullToNothing(rule.udp_options.source_port_range.min)
                    smax = convertNullToNothing(rule.udp_options.source_port_range.max)
                    dmin = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    dmax = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    printstr = (dn + ",egress,udp," + str(rule.is_stateless) + ",,,," + rule.destination + ",," + smin + "," + smax + "," + dmin + "," + dmax + ",,," + desc)
                    insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, 'egress', 'udp', smin, smax,dmin, dmax, '', '')

            #Any Other protocol
            else:
                protocol=commonTools().protocol_dict[rule.protocol].lower()
                insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'egress', protocol, '', '','', '', '', '')

            if not tf_import_cmd:
                print(printstr)
        for rule in isec_rules:
            oci_objs=[seclist,rule]
            desc = str(rule.description)
            if (desc == "None"):
                desc = ""
            if rule.protocol == "6":
                if rule.tcp_options is None:
                    printstr= (dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', 'tcp', '', '', '', '', '', '')
                elif rule.tcp_options.destination_port_range is not None and rule.tcp_options.source_port_range is None:
                    min = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    printstr= (dn + ",ingress,tcp," + str(rule.is_stateless) + "," + rule.source + ",,,," + min + "," + max+",,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name,'ingress', 'tcp','', '',min, max, '', '')
                elif rule.tcp_options.source_port_range is not None and rule.tcp_options.destination_port_range is None:
                    min = convertNullToNothing(rule.tcp_options.source_port_range.min)
                    max = convertNullToNothing(rule.tcp_options.source_port_range.max)
                    printstr = (dn + ",ingress,tcp," + str(rule.is_stateless) + ",,,," + rule.source + ",," + min + "," + max + ",,," + desc)
                    insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, 'ingress', 'tcp', min, max,'', '', '', '')
                elif rule.tcp_options.destination_port_range is not None and rule.tcp_options.source_port_range is not None:
                    smin = convertNullToNothing(rule.tcp_options.source_port_range.min)
                    smax = convertNullToNothing(rule.tcp_options.source_port_range.max)
                    dmin = convertNullToNothing(rule.tcp_options.destination_port_range.min)
                    dmax = convertNullToNothing(rule.tcp_options.destination_port_range.max)
                    printstr = (dn + ",ingress,tcp," + str(rule.is_stateless) + ",,,," + rule.source + ",," + smin + "," + smax + "," + dmin + "," + dmax + ",,," + desc)
                    insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, 'ingress', 'tcp', smin, smax,dmin, dmax, '', '')


            elif rule.protocol == "1":
                if rule.icmp_options is None:
                    printstr= (dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', 'icmp','', '', '','', '', '')
                else:
                    code = convertNullToNothing(rule.icmp_options.code)
                    type = convertNullToNothing(rule.icmp_options.type)
                    printstr= (dn + ",ingress,icmp," + str(rule.is_stateless) + "," + rule.source + ",,,,,," + type + "," + code+","+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', 'icmp', '', '','', '', type, code)

            elif rule.protocol == "17":
                if rule.udp_options is None:
                    printstr= (dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', 'udp', '', '', '','', '', '')
                elif rule.udp_options.destination_port_range is not None and rule.udp_options.source_port_range is None:
                    min = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    max = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    printstr= (dn + ",ingress,udp," + str(rule.is_stateless) + "," + rule.source + ",,,," + min + "," + max+",,,"+desc)
                    insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', 'udp', '', '',min, max, '', '')
                elif rule.udp_options.source_port_range is not None and rule.udp_options.destination_port_range is None:
                    min = convertNullToNothing(rule.udp_options.source_port_range.min)
                    max = convertNullToNothing(rule.udp_options.source_port_range.max)
                    printstr = (dn + ",ingress,udp," + str(rule.is_stateless) + ",,,," + rule.source + ",," + min + "," + max + ",,," + desc)
                    insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, 'ingress', 'udp', min, max,'', '', '', '')
                elif rule.udp_options.destination_port_range is not None and rule.udp_options.source_port_range is not None:
                    smin = convertNullToNothing(rule.udp_options.source_port_range.min)
                    smax = convertNullToNothing(rule.udp_options.source_port_range.max)
                    dmin = convertNullToNothing(rule.udp_options.destination_port_range.min)
                    dmax = convertNullToNothing(rule.udp_options.destination_port_range.max)
                    printstr = (dn + ",ingress,udp," + str(rule.is_stateless) + ",,,," + rule.source + ",," + smin + "," + smax + "," + dmin + "," + dmax + ",,," + desc)
                    insert_values(values_for_column, oci_objs, region, comp_name, vcn_name, 'ingress', 'udp', smin, smax,dmin, dmax, '', '')

            elif rule.protocol == "all":
                printstr= (dn + ",ingress,all," + str(rule.is_stateless) + "," + rule.source + ",,,,,,,,"+desc)
                insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', 'all','', '', '', '','', '')
            #Any Other protocol
            else:
                protocol=commonTools().protocol_dict[rule.protocol].lower()
                insert_values(values_for_column,oci_objs,region, comp_name, vcn_name, 'ingress', protocol, '', '', '','', '', '')

            if not tf_import_cmd:
                print(printstr)


def parse_args():
    parser = argparse.ArgumentParser(description='Export Security list on OCI to CD3')
    parser.add_argument('inputfile', help='path of CD3 excel file to export rules to')
    parser.add_argument('--network-compartments', nargs='*', help='comma seperated Compartments for which to export Networking Objects')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    parser.add_argument('--tf-import-cmd', default=False, action='store_action', help='write tf import commands')
    parser.add_argument('--outdir', default=None, required=False, help='outdir for TF import commands script')
    return parser.parse_args()


def export_seclist(inputfile, network_compartments, _config, _tf_import_cmd, outdir):
    global tf_import_cmd
    global values_for_column
    global sheet_dict
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
    df, values_for_column = commonTools.read_cd3(cd3file,"SecRulesinOCI")

    ct = commonTools()
    ct.get_subscribedregions(_config)
    config = oci.config.from_file(_config)
    ct.get_network_compartment_ids(config['tenancy'],"root", _config)

    '''
    input_compartment_list = network_compartments
    if(input_compartment_list is not None):
        #input_compartment_names = input_compartment_list.split(",")
        input_compartment_names = [x.strip() for x in input_compartment_list]
    else:
        input_compartment_names = None
    '''
    print("\nFetching Security Rules...")

    # Check Compartments
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments, ct.ntk_compartment_ids)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict["SecRulesinOCI"]

    if tf_import_cmd:
        importCommands={}
        for reg in ct.all_regions:
            if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_network_secrules_nonGF.sh")):
                commonTools.backup_file(outdir + "/" + reg, "tf_import_network",
                                        "tf_import_commands_network_major-objects_nonGF.sh")
            importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_secrules_nonGF.sh", "w")
            importCommands[reg].write("#!/bin/bash")
            importCommands[reg].write("\n\n######### Writing import for Security Lists #########\n\n")


    for reg in ct.all_regions:
        config.__setitem__("region", commonTools().region_dict[reg])
        vcn = VirtualNetworkClient(config)
        region = reg.capitalize()
        #comp_ocid_done = []
        for ntk_compartment_name in comp_list_fetch:
        #    if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
        #        if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
        #            continue
        #        comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                for v in vcns.data:
                    vcn_id = v.id
                    vcn_name=v.display_name
        #            comp_ocid_done_again = []
                    for ntk_compartment_name_again in comp_list_fetch:
        #                if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
        #                    if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
        #                        continue
        #                    comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
                            seclists = oci.pagination.list_call_get_all_results(vcn.list_security_lists,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE',sort_by='DISPLAYNAME')
                            print_secrules(seclists,region,vcn_name,ntk_compartment_name_again)

    commonTools.write_to_cd3(values_for_column,cd3file,"SecRulesinOCI")
    print("SecRules exported to CD3\n")
    if tf_import_cmd:
        for reg in ct.all_regions:
            importCommands[reg].close()

if __name__=="__main__":
    args = parse_args()
    export_seclist(args.inputfile, args.network_compartments, args.config, args.tf_import_cmd, args.outdir)

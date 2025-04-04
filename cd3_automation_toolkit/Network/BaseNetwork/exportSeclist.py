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


def print_secrules(seclists,region,vcn_name,comp_name,export_tags,state):
    for seclist in seclists.data:
        # Tags filter
        defined_tags = seclist.defined_tags
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

        isec_rules = seclist.ingress_security_rules
        esec_rules = seclist.egress_security_rules
        display_name = seclist.display_name
        dn=display_name

        if tf_import_cmd:
            tf_name = vcn_name + "_" + dn
            tf_name = commonTools.check_tf_variable(tf_name)
            if("Default Security List for " in dn):
                tf_resource = f'module.security-lists[\\"{tf_name}\\"].oci_core_default_security_list.default_security_list[0]'
            else:
                tf_resource = f'module.security-lists[\\"{tf_name}\\"].oci_core_security_list.security_list[0]'
            if tf_resource not in state["resources"]:
                importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(seclist.id)}'


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

# Execution of the code begins here
def export_seclist(inputfile, outdir, service_dir,config,signer, ct, export_compartments,export_regions,export_tags,_tf_import_cmd):
    global tf_import_cmd
    global values_for_column
    global sheet_dict
    global importCommands,tf_or_tofu

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

    cd3file = inputfile

    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    tf_import_cmd = _tf_import_cmd
    if tf_import_cmd and not outdir:
        exit_menu('out directory is a mandatory argument to write tf import commands')

    # Read CD3
    df, values_for_column = commonTools.read_cd3(cd3file,"SecRulesinOCI")

    print("\nFetching Security Rules...")

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict["SecRulesinOCI"]

    if tf_import_cmd:
        importCommands={}
        for reg in export_regions:
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir+ "/import_commands_network_secrules.sh")):
                commonTools.backup_file(outdir + "/" + reg+ "/" + service_dir, "import_network",
                                        "import_commands_network_secrules.sh")
            importCommands[reg] = ''

    else:
        vcns_check = parseVCNs(cd3file)

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
        vcn = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        region = reg.capitalize()
        #comp_ocid_done = []
        for ntk_compartment_name in export_compartments:
                vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                for v in vcns.data:
                    # Tags filter
                    defined_tags = v.defined_tags
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

                    vcn_id = v.id
                    vcn_name=v.display_name
                    if not tf_import_cmd:
                        # Process only those VCNs which are present in cd3(and have been created via TF)
                        check = vcn_name, reg
                        #rtname = str(df.loc[i, 'Route Table Name']).strip()
                        if (check not in vcns_check.vcn_names):
                            print(f'skipping sec list as its vcn {vcn_name} is not in VCNs tab')
                            continue
                    for ntk_compartment_name_again in export_compartments:
                            seclists = oci.pagination.list_call_get_all_results(vcn.list_security_lists,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE',sort_by='DISPLAYNAME')
                            print_secrules(seclists,region,vcn_name,ntk_compartment_name_again,export_tags,state)

    commonTools.write_to_cd3(values_for_column,cd3file,"SecRulesinOCI")
    print("SecRules exported to CD3\n")
    if tf_import_cmd:
        for reg in export_regions:
            script_file = f'{outdir}/{reg}/{service_dir}/import_commands_network_secrules.sh'
            init_commands = f'\n#!/bin/bash\n{tf_or_tofu} init\n######### Writing import for Security Lists #########\n'
            if importCommands[reg] != "":
                importCommands[reg] += f'\n{tf_or_tofu} plan\n'
                with open(script_file, 'a') as importCommandsfile:
                    importCommandsfile.write(init_commands + importCommands[reg])


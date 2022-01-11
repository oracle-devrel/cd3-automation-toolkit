#!/usr/bin/python3

import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *


def get_network_entity_name(config,network_identity_id):
    vcn1 = VirtualNetworkClient(config)
    if('internetgateway' in network_identity_id):
        igw=vcn1.get_internet_gateway(network_identity_id)
        network_identity_name = "igw:"+igw.data.display_name
        return  network_identity_name

    elif ('servicegateway' in network_identity_id):
        sgw = vcn1.get_service_gateway(network_identity_id)
        network_identity_name = "sgw:"+sgw.data.display_name
        return network_identity_name


    elif ('natgateway' in network_identity_id):
        ngw = vcn1.get_nat_gateway(network_identity_id)
        network_identity_name = "ngw:"+ngw.data.display_name
        return network_identity_name

    elif ('localpeeringgateway' in network_identity_id):
        lpg = vcn1.get_local_peering_gateway(network_identity_id)
        network_identity_name = "lpg:"+lpg.data.display_name
        return network_identity_name
    elif ('drgattachment' in network_identity_id):
        drg_attach = vcn1.get_drg_attachment(network_identity_id)

        if (drg_attach.data.network_details is not None):
            drg_attach_type = drg_attach.data.network_details.type
        #DRG v1
        else:
            drg_attach_type= "VCN"

        if (drg_attach_type == "VCN"):
            network_identity_name = drg_attach.data.display_name
        else:
            network_identity_name = network_identity_id
        return network_identity_name
    elif ('drg' in network_identity_id):
        drg = vcn1.get_drg(network_identity_id)
        network_identity_name = "drg:"+drg.data.display_name
        return network_identity_name

        """
    elif ('privateip' in network_identity_id):
        privateip = vcn1.get_private_ip(network_identity_id)
        network_identity_name = "privateip:"+privateip.data.ip_address
        return network_identity_name
        """
    else:
        return network_identity_id

def insert_values(routetable,values_for_column,region,comp_name,name,routerule):
    for col_header in values_for_column.keys():
        if (col_header == "Region"):
            values_for_column[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column[col_header].append(name)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(routetable, col_header, values_for_column)

        elif (routerule != None and col_header == 'Route Destination Object'):
            network_entity_id = routerule.network_entity_id
            network_entity_name = get_network_entity_name(config, network_entity_id)
            values_for_column[col_header].append(network_entity_name)
            if ('internetgateway' in network_entity_id):
                if (routerule.destination not in values_for_vcninfo['igw_destinations']):
                    values_for_vcninfo['igw_destinations'].append(routerule.destination)
            elif ('natgateway' in network_entity_id):
                if (routerule.destination not in values_for_vcninfo['ngw_destinations']):
                    values_for_vcninfo['ngw_destinations'].append(routerule.destination)
            elif('drg' in network_entity_id):
                if(routerule.destination not in values_for_vcninfo['onprem_destinations']):
                    values_for_vcninfo['onprem_destinations'].append(routerule.destination)
        else:
            oci_objs = [routetable,routerule]
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict,values_for_column)


def insert_values_drg(routetable,import_drg_route_distribution_name,values_for_column_drg,region,comp_name,name,routerule):
    for col_header in values_for_column_drg.keys():
        if (col_header == "Region"):
            values_for_column_drg[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column_drg[col_header].append(comp_name)
        elif (col_header == "DRG Name"):
            values_for_column_drg[col_header].append(name)
        elif (col_header == "Import DRG Route Distribution Name"):
            values_for_column_drg[col_header].append(import_drg_route_distribution_name)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column_drg = commonTools.export_tags(routetable, col_header, values_for_column_drg)

        elif (routerule != None and col_header == 'Next Hop Attachment'):
            next_hop_attachment_id=routerule.next_hop_drg_attachment_id
            network_entity_name = get_network_entity_name(config, next_hop_attachment_id)
            values_for_column_drg[col_header].append(network_entity_name)

        else:
            oci_objs = [routetable,routerule]
            values_for_column_drg = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_drg,values_for_column_drg)



def print_drg_routerules(drg_rt_info,drg_display_name,drg_route_table_name,import_drg_route_distribution_name,drg_rules,region,comp_name):
    drg_rt_name = drg_display_name + "_" + drg_route_table_name
    drg_rt_tf_name = commonTools.check_tf_variable(drg_rt_name)

    if (not drg_rules.data):
        insert_values_drg(drg_rt_info, import_drg_route_distribution_name,values_for_column_drg, region, comp_name, drg_display_name, None)
        if not tf_import_cmd_drg:
            print(drg_route_table_name)
    i=1
    for rule in drg_rules.data:
        insert_values_drg(drg_rt_info, import_drg_route_distribution_name,values_for_column_drg, region, comp_name, drg_display_name, rule)
        if not tf_import_cmd_drg:
            print(drg_route_table_name)
        else:
            if rule.route_type.lower()=='static':
                importCommands_drg[region.lower()].write("\nterraform import oci_core_drg_route_table_route_rule." + drg_rt_tf_name+ "_route_rule" + str(i) + " drgRouteTables/"+str(drg_rt_info.id)+"/routeRules/"+str(rule.id))
        i=i+1

def print_routetables(routetables,region,vcn_name,comp_name):
    for routetable in routetables.data:
        rules = routetable.route_rules
        display_name = routetable.display_name
        dn=display_name
        if tf_import_cmd:
            tf_name = vcn_name + "_" + dn
            tf_name = commonTools.check_tf_variable(tf_name)

            if ("Default Route Table for " in dn):
                importCommands[region.lower()].write("\nterraform import oci_core_default_route_table." + tf_name + " " + str(routetable.id))
            else:
                importCommands[region.lower()].write("\nterraform import oci_core_route_table." + tf_name + " " + str(routetable.id))

        if(not rules):
            insert_values(routetable, values_for_column, region, comp_name, vcn_name,None)
            if not tf_import_cmd:
                print(dn)

        for rule in rules:
            insert_values(routetable, values_for_column, region, comp_name, vcn_name,rule)
            desc = str(rule.description)
            if (desc == "None"):
                desc = ""
            if not tf_import_cmd:
                print(dn + "," +str(rule.destination)+","+desc)



def parse_args():
    parser = argparse.ArgumentParser(description='Export Route Table on OCI to CD3')
    parser.add_argument('cd3file', help='path of CD3 excel file to export rules to')
    parser.add_argument('--network-compartment', nargs='*', help='comma seperated Compartments for which to export Networking Objects')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    parser.add_argument('--tf-import-cmd', default=False, action='store_true', help='write tf import commands')
    parser.add_argument('--outdir', default=None, required=False, help='outdir for TF import commands script')
    args = parser.parse_args()

def export_drg_routetable(inputfile, network_compartments, _config, _tf_import_cmd, outdir):
    # Read the arguments
    global tf_import_cmd_drg
    global values_for_column_drg
    global sheet_dict_drg
    global importCommands_drg
    global config

    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    tf_import_cmd_drg = _tf_import_cmd
    if tf_import_cmd_drg and not outdir:
        print("out directory is a mandatory arguement to write tf import commands ")
        exit(1)

    # Read CD3
    df, values_for_column_drg = commonTools.read_cd3(cd3file, "DRGRouteRulesinOCI")

    ct = commonTools()
    ct.get_subscribedregions(_config)
    config = oci.config.from_file(_config)
    ct.get_network_compartment_ids(config['tenancy'], "root", _config)

    # Get dict for columns from Excel_Columns
    sheet_dict_drg = ct.sheet_dict["DRGRouteRulesinOCI"]

    '''
    input_compartment_list = network_compartments
    if (input_compartment_list is not None):
        input_compartment_names = [x.strip() for x in input_compartment_list]
    else:
        input_compartment_names = None
    '''

    # Check Compartments
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments,ct.ntk_compartment_ids)

    if tf_import_cmd_drg:
        importCommands_drg = {}
        for reg in ct.all_regions:
            importCommands_drg[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "a")
            importCommands_drg[reg].write("\n\n######### Writing import for DRG Route Tables #########\n\n")

    print("\nFetching DRG Route Rules...")

    for reg in ct.all_regions:
        config.__setitem__("region", commonTools().region_dict[reg])
        vcn = VirtualNetworkClient(config)
        region = reg.capitalize()
        #comp_ocid_done = []

        for ntk_compartment_name in comp_list_fetch:
            #if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
            #    if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
            #        continue
            #    comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                drgs = oci.pagination.list_call_get_all_results(vcn.list_drgs,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
                for drg in drgs.data:
                    #DRG v1
                    if drg.default_drg_route_tables is None:
                        continue

                    # Get DRG RT Tables for the DRG - They are in same compartment s DRG by default
                    DRG_RTs = oci.pagination.list_call_get_all_results(vcn.list_drg_route_tables, drg_id=drg.id)
                    for drg_route_table_info in DRG_RTs.data:
                        drg_info = drg
                        drg_route_table_id = drg_route_table_info.id
                        drg_route_table_name = drg_route_table_info.display_name
                        drg_display_name = drg_info.display_name
                        import_drg_route_distribution_name = ''
                        import_drg_route_distribution_id = drg_route_table_info.import_drg_route_distribution_id
                        if (import_drg_route_distribution_id != None):
                            import_drg_route_distribution_info = vcn.get_drg_route_distribution(import_drg_route_distribution_id).data
                            import_drg_route_distribution_name=import_drg_route_distribution_info.display_name

                        drg_rt_name = drg_display_name + "_" + drg_route_table_name
                        drg_rt_tf_name = commonTools.check_tf_variable(drg_rt_name)
                        if tf_import_cmd_drg:
                            if drg_route_table_name not in commonTools.drg_auto_RTs:
                                importCommands_drg[reg].write("\nterraform import oci_core_drg_route_table." + drg_rt_tf_name + " " + drg_route_table_id)



                        #drg_rt_rules = vcn.list_drg_route_rules(drg_route_table_id)
                        drg_rt_rules = oci.pagination.list_call_get_all_results(vcn.list_drg_route_rules, drg_route_table_id)
                        print_drg_routerules(drg_route_table_info, drg_display_name,drg_route_table_name, import_drg_route_distribution_name,
                                             drg_rt_rules, region, ntk_compartment_name)

    commonTools.write_to_cd3(values_for_column_drg, cd3file, "DRGRouteRulesinOCI")
    if tf_import_cmd_drg:
        for reg in ct.all_regions:
            importCommands_drg[reg].close()


def export_routetable(inputfile, network_compartments, _config, _tf_import_cmd, outdir):
    # Read the arguments
    global tf_import_cmd
    global values_for_column
    global sheet_dict
    global importCommands
    global config
    global values_for_vcninfo

    cd3file = inputfile
    if '.xls' not in cd3file:
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    tf_import_cmd = _tf_import_cmd
    if tf_import_cmd and not outdir:
        print("out directory is a mandatory arguement to write tf import commands ")
        exit(1)

    values_for_vcninfo={}
    values_for_vcninfo['igw_destinations']=[]
    values_for_vcninfo['ngw_destinations']=[]
    values_for_vcninfo['onprem_destinations']=[]

    # Read CD3
    df,values_for_column=commonTools.read_cd3(cd3file,"RouteRulesinOCI")

    ct = commonTools()
    ct.get_subscribedregions(_config)
    config = oci.config.from_file(_config)
    ct.get_network_compartment_ids(config['tenancy'], "root", _config)


    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict["RouteRulesinOCI"]

    '''
    input_compartment_list = network_compartments
    if(input_compartment_list is not None):
        input_compartment_names = [x.strip() for x in input_compartment_list]
    else:
        input_compartment_names = None
    '''

    # Check Compartments
    comp_list_fetch = commonTools.get_comp_list_for_export(network_compartments, ct.ntk_compartment_ids)

    if tf_import_cmd:
        importCommands={}
        for reg in ct.all_regions:
            importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh", "a")
            importCommands[reg].write("\n\n######### Writing import for Route Tables #########\n\n")

    print("\nFetching Route Rules...")

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
                    #comp_ocid_done_again = []

                    for ntk_compartment_name_again in comp_list_fetch:
                    #    if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                    #        if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                    #            continue
                    #        comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
                            routetables = oci.pagination.list_call_get_all_results(vcn.list_route_tables, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE')
                            print_routetables(routetables,region,vcn_name,ntk_compartment_name_again)
    commonTools.write_to_cd3(values_for_column,cd3file,"RouteRulesinOCI")

    if tf_import_cmd:
        commonTools.write_to_cd3(values_for_vcninfo, cd3file, "VCN Info")
        for reg in ct.all_regions:
            importCommands[reg].close()

if __name__=="__main__":
    args = parse_args()
    export_routetable(args.inputfile, args.network_compartments, args.config, args.tf_import_cmd, args.outdir)
    export_drg_routetable(args.inputfile, args.network_compartments, args.config, args.tf_import_cmd, args.outdir)


#!/usr/bin/python3

import argparse
import sys
import oci
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

def insert_values(routetable,values_for_column,region,comp_name,vcn_name,routerule):
    for col_header in values_for_column.keys():
        if (col_header == "Region"):
            values_for_column[col_header].append(region)
        elif (col_header == "Compartment Name"):
            values_for_column[col_header].append(comp_name)
        elif (col_header == "VCN Name"):
            values_for_column[col_header].append(vcn_name)
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
        """elif (col_header in sheet_dict.keys()):
            #Check if property exists for routeTable
            try:
                value=oci_obj.__getattribute__(sheet_dict[col_header])
                value = commonTools.check_exported_value(value)
                values_for_column[col_header].append(value)
            except AttributeError as e:
                # Check if property exists for routeRule when Route Table has some rules
                if (obj != None):
                    try:
                        value = obj.__getattribute__(sheet_dict[col_header])
                        value = commonTools.check_exported_value(value)
                        values_for_column[col_header].append(value)
                    except AttributeError as e:
                        value = ""
                        values_for_column[col_header].append(value)
                # empty route table - put null values for all other cols
                else:
                    value = ""
                    values_for_column[col_header].append(value)

        #For Cols not defined in Excel_Columns sheet
        else:
            # Check if property exists for routeTable
            try:
                value = oci_obj.__getattribute__(commonTools.check_column_headers(col_header))
                value = commonTools.check_exported_value(value)
                values_for_column[col_header].append(value)
            except AttributeError as e:
                # Check if property exists for routeRule when Route Table has some rules
                if (obj != None):
                    try:
                        value = obj.__getattribute__(commonTools.check_column_headers(col_header))
                        value = commonTools.check_exported_value(value)
                        values_for_column[col_header].append(value)
                    except AttributeError as e:
                        value = ""
                        values_for_column[col_header].append(value)
                # empty route table - put null values for all other cols
                else:
                    value = ""
                    values_for_column[col_header].append(value)
        """
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
    parser.add_argument('--tf-import-cmd', action='store_true', help='write tf import commands')
    parser.add_argument('--outdir', required=False, help='outdir for TF import commands script')
    args = parser.parse_args()



def export_routetable(inputfile, network_compartments, _config, _tf_import_cmd=False, outdir=None):
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

    input_compartment_list = network_compartments
    if(input_compartment_list is not None):
        #input_compartment_names = input_compartment_list.split(",")
        input_compartment_names = [x.strip() for x in input_compartment_list]
    else:
        input_compartment_names = None

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
        comp_ocid_done = []
        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                for v in vcns.data:
                    vcn_id = v.id
                    vcn_name=v.display_name
                    comp_ocid_done_again = []
                    for ntk_compartment_name_again in ct.ntk_compartment_ids:
                        if ct.ntk_compartment_ids[ntk_compartment_name_again] not in comp_ocid_done_again:
                            if (input_compartment_names is not None and ntk_compartment_name_again not in input_compartment_names):
                                continue
                            comp_ocid_done_again.append(ct.ntk_compartment_ids[ntk_compartment_name_again])
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

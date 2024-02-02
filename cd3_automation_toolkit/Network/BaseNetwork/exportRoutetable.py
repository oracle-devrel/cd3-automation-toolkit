#!/usr/bin/python3

import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *


def get_network_entity_name(config,signer,network_identity_id):
    vcn1 = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
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
            network_entity_name = get_network_entity_name(config, signer, network_entity_id)
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
            network_entity_name = get_network_entity_name(config, signer, next_hop_attachment_id)
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
                importCommands_drg[region.lower()].write("\nterraform import \"module.drg-route-rules[\\\"" + drg_rt_tf_name+ "_route_rule" + str(i) + "\\\"].oci_core_drg_route_table_route_rule.drg_route_rule\" drgRouteTables/"+str(drg_rt_info.id)+"/routeRules/"+str(rule.id))
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
                importCommands[region.lower()].write("\nterraform import \"module.default-route-tables[\\\"" + tf_name + "\\\"].oci_core_default_route_table.default_route_table\" " + str(routetable.id))
            else:
                importCommands[region.lower()].write("\nterraform import \"module.route-tables[\\\"" + tf_name + "\\\"].oci_core_route_table.route_table\" " + str(routetable.id))

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

# Execution of the code begins here for drg route table
def export_drg_routetable(inputfile, outdir, service_dir,config1,signer1, ct, export_compartments,export_regions,_tf_import_cmd):
    # Read the arguments
    global tf_import_cmd_drg
    global values_for_column_drg
    global sheet_dict_drg
    global importCommands_drg
    global config
    config=config1
    global signer
    signer=signer1

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

    # Get dict for columns from Excel_Columns
    sheet_dict_drg = ct.sheet_dict["DRGRouteRulesinOCI"]

    print("\nFetching DRG Route Rules...")

    if tf_import_cmd_drg:
        importCommands_drg = {}
        for reg in export_regions:
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir+ "/tf_import_commands_network_drg_routerules_nonGF.sh")):
                commonTools.backup_file(outdir + "/" + reg+ "/" + service_dir, "tf_import_network",
                                        "tf_import_commands_network_drg_routerules_nonGF.sh")
            importCommands_drg[reg] = open(outdir + "/" + reg + "/" + service_dir+ "/tf_import_commands_network_drg_routerules_nonGF.sh", "w")
            importCommands_drg[reg].write("#!/bin/bash")
            importCommands_drg[reg].write("\n")
            importCommands_drg[reg].write("terraform init")
            importCommands_drg[reg].write("\n\n######### Writing import for DRG Route Tables #########\n\n")

    for reg in export_regions:
        config.__setitem__("region", commonTools().region_dict[reg])
        vcn = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer,timeout=(30,120))
        region = reg.capitalize()
        #comp_ocid_done = []

        for ntk_compartment_name in export_compartments:
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
                                importCommands_drg[reg].write("\nterraform import \"module.drg-route-tables[\\\"" + drg_rt_tf_name + "\\\"].oci_core_drg_route_table.drg_route_table\" " + drg_route_table_id)



                        #drg_rt_rules = vcn.list_drg_route_rules(drg_route_table_id)
                        drg_rt_rules = oci.pagination.list_call_get_all_results(vcn.list_drg_route_rules, drg_route_table_id,route_type="STATIC")
                        #drg_rt_rules = None
                        print_drg_routerules(drg_route_table_info, drg_display_name,drg_route_table_name, import_drg_route_distribution_name,
                                             drg_rt_rules, region, ntk_compartment_name)

    commonTools.write_to_cd3(values_for_column_drg, cd3file, "DRGRouteRulesinOCI")
    print("DRG RouteRules exported to CD3\n")

    if tf_import_cmd_drg:
        for reg in export_regions:
            importCommands_drg[reg].write('\n\nterraform plan\n')
            importCommands_drg[reg].close()


# Execution of the code begins here for route table export
def export_routetable(inputfile, outdir, service_dir,config1,signer1, ct, export_compartments,export_regions,_tf_import_cmd):
    # Read the arguments
    global tf_import_cmd
    global values_for_column
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global config
    config=config1
    global signer
    signer=signer1

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

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict["RouteRulesinOCI"]

    print("\nFetching Route Rules...")
    if tf_import_cmd:
        importCommands={}
        for reg in export_regions:
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir+ "/tf_import_commands_network_routerules_nonGF.sh")):
                commonTools.backup_file(outdir + "/" + reg+ "/" + service_dir, "tf_import_network",
                                        "tf_import_commands_network_routerules_nonGF.sh")
            importCommands[reg] = open(outdir + "/" + reg + "/" + service_dir+ "/tf_import_commands_network_routerules_nonGF.sh", "a")
            importCommands[reg].write("#!/bin/bash")
            importCommands[reg].write("\n")
            importCommands[reg].write("terraform init")
            importCommands[reg].write("\n\n######### Writing import for Route Tables #########\n\n")

    for reg in export_regions:
        config.__setitem__("region", commonTools().region_dict[reg])
        vcn = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        region = reg.capitalize()
        #comp_ocid_done = []

        for ntk_compartment_name in export_compartments:
                vcns = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],lifecycle_state="AVAILABLE")
                for v in vcns.data:
                    vcn_id = v.id
                    vcn_name=v.display_name
                    for ntk_compartment_name_again in export_compartments:
                            routetables = oci.pagination.list_call_get_all_results(vcn.list_route_tables, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE')
                            print_routetables(routetables,region,vcn_name,ntk_compartment_name_again)
    commonTools.write_to_cd3(values_for_column,cd3file,"RouteRulesinOCI")
    print("RouteRules exported to CD3\n")

    if tf_import_cmd:
        commonTools.write_to_cd3(values_for_vcninfo, cd3file, "VCN Info")
        for reg in export_regions:
            importCommands[reg].write('\n\nterraform plan\n')
            importCommands[reg].close()


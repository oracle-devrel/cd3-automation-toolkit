#!/usr/bin/python3

import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
import os
import subprocess as sp
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

def get_network_entity_name(config,signer,network_identity_id,export_tags):
    vcn1 = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    if('internetgateway' in network_identity_id):
        igw=vcn1.get_internet_gateway(network_identity_id)
        network_entity_comp_id=igw.data.compartment_id

        # Tags filter for DRG attachment
        defined_tags = igw.data.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)

        # None of Tags from export_tags exist on this instance or not in the compartment specified for export; Dont export this instance
        if check == False or network_entity_comp_id not in export_compartment_ids:
            network_identity_name = "igw:" + igw.data.id
        else:
            network_identity_name = "igw:" + igw.data.display_name
        '''
        if network_entity_comp_id in export_compartment_ids:
            network_identity_name = "igw:"+igw.data.display_name
        else:
            network_identity_name = "igw:" + igw.data.id
        '''

        return  network_identity_name

    elif ('servicegateway' in network_identity_id):
        sgw = vcn1.get_service_gateway(network_identity_id)
        network_entity_comp_id = sgw.data.compartment_id

        # Tags filter for DRG attachment
        defined_tags = sgw.data.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)

        # None of Tags from export_tags exist on this instance or not in the compartment specified for export; Dont export this instance
        if check == False or network_entity_comp_id not in export_compartment_ids:
            network_identity_name = "sgw:" + sgw.data.id
        else:
            network_identity_name = "sgw:" + sgw.data.display_name

        '''
        if network_entity_comp_id in export_compartment_ids:
            network_identity_name = "sgw:" + sgw.data.display_name
        else:
            network_identity_name = "sgw:"+sgw.data.id
        '''
        return network_identity_name


    elif ('natgateway' in network_identity_id):
        ngw = vcn1.get_nat_gateway(network_identity_id)
        network_entity_comp_id = ngw.data.compartment_id

        # Tags filter for DRG attachment
        defined_tags = ngw.data.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)

        # None of Tags from export_tags exist on this instance or not in the compartment specified for export; Dont export this instance
        if check == False or network_entity_comp_id not in export_compartment_ids:
            network_identity_name = "ngw:" + ngw.data.id
        else:
            network_identity_name = "ngw:" + ngw.data.display_name
        '''
        if network_entity_comp_id in export_compartment_ids:
            network_identity_name = "ngw:" + ngw.data.display_name
        else:
            network_identity_name = "ngw:"+ngw.data.id
        '''

        return network_identity_name

    elif ('localpeeringgateway' in network_identity_id):
        lpg = vcn1.get_local_peering_gateway(network_identity_id)
        network_entity_comp_id = lpg.data.compartment_id

        # Tags filter for DRG attachment
        defined_tags = lpg.data.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)

        # None of Tags from export_tags exist on this instance or not in the compartment specified for export; Dont export this instance
        if check == False or network_entity_comp_id not in export_compartment_ids:
            network_identity_name = "lpg:" + lpg.data.id
        else:
            network_identity_name = "lpg:" + lpg.data.display_name

        '''
        if network_entity_comp_id in export_compartment_ids:
            network_identity_name = "lpg:" + lpg.data.display_name
        else:
            network_identity_name = "lpg:"+lpg.data.id
        '''

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
        network_entity_comp_id = drg.data.compartment_id

        # Tags filter for DRG attachment
        defined_tags = drg.data.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)

        # None of Tags from export_tags exist on this instance or not in the compartment specified for export; Dont export this instance
        if check == False or network_entity_comp_id not in export_compartment_ids:
            network_identity_name = "drg:" + drg.data.id
        else:
            network_identity_name = "drg:" + drg.data.display_name

        '''
        if network_entity_comp_id in export_compartment_ids:
            network_identity_name = "drg:" + drg.data.display_name
        else:
            network_identity_name = "drg:"+drg.data.id
        '''
        return network_identity_name

        '''
        elif ('privateip' in network_identity_id):
            privateip = vcn1.get_private_ip(network_identity_id)
            network_identity_name = "privateip:"+privateip.data.ip_address
            return network_identity_name
        '''
    else:
        return network_identity_id

def insert_values(routetable,values_for_column,region,comp_name,name,routerule,export_tags):
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
            network_entity_name = get_network_entity_name(config, signer, network_entity_id,export_tags)
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


def insert_values_drg(routetable,import_drg_route_distribution_name,values_for_column_drg,region,comp_name,name,routerule,export_tags):
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
            network_entity_name = get_network_entity_name(config, signer, next_hop_attachment_id,export_tags)
            values_for_column_drg[col_header].append(network_entity_name)

        else:
            oci_objs = [routetable,routerule]
            values_for_column_drg = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_drg,values_for_column_drg)



def print_drg_routerules(drg_rt_info,drg_display_name,drg_route_table_name,import_drg_route_distribution_name,drg_rules,region,comp_name,export_tags,state):
    drg_rt_name = drg_display_name + "_" + drg_route_table_name
    drg_rt_tf_name = commonTools.check_tf_variable(drg_rt_name)
    if (not drg_rules.data):
        insert_values_drg(drg_rt_info, import_drg_route_distribution_name,values_for_column_drg, region, comp_name, drg_display_name, None,export_tags)
        if not tf_import_cmd_drg:
            print(drg_route_table_name)
    i=1
    for rule in drg_rules.data:
        insert_values_drg(drg_rt_info, import_drg_route_distribution_name,values_for_column_drg, region, comp_name, drg_display_name, rule,export_tags)
        if not tf_import_cmd_drg:
            print(drg_route_table_name)
        else:
            if rule.route_type.lower()=='static':
                tf_resource = f'module.drg-route-rules[\\"{drg_rt_tf_name}_route_rule{str(i)}\\"].oci_core_drg_route_table_route_rule.drg_route_rule'
                if tf_resource not in state["resources"]:
                    importCommands_drg[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" drgRouteTables/{str(drg_rt_info.id)}/routeRules/{str(rule.id)}'
        i=i+1

def print_routetables(routetables,region,vcn_name,comp_name,export_tags,gw_route_table_ids,state):
    for routetable in routetables.data:
        # Tags filter
        defined_tags = routetable.defined_tags
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

        rules = routetable.route_rules
        display_name = routetable.display_name
        dn=display_name
        if tf_import_cmd:
            tf_name = vcn_name + "_" + dn
            tf_name = commonTools.check_tf_variable(tf_name)

            if routetable.id in gw_route_table_ids:
                if ("Default Route Table for " in dn):
                    tf_resource = f'module.gateway-route-tables[\\"{tf_name}\\"].oci_core_default_route_table.default_route_table[0]'
                else:
                    tf_resource = f'module.gateway-route-tables[\\"{tf_name}\\"].oci_core_route_table.route_table[0]'
            else:
                if ("Default Route Table for " in dn):
                    tf_resource = f'module.route-tables[\\"{tf_name}\\"].oci_core_default_route_table.default_route_table[0]'
                else:
                    tf_resource = f'module.route-tables[\\"{tf_name}\\"].oci_core_route_table.route_table[0]'

            if tf_resource not in state["resources"]:
                importCommands[region.lower()] += f'\n{tf_or_tofu} import "{tf_resource}" {str(routetable.id)}'

        if(not rules):
            insert_values(routetable, values_for_column, region, comp_name, vcn_name,None,export_tags)
            if not tf_import_cmd:
                print(dn)

        for rule in rules:
            insert_values(routetable, values_for_column, region, comp_name, vcn_name,rule,export_tags)
            desc = str(rule.description)
            if (desc == "None"):
                desc = ""
            if not tf_import_cmd:
                print(dn + "," +str(rule.destination)+","+desc)

# Execution of the code begins here for drg route table
def export_drg_routetable(inputfile, outdir, service_dir,config1,signer1, ct, export_compartments,export_regions,export_tags,_tf_import_cmd):
    # Read the arguments
    global tf_import_cmd_drg
    global values_for_column_drg
    global sheet_dict_drg
    global importCommands_drg
    global config
    config=config1
    global signer,tf_or_tofu
    signer=signer1

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

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
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir+ "/import_commands_network_drg_routerules.sh")):
                commonTools.backup_file(outdir + "/" + reg+ "/" + service_dir, "import_network",
                                        "import_commands_network_drg_routerules.sh")
            importCommands_drg[reg] = ""
    else:
        drgv2=parseDRGs(cd3file)

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
        vcn = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer,timeout=(30,120))
        region = reg.capitalize()
        #comp_ocid_done = []

        for ntk_compartment_name in export_compartments:
                drgs = oci.pagination.list_call_get_all_results(vcn.list_drgs,
                                                                compartment_id=ct.ntk_compartment_ids[ntk_compartment_name])
                for drg in drgs.data:

                    # Tags filter
                    defined_tags = drg.defined_tags
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

                    #DRG v1
                    DRG_Name = drg.display_name
                    if drg.default_drg_route_tables is None:
                        continue
                    if not tf_import_cmd_drg:
                        try:
                            if (DRG_Name not in drgv2.drg_names[reg]):
                                print(f'skipping DRG route table as its DRG {DRG_Name} is not part of DRGs tab in cd3')
                                continue
                        except KeyError:
                            print("skipping DRG route table as no DRG is declared for region " + reg )
                            continue

                    # Get DRG RT Tables for the DRG - They are in same compartment s DRG by default
                    DRG_RTs = oci.pagination.list_call_get_all_results(vcn.list_drg_route_tables, drg_id=drg.id)
                    for drg_route_table_info in DRG_RTs.data:
                        # Tags filter
                        defined_tags = drg_route_table_info.defined_tags
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

                        drg_info = drg
                        drg_route_table_id = drg_route_table_info.id
                        drg_route_table_name = drg_route_table_info.display_name
                        drg_display_name = drg_info.display_name
                        import_drg_route_distribution_name = ''
                        import_drg_route_distribution_id = drg_route_table_info.import_drg_route_distribution_id

                        if (import_drg_route_distribution_id != None):
                            import_drg_route_distribution_info = vcn.get_drg_route_distribution(import_drg_route_distribution_id).data

                            # Tags filter
                            defined_tags = import_drg_route_distribution_info.defined_tags
                            if defined_tags != {}:
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
                                    import_drg_route_distribution_id = None

                            import_drg_route_distribution_name=import_drg_route_distribution_info.display_name

                        drg_rt_name = drg_display_name + "_" + drg_route_table_name
                        drg_rt_tf_name = commonTools.check_tf_variable(drg_rt_name)
                        if tf_import_cmd_drg:
                            if drg_route_table_name not in commonTools.drg_auto_RTs:
                                tf_resource = f'module.drg-route-tables[\\"{drg_rt_tf_name}\\"].oci_core_drg_route_table.drg_route_table'
                                if tf_resource not in state["resources"]:
                                    importCommands_drg[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {drg_route_table_id}'

                        #drg_rt_rules = vcn.list_drg_route_rules(drg_route_table_id)
                        drg_rt_rules = oci.pagination.list_call_get_all_results(vcn.list_drg_route_rules, drg_route_table_id,route_type="STATIC")
                        #drg_rt_rules = None
                        print_drg_routerules(drg_route_table_info, drg_display_name,drg_route_table_name, import_drg_route_distribution_name,
                                             drg_rt_rules, region, ntk_compartment_name,export_tags,state)

    commonTools.write_to_cd3(values_for_column_drg, cd3file, "DRGRouteRulesinOCI")
    print("DRG RouteRules exported to CD3\n")

    if tf_import_cmd_drg:
        for reg in export_regions:
            script_file = f'{outdir}/{reg}/{service_dir}/import_commands_network_drg_routerules.sh'
            init_commands = f'\n#!/bin/bash\n{tf_or_tofu} init\n######### Writing import for DRG Route Tables #########\n'
            if importCommands_drg[reg] != "":
                importCommands_drg[reg] += f'\n{tf_or_tofu} plan\n'
                with open(script_file, 'a') as importCommandsfile:
                    importCommandsfile.write(init_commands + importCommands_drg[reg])



# Execution of the code begins here for route table export
def export_routetable(inputfile, outdir, service_dir,config1,signer1, ct, export_compartments,export_regions,export_tags,_tf_import_cmd):
    # Read the arguments
    global tf_import_cmd
    global values_for_column
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global config
    config=config1
    global signer,tf_or_tofu
    signer=signer1
    global export_compartment_ids

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]

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
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir+ "/import_commands_network_routerules.sh")):
                commonTools.backup_file(outdir + "/" + reg+ "/" + service_dir, "import_network",
                                        "import_commands_network_routerules.sh")
            importCommands[reg] = ''
    else:
        vcns_check = parseVCNs(cd3file)

    export_compartment_ids = []
    for comp in export_compartments:
        export_compartment_ids.append(ct.ntk_compartment_ids[comp])

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
                gw_route_table_ids = []
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
                        # rtname = str(df.loc[i, 'Route Table Name']).strip()
                        if (check not in vcns_check.vcn_names):
                            print(f'skipping route table for vcn {vcn_name} in region {reg}')
                            continue
                    IGWs = oci.pagination.list_call_get_all_results(vcn.list_internet_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],
                                                                    vcn_id=vcn_id, lifecycle_state="AVAILABLE")
                    NGWs = oci.pagination.list_call_get_all_results(vcn.list_nat_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],
                                                                    vcn_id=vcn_id, lifecycle_state="AVAILABLE")
                    SGWs = oci.pagination.list_call_get_all_results(vcn.list_service_gateways,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],
                                                                    vcn_id=vcn_id, lifecycle_state="AVAILABLE")
                    for igw in IGWs.data:
                        if igw.route_table_id not in gw_route_table_ids:
                            gw_route_table_ids.append(igw.route_table_id)
                    for ngw in NGWs.data:
                        if ngw.route_table_id not in gw_route_table_ids:
                            gw_route_table_ids.append(ngw.route_table_id)
                    for sgw in SGWs.data:
                        if sgw.route_table_id not in gw_route_table_ids:
                            gw_route_table_ids.append(sgw.route_table_id)

                    for ntk_compartment_name_again in export_compartments:
                            routetables = oci.pagination.list_call_get_all_results(vcn.list_route_tables, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name_again], vcn_id=vcn_id, lifecycle_state='AVAILABLE')
                            print_routetables(routetables,region,vcn_name,ntk_compartment_name_again,export_tags,gw_route_table_ids,state)
    commonTools.write_to_cd3(values_for_column,cd3file,"RouteRulesinOCI")
    print("RouteRules exported to CD3\n")

    if tf_import_cmd:
        commonTools.write_to_cd3(values_for_vcninfo, cd3file, "VCN Info")
        for reg in export_regions:
            script_file = f'{outdir}/{reg}/{service_dir}/import_commands_network_routerules.sh'
            init_commands = f'\n#!/bin/bash\n{tf_or_tofu} init\n######### Writing import for Route Tables #########\n'
            if importCommands[reg] != "":
                importCommands[reg] += f'\n{tf_or_tofu} plan\n'
                with open(script_file, 'a') as importCommandsfile:
                    importCommandsfile.write(init_commands + importCommands[reg])



#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Modify Route Table
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Takes in input  CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######

# Execution of the code begins here for drg route table
def modify_terraform_drg_routerules(inputfile, outdir, service_dir,prefix, ct, non_gf_tenancy):
    filename = inputfile

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    routerule_drg = env.get_template('drg-route-rule-template')
    routetable_drg = env.get_template('drg-route-table-template')
    auto_tfvars_filename = "_drg-routetables.auto.tfvars"
    rule_auto_tfvars_filename = "_drg-route-rules.auto.tfvars"

    tempStr = {}
    tempdict={}
    tempSkeletonDRGRouteTable = {}
    tempSkeletonDRGRouteRule = {}
    tfStr = {}
    tfStrRT = {}

    drgv2=parseDRGs(filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "DRGRouteRulesinOCI")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    rts_done={}
    oname_rt=None


    for reg in ct.all_regions:
        rts_done[reg] = []
        tempSkeletonDRGRouteTable[reg] = []
        tempSkeletonDRGRouteRule[reg] = []
        tfStr[reg] = ''
        tfStrRT[reg] = ''

        # Backup existing route table files in ash and phx dir
        resource = "DRGRTs"
        commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, auto_tfvars_filename)
        commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, rule_auto_tfvars_filename)


        # Create Skeleton Template
        tempSkeletonDRGRouteTable[reg] = routetable_drg.render(tempStr, skeleton=True, region=reg)
        tempSkeletonDRGRouteRule[reg] = routerule_drg.render(tempStr, skeleton=True, region=reg)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:

        drg_rt_dstrb_tf_name=''
        drg_rt_dstrb_res_name = ''
        drg_rt_tf_name = ''
        new_rule=0

        region = str(df.loc[i, 'Region']).strip()
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        DRG_RT = str(df.loc[i, 'DRG RT Name']).strip()
        DRG_Name = str(df.loc[i, 'DRG Name']).strip()
        DRG_RD_Name = str(df.loc[i, 'Import DRG Route Distribution Name']).strip()

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'DRG Name']).lower() == 'nan' or str(df.loc[i, 'DRG RT Name']).lower() == 'nan'):# or str(df.loc[i, 'Import DRG Route Distribution Name']).lower() == 'nan'):
            print("\nColumn Region, DRG Name and DRG RT Name and Import DRG Route Distribution Name cannot be left empty in DRGRouteRulesinOCI sheet of CD3..Exiting!")
            exit(1)

        # Process RTs only for those DRG which are present in cd3(and have been created via TF)
        try:
            if (DRG_Name not in drgv2.drg_names[region]):
                print("skipping DRG route table: " + str(df.loc[i, 'DRG RT Name']) + " as its DRG is not part of DRGs tab in cd3")
                continue
        except KeyError:
            print("skipping DRG route table: " + str(df.loc[i, 'DRG RT Name']) + " as no DRG is declared for region "+region)
            continue

        # Process RTs only for those Import DRG Route Distribution Names which are present in cd3(and have been created via TF)
        if (DRG_RD_Name not in drgv2.drg_rds[DRG_Name,region] and  DRG_RD_Name.lower()!='nan' and DRG_RD_Name not in commonTools.drg_auto_RDs):
            print("skipping DRG route table: " + str(df.loc[i, 'DRG RT Name']) + " as either its DRG is not part of DRGv2 tab in cd3 or its Import Route Distribution Name is not attached to DRG "+ DRG_Name+" as per DRGv2 tab in cd3")
            continue


        #new rule to be added
        if (str(df.loc[i, 'Destination CIDR']).lower() != 'nan' and str(df.loc[i, 'Next Hop Attachment']).lower() != 'nan' and str(df.loc[i, 'Destination Type']).lower() != 'nan' and str(df.loc[i, 'Route Type']).lower() == 'static'):
            new_rule = 1


        #Route table without any rule
        if (str(df.loc[i, 'Destination CIDR']).lower() == 'nan' and str(df.loc[i, 'Next Hop Attachment']).lower() == 'nan' and str(df.loc[i, 'Destination Type']).lower() == 'nan' and str(df.loc[i, 'Route Type']).lower() != 'static'):
            new_rule = -1


        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            tempStr.update(tempdict)

            if columnname == 'DRG Name':
                drg_name = columnvalue
                drg_tf_name = commonTools.check_tf_variable(drg_name)
                tempStr['drg_tf_name'] = drg_tf_name

            if columnname == 'DRG RT Name':
                rt=columnvalue
                drg_rt_tf_name = commonTools.check_tf_variable(drg_name + "_" + rt)

                tempStr['display_name']= rt
                tempStr['drg_rt_tf_name'] = drg_rt_tf_name

            if(columnname == "Import DRG Route Distribution Name"):

                if columnvalue in commonTools.drg_auto_RDs:
                    drg_rt_dstrb_tf_name = commonTools.check_tf_variable(drg_name + "_" + columnvalue)
                    drg_rt_dstrb_res_name = drg_rt_dstrb_tf_name
                elif columnvalue!='':
                    drg_rt_dstrb_tf_name = commonTools.check_tf_variable(drg_name + "_" + columnvalue)
                    drg_rt_dstrb_res_name = drg_rt_dstrb_tf_name

                #Route Distribution name can be null also in that dont assign any distribution name to the rote table

                tempStr['drg_rt_dstrb_tf_name']=drg_rt_dstrb_tf_name
                tempStr['drg_rt_dstrb_res_name'] = drg_rt_dstrb_res_name

            if columnname == 'Next Hop Attachment':
                dest_obj = columnvalue.strip()
                if dest_obj != '':
                    if("ocid1.drgattachment.oc" in dest_obj):
                        dest_objs = str(dest_obj).strip().split(".")
                        if(len(dest_objs)==5):
                            dest_obj = dest_obj.strip()
                        else:
                            print("wrong OCID")
                            break
                    else:
                        dest_obj = commonTools.check_tf_variable(dest_obj.strip())

                    tempdict = {'next_hop_drg_attachment_id': dest_obj}
                    tempStr.update(tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Process first RT
        if(len(rts_done[region])==0):
            k=1
            #Create RT resource only if it is not Auto Generated one
            if (DRG_RT not in commonTools.drg_auto_RTs):
                tfStrRT[region] = tfStrRT[region] + routetable_drg.render(tempStr)
            rts_done[region].append(drg_rt_tf_name)

        if (drg_rt_tf_name not in rts_done[region]):
            rts_done[region].append(drg_rt_tf_name)

            # Create RT resource only if it is not Auto Generated one
            if (DRG_RT not in commonTools.drg_auto_RTs):
                tfStrRT[region] = tfStrRT[region] + routetable_drg.render(tempStr)
            k=1

            #Empty Route Table
            if(new_rule == -1):

                if (drg_rt_tf_name not in rts_done[region]):
                    rts_done[region].append(drg_rt_tf_name)
                #tfStr[region]=""

        #Add rules to RTs
        if(new_rule == 1):
            tempStr['drg_rt_rule_tf_name'] = drg_rt_tf_name+"_route_rule"+str(k)
            k=k+1
            tfStrRule=routerule_drg.render(tempStr)
            tfStr[region] = tfStr[region] + tfStrRule
            if(drg_rt_tf_name not in rts_done[region]):
                rts_done[region].append(drg_rt_tf_name)

    for reg in ct.all_regions:
        outfile = outdir + "/" + reg + "/" + service_dir+ "/"  + prefix + auto_tfvars_filename
        ruleoutfile = outdir + "/" + reg + "/" + service_dir+ "/" + prefix + rule_auto_tfvars_filename

        rtskeletonStr = "###Add route tables here for "+reg.lower()+" ###"
        rrskeletonStr = "###Add route rules here for "+reg.lower()+" ###"

        if tfStrRT[reg] != '':
            srcStr="###Add route tables here for "+reg.lower()+" ###"
            tempSkeletonDRGRouteTable[reg] = tempSkeletonDRGRouteTable[reg].replace(srcStr, tfStrRT[reg] + "\n" + rtskeletonStr)

            tempSkeletonDRGRouteTable[reg] = "".join([s for s in tempSkeletonDRGRouteTable[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname_rt = open(outfile, "w+")
            print("Writing to..." + str(outfile))
            oname_rt.write(tempSkeletonDRGRouteTable[reg])
            oname_rt.close()

        if tfStr[reg] != '':
            srcStr="###Add route rules here for "+reg.lower()+" ###"
            tempSkeletonDRGRouteRule[reg] = tempSkeletonDRGRouteRule[reg].replace(srcStr, tfStr[reg] + "\n" + rrskeletonStr)

            tempSkeletonDRGRouteRule[reg] = "".join([s for s in tempSkeletonDRGRouteRule[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname_rt = open(ruleoutfile, "w+")
            print("Writing to..." + str(ruleoutfile))
            oname_rt.write(tempSkeletonDRGRouteRule[reg])
            oname_rt.close()
# Execution of the code begins here for route rule modification
def modify_terraform_routerules(inputfile, outdir, service_dir,prefix, ct, non_gf_tenancy):
    filename = inputfile

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    routerule = env.get_template('route-rule-template')
    defaultrt = env.get_template('default-route-table-template')
    routetable = env.get_template('route-table-template')
    auto_tfvars_filename = "_routetables.auto.tfvars"
    default_auto_tfvars_filename = "_default-routetables.auto.tfvars"
    region_included = []
    common_rt = []

    subnets_done={}
    default_ruleStr={}
    default_rtables_done={}
    default_rule={}

    def create_route_rule_string(routetableStr,tempStr,region):
        srcStr = "####ADD_NEW_"+tempStr['resource']+"_RULES " + tempStr['region_rt_name'] + " ####"
        new_route_rule = routerule.render(tempStr)
        new_route_rule = new_route_rule + "\n" + srcStr + "\n"
        routetableStr[region] = routetableStr[region].replace(srcStr, new_route_rule)
        return routetableStr[region]


    def generate_route_table_string(region_rt_name,region,routetableStr,tempStr,common_rt):
        if (region_rt_name not in common_rt and region_rt_name not in routetableStr[region]):
            routetableStr[region] = routetableStr[region] + routetable.render(tempStr,
                                                                            route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                                                            route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                                                            route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                                                            route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                                                            route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                                                            route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )

        if tempStr['network_entity_id'] != '':
            if tempStr['resource'] == "NGW":
                routetableStr[region] = create_route_rule_string(routetableStr,tempStr,region)

            if tempStr['resource'] == "IGW":
                routetableStr[region] = create_route_rule_string(routetableStr,tempStr,region)

            if tempStr['resource'] == "SGW":
                routetableStr[region] = create_route_rule_string(routetableStr,tempStr,region)

            if tempStr['resource'] == "LPG":
                routetableStr[region] = create_route_rule_string(routetableStr,tempStr,region)

            if tempStr['resource'] == "DRG":
                routetableStr[region] = create_route_rule_string(routetableStr,tempStr,region)

            if tempStr['resource'] == "IP":
                routetableStr[region] = create_route_rule_string(routetableStr,tempStr,region)

        common_rt.append(region_rt_name)
        return routetableStr[region]

    vcns=parseVCNs(filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "RouteRulesinOCI")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    tempSkeleton = {}
    default_rt_tempSkeleton = {}
    tfStr = {}
    deftfStr = {}

    for reg in ct.all_regions:
        default_ruleStr[reg] = ''
        default_rule[reg] = ''
        default_rtables_done[reg]=[]
        subnets_done[reg] = []
        default_rt_tempSkeleton[reg] = ''
        tempSkeleton[reg] = ''
        tfStr[reg] = ''
        deftfStr[reg] = ''

        # Backup existing route table files in ash and phx dir
        resource = "RTs"
        commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, prefix + auto_tfvars_filename)
        commonTools.backup_file(outdir + "/" + reg+ "/" + service_dir, resource, prefix + default_auto_tfvars_filename)

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}
    vcn_tf_name = ''
    obj_tf_name = ''
    display_name=''
    region_rt_name = ''

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).strip().lower() == 'nan' or str(df.loc[i, 'VCN Name']).strip().lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan'):
            print("\nColumn Region, VCN Name and Compartment Name cannot be left empty in RouteRulesinOCI sheet of CD3..Exiting!")
            exit(1)

        # Process only those VCNs which are present in cd3(and have been created via TF)
        vcn_name=str(df.loc[i, 'VCN Name']).strip()
        check = vcn_name, region
        rtname = str(df.loc[i, 'Route Table Name']).strip()
        if (check not in vcns.vcn_names):
            print("skipping route table: " + rtname + " as its VCN is not part of VCNs tab in cd3")
            continue

        tempStr.update({'count': 1})
        if ('Default Route Table for' in rtname):
            if ('Default Route Table for' + region not in region_included):
                tempStr.update({'count': 0})
                region_included.append('Default Route Table for' + str(df.loc[i, 'Region']).lower())
        elif region not in region_included:
            tempStr.update({'count': 0})
            region_included.append(region.lower())

        # Create Skeleton Template
        if tempStr['count'] == 0:
            if ('Default Route Table for' in str(df.loc[i,'Route Table Name']).strip()):
                default_rt_tempSkeleton[region] = defaultrt.render(tempStr, skeleton=True, region=region)
            elif ('Default Route Table for' not in str(df.loc[i,'Route Table Name']).strip()):
                tempSkeleton[region] = routetable.render(tempStr, skeleton=True, region=region)



        res_igw = any(rtname in sublist for sublist in vcns.vcn_igws.values())
        res_ngw = any(rtname in sublist for sublist in vcns.vcn_ngws.values())
        res_sgw = any(rtname in sublist for sublist in vcns.vcn_sgws.values())

        gateway_rt = res_igw or res_ngw or res_sgw

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                tempStr.update(tempdict)

            if columnname == 'Compartment Name':
                compartment_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartment_tf_name}
                tempStr.update(tempdict)

            if columnname == 'VCN Name':
                vcn_name = columnvalue
                display_name = str(df.loc[i,'Route Table Name'])

                vcn_tf_name = commonTools.check_tf_variable(vcn_name)
                tempdict = {'vcn_tf_name': vcn_tf_name,'display_name' : display_name}
                tempStr.update(tempdict)

            # Check this code once
            if columnname == 'Route Table Name':
                if columnvalue == '':
                    continue
                else:
                    columnvalue = vcn_tf_name+"_"+commonTools.check_tf_variable(str(columnvalue).strip())
                    tempdict = {'rt_tf_name' :  columnvalue}
                    add_rules_tf_name = columnvalue
                    tempStr.update(tempdict)

            if columnname == 'Destination CIDR':
                destination = columnvalue.strip()
                tempdict = { 'destination': destination }
                tempStr.update(tempdict)

            if columnname == 'Rule Description':
                description = columnvalue.strip()
                if description == 'nan':
                    description = ""
                tempdict = {'description': description}
                tempStr.update(tempdict)

            if columnname == 'Route Destination Object':
                dest_objs = columnvalue.strip()
                if dest_objs != '':
                    dest_objs = str(dest_objs).strip().split(":")
                    if (len(dest_objs) == 2):
                        if "ocid1." not in dest_objs[1].strip():
                            obj_tf_name = vcn_tf_name + "_" + dest_objs[1].strip()
                            obj_tf_name = commonTools.check_tf_variable(obj_tf_name)
                        else:
                            obj_tf_name = dest_objs[1].strip()
                    if (dest_objs[0].lower().strip().startswith('ngw')):
                        tempdict = {'resource' : 'NGW','network_entity_id': obj_tf_name }
                        tempStr.update(tempdict)
                    elif (dest_objs[0].lower().strip().startswith('sgw')):
                        tempdict = {'resource': 'SGW','network_entity_id': obj_tf_name}
                        tempStr.update(tempdict)
                    elif (dest_objs[0].lower().strip().startswith('igw')):
                        tempdict = {'resource': 'IGW','network_entity_id': obj_tf_name}
                        tempStr.update(tempdict)
                    elif (dest_objs[0].lower().strip().startswith('lpg')):
                        tempdict = {'resource': 'LPG','network_entity_id': obj_tf_name}
                        tempStr.update(tempdict)
                    elif (dest_objs[0].lower().strip().startswith('drg')):
                        # dest_obj = "${oci_core_drg." + vcn_tf_name+"_"+obj_tf_name + ".id}"

                        if "ocid1." not in dest_objs[1].strip():
                            dest_obj = commonTools.check_tf_variable(dest_objs[1].strip())
                        else:
                            dest_obj = dest_objs[1].strip()

                        tempdict = {'resource': 'DRG','network_entity_id': dest_obj}
                        tempStr.update(tempdict)
                    elif('privateip' in dest_objs[0].lower().strip()):
                        tempdict = {'resource': 'IP','network_entity_id': dest_objs[0].lower().strip() }
                        tempStr.update(tempdict)
                else:
                    tempStr.update({'network_entity_id' : ''})

            rt_var = vcn_tf_name + "_" + display_name
            rt_tf_name = commonTools.check_tf_variable(rt_var)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

            region_rt_name = "#"+region.lower()+"_"+rt_tf_name+"#"

            tempdict = { 'region_rt_name' : region_rt_name }
            tempStr.update(tempdict)

        if ('Default Route Table for' in display_name):
            deftfStr[region] = generate_route_table_string(region_rt_name=region_rt_name,region=region, routetableStr=deftfStr,tempStr=tempStr,common_rt=common_rt)
        elif ('Default Route Table for' not in display_name.strip()):
            tfStr[region] = generate_route_table_string(region_rt_name=region_rt_name,region=region, routetableStr=tfStr,tempStr=tempStr,common_rt=common_rt)

        if gateway_rt:
            ss = "### gateway_route_table for " + region_rt_name + " ##"
            rr = "gateway_route_table = true"
            tfStr[region] = tfStr[region].replace(ss, rr)
            deftfStr[region] = deftfStr[region].replace(ss, rr)


    for reg in ct.all_regions:

        textToAddSeclistSearch = "##Add New Route Tables for " + reg + " here##"
        defaultTextToAddSeclistSearch = "##Add New Default Route Tables for " + reg + " here##"

        outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + auto_tfvars_filename
        default_outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + default_auto_tfvars_filename

        default_rt_tempSkeleton[reg] = default_rt_tempSkeleton[reg].replace(defaultTextToAddSeclistSearch,deftfStr[reg] +"\n"+ defaultTextToAddSeclistSearch)
        tempSkeleton[reg] = tempSkeleton[reg].replace(textToAddSeclistSearch,tfStr[reg] +"\n"+ textToAddSeclistSearch)

        if tfStr[reg] != '' :
            tempSkeleton[reg] = "".join([s for s in tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            oname.write(tempSkeleton[reg])
            oname.close()
            print(outfile + " for route tables has been created for region " + reg)

        if deftfStr[reg] !='':
            default_rt_tempSkeleton[reg] = "".join([s for s in default_rt_tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(default_outfile, "w+")
            oname.write(default_rt_tempSkeleton[reg])
            oname.close()
            print(default_outfile + " for default route tables has been created for region " + reg)

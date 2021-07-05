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
import argparse
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Takes in input  CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######

# If the input is CD3
def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
    parser.add_argument("inputfile", help="Required; Full Path to input route file (CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
    parser.add_argument("outdir",help="directory path for output tf files ")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    return parser.parse_args()


def modify_terraform_drg_routerules(inputfile, outdir, prefix=None, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    routerule_drg = env.get_template('drg-route-rule-template')
    routetable_drg = env.get_template('drg-route-table-template')
    tempStr = {}
    tempdict={}

    drgv2=parseDRGv2(filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "DRGRouteRulesinOCI")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    rts_done={}
    oname_rt=None


    for reg in ct.all_regions:
        rts_done[reg] = []
        # Backup existing route table files in ash and phx dir
        resource = "DRGRTs"
        commonTools.backup_file(outdir + "/" + reg, resource, "_drgroutetable.tf")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    tfStr = ''
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
        if (DRG_Name not in drgv2.drg_names[region]):
            print("skipping DRG route table: " + str(df.loc[i, 'DRG RT Name']) + " as its DRG is not part of DRGv2 tab in cd3")
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
                if (rt in commonTools.drg_auto_RTs):
                    drg_rt_res_name = "data.oci_core_drg_route_tables." + drg_rt_tf_name + ".drg_route_tables[0].id"
                else:
                    drg_rt_res_name = "oci_core_drg_route_table." + drg_rt_tf_name + ".id"

                tempStr['display_name']= rt
                tempStr['drg_rt_tf_name'] = drg_rt_tf_name
                tempStr['drg_rt_res_name'] = drg_rt_res_name

            if(columnname == "Import DRG Route Distribution Name"):

                if columnvalue in commonTools.drg_auto_RDs:
                    drg_rt_dstrb_tf_name = commonTools.check_tf_variable(drg_name + "_" + columnvalue)
                    drg_rt_dstrb_res_name = "data.oci_core_drg_route_distributions." + drg_rt_dstrb_tf_name + ".drg_route_distributions[0].id"
                elif columnvalue!='':
                    drg_rt_dstrb_tf_name = commonTools.check_tf_variable(drg_name + "_" + columnvalue)
                    drg_rt_dstrb_res_name = "oci_core_drg_route_distribution."+drg_rt_dstrb_tf_name+".id"

                #Route Distribution name can be null also in that dont assign any distribution name to the rote table

                tempStr['drg_rt_dstrb_tf_name']=drg_rt_dstrb_tf_name
                tempStr['drg_rt_dstrb_res_name'] = drg_rt_dstrb_res_name

            if columnname == 'Next Hop Attachment':
                dest_obj = columnvalue.strip()
                if dest_obj != '':
                    if("ocid1.drgattachment.oc1" in dest_obj):
                        dest_objs = str(dest_obj).strip().split(".")
                        if(len(dest_objs)==5):
                            dest_obj = "\"" + dest_obj.strip() + "\""
                        else:
                            print("wrong OCID")
                            break
                    else:
                        dest_obj = "oci_core_drg_attachment." + commonTools.check_tf_variable(dest_obj.strip()) + ".id"

                    tempdict = {'next_hop_drg_attachment_id': dest_obj}
                    tempStr.update(tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()


        # Process first RT
        tfStrRT=''
        if(len(rts_done[region])==0):
            #Write Previous Region's file
            if(tfStr!=''):
                print("Writing to..." + str(oname_rt.name))
                oname_rt.write(tfStr)
                oname_rt.close()


            outfile = outdir + "/" + region + "/" + drg_rt_tf_name + "_drgroutetable.tf"
            oname_rt = open(outfile, "w")
            k=1
            #Create RT resource only if it is not Auto Generated one
            if (DRG_RT not in commonTools.drg_auto_RTs):
                tfStrRT = routetable_drg.render(tempStr)
            tfStr = tfStrRT
            rts_done[region].append(drg_rt_tf_name)

        if (drg_rt_tf_name not in rts_done[region]):
            rts_done[region].append(drg_rt_tf_name)
            if (tfStr != ''):
                print("Writing to..." + str(oname_rt.name))
                oname_rt.write(tfStr)
                oname_rt.close()

            # Create RT resource only if it is not Auto Generated one
            if (DRG_RT not in commonTools.drg_auto_RTs):
                tfStrRT = routetable_drg.render(tempStr)
            tfStr = tfStrRT
            k=1
            outfile = outdir + "/" + region + "/" + drg_rt_tf_name + "_drgroutetable.tf"
            oname_rt = open(outfile,"w")

            #Empty Route Table
            if(new_rule == -1):
                if(tfStr!=""):
                    print("Writing to..." + str(oname_rt.name))
                    oname_rt.write(tfStr)
                    oname_rt.close()

                if (drg_rt_tf_name not in rts_done[region]):
                    rts_done[region].append(drg_rt_tf_name)
                tfStr=""

        #Add rules to RTs
        if(new_rule ==1):
            tempStr['drg_rt_rule_tf_name']=drg_rt_tf_name+"_route_rule"+str(k)
            k=k+1
            tfStrRule=routerule_drg.render(tempStr)
            tfStr = tfStr + tfStrRule
            if(drg_rt_tf_name not in rts_done[region]):
                rts_done[region].append(drg_rt_tf_name)


    #write last routetable
    if(tfStr!=""):
        print("Writing to..." + str(oname_rt.name))
        oname_rt.write(tfStr)
        oname_rt.close()


def modify_terraform_routerules(inputfile, outdir, prefix=None, config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    routerule = env.get_template('route-rule-template')
    defaultrt = env.get_template('default-route-table-template')
    routetable = env.get_template('route-table-template')


    subnets_done={}
    oname = None
    default_ruleStr={}
    defaultname={}
    default_rtables_done={}
    default_rule={}

    def create_route_rule_string(new_route_rule,tempStr):
        new_route_rule = new_route_rule + routerule.render(tempStr)
        return new_route_rule

    vcns=parseVCNs(filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "RouteRulesinOCI")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in ct.all_regions:
        if(os.path.exists(outdir + "/" +reg)):
            defaultname[reg] = open(outdir + "/" + reg + "/VCNs_Default_RouteTable.tf", "w")
        default_ruleStr[reg] = ''
        default_rule[reg] = ''
        default_rtables_done[reg]=[]
        subnets_done[reg] = []
        # Backup existing route table files in ash and phx dir
        resource = "RTs"
        commonTools.backup_file(outdir + "/" + reg, resource, "_routetable.tf")

    # temporary dictionary1 and dictionary2
    tempStr = {}
    tempdict = {}
    vcn_tf_name = ''
    obj_tf_name = ''
    display_name=''
    rt_tf_name=''
    dest_objs=[]
    tfStr = ''

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
        if (str(df.loc[i, 'VCN Name'].strip()) not in vcns.vcn_names):
            print("skipping route table: " + str(df.loc[i, 'Route Table Name']) + " as its VCN is not part of VCNs tab in cd3")
            continue

        destination = str(df.loc[i, 'Destination CIDR']).strip()
        destination = "\"" + destination + "\""
        description = str(df.loc[i, 'Rule Description'])
        if description == 'nan':
            description = ""
        tempdict = {'destination': destination, 'description': description}

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

            if columnname == 'Compartment Name':
                compartment_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartment_tf_name}
                tempStr.update(tempdict)

            if columnname == 'VCN Name':
                vcn_name = columnvalue
                display_name = str(df.loc[i,'Route Table Name'])

                vcn_tf_name = commonTools.check_tf_variable(vcn_name)
                tempdict = {'vcn_tf_name': vcn_tf_name,'rt_display' : display_name}
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

            if columnname == 'Route Destination Object':
                dest_objs = columnvalue.strip()
                if dest_objs != '':
                    dest_objs = str(dest_objs).strip().split(":")
                    if (len(dest_objs) == 2):
                        obj_tf_name = vcn_tf_name + "_" + dest_objs[1].strip()
                        obj_tf_name = commonTools.check_tf_variable(obj_tf_name)
                    if ('ngw' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_nat_gateway." + obj_tf_name + ".id"
                    elif ('sgw' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_service_gateway." + obj_tf_name + ".id"
                    elif ('igw' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_internet_gateway." + obj_tf_name + ".id"
                    elif ('lpg' in dest_objs[0].lower().strip()):
                        dest_obj = "oci_core_local_peering_gateway." + obj_tf_name + ".id"
                    elif ('drg' in dest_objs[0].lower().strip()):
                        # dest_obj = "${oci_core_drg." + vcn_tf_name+"_"+obj_tf_name + ".id}"
                        dest_obj = "oci_core_drg." + commonTools.check_tf_variable(dest_objs[1].strip()) + ".id"
                    #        elif ('privateip' in dest_objs[0].lower()):
                    # direct OCID is provided
                    else:
                        dest_obj = "\""+dest_objs[0].strip()+"\""

                    tempdict = {'network_entity_id' : dest_obj}
                    tempStr.update(tempdict)

            rt_var = vcn_tf_name + "_" + display_name
            rt_tf_name = commonTools.check_tf_variable(rt_var)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        srcStr = "####ADD_NEW_ROUTE_RULES####" + add_rules_tf_name

        if("Default Route Table for " in display_name):
            if (rt_tf_name not in default_rtables_done[region]):
                default_ruleStr[region] = default_ruleStr[region] + defaultrt.render(tempStr)
                default_rtables_done[region].append(rt_tf_name)

            default_rule[region] = ''
            if(dest_objs and dest_objs[0]!=""):
                default_rule[region]=create_route_rule_string(default_rule[region],tempStr)
            default_rule[region] = default_rule[region] + "\n" + "    " + srcStr
            default_ruleStr[region] = default_ruleStr[region].replace(srcStr, default_rule[region])

            continue

        #Process other route tables
        outfile = outdir + "/" + region + "/"+rt_tf_name+"_routetable.tf"
        oname = open(outfile, "w")
        if(rt_tf_name not in subnets_done[region] or len(subnets_done[region])==0):
            if (tfStr != ""):
                print("Writing to..."+str(oname.name))
                oname.write(tfStr)
                oname.close()
                tfStr = ""

            tfStr = routetable.render(tempStr)

            new_route_rule = ""
            if (dest_objs and dest_objs[0] != ""):
                new_route_rule = create_route_rule_string(new_route_rule, tempStr)
            subnets_done[region].append(rt_tf_name)
        else:
            new_route_rule = ""
            if (dest_objs and dest_objs[0] != ""):
                new_route_rule = create_route_rule_string(new_route_rule,tempStr)

        new_route_rule = new_route_rule + "\n" + "    " + srcStr
        tfStr = tfStr.replace(srcStr, new_route_rule)

        if (tfStr != ''):
            oname = open(outfile, "w")
            print("Writing to ..."+str(oname.name))
            oname.write(tfStr)
            oname.close()

    for reg in ct.all_regions:
        if (default_ruleStr[reg] != ''):
            print("Writing to ..." + str(defaultname[reg].name))
            defaultname[reg].write(default_ruleStr[reg])
            defaultname[reg].close()

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    modify_terraform_routerules(args.inputfile, args.outdir, prefix=None, config=args.config)
    modify_terraform_drg_routerules(args.inputfile, args.outdir, prefix=None, config=args.config)


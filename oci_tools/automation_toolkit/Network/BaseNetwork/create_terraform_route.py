#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Route Table
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import re
import os
from pathlib import Path
from oci.config import DEFAULT_LOCATION
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file, Modify Network AND outdir
######

def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description='Creates route tables containing default routes for each subnet based on inputs given in CD3 excel sheet.')
    parser.add_argument('inputfile', help='Full Path of input file. eg: cd3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument('--modify-network', action='store_true', help='Modify: true or false')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()



def create_terraform_drg_route(inputfile, outdir, prefix, config, modify_network=False):
    filename = inputfile
    configFileName = config
    drgv2=parseDRGs(filename)

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    drg_routetablefiles = {}
    drg_routedistributionfiles = {}
    tempStr={}

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    drg_rt_template=env.get_template('drg-route-table-template')
    drg_rd_template = env.get_template('drg-route-distribution-template')
    drg_rd_stmt_template = env.get_template('drg-route-distribution-statement-template')

    # If input is CD3 excel file
    if ('.xls' in filename):

        df, col_headers = commonTools.read_cd3(filename, "DRGs")
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)

        # Purge existing routetable files
        if not modify_network:
            for reg in ct.all_regions:
                drg_routetablefiles.setdefault(reg, [])
                drg_routedistributionfiles.setdefault(reg, [])
                purge(outdir + "/" + reg, "_drgroutetable.tf")
                purge(outdir + "/" + reg, "_drgroutedistribution.tf")

        # Get existing list of route table files
        if modify_network:
            for reg in ct.all_regions:
                drg_routetablefiles.setdefault(reg, [])
                drg_routedistributionfiles.setdefault(reg, [])
                lisoffiles = os.listdir(outdir + "/" + reg)
                for file in lisoffiles:
                    if "_drgroutetable.tf" in file:
                        drg_routetablefiles[reg].append(file)
                    if "_drgroutedistribution.tf" in file:
                        drg_routedistributionfiles[reg].append(file)



        # List of the column headers
        dfcolumns = df.columns.values.tolist()
        tempStr = {}
        tempdict = {}
        for i in df.index:
            drg_rt_dstrb_tf_name = ''
            drg_rt_dstrb_res_name = ''
            drg_tf_name= ''
            region = str(df.loc[i, 'Region']).strip()

            if (region in commonTools.endNames):
                break

            DRG_RT=str(df.loc[i, 'DRG RT Name']).strip()
            DRG_RD=str(df.loc[i, 'Import DRG Route Distribution Name']).strip()

            #Dont create any route table or route distribution name if left empty - attach Auto Generated ones
            if(DRG_RT.lower()=='nan' and DRG_RD.lower()=='nan'):# and DRG_RD_stmts.lower()=='nan'):
                continue

            #Dont create any route table or route distribution name if using Auto Generated ones
            if(DRG_RT in commonTools.drg_auto_RTs and DRG_RD in commonTools.drg_auto_RDs):
                continue


            region = region.strip().lower()
            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            for columnname in dfcolumns:
                # Column value
                columnvalue = str(df[columnname][i]).strip()

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)


                # Process Freeform and Defined Tags
                if columnname.lower() in commonTools.tagColumns:
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

                if columnname == "DRG Name":
                    drg_name=columnvalue
                    drg_tf_name=commonTools.check_tf_variable(columnvalue)
                    tempdict['drg_tf_name'] = commonTools.check_tf_variable(columnvalue)


                if columnname == "DRG RT Name":
                    tempdict['display_name'] = columnvalue
                    drg_rt_name=drg_name+"_"+columnvalue
                    drg_rt_tf_name = commonTools.check_tf_variable(drg_rt_name)
                    tempdict['drg_rt_tf_name'] =drg_rt_tf_name


                if columnname == 'Import DRG Route Distribution Name':
                    if(columnvalue.lower()!=''):
                        drg_rt_dstrb_name = drg_name+"_"+columnvalue
                        drg_rt_dstrb_tf_name=commonTools.check_tf_variable(drg_rt_dstrb_name)
                        drg_rt_dstrb_res_name = "oci_core_drg_route_distribution." + drg_rt_dstrb_tf_name+".id"
                    tempdict['drg_rt_dstrb_tf_name'] = drg_rt_dstrb_tf_name
                    tempdict['drg_rt_dstrb_res_name'] = drg_rt_dstrb_res_name
                    tempdict['dstrb_display_name']=columnvalue
                    tempdict['distribution_type'] = "IMPORT"
                    tempStr.update(tempdict)

                # Check for multivalued columns
                if (columnname == 'Import DRG Route Distribution Statements'):
                    columnvalues = columnvalue.split("\n")
                    k = 1
                    drg_rd_stmt = ''
                    for cv in columnvalues:
                        if(cv!=''):
                            tempdict = commonTools.check_multivalues_columnvalue(cv, columnname, tempdict)
                            tempStr.update(tempdict)
                            tempStr['statements']=tempStr['import_drg_route_distribution_statements']
                            tempStr['drg_rt_dstrb_statement_tf_name'] = drg_rt_dstrb_tf_name + "_statement" + str(k)
                            k = k + 1
                            drg_rd_stmt = drg_rd_stmt + drg_rd_stmt_template.render(tempStr)

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = columnvalue
                tempStr.update(tempdict)

            if(DRG_RT!='nan' and DRG_RT not in commonTools.drg_auto_RTs):
                outfile = outdir + "/" + region + "/" + drg_rt_tf_name + "_drgroutetable.tf"
                if (not os.path.exists(outfile)):
                    drg_rt = drg_rt_template.render(tempStr)
                    oname=open(outfile,"w")
                    oname.write(drg_rt)
                    oname.close()
                    print(outfile + " containing TF for DRG Route Table has been created for region " + region)

            #create Import Route Distribution only when specified some name else attach Auto Generated
            #if(DRG_RD.lower()!='nan' and DRG_RD_stmts.lower()!='nan'):
            if(DRG_RD.lower() != 'nan' and DRG_RD not in commonTools.drg_auto_RDs):
                outfile_rd = outdir + "/" + region + "/" + drg_rt_dstrb_tf_name + "_drgroutedistribution.tf"
                drg_rd = drg_rd_template.render(tempStr)
                tfStr=drg_rd+drg_rd_stmt
                oname = open(outfile_rd, "w")
                oname.write(tfStr)
                oname.close()
                print(outfile_rd + " containing TF for DRG Route Distribution has been created for region " + region)

            if (drg_rt_tf_name + "_drgroutetable.tf" in drg_routetablefiles[region]):
                drg_routetablefiles[region].remove(drg_rt_tf_name + "_drgroutetable.tf")
            if (drg_rt_dstrb_tf_name + "_drgroutedistribution.tf" in drg_routedistributionfiles[region]):
                drg_routedistributionfiles[region].remove(drg_rt_dstrb_tf_name + "_drgroutedistribution.tf")

#        for drg_name in drg_list.keys():
#            region=drg_list[drg_name]
        for region in drgv2.drg_names.keys():
            for drg_name in drgv2.drg_names[region]:
                for RT in commonTools.drg_auto_RTs:
                    rt_name=commonTools.check_tf_variable(drg_name+"_"+RT)+"_drgroutetable.tf"
                    if rt_name in drg_routetablefiles[region]:
                        drg_routetablefiles[region].remove(rt_name)

                for RD in commonTools.drg_auto_RDs:
                    rd_name = commonTools.check_tf_variable(drg_name + "_" + RD)+"_drgroutedistribution.tf"
                    if rd_name in drg_routedistributionfiles[region]:
                        drg_routedistributionfiles[region].remove(rd_name)


    for reg in ct.all_regions:
        if (len(drg_routetablefiles[reg]) != 0):
            print("\nATTENION!!! Below DRG RouteTables are not attached to any attachment; If you want to delete any of them, remove the TF file!!!")
            for remaining_rt_file in drg_routetablefiles[reg]:
                print(outdir + "/" + reg + "/" + remaining_rt_file)
        if (len(drg_routedistributionfiles[reg]) != 0):
            print("\nATTENION!!! Below Route Distributions are not attached to DRG Route Table; If you want to delete any of them, remove the TF file!!!")
            for remaining_rt_file in drg_routedistributionfiles[reg]:
                print(outdir + "/" + reg + "/" + remaining_rt_file)



def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." + os.path.join(dir, f))
            os.remove(os.path.join(dir, f))

# If input in cd3 file
def create_terraform_route(inputfile, outdir, prefix, config, modify_network=False):
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    routetablefiles = {}
    tempStr={}

    ADS = ["AD1", "AD2", "AD3"]
    fname = None

    # Get Hub VCN name and create route rules for LPGs as per Section VCN_PEERING

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('route-table-template')
    routerule = env.get_template("route-rule-template")


    def createLPGRouteRules(peering_dict):
        for left_vcn, value in peering_dict.items():
            right_vcns = value.split(",")
            left_vcn_tf_name = commonTools.check_tf_variable(left_vcn)

            for right_vcn in right_vcns:
                if (right_vcn == ""):
                    continue
                right_vcn = right_vcn.strip()
                right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)

                # Build rule for VCN on left
                lpg_name = vcns.vcn_lpg_names1[left_vcn][0]

                lpg_name = left_vcn + "_" + lpg_name
                lpg_name_tf_name = commonTools.check_tf_variable(lpg_name)

                vcns.vcn_lpg_names1[left_vcn].pop(0)
                tempStr['destination']= "oci_core_vcn."+right_vcn_tf_name+".cidr_block"
                tempStr['lpg_vcn_name']=lpg_name_tf_name
                tempStr['destination_type']="CIDR_BLOCK"
                tempStr['network_entity_id']="oci_core_local_peering_gateway."+lpg_name_tf_name+".id"
                ruleStr = routerule.render(tempStr)

                vcns.vcn_lpg_rules[left_vcn] = vcns.vcn_lpg_rules[left_vcn] + ruleStr

                # Build rule for VCNs on right
                lpg_name = vcns.vcn_lpg_names1[right_vcn][0]
                lpg_name = right_vcn + "_" + lpg_name
                lpg_name_tf_name = commonTools.check_tf_variable(lpg_name)

                vcns.vcn_lpg_names1[right_vcn].pop(0)
                tempStr['destination']= "oci_core_vcn."+left_vcn_tf_name+".cidr_block"
                tempStr['lpg_vcn_name']=lpg_name_tf_name
                tempStr['destination_type']="CIDR_BLOCK"
                tempStr['network_entity_id']="oci_core_local_peering_gateway."+lpg_name_tf_name+".id"
                ruleStr = routerule.render(tempStr)

                vcns.vcn_lpg_rules[right_vcn] = vcns.vcn_lpg_rules[right_vcn] + ruleStr

    def createVCNDRGRtTableString(compartment_var_name, vcn_with_drg, peering_dict, region, tempStr,hub):
        if (vcns.vcn_drgs[vcn_with_drg] == 'y'):
            drg_name = region + "_drg"
        elif (vcns.vcn_drgs[vcn_with_drg] != 'n'):
            drg_name = vcns.vcn_drgs[vcn_with_drg]
        elif (vcns.vcn_drgs[vcn_with_drg] == 'n' and hub==1):
            print("\ndrg_required column for VCN " + vcn_name + " marked as Hub should not be set to n!!\n")
            return

        drg_rt_name = ""
        if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
            with open(outdir + "/" + region + "/obj_names.safe") as f:
                for line in f:
                    if ("drginfo::::" + vcn_with_drg + "::::" + drg_name in line):
                        drg_rt_name = line.split("::::")[3].strip()

        if (drg_rt_name == ""):
            rt_display = "Route Table associated with DRG-" + drg_name
            rt_var = vcn_with_drg + "_" + rt_display
        # Route table associated with DRG inside VCN is not existing
        elif(drg_rt_name=="None"):
            return
        else:
            rt_var = vcn_with_drg + "_" + drg_rt_name
            rt_display = drg_rt_name

        rt_tf_name = commonTools.check_tf_variable(rt_var)

        outfile = outdir + "/" + region + "/" + rt_tf_name + "_routetable.tf"

        if(hub==0):
            if (not os.path.exists(outfile)):
                oname = open(outfile, "w")
                tempStr['rt_tf_name'] = rt_tf_name
                tempStr['compartment_tf_name'] = compartment_var_name
                tempStr['rt_display'] = rt_display
                tempStr['vcn_tf_name'] = commonTools.check_tf_variable(vcn_with_drg)
                #srcStr = "####ADD_NEW_ROUTE_RULES####" + rt_tf_name
                drgStr = template.render(tempStr)
                oname.write(drgStr)
                oname.close()
                print(outfile + " containing TF for Route Table has been created for region " + region)

        elif(hub==1):
            right_vcns = peering_dict[vcn_with_drg]
            right_vcns = right_vcns.split(",")

            drgRuleStr = ''
            for right_vcn in right_vcns:
                if right_vcn == '':
                    continue
                if right_vcn in vcns.spoke_vcn_names:
                    right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)
                    lpg_name = vcns.vcn_lpg_names2[vcn_with_drg][0]
                    lpg_name = hub_vcn_name + "_" + lpg_name
                    lpg_tf_name = commonTools.check_tf_variable(lpg_name)
                    hub_vcn_tf_name = commonTools.check_tf_variable(hub_vcn_name)
                    vcns.vcn_lpg_names2[vcn_with_drg].pop(0)

                    tempStr['rt_tf_name'] = rt_tf_name
                    tempStr['destination']= "oci_core_vcn."+right_vcn_tf_name+".cidr_block"
                    tempStr['lpg_vcn_name']=lpg_tf_name
                    tempStr['destination_type']="CIDR_BLOCK"
                    tempStr['network_entity_id']="oci_core_local_peering_gateway."+lpg_tf_name+".id"
                    temprule = routerule.render(tempStr)

                    if (os.path.exists(outfile)):
                        filedata = open(outfile, "r").read()
                        if temprule not in filedata:
                            srcStr = "####ADD_NEW_ROUTE_RULES####"+ rt_tf_name
                            tempstr = temprule + srcStr
                            filedata = filedata.replace(srcStr, tempstr)
                            oname = open(outfile, "w")
                            oname.write(filedata)
                            oname.close()

                    else:
                        oname = open(outfile, "w")
                        tempStr['rt_tf_name'] = rt_tf_name
                        tempStr['compartment_tf_name'] = compartment_var_name
                        tempStr['rt_display'] = rt_display
                        tempStr['vcn_tf_name'] =hub_vcn_tf_name
                        srcStr = "####ADD_NEW_ROUTE_RULES####"+ rt_tf_name
                        drgStr = template.render(tempStr)
                        temprule = temprule + srcStr
                        drgStr = drgStr.replace(srcStr,temprule)
                        oname.write(drgStr)
                        oname.close()
                        print(outfile + " containing TF for Route Table has been created for region " + region)

        if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
            routetablefiles[region].remove(rt_tf_name + "_routetable.tf")


    def createLPGRtTableString(compartment_var_name, hub_vcn_name, peering_dict, region, tempStr):
        # Retain exported route tables associated with exported LPGs
        if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
            with open(outdir + "/" + region + "/obj_names.safe") as f:
                for line in f:
                    if ("lpginfo::::" + hub_vcn_name in line):
                        lpg_rt_name = line.split("::::")[3].strip()
                        rt_var = hub_vcn_name + "_" + lpg_rt_name
                        rt_tf_name = commonTools.check_tf_variable(rt_var)
                        if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
                            routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

        # Create Rt table String for new spoke VCNs
        right_vcns = peering_dict[hub_vcn_name]
        right_vcns = right_vcns.split(",")

        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            temprule=''
            if (right_vcn in vcns.spoke_vcn_names):
                lpg_name = vcns.vcn_lpg_names3[hub_vcn_name][0]
                vcns.vcn_lpg_names3[hub_vcn_name].pop(0)
                # rt_var = hub_vcn_name + "_" + lpg_name + "_rt"
                rt_display = "Route Table associated with LPG-""" + lpg_name
                rt_var = hub_vcn_name + "_" + rt_display
                rt_tf_name = commonTools.check_tf_variable(rt_var)
                hub_vcn_tf_name = commonTools.check_tf_variable(hub_vcn_name)

                outfile = outdir + "/" + region + "/" + rt_tf_name + "_routetable.tf"
                oname = open(outfile, "w")

                tempStr['rt_display']= rt_display
                tempStr['rt_var'] = rt_var
                tempStr['rt_tf_name'] = rt_tf_name
                tempStr['vcn_tf_name'] = hub_vcn_tf_name
                tempStr['compartment_tf_name'] = compartment_var_name

                lpgStr = template.render(tempStr)
                srcStr = "####ADD_NEW_ROUTE_RULES####"+ rt_tf_name
                drg_name = ""
                if (vcns.vcn_drgs[hub_vcn_name] == 'y'):
                    # drg_name = hub_vcn_name + "_drg"
                    drg_name = region + "_drg"
                elif (vcns.vcn_drgs[hub_vcn_name] != 'n'):
                    drg_name = vcns.vcn_drgs[hub_vcn_name]

                if (drg_name != ""):
                    drg_tf_name = commonTools.check_tf_variable(drg_name)
                    for drg_destination in vcnInfo.onprem_destinations:
                        if (drg_destination != ''):
                            tempStr['vcn_tf_name'] = ''
                            tempStr['destination'] = "\"" + drg_destination + "\""
                            tempStr['destination_type'] = "CIDR_BLOCK"
                            tempStr['network_entity_id'] = "oci_core_drg." + drg_tf_name + ".id"
                            temprule = temprule + routerule.render(tempStr)

                temprule = srcStr + temprule
                lpgStr = lpgStr.replace(srcStr,temprule)
                #print(lpgStr)
                oname.write(lpgStr)
                oname.close()
                print(outfile + " containing TF for LPG Route Table has been created for region " + region)
                if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
                    routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

    def prepareSGWRuleStr(sgw_name,destination,configure_sgw,tempStr,data):
        sgw_tf_name = vcn_name + "_" + sgw_name
        sgw_tf_name = commonTools.check_tf_variable(sgw_tf_name)
        if (configure_sgw=="all_services"):
            destination = "contains(split(\"-\",data.oci_core_services.oci_services.services.0.cidr_block),\"all\") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block"
        elif (configure_sgw=="object_storage"):
            destination = "contains(split(\"-\",data.oci_core_services.oci_services.services.0.cidr_block),\"objectstorage\") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block"
        tempStr['destination'] = destination
        tempStr['sgw_tf_name'] = sgw_tf_name
        tempStr['configure_sgw'] = configure_sgw
        tempStr['destination_type'] = "SERVICE_CIDR_BLOCK"
        tempStr['network_entity_id'] = "oci_core_service_gateway."+sgw_tf_name+".id"
        rem_keys=['vcn_tf_name','drg_tf_name','ngw_tf_name','igw_tf_name','lpg_tf_name']
        [tempStr.pop(key) for key in rem_keys if key in tempStr]
        data = data + routerule.render(tempStr)
        return data

    def prepareNGWRuleStr(ngw_name,tempStr):
        ngw_tf_name = vcn_name + "_" + ngw_name
        ngw_tf_name = commonTools.check_tf_variable(ngw_tf_name)
        data = ""
        for ngw_destination in vcnInfo.ngw_destinations:
            if (ngw_destination != ''):
                tempStr['destination'] = "\""+ngw_destination+"\""
                tempStr['ngw_tf_name'] = ngw_tf_name
                tempStr['destination_type'] = "CIDR_BLOCK"
                tempStr['network_entity_id'] = "oci_core_nat_gateway." + ngw_tf_name + ".id"
                rem_keys = ['vcn_tf_name', 'drg_tf_name', 'configure_sgw', 'igw_tf_name', 'lpg_tf_name']
                [tempStr.pop(key) for key in rem_keys if key in tempStr]
                data = data + routerule.render(tempStr)
        return data

    def prepareIGWRuleStr(igw_name,tempStr):
        igw_tf_name = vcn_name + "_" + igw_name
        igw_tf_name = commonTools.check_tf_variable(igw_tf_name)
        data = ""
        for igw_destination in vcnInfo.igw_destinations:
            if (igw_destination != ''):
                tempStr['igw_tf_name'] = igw_tf_name
                tempStr['destination'] = "\""+igw_destination+"\""
                tempStr['destination_type'] = "CIDR_BLOCK"
                tempStr['network_entity_id'] = "oci_core_internet_gateway." + igw_tf_name + ".id"
                rem_keys = ['vcn_tf_name', 'drg_tf_name', 'configure_sgw', 'ngw_tf_name', 'lpg_tf_name']
                [tempStr.pop(key) for key in rem_keys if key in tempStr]
                data = data + routerule.render(tempStr)
        return data

    def prepareOnpremRuleStr(drg_name,tempStr):
        data = ""
        v_list_having_drg=[]
        for key in vcns.vcns_having_drg.keys():
            v_list_having_drg.append(key[0])
        if vcns.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'hub' or vcn_name in v_list_having_drg:
            drg_tf_name = commonTools.check_tf_variable(drg_name)
            for drg_destination in vcnInfo.onprem_destinations:
                if (drg_destination != ''):
                    tempStr['drg_tf_name'] = drg_tf_name
                    tempStr['destination'] = "\""+drg_destination+"\""
                    tempStr['destination_type'] = "CIDR_BLOCK"
                    tempStr['network_entity_id'] = "oci_core_drg."+ drg_tf_name +".id"
                    rem_keys = ['vcn_tf_name', 'igw_tf_name', 'configure_sgw', 'ngw_tf_name', 'lpg_tf_name']
                    [tempStr.pop(key) for key in rem_keys if key in tempStr]
                    data = data + routerule.render(tempStr)

        if vcns.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'spoke':
            """for left_vcn, value in peering_dict.items():
                right_vcns = value.split(",")
                for right_vcn in right_vcns:
                    if (right_vcn == vcn_name):
                        hub_vcn_name = left_vcn
                        break
    
            lpg_name = vcn_name + "_" + hub_vcn_name + "_lpg"""""
            lpg_name = vcns.vcn_lpg_names[vcn_name][0]
            lpg_name = vcn_name + "_" + lpg_name
            lpg_tf_name = commonTools.check_tf_variable(lpg_name)
            for drg_destination in vcnInfo.onprem_destinations:
                if (drg_destination != ''):
                    tempStr['lpg_tf_name'] = lpg_tf_name
                    tempStr['destination'] = "\""+drg_destination+"\""
                    tempStr['destination_type'] = "CIDR_BLOCK"
                    tempStr['network_entity_id'] = "oci_core_local_peering_gateway."+ lpg_tf_name +".id"
                    rem_keys = ['vcn_tf_name', 'igw_tf_name', 'configure_sgw', 'ngw_tf_name', 'drg_tf_name']
                    [tempStr.pop(key) for key in rem_keys if key in tempStr]
                    data = data + routerule.render(tempStr)
        return data

    def prepareVCNPeerRuleStr():
        data = ""
        data = data + vcns.vcn_lpg_rules[vcn_name]
        return data

    def processSubnet(tempStr):

        rt_name = tempStr['route_table_name']
        AD = tempStr['availability_domain']
        subnet =  tempStr['cidr_block']
        configure_sgw = tempStr['configure_sgw_route'].strip()
        configure_ngw = tempStr['configure_ngw_route'].strip()
        configure_igw = tempStr['configure_igw_route'].strip()
        configure_onprem = tempStr['configure_onprem_route'].strip()
        configure_vcnpeering = tempStr['configure_vcnpeering_route'].strip()

        # Route Table name specifiied as 'n' - dont create any routetable
        if (rt_name == "n"):
            return

        if (AD.strip().lower() != 'regional'):
            AD = AD.strip().upper()
            ad = ADS.index(AD)
            ad_name_int = ad + 1
            ad_name = str(ad_name_int)
        else:
            ad_name = ""

        tempStr['ad_name'] = ad_name

        # check if subnet codr needs to be attached
        if (vcnInfo.subnet_name_attach_cidr == 'y'):
            if (str(ad_name) != ''):
                name1 = rt_name + "-ad" + str(ad_name)
            else:
                name1 = rt_name
            display_name = name1 + "-" + subnet
        else:
            display_name = rt_name

        tempStr['display_name'] = display_name

        vcn_tf_name=commonTools.check_tf_variable(tempStr['vcn_name'])
        subnet_tf_name = tempStr['vcn_name']+"_"+display_name

        subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)

        tempStr['vcn_tf_name'] = vcn_tf_name
        tempStr['subnet_tf_name'] = subnet_tf_name

        #Create Route Table File Name
        outfile = outdir + "/" + region + "/" + subnet_tf_name + "_routetable.tf"
        if (subnet_tf_name + "_routetable.tf" in routetablefiles[region]):
            routetablefiles[region].remove(subnet_tf_name + "_routetable.tf")

        # Get VCN component names
        vcn_drg = vcns.vcn_drgs[vcn_name]
        drg_name = ""
        if (vcn_drg == "y"):
            # drg_name = vcn_name + "_drg"
            drg_name = region + "_drg"
        elif (vcn_drg != "n"):
            drg_name = vcn_drg
        tempStr['drg_name'] = drg_name

        vcn_igw = vcns.vcn_igws[vcn_name]
        igw_name = ""
        if (vcn_igw == "y"):
            igw_name = vcn_name + "_igw"
        elif (vcn_igw != "n"):
            igw_name = vcn_igw
        tempStr['igw_name'] = igw_name

        vcn_ngw = vcns.vcn_ngws[vcn_name]
        ngw_name = ""
        if (vcn_ngw == "y"):
            ngw_name = vcn_name + "_ngw"
        elif (vcn_ngw != "n"):
            ngw_name = vcn_ngw
        tempStr['ngw_name'] = ngw_name

        vcn_sgw = vcns.vcn_sgws[vcn_name]
        sgw_name = ""
        if (vcn_sgw == "y"):
            sgw_name = vcn_name + "_sgw"
        elif (vcn_sgw != "n"):
            sgw_name = vcn_sgw
        tempStr['sgw_name'] = sgw_name

        # Prepare rule str
        data=''
        data_sgw = prepareSGWRuleStr(sgw_name,destination,configure_sgw,tempStr,data)
        data_ngw = prepareNGWRuleStr(ngw_name,tempStr)
        data_igw = prepareIGWRuleStr(igw_name,tempStr)
        data_onprem = prepareOnpremRuleStr(drg_name,tempStr)
        data_vcnpeer = prepareVCNPeerRuleStr()

        dataStr = """#SubnetRules Start \n"""
        if configure_sgw.strip() == 'all_services' or configure_sgw.strip() == 'object_storage' and vcn_sgw != 'n':
            dataStr = dataStr + data_sgw
        if configure_ngw.strip() == 'y' and vcn_ngw != 'n':
            dataStr = dataStr + data_ngw
        if configure_igw.strip() == 'y' and vcn_igw != 'n':
            dataStr = dataStr + data_igw
        if configure_onprem.strip() == 'y':
            v_list_having_drg = []
            for key in vcns.vcns_having_drg.keys():
                v_list_having_drg.append(key[0])
            if (vcn_name in vcns.hub_vcn_names or vcn_name in vcns.spoke_vcn_names or vcn_name in v_list_having_drg):
                dataStr = dataStr + data_onprem
        if (configure_vcnpeering.strip() == 'y' and vcns.vcn_lpg_rules[vcn_name] != ''):
            dataStr = dataStr + data_vcnpeer
        dataStr = dataStr + """
                    #SubnetRules End
                    """

        # Either same route table name is used for subsequent subnets or Modify Network is set to true - Add rules modified to y
        # and remove rules modified to n
        if (os.path.exists(outfile)):  # and modify_network == 'true'):
            newlines = []
            with open(outfile, 'r') as file:
                copy = True
                for line in file:
                    if line.strip() == "#SubnetRules Start":
                        copy = False
                        newlines.append(dataStr)
                        continue
                    elif (line.strip() == "#SubnetRules End"):
                        copy = True
                        continue
                    elif copy:
                        newlines.append(line)
                file.close()
            with open(outfile, 'w') as file:
                file.writelines(newlines)
                file.close()
            return

        # New routetable
        oname = open(outfile, "w")
        rt_tf_name = subnet_tf_name
        tempStr['rt_tf_name'] = rt_tf_name
        tempStr['vcn_tf_name'] = vcn_tf_name
        tempStr['rt_display'] = display_name
        tempStr['compartment_tf_name'] = compartment_var_name
        srcStr = "####ADD_NEW_ROUTE_RULES####"+ rt_tf_name
        dataStr = dataStr + "\n" +"    "+ srcStr
        data_res = template.render(tempStr)
        tempStr = data_res.replace(srcStr, dataStr)

        oname.write(tempStr)
        oname.close()
        print(outfile + " containing TF for routerules has been created for region " + region)


    # If input is CD3 excel file
    if ('.xls' in filename):
        vcnInfo = parseVCNInfo(filename)
        vcns = parseVCNs(filename)

        # Purge existing routetable files
        if not modify_network:
            for reg in ct.all_regions:
                routetablefiles.setdefault(reg, [])
                purge(outdir + "/" + reg, "_routetable.tf")
        # Get existing list of route table files
        if modify_network:
            for reg in ct.all_regions:
                routetablefiles.setdefault(reg, [])
                lisoffiles = os.listdir(outdir + "/" + reg)
                for file in lisoffiles:
                    if "_routetable.tf" in file:
                        routetablefiles[reg].append(file)
        if (vcnInfo.onprem_destinations[0] == ""):
            print("\nonprem_destinations field is empty in VCN Info Sheet.. It will create empty route tables!!\n")



        # Read cd3 using pandas dataframe
        df, col_headers = commonTools.read_cd3(filename, "Subnets")

        df = df.dropna(how='all')
        df = df.reset_index(drop=True)

        # temporary dictionary1, dictionary2
        tempStr = {}
        tempdict = {}
        compartment_var_name=''
        destination = ''

        # List of the column headers
        dfcolumns = df.columns.values.tolist()

        # Create LPG Rules
        createLPGRouteRules(vcns.peering_dict)

        for i in df.index:

            # Get subnet data
            region = str(df.loc[i,'Region'])

            if (region in commonTools.endNames):
                break

            compartment_var_name = str(df.loc[i, 'Compartment Name'])
            region = region.strip().lower()
            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)
            vcn_name = str(df['VCN Name'][i]).strip()
            if (vcn_name.strip() not in vcns.vcn_names):
                print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
                exit(1)

            if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                    df.loc[i, 'VCN Name']).lower() == 'nan' or
                    str(df.loc[i, 'Subnet Name']).lower() == 'nan' or str(df.loc[i, 'CIDR Block']).lower() == 'nan' or str(
                        df.loc[i, 'Availability Domain(AD1|AD2|AD3|Regional)']).lower() == 'nan' or
                    str(df.loc[i, 'Type(private|public)']).lower() == 'nan' or str(
                        df.loc[i, 'Configure SGW Route(n|object_storage|all_services)']).lower() == 'nan' or str(df.loc[i, 'Configure NGW Route(y|n)']).lower() == 'nan' or
                    str(df.loc[i, 'Configure IGW Route(y|n)']).lower() == 'nan' or str(df.loc[i, 'Configure OnPrem Route(y|n)']).lower() == 'nan' or str(df.loc[i, 'Configure VCNPeering Route(y|n)']).lower() == 'nan'):
                print("\nERROR!!! Column Values (except DHCP Option Name, Route Table Name, Seclist Name or DNS Label) or Rows cannot be left empty in Subnets sheet in CD3..Exiting!")
                exit(1)

            for columnname in dfcolumns:
                # Column value
                columnvalue = str(df[columnname][i]).strip()

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Check for multivalued columns
                tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

                # Process Freeform and Defined Tags
                if columnname.lower() in commonTools.tagColumns:
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

                if columnname == 'Availability Domain(AD1|AD2|AD3|Regional)':
                    columnname = 'availability_domain'
                    tempdict = {'availability_domain' : columnvalue }

                if columnname == 'Compartment Name':
                    compartment_var_name = columnvalue
                    compartment_var_name = compartment_var_name.strip()
                    # Added to check if compartment name is compatible with TF variable name syntax
                    compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                    tempdict = {'compartment_tf_name' : compartment_var_name }

                if columnname == 'Configure SGW Route(n|object_storage|all_services)':
                    columnname = 'configure_sgw_route'
                    columnvalue = columnvalue.lower().strip()
                    tempdict = { 'configure_sgw_route' : columnvalue }

                if columnname == 'Configure NGW Route(y|n)':
                    columnname = 'configure_ngw_route'
                    columnvalue = columnvalue.lower().strip()
                    tempdict = {'configure_ngw_route' : columnvalue }

                if columnname == 'Configure IGW Route(y|n)':
                    columnname = 'configure_igw_route'
                    columnvalue = columnvalue.lower().strip()
                    tempdict = {'configure_igw_route' : columnvalue }

                if columnname == 'Configure OnPrem Route(y|n)':
                    columnname = 'configure_onprem_route'
                    columnvalue = columnvalue.lower().strip()
                    tempdict = {'configure_onprem_route' : columnvalue }

                if columnname == 'Configure VCNPeering Route(y|n)':
                    columnname = 'configure_vcnpeering_route'
                    columnvalue = columnvalue.lower().strip()
                    tempdict = {'configure_vcnpeering_route' : columnvalue }

                if columnname == 'Route Table Name':
                    if str(columnvalue).lower().strip() != 'nan' and str(columnvalue).lower().strip() != '':
                        rt_name = columnvalue.strip()
                        tempdict = {'route_table_name': rt_name}
                    else:
                        rt_name = str(df.loc[i,'Subnet Name']).strip()
                        tempdict = {'route_table_name': rt_name}

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = columnvalue
                tempStr.update(tempdict)

            processSubnet(tempStr)


        #Create Route Table associated with DRG(in VCN) for each VCN attached to DRG
        for key in vcns.vcns_having_drg.keys():
            vcn=key[0]
            if(vcn in vcns.hub_vcn_names):
                continue
            compartment_var_name = vcns.vcn_compartment[vcn]

            # Added to check if compartment name is compatible with TF variable name syntax
            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

            # String for Route Table Assocaited with DRG
            r = vcns.vcn_region[vcn].strip().lower()
            createVCNDRGRtTableString(compartment_var_name, vcn, vcns.peering_dict, r, tempStr,hub=0)

        # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
        for hub_vcn_name in vcns.hub_vcn_names:
            compartment_var_name = vcns.vcn_compartment[hub_vcn_name]

            # Added to check if compartment name is compatible with TF variable name syntax
            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

            # String for Route Table Assocaited with DRG
            r = vcns.vcn_region[hub_vcn_name].strip().lower()
            createVCNDRGRtTableString(compartment_var_name, hub_vcn_name, vcns.peering_dict, r, tempStr,hub=1)

        # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
        for hub_vcn_name in vcns.hub_vcn_names:
            compartment_var_name = vcns.vcn_compartment[hub_vcn_name]
            # Added to check if compartment name is compatible with TF variable name syntax
            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

            r = vcns.vcn_region[hub_vcn_name].strip().lower()
            # String for Route Table Associated with each LPG in hub VCN peered with Spoke VCN
            createLPGRtTableString(compartment_var_name, hub_vcn_name, vcns.peering_dict, r, tempStr)

        # remove any extra route table files (not part of latest cd3)
        RTs_in_objnames = []
        for reg in ct.all_regions:
            # Get any route tables from objnames.safe
            if (os.path.exists(outdir + "/" + reg + "/obj_names.safe")):
                with open(outdir + "/" + reg + "/obj_names.safe") as f:
                    for line in f:
                        if (line != "\n"):
                            names = line.split("::::")
                            file_name = names[1] + "_" + commonTools.check_tf_variable(names[3].strip()) + "_routetable.tf"
                            RTs_in_objnames.append(file_name)

            if (len(routetablefiles[reg]) != 0):
                print("\nATTENION!!! Below RouteTables are not attached to any subnet or DRG and LPG; If you want to delete any of them, remove the TF file!!!")
                for remaining_rt_file in routetablefiles[reg]:
                    if (remaining_rt_file in RTs_in_objnames):
                        continue
                    print(outdir + "/" + reg + "/" + remaining_rt_file)
                # print("Removing "+outdir+"/"+reg+"/"+remaining_rt_file)
                # os.remove(outdir+"/"+reg+"/"+remaining_rt_file)
                # routetablefiles[reg].remove(remaining_rt_file)

    if (fname != None):
        fname.close()

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_route(args.inputfile, args.outdir, args.prefix, args.config, args.modify_network)
    create_terraform_drg_route(args.inputfile, args.outdir, args.prefix, args.config, args.modify_network)

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
import re
import os
from pathlib import Path
sys.path.append(os.getcwd() + "/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


######
# Required Inputs-CD3 excel file, Config file, Modify Network AND outdir
######

def read_infile_data(modifiedroutetableStr, reg, start, end):
    modifiedroutetableStr[reg] = re.sub(start+'.*?'+end, '',modifiedroutetableStr[reg] , flags=re.DOTALL)
    modifiedroutetableStr[reg] = re.sub('\n\n+','\n\n',modifiedroutetableStr[reg])
    filedata = modifiedroutetableStr[reg]
    return modifiedroutetableStr[reg], filedata

def recursive_process_filedata(common_rt, modifiedroutetableStr, reg, processed_rt, count):

    for rt in common_rt:
        if reg in rt:
            # If the route table in auto.tfvars is in exported RouteRules sheet but absent in Subnets sheet, copy it.
            if rt in modifiedroutetableStr[reg] and rt not in processed_rt:
                start = "# Start of " + rt + " #"
                end = "# End of " + rt + " #"
                modifiedroutetableStr[reg],filedata = read_infile_data(modifiedroutetableStr, reg, start, end)
                common_rt.pop(common_rt.index(rt))
                recursive_process_filedata(common_rt, modifiedroutetableStr, reg, processed_rt, count)
                count = count + 1
            else:
                continue
            processed_rt.append(rt)
    return modifiedroutetableStr[reg]

def merge_or_generate_route_rule(reg, tempStr, modifiedroutetableStr,routetableStr, start_rule, data, modify_network, routerule, gateway):
    replace_str = "####ADD_NEW_" + gateway + "_RULES " + reg.lower() + "_" + tempStr['rt_tf_name'] + " ####"
    if modify_network:
        end_rule = "## End Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr[
            'network_entity_id'] + "_" + tempStr['destination']
        if start_rule in modifiedroutetableStr[reg]:  # If the rule is present in filedata

            if start_rule not in routetableStr[reg]:  # But the rule is not in routetableStr then add it to filedata
                if routerule.render(tempStr).strip() != '':
                    if reg != 'lpg_route_rules':
                        modifiedroutetableStr[reg] = re.sub(start_rule + '.*?' + end_rule,
                                                            routerule.render(tempStr).strip(),
                                                            modifiedroutetableStr[reg], flags=re.DOTALL)
                    else:
                        modifiedroutetableStr[reg] = re.sub(start_rule + '.*?' + end_rule,
                                                            routerule.render(tempStr,lpg_route_rules=True, region='lpg_route_rules').strip(),
                                                            modifiedroutetableStr[reg], flags=re.DOTALL)
        else:
            if start_rule not in routetableStr[reg]:  # If the rule is not present in routetableStr and filedata
                if replace_str in modifiedroutetableStr[reg]:  # But the table is present in filedata
                    if routerule.render(tempStr).strip() != '':
                        if reg != 'lpg_route_rules':
                            modifiedroutetableStr[reg] = modifiedroutetableStr[reg].replace(replace_str, routerule.render(tempStr) + "\n" + replace_str)
                        else:
                            modifiedroutetableStr[reg] = modifiedroutetableStr[reg].replace(replace_str,routerule.render(tempStr,lpg_route_rules=True, region='lpg_route_rules') + "\n" + replace_str)
                else:  # Else if the Table and rule are not present in filedata and routetableStr
                    if reg != 'lpg_route_rules':
                        data = data + routerule.render(tempStr)
                    else:
                        data = routerule.render(tempStr,lpg_route_rules=True, region='lpg_route_rules')
    else:
        if start_rule not in routetableStr[reg]:
            if reg != 'lpg_route_rules':
                data = data + routerule.render(tempStr)
            else:
                data = routerule.render(tempStr, lpg_route_rules=True, region='lpg_route_rules')
    return data

# Execution of the code begins here for drg routes
def create_terraform_drg_route(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy,network_connectivity_in_setupoci, modify_network):
    filename = inputfile
    drgv2 = parseDRGs(filename)
    common_rt = []

    drg_routetablefiles = {}
    drg_routedistributionfiles = {}
    tempStr = {}
    region_rt_name = ''

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    drg_rt_template = env.get_template('drg-route-table-template')
    drg_rd_template = env.get_template('drg-route-distribution-template')
    drg_rd_stmt_template = env.get_template('drg-route-distribution-statement-template')
    drg_distribution_auto_tfvars_template = "_drg-distributions.auto.tfvars"
    drg_rt_auto_tfvars_filename = "_drg-routetables.auto.tfvars"

    tempSkeletonDRGRouteTable = {}
    tempSkeletonDRGDistribution = {}
    tempSkeletonDRGDistributionStmt = {}
    modifiedroutetableStr = {}

    drg_rt = {}
    drg_rd = {}
    drg_rd_stmt = {}
    drgrts_from_DRGRouteRulesInOCI_sheet = []

    # If input is CD3 excel file
    if ('.xls' in filename):

        df, col_headers = commonTools.read_cd3(filename, "DRGs")
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)


        # Read cd3 using pandas dataframe
        dfdrgroutetable, col_headers = commonTools.read_cd3(filename, "DRGRouteRulesinOCI")

        dfdrgroutetable = dfdrgroutetable.dropna(how='all')
        dfdrgroutetable = dfdrgroutetable.reset_index(drop=True)

        # Start processing each RT
        for i in dfdrgroutetable.index:
            region = str(dfdrgroutetable['Region'][i]).strip()
            if (region in commonTools.endNames):
                break

            drgrt_tf_from_rtRulesInOCI_sheet_name = "#"+commonTools.check_tf_variable(dfdrgroutetable.loc[i, 'Region']).lower()+"_"+commonTools.check_tf_variable(dfdrgroutetable.loc[i, 'DRG Name'])+"_"+commonTools.check_tf_variable(dfdrgroutetable.loc[i, 'DRG RT Name'])+"#"
            if drgrt_tf_from_rtRulesInOCI_sheet_name not in drgrts_from_DRGRouteRulesInOCI_sheet:
                drgrts_from_DRGRouteRulesInOCI_sheet.append(drgrt_tf_from_rtRulesInOCI_sheet_name)

        # Rename the .txt files in outdir to .tf; Generate the Skeleton Templates
        for reg in ct.all_regions:
            drg_rt[reg] = ''
            drg_rd[reg] = ''
            drg_rd_stmt[reg] = ''
            modifiedroutetableStr[reg] = ''
            tempSkeletonDRGRouteTable[reg] = ''

            rtfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + drg_rt_auto_tfvars_filename

            if modify_network:
                # Read the file if it exists
                if os.path.exists(rtfile):
                    # Read the contents of file in outdir
                    with open(rtfile, 'r+') as file:
                        filedata = file.read()
                    file.close()

                    # for the RTs in RouteRulesInOCI sheet, see if the start string is there in filedata, if yes, retain it, if no delete the remaining information.
                    for drgrts in drgrts_from_DRGRouteRulesInOCI_sheet:
                        if "# Start of " + drgrts + " #" in filedata and "# Start of " + drgrts + " #" not in modifiedroutetableStr[reg]:
                            modifiedroutetableStr[reg] = ct.copy_data_from_file(rtfile, drgrts, modifiedroutetableStr[reg])
                    tempSkeletonDRGRouteTable[reg] = drg_rt_template.render(count=0, region=reg, skeleton=True)
                    srcStr = "###Add route tables here for " + reg.lower() + " ###"
                    if modifiedroutetableStr[reg] != '':
                        modifiedroutetableStr[reg] = tempSkeletonDRGRouteTable[reg].replace(srcStr, modifiedroutetableStr[reg] + "\n" + srcStr)
                else:
                    modifiedroutetableStr[reg] = ''

        # Option Modify = False
        # Purge existing routetable files
        for reg in ct.all_regions:

            if not modify_network:
                drg_routetablefiles.setdefault(reg, [])
                drg_routedistributionfiles.setdefault(reg, [])
                purge(outdir + "/" + reg + "/" + service_dir, prefix + drg_distribution_auto_tfvars_template)
                purge(outdir + "/" + reg + "/" + service_dir, prefix + drg_rt_auto_tfvars_filename)

        # List of the column headers
        dfcolumns = df.columns.values.tolist()
        tempStr = {}
        tempdict = {}

        for i in df.index:
            drg_rt_dstrb_tf_name = ''
            drg_rt_dstrb_res_name = ''
            region = str(df.loc[i, 'Region']).strip()
            vcn_connectivity_in_excel = ""
            if str(df.loc[i, 'Attached To']).lower().startswith("rpc"):
                vcn_connectivity_in_excel = "connectivity"
            elif str(df.loc[i, 'Attached To']).lower().startswith("vcn"):
                vcn_connectivity_in_excel = "vcn"

            if (region in commonTools.endNames):
                break

            DRG_RT = str(df.loc[i, 'DRG RT Name']).strip()
            DRG_RD = str(df.loc[i, 'Import DRG Route Distribution Name']).strip()

            #Greenfield workflow
            if not non_gf_tenancy:
                # skip RPC rows while create network
                if not modify_network and vcn_connectivity_in_excel.lower().startswith('connectivity'):
                    continue

                # skip RPC rows while running option modify network
                #if modify_network and network_connectivity_in_setupoci == 'network' and vcn_connectivity_in_excel.lower().startswith('connectivity'):
                #    continue

                # skip VCN rows while running option Create Connectivity
        #        if modify_network and network_connectivity_in_setupoci == 'connectivity' and vcn_connectivity_in_excel.startswith('vcn'):
        #            continue

            # Dont create any route table or route distribution name if left empty - attach Auto Generated ones
            if (DRG_RT.lower() == 'nan' and DRG_RD.lower() == 'nan'):  # and DRG_RD_stmts.lower()=='nan'):
                continue

            # Dont create any route table or route distribution name if using Auto Generated ones
            if (DRG_RT in commonTools.drg_auto_RTs and DRG_RD in commonTools.drg_auto_RDs):
                continue
            # Dont create any oute table or route distribution name if OCID is goven in DRG RT Name
            if ("ocid1.drgroutetable.oc" in DRG_RT):
                continue

            region = region.strip().lower()
            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            drg_name = ''

            for columnname in dfcolumns:
                # Column value
                if (columnname != 'Rule Description'):
                    columnvalue = str(df[columnname][i]).strip()
                else:
                    columnvalue = str(df[columnname][i])

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Process Freeform and Defined Tags
                if columnname.lower() in commonTools.tagColumns:
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

                if columnname == "DRG Name":
                    drg_name = columnvalue
                    tempdict['drg_tf_name'] = commonTools.check_tf_variable(columnvalue)

                if columnname == "DRG RT Name":
                    tempdict['display_name'] = columnvalue
                    drg_rt_name = drg_name + "_" + columnvalue
                    drg_rt_tf_name = commonTools.check_tf_variable(drg_rt_name)
                    tempdict['drg_rt_tf_name'] = drg_rt_tf_name

                if columnname == 'Import DRG Route Distribution Name':
                    if (columnvalue.lower() != ''):
                        drg_rt_dstrb_name = drg_name + "_" + columnvalue
                        drg_rt_dstrb_tf_name = commonTools.check_tf_variable(drg_rt_dstrb_name)
                        drg_rt_dstrb_res_name = drg_rt_dstrb_tf_name

                    tempdict['drg_rt_dstrb_tf_name'] = drg_rt_dstrb_tf_name
                    tempdict['drg_rt_dstrb_res_name'] = drg_rt_dstrb_res_name
                    tempdict['dstrb_display_name'] = columnvalue
                    tempdict['distribution_type'] = "IMPORT"
                    tempStr.update(tempdict)

                # Check for multivalued columns
                if (columnname == 'Import DRG Route Distribution Statements'):
                    columnvalues = columnvalue.split("\n")
                    k = 1
                    for cv in columnvalues:
                        if (cv != ''):
                            tempdict = commonTools.check_multivalues_columnvalue(cv, columnname, tempdict)
                            tempStr.update(tempdict)
                            tempStr['statements'] = tempStr['import_drg_route_distribution_statements']
                            tempStr['drg_rt_dstrb_statement_tf_name'] = drg_rt_dstrb_tf_name + "_statement" + str(k)
                            k = k + 1
                            drg_rd_stmt[region] = drg_rd_stmt[region] + drg_rd_stmt_template.render(tempStr)

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = columnvalue
                tempStr.update(tempdict)

            region_rt_name = "#"+region.lower() + "_" + tempStr['drg_rt_tf_name']+"#"
            tempStr['region_rt_name'] = region_rt_name

            if (DRG_RT != 'nan' and DRG_RT not in commonTools.drg_auto_RTs and region_rt_name not in common_rt):
                    drg_rt[region] = drg_rt[region] + drg_rt_template.render(tempStr)

            if (DRG_RD.lower() != 'nan' and DRG_RD not in commonTools.drg_auto_RDs):
                drg_rd[region] = drg_rd[region] + drg_rd_template.render(tempStr)

            if region_rt_name not in common_rt:
                common_rt.append(region_rt_name)

    for reg in ct.all_regions:

        tempSkeletonDRGRouteTable[reg] = ''
        tempSkeletonDRGDistribution[reg] = ''
        tempSkeletonDRGDistributionStmt[reg] = ''

        tempSkeletonDRGDistribution[reg] = drg_rd_template.render(tempStr, skeleton=True, region=reg)
        tempSkeletonDRGDistributionStmt[reg] = drg_rd_stmt_template.render(tempStr, skeleton=True, region=reg)

        # Create Skeleton Template
        rtdistribution = outdir + "/" + reg + "/" + service_dir + "/" + prefix + drg_distribution_auto_tfvars_template
        rtfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + drg_rt_auto_tfvars_filename

        if not modify_network:

            tempSkeletonDRGRouteTable[reg] = drg_rt_template.render(tempStr, skeleton=True, region=reg)

            if drg_rt[reg] != '':
                srcStr = "###Add route tables here for " + reg.lower() + " ###"
                tempSkeletonDRGRouteTable[reg] = tempSkeletonDRGRouteTable[reg].replace(srcStr, drg_rt[reg] + "\n" + srcStr)

        # If Modify Network
        else:
            skeletonStr = "###Add route tables here for "+reg.lower()+" ###"
            # Option if Modify Network is TRUE
            processed_rt = []

            modifiedroutetableStr[reg] = recursive_process_filedata(common_rt, modifiedroutetableStr, reg, processed_rt,count=0)

            if modifiedroutetableStr[reg] == '':
                tempSkeletonDRGRouteTable[reg] = drg_rt_template.render(tempStr, skeleton=True, region=reg)

            if drg_rt[reg] != '':
                if modifiedroutetableStr[reg] != '':
                    tempSkeletonDRGRouteTable[reg] = modifiedroutetableStr[reg].replace(skeletonStr, drg_rt[reg] + "\n" + skeletonStr)
                else:
                    tempSkeletonDRGRouteTable[reg] = tempSkeletonDRGRouteTable[reg].replace(skeletonStr, drg_rt[reg] + "\n" + skeletonStr)

        if drg_rd[reg] != '':
            srcStr="###Add DRG Distribution here for "+reg.lower()+" ###"
            tempSkeletonDRGDistribution[reg] = tempSkeletonDRGDistribution[reg].replace(srcStr, drg_rd[reg] + "\n" + srcStr)
        if drg_rd_stmt[reg] != '':
            srcStr="###Add DRG Distribution Statement here for "+reg.lower()+" ###"
            tempSkeletonDRGDistributionStmt[reg] = tempSkeletonDRGDistributionStmt[reg].replace(srcStr, drg_rd_stmt[reg] + "\n" + srcStr)

        tempSkeletonDRGDistribution[reg] = tempSkeletonDRGDistribution[reg] + tempSkeletonDRGDistributionStmt[reg]

        if drg_rt[reg] != '' :
            if (os.path.exists(rtfile)):
                resource = 'DRGRTs'
                srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                commonTools.backup_file(srcdir, resource, prefix + drg_rt_auto_tfvars_filename)
            tempSkeletonDRGRouteTable[reg] = "".join([s for s in tempSkeletonDRGRouteTable[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname_rt = open(rtfile, "w+")
            print("Writing to..." + str(rtfile))
            oname_rt.write(tempSkeletonDRGRouteTable[reg])
            oname_rt.close()
        else:
            if drg_rt[reg] == '':
                if (os.path.exists(rtfile)):
                    resource = 'DRGRTs'
                    srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                    commonTools.backup_file(srcdir, resource, prefix + drg_rt_auto_tfvars_filename)

        if drg_rd_stmt[reg] != '' or drg_rd[reg] != '':
            if (os.path.exists(rtdistribution)):
                resource = 'DRGRTs'
                srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                commonTools.backup_file(srcdir, resource, prefix + drg_distribution_auto_tfvars_template)
            tempSkeletonDRGDistribution[reg] = "".join([s for s in tempSkeletonDRGDistribution[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname_drg_dis = open(rtdistribution, "w+")
            print("Writing to..." + str(rtdistribution))
            oname_drg_dis.write(tempSkeletonDRGDistribution[reg])
            oname_drg_dis.close()
        else:
            if (drg_rd_stmt[reg] == '' and drg_rd[reg] == ''):
                # Backup the existing files
                if (os.path.exists(rtdistribution)):
                    resource = 'DRGRTs'
                    srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                    commonTools.backup_file(srcdir, resource, prefix + drg_distribution_auto_tfvars_template)


def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." + os.path.join(dir, f))
            os.remove(os.path.join(dir, f))


# Execution of the code begins here for route creation
def create_terraform_route(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci,modify_network):
    filename = inputfile

    tempSkeleton = {}
    common_rt = []
    routetablefiles = {}
    tempStr = {}
    routetableStr = {}
    modifiedroutetableStr = {}
    lpgStrCommon = {}
    ADS = ["AD1", "AD2", "AD3"]
    fname = None
    right_vcn_lpgroute_done = []
    modified_network_new_rt = []
    rts_from_RouteRulesInOCI_sheet = []
    routetable_regions_list = []


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('route-table-template')
    routerule = env.get_template("route-rule-template")
    auto_tfvars_filename = "_routetables.auto.tfvars"

    # Purge existing routetable files
    if not modify_network:
        for reg in ct.all_regions:
            routetablefiles.setdefault(reg, [])
            purge(outdir + "/" + reg + "/"+service_dir, prefix + auto_tfvars_filename)

    # Option "Modify Network"
    elif modify_network:
        # Read cd3 using pandas dataframe
        dfroutetable, col_headers = commonTools.read_cd3(filename, "RouteRulesinOCI")

        dfroutetable = dfroutetable.dropna(how='all')
        dfroutetable = dfroutetable.reset_index(drop=True)

        routetable_regions_list = dfroutetable['Region'].str.lower().tolist()

        # Start processing each RT
        for i in dfroutetable.index:
            region = str(dfroutetable['Region'][i]).strip()
            if (region in commonTools.endNames):
                break
            rt_tf_from_rtRulesInOCI_sheet_name = "#"+commonTools.check_tf_variable(dfroutetable.loc[i, 'Region']).lower()+"_"+commonTools.check_tf_variable(dfroutetable.loc[i, 'VCN Name'])+"_"+commonTools.check_tf_variable(dfroutetable.loc[i, 'Route Table Name'])+"#"
            if rt_tf_from_rtRulesInOCI_sheet_name not in rts_from_RouteRulesInOCI_sheet:
                rts_from_RouteRulesInOCI_sheet.append(rt_tf_from_rtRulesInOCI_sheet_name)

    for reg in ct.all_regions:
        tempSkeleton[reg] = ''
        routetableStr[reg] = ''
        lpgStrCommon[reg] = ''
        modifiedroutetableStr[reg] = ''

        outfile = outdir + "/" + reg + "/" + service_dir + "/"+prefix + auto_tfvars_filename

        # Option Modify Network as True
        if modify_network:

            # Read the file if it exists
            if os.path.exists(outfile):
                # Read the contents of file in outdir
                with open(outfile, 'r+') as file:
                    filedata = file.read()
                file.close()

                # for the RTs in RouteRulesInOCI sheet, see if the start string is there in filedata, if yes, retain it, if no delete the remaining information.
                for rts in rts_from_RouteRulesInOCI_sheet:
                    if "# Start of " + rts + " #" in filedata and "# Start of " + rts + " #" not in modifiedroutetableStr[reg]:
                        modifiedroutetableStr[reg] = ct.copy_data_from_file(outfile, rts, modifiedroutetableStr[reg])
                tempSkeleton[reg] = template.render(count = 0, region = reg, skeleton=True)
                srcStr = "##Add New Route Tables for "+reg.lower()+" here##"
                modifiedroutetableStr[reg] = tempSkeleton[reg].replace(srcStr,modifiedroutetableStr[reg]) #+"\n"+srcStr) ----> ToTest, if fails add +"\n"+srcStr
            else:
                 modifiedroutetableStr[reg] = ''
     # Get Hub VCN name and create route rules for LPGs as per Section VCN_PEERING
    def createLPGRouteRules(peering_dict):
        ruleStr = ''
        region=''
        for key, value in peering_dict.items():
            left_vcn=key[0]
            r=key[1]
            right_vcns = value.split(",")
            left_vcn_tf_name = commonTools.check_tf_variable(left_vcn)

            for right_vcn in right_vcns:
                if (right_vcn == ""):
                    continue
                right_vcn = right_vcn.strip()
                right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)

                # Build rule for VCN on left
                lpg_name = vcns.vcn_lpg_names1[left_vcn,r][0]

                lpg_name = left_vcn + "_" + lpg_name
                lpg_name_tf_name = commonTools.check_tf_variable(lpg_name)

                vcns.vcn_lpg_names1[left_vcn,r].pop(0)
                right_vcn_cidrs = [x.strip() for x in vcns.vcn_cidrs[right_vcn,r].split(',')]

                for vcn_cidr in right_vcn_cidrs:
                    tempStr['destination'] = vcn_cidr
                    tempStr['lpg_vcn_name'] = lpg_name_tf_name
                    tempStr['destination_type'] = "CIDR_BLOCK"
                    tempStr['network_entity_id'] = lpg_name_tf_name
                    start_rule = "## Start Route Rule lpg_route_rules__" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                    if start_rule not in vcns.vcn_lpg_rules[left_vcn,r]:
                        ruleStr = routerule.render(tempStr,lpg_route_rules=True, region='lpg_route_rules')
                    vcns.vcn_lpg_rules[left_vcn,r] = vcns.vcn_lpg_rules[left_vcn,r] + ruleStr

                # Build rule for VCNs on right
                lpg_name = vcns.vcn_lpg_names1[right_vcn,r][0]
                lpg_name = right_vcn + "_" + lpg_name
                lpg_name_tf_name = commonTools.check_tf_variable(lpg_name)

                vcns.vcn_lpg_names1[right_vcn,r].pop(0)
                left_vcn_cidrs = [x.strip() for x in vcns.vcn_cidrs[left_vcn,r].split(',')]
                for vcn_cidr in left_vcn_cidrs:
                    tempStr['destination'] = vcn_cidr
                    tempStr['lpg_vcn_name'] = lpg_name_tf_name
                    tempStr['destination_type'] = "CIDR_BLOCK"
                    tempStr['network_entity_id'] = lpg_name_tf_name
                    start_rule = "## Start Route Rule lpg_route_rules__" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                    if start_rule not in vcns.vcn_lpg_rules[right_vcn,r]:
                        ruleStr =  routerule.render(tempStr,lpg_route_rules=True, region='lpg_route_rules')
                    vcns.vcn_lpg_rules[right_vcn,r] = vcns.vcn_lpg_rules[right_vcn,r] + ruleStr

    def createVCNRtTableString(items):
        # Create IGW/NGW/SGW Route Table
        for key, value in items:
            vn = key[0]
            rn = key[1]
            rt_name = value[1]
            if rt_name != '':
                Str = ''
                srcStr = "##Add New Route Tables for " + rn + " here##"
                if srcStr not in routetableStr[rn]:
                    routetableStr[rn] = routetableStr[rn] + srcStr
                tempStr['region'] = rn

                rt_var = vn + "_" + rt_name
                rt_display = rt_name
                rt_tf_name = commonTools.check_tf_variable(rt_var)
                #outfile = outdir + "/" + rn + "/" + service_dir + "/" + prefix + auto_tfvars_filename
                region_rt_name = "#" + rn + "_" + rt_tf_name + "#"

                if (region_rt_name not in common_rt):
                    common_rt.append(region_rt_name)
                    tempStr['rt_tf_name'] = rt_tf_name
                    tempStr['compartment_tf_name'] = compartment_var_name
                    tempStr['display_name'] = rt_display
                    #tempStr['gateway_route_table'] = 'true'
                    tempStr['vcn_tf_name'] = commonTools.check_tf_variable(vn)


                    if region_rt_name not in modifiedroutetableStr[rn]:
                        Str = template.render(tempStr,
                                              route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                              route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                              route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                              route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                              route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                              route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )

                        modified_network_new_rt.append(region_rt_name)
                        if Str != "" and Str != None:
                            routetableStr[rn] = routetableStr[rn].replace(srcStr, Str)

                ## Add parameter for igw/ngw/sgw route tables
                ss = "### gateway_route_table for " + region_rt_name + " ##"
                rr = "gateway_route_table = true"
                routetableStr[rn] = routetableStr[rn].replace(ss, rr)


    def createVCNDRGRtTableString(compartment_var_name, vcn_with_drg, peering_dict, region, tempStr, hub):
        drgStr = ''
        temprule = ''
        if (vcns.vcn_drgs[vcn_with_drg,region][0] == 'y'):
            drg_name = region + "_drg"
        elif (vcns.vcn_drgs[vcn_with_drg,region][0] != 'n'):
            drg_name = vcns.vcn_drgs[vcn_with_drg,region][0]
        elif (vcns.vcn_drgs[vcn_with_drg,region][0] == 'n' and hub == 1):
            print("\ndrg_required column for VCN " + vcn_name + " marked as Hub should not be set to n!!\n")
            return

        drg_rt_name = vcns.vcn_drgs[vcn_with_drg,region][1]
        '''
        if (os.path.exists(outdir + "/" + region + "/" + service_dir + "/obj_names.safe")):
            with open(outdir + "/" + region + "/" + service_dir + "/obj_names.safe") as f:
                for line in f:
                    if ("drginfo::::" + vcn_with_drg + "::::" + drg_name in line):
                        drg_rt_name = line.split("::::")[3].strip()
        '''

        # Dont Attach any Route Table with DRG if it is ''
        if (drg_rt_name == ""):
            return
            #rt_display = "Route Table associated with DRG-" + drg_name
            #rt_var = vcn_with_drg + "_" + rt_display
        # Route table associated with DRG inside VCN is not existing
        else:
            rt_var = vcn_with_drg + "_" + drg_rt_name
            rt_display = drg_rt_name

        rt_tf_name = commonTools.check_tf_variable(rt_var)
        outfile = outdir + "/" + region + "/" +  service_dir + "/" + prefix + auto_tfvars_filename

        region_rt_name = "#"+region + "_" + rt_tf_name+"#"


        if (hub == 0):
            if (region_rt_name not in common_rt):
                tempStr['rt_tf_name'] = rt_tf_name
                tempStr['compartment_tf_name'] = compartment_var_name
                tempStr['display_name'] = rt_display
                tempStr['vcn_tf_name'] = commonTools.check_tf_variable(vcn_with_drg)

                if region_rt_name not in modifiedroutetableStr[region]:
                    drgStr = template.render(tempStr,
                                             route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                             route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                             route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                             route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                             route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                             route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )

                    modified_network_new_rt.append(region_rt_name)

        elif (hub == 1):
            right_vcns = peering_dict[vcn_with_drg,region]
            right_vcns = right_vcns.split(",")

            for right_vcn in right_vcns:
                if right_vcn == '':
                    continue
                check=right_vcn,region
                if check in vcns.spoke_vcn_names:
                    right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)
                    lpg_name = vcns.vcn_lpg_names2[vcn_with_drg,region][0]
                    lpg_name = hub_vcn_name + "_" + lpg_name
                    lpg_tf_name = commonTools.check_tf_variable(lpg_name)
                    hub_vcn_tf_name = commonTools.check_tf_variable(hub_vcn_name)
                    vcns.vcn_lpg_names2[vcn_with_drg,region].pop(0)
                    srcStr = "####ADD_NEW_LPG_RULES " + region_rt_name + " ####"

                    right_vcn_cidrs = [x.strip() for x in vcns.vcn_cidrs[right_vcn, r].split(',')]
                    for vcn_cidr in right_vcn_cidrs:

                        tempStr['rt_tf_name'] = rt_tf_name
                        tempStr['destination'] = vcn_cidr
                        tempStr['display_name'] = rt_display
                        tempStr['lpg_vcn_name'] = lpg_tf_name
                        tempStr['destination_type'] = "CIDR_BLOCK"
                        tempStr['network_entity_id'] = lpg_tf_name
                        start_rule = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                        temprule = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr,
                                                                routetableStr, start_rule, temprule,
                                                                modify_network=modify_network,
                                                                routerule=routerule, gateway='LPG')

                        if (region_rt_name in common_rt):
                            if temprule not in modifiedroutetableStr[reg]:
                                tempstr = temprule + "\n" + srcStr
                                drgStr = drgStr.replace(srcStr, tempstr + "\n")
                        else:
                            tempStr['rt_tf_name'] = rt_tf_name
                            tempStr['compartment_tf_name'] = compartment_var_name
                            tempStr['display_name'] = rt_display
                            tempStr['vcn_tf_name'] = hub_vcn_tf_name

                            if region_rt_name not in modifiedroutetableStr[region]:
                                drgStr = template.render(tempStr,
                                                         route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                                         route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                                         route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                                         route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                                         route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                                         route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )

                                drgStr = drgStr.replace(srcStr, temprule + "\n" + srcStr)
                                modified_network_new_rt.append(region_rt_name)

        return drgStr

    def createLPGRtTableString(compartment_var_name, hub_vcn_name, peering_dict, region, tempStr):
        region=region.lower()
        # Retain exported route tables associated with exported LPGs
        if (os.path.exists(outdir + "/" + region + "/" + service_dir + "/obj_names.safe")):
            with open(outdir + "/" + region + "/"+ service_dir + "/obj_names.safe") as f:
                for line in f:
                    if ("lpginfo::::" + hub_vcn_name in line):
                        lpg_rt_name = line.split("::::")[3].strip()
                        rt_var = hub_vcn_name + "_" + lpg_rt_name
                        rt_tf_name = commonTools.check_tf_variable(rt_var)

        # Create Rt table String for new spoke VCNs
        right_vcns = peering_dict[hub_vcn_name,region]
        right_vcns = right_vcns.split(",")
        lpgStr = ''
        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            temprule = ''
            check=right_vcn,region
            if (check in vcns.spoke_vcn_names):
                lpg_name = vcns.vcn_lpg_names3[hub_vcn_name,region][0]
                vcns.vcn_lpg_names3[hub_vcn_name,region].pop(0)
                # rt_var = hub_vcn_name + "_" + lpg_name + "_rt"
                rt_display = "Route Table associated with LPG-""" + lpg_name
                rt_var = hub_vcn_name + "_" + rt_display
                rt_tf_name = commonTools.check_tf_variable(rt_var)

                hub_vcn_tf_name = commonTools.check_tf_variable(hub_vcn_name)
                tempStr['display_name'] = rt_display
                tempStr['rt_var'] = rt_var
                tempStr['rt_tf_name'] = rt_tf_name
                tempStr['vcn_tf_name'] = hub_vcn_tf_name
                tempStr['compartment_tf_name'] = compartment_var_name
                region_rt_name = "#"+region + "_" + rt_tf_name+"#"

                if (region_rt_name not in common_rt):
                    lpgStr = template.render(tempStr,
                                             route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                             route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                             route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                             route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                             route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                             route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )

                    if region_rt_name not in modifiedroutetableStr[region]:
                        modified_network_new_rt.append(region_rt_name)

                srcStr = "####ADD_NEW_DRG_RULES " + region_rt_name + " ####"
                drg_name = ""
                if (vcns.vcn_drgs[hub_vcn_name,region][0] == 'y'):
                    # drg_name = hub_vcn_name + "_drg"
                    drg_name = region + "_drg"
                elif (vcns.vcn_drgs[hub_vcn_name,region][0] != 'n'):
                    drg_name = vcns.vcn_drgs[hub_vcn_name,region][0]

                if (drg_name != ""):

                    drg_tf_name = commonTools.check_tf_variable(drg_name)
                    for drg_destination in vcnInfo.onprem_destinations:
                        if (drg_destination != ''):
                            tempStr['vcn_tf_name'] = ''
                            tempStr['destination'] = drg_destination.strip()
                            tempStr['destination_type'] = "CIDR_BLOCK"
                            tempStr['network_entity_id'] = drg_tf_name
                            start_rule = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                            temprule = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr,
                                            routetableStr, start_rule, temprule, modify_network=modify_network,
                                            routerule=routerule, gateway='DRG')

                            lpgStr = lpgStr.replace(srcStr, temprule + "\n" + srcStr)

                lpgStrCommon[region] = lpgStrCommon[region] + "\n" + lpgStr
                right_vcn_lpgroute_done.append(right_vcn)

        return lpgStrCommon[region]

    def prepareSGWRuleStr(vcn_name, sgw_name, destination, configure_sgw, tempStr, data):
        if configure_sgw != 'n' and sgw_name != '':
            sgw_tf_name = vcn_name + "_" + sgw_name
            sgw_tf_name = commonTools.check_tf_variable(sgw_tf_name)
            if (configure_sgw == "all_services"):
                destination = "all"
            elif (configure_sgw == "object_storage"):
                destination = "objectstorage"
            tempStr['destination'] = destination
            tempStr['sgw_tf_name'] = sgw_tf_name
            tempStr['configure_sgw'] = configure_sgw
            tempStr['destination_type'] = "SERVICE_CIDR_BLOCK"
            tempStr['network_entity_id'] = sgw_tf_name
            vcn_name = tempStr['vcn_tf_name']

            # If the auto.tfvars has a rule for all/objectstorage, and the Excel sheet has a RT with both the options in Subnet's Tab, add only the latest/last one.
            # Both cannot co-exist in the same route table. Must be either all/objectstorage.
            start = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id']
            end = "## End Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_objectstorage"
            if start+ "_objectstorage" in routetableStr[region.lower()] and tempStr['destination'] == 'all':
                routetableStr[region.lower()], filedata = read_infile_data(routetableStr, region.lower(), start, end)
            elif start+"_all" in routetableStr[region.lower()] and tempStr['destination'] == 'objectstorage':
                end = "## End Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_all"
                routetableStr[region.lower()], filedata = read_infile_data(routetableStr, region.lower(),start, end)

            start_rule = "## Start Route Rule "+tempStr['region'].lower()+"_"+tempStr['rt_tf_name']+"_"+tempStr['network_entity_id']+"_"+tempStr['destination']
            rem_keys = ['vcn_tf_name', 'drg_tf_name', 'ngw_tf_name', 'igw_tf_name', 'lpg_tf_name']
            [tempStr.pop(key) for key in rem_keys if key in tempStr]
            data = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr,
                                                routetableStr, start_rule, data,modify_network=modify_network,
                                                routerule=routerule, gateway='SGW')

            tempStr['vcn_tf_name'] = vcn_name
        return data

    def prepareNGWRuleStr(vcn_name, ngw_name, configure_ngw, tempStr):
        data = ''
        if configure_ngw != 'n' and ngw_name != '':
            ngw_tf_name = vcn_name + "_" + ngw_name
            ngw_tf_name = commonTools.check_tf_variable(ngw_tf_name)
            vcn_name = tempStr['vcn_tf_name']
            data = ""
            for ngw_destination in vcnInfo.ngw_destinations:
                if (ngw_destination != ''):
                    tempStr['destination'] = ngw_destination
                    tempStr['ngw_tf_name'] = ngw_tf_name
                    tempStr['destination_type'] = "CIDR_BLOCK"
                    tempStr['network_entity_id'] = ngw_tf_name
                    start_rule = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                    rem_keys = ['vcn_tf_name', 'drg_tf_name', 'configure_sgw', 'igw_tf_name', 'lpg_tf_name']
                    [tempStr.pop(key) for key in rem_keys if key in tempStr]
                    data = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr, routetableStr,
                                                        start_rule, data, modify_network=modify_network, routerule=routerule,
                                                        gateway='NGW')

            tempStr['vcn_tf_name'] = vcn_name
        return data

    def prepareIGWRuleStr(vcn_name, igw_name, configure_igw,tempStr):
        data = ''
        if configure_igw != 'n' and igw_name != '':
            igw_tf_name = vcn_name + "_" + igw_name
            igw_tf_name = commonTools.check_tf_variable(igw_tf_name)
            vcn_name = tempStr['vcn_tf_name']
            data = ""
            for igw_destination in vcnInfo.igw_destinations:
                if (igw_destination != ''):
                    tempStr['igw_tf_name'] = igw_tf_name
                    tempStr['destination'] =  igw_destination
                    tempStr['destination_type'] = "CIDR_BLOCK"
                    tempStr['network_entity_id'] = igw_tf_name
                    start_rule = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                    rem_keys = ['vcn_tf_name', 'drg_tf_name', 'configure_sgw', 'ngw_tf_name', 'lpg_tf_name']
                    [tempStr.pop(key) for key in rem_keys if key in tempStr]
                    data = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr, routetableStr,
                                                        start_rule, data, modify_network=modify_network, routerule=routerule,
                                                        gateway='IGW')
            tempStr['vcn_tf_name'] = vcn_name
        return data

    def prepareOnpremRuleStr(vcn_name, drg_name, configure_onprem,tempStr,region):
        data = ""
        vcn_tf_name = tempStr['vcn_tf_name']
        if configure_onprem!= 'n' and drg_name != '':
            #v_list_having_drg = []
            #for key in vcns.vcns_having_drg.keys():
            #    if(region == key[1]):
            #        v_list_having_drg.append(key[0])
            if vcns.vcn_hub_spoke_peer_none[vcn_name,region][0].lower() == 'hub' or (vcn_name,region) in vcns.vcns_having_drg.keys():
                drg_tf_name = commonTools.check_tf_variable(drg_name)
                for drg_destination in vcnInfo.onprem_destinations:
                    if (drg_destination != ''):
                        tempStr['drg_tf_name'] = drg_tf_name
                        tempStr['destination'] = drg_destination.strip()
                        tempStr['destination_type'] = "CIDR_BLOCK"
                        tempStr['network_entity_id'] = drg_tf_name
                        tempStr['lpg'] = False
                        start_rule = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                        rem_keys = ['vcn_tf_name', 'igw_tf_name', 'configure_sgw', 'ngw_tf_name', 'lpg_tf_name']
                        [tempStr.pop(key) for key in rem_keys if key in tempStr]
                        data = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr, routetableStr,
                                                            start_rule, data, modify_network=modify_network, routerule=routerule,
                                                            gateway='DRG')


            if vcns.vcn_hub_spoke_peer_none[vcn_name,region][0].lower() == 'spoke':
                lpg_name = vcns.vcn_lpg_names[vcn_name][0]
                lpg_name = vcn_name + "_" + lpg_name
                lpg_tf_name = commonTools.check_tf_variable(lpg_name)
                for drg_destination in vcnInfo.onprem_destinations:
                    if (drg_destination != ''):
                        tempStr['lpg_tf_name'] = lpg_tf_name
                        tempStr['destination'] = drg_destination.strip()
                        tempStr['destination_type'] = "CIDR_BLOCK"
                        tempStr['network_entity_id'] = lpg_tf_name
                        tempStr['lpg'] = True
                        start_rule = "## Start Route Rule " + tempStr['region'].lower() + "_" + tempStr['rt_tf_name'] + "_" + tempStr['network_entity_id'] + "_" + tempStr['destination']
                        rem_keys = ['vcn_tf_name', 'igw_tf_name', 'configure_sgw', 'ngw_tf_name', 'drg_tf_name']
                        [tempStr.pop(key) for key in rem_keys if key in tempStr]
                        data = merge_or_generate_route_rule(region.lower(), tempStr, modifiedroutetableStr, routetableStr,
                                                            start_rule, data, modify_network=modify_network, routerule=routerule,
                                                            gateway='LPG')

            tempStr['vcn_tf_name'] = vcn_tf_name
        return data

    def prepareVCNPeerRuleStr(configure_vcnpeering,region):
        data = ""
        if configure_vcnpeering != 'n':
            data = data + vcns.vcn_lpg_rules[vcn_name,region]
        return data

    def processSubnet(tempStr):

        rt_name = tempStr['route_table_name']
        AD = tempStr['availability_domain']
        subnet = tempStr['cidr_block']
        configure_sgw = tempStr['configure_sgw_route'].strip()
        configure_ngw = tempStr['configure_ngw_route'].strip()
        configure_igw = tempStr['configure_igw_route'].strip()
        configure_onprem = tempStr['configure_onprem_route'].strip()
        configure_vcnpeering = tempStr['configure_vcnpeering_route'].strip()

        # Route Table name specifiied as 'n' - dont create any routetable
        if (rt_name == "n"):
            # Create Skeleton Template
            if tempStr['count'] == 0:
                tempSkeleton[region] = template.render(tempStr, skeleton=True)
            return

        display_name = rt_name
        tempStr['display_name'] = display_name

        vcn_tf_name = commonTools.check_tf_variable(tempStr['vcn_name'])
        subnet_tf_name = tempStr['vcn_name'] + "_" + display_name

        subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)

        tempStr['vcn_tf_name'] = vcn_tf_name
        tempStr['subnet_tf_name'] = subnet_tf_name

        tempStr['rt_tf_name'] = commonTools.check_tf_variable(vcn_tf_name + "_" + rt_name)
        region_rt_name = "#"+region + "_" + tempStr['rt_tf_name']+"#"

        # Get VCN component names
        vcn_drg = vcns.vcn_drgs[vcn_name,region][0]
        drg_name = ""
        if (vcn_drg == "y"):
            # drg_name = vcn_name + "_drg"
            drg_name = region + "_drg"
        elif (vcn_drg != "n"):
            drg_name = vcn_drg
        tempStr['drg_name'] = drg_name

        vcn_igw = vcns.vcn_igws[vcn_name,region][0]
        igw_name = ""
        if (vcn_igw == "y"):
            igw_name = vcn_name + "_igw"
        elif (vcn_igw != "n"):
            igw_name = vcn_igw
        tempStr['igw_name'] = igw_name

        vcn_ngw = vcns.vcn_ngws[vcn_name,region][0]
        ngw_name = ""
        if (vcn_ngw == "y"):
            ngw_name = vcn_name + "_ngw"
        elif (vcn_ngw != "n"):
            ngw_name = vcn_ngw
        tempStr['ngw_name'] = ngw_name

        vcn_sgw = vcns.vcn_sgws[vcn_name,region][0]
        sgw_name = ""
        if (vcn_sgw == "y"):
            sgw_name = vcn_name + "_sgw"
        elif (vcn_sgw != "n"):
            sgw_name = vcn_sgw
        tempStr['sgw_name'] = sgw_name

        # Prepare rule str
        data = ''
        data_sgw = prepareSGWRuleStr(vcn_name, sgw_name, destination, configure_sgw, tempStr, data)
        data_ngw = prepareNGWRuleStr(vcn_name, ngw_name, configure_ngw, tempStr)
        data_igw = prepareIGWRuleStr(vcn_name, igw_name, configure_igw, tempStr)
        data_onprem = prepareOnpremRuleStr(vcn_name, drg_name, configure_onprem, tempStr, region)
        data_vcnpeer = prepareVCNPeerRuleStr(configure_vcnpeering,region)

        # Create Skeleton Template
        if tempStr['count'] == 0:
            tempSkeleton[region] = template.render(tempStr, skeleton=True)

        start = "# Start of " + region_rt_name + " #"
        end = "# End of " + region_rt_name + " #"


        # Create Route Tables for all the unique names in Subnet Sheet
        if (start not in routetableStr[region] and start not in modifiedroutetableStr[region]):
            routetableStr[region] = routetableStr[region] + template.render(tempStr,
                                                                            route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                                                            route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                                                            route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                                                            route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                                                            route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                                                            route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )

            modified_network_new_rt.append(region_rt_name)
        # Peering Rules
        if configure_vcnpeering.strip() == 'y' and data_vcnpeer != '' and region_rt_name not in lpgrule_added:
            lpgStr = "####ADD_NEW_LPG_RULES "+ region_rt_name + " ####"
            if data_vcnpeer != '':
                data_vcnpeer = data_vcnpeer + "\n" + lpgStr
                routetableStr[region] = routetableStr[region].replace(lpgStr, data_vcnpeer)
                lpgrule_added.append(region_rt_name)

        # SGW Rules
        if configure_sgw.strip() == 'all_services' or configure_sgw.strip() == 'object_storage' and vcn_sgw != 'n':
            sgwStr = "####ADD_NEW_SGW_RULES " + region_rt_name + " ####"
            if data_sgw != '':
                data_sgw = data_sgw + "\n" + sgwStr
                routetableStr[region] = routetableStr[region].replace(sgwStr, data_sgw)

        # NGW Rules
        if configure_ngw.strip() == 'y' and vcn_ngw != 'n':
            ngwStr = "####ADD_NEW_NGW_RULES " + region_rt_name + " ####"
            if data_ngw !=  '':
                data_ngw = data_ngw + "\n" + ngwStr
                routetableStr[region] = routetableStr[region].replace(ngwStr, data_ngw)

        # IGW Rules
        if configure_igw.strip() == 'y' and vcn_igw != 'n':
            igwStr = "####ADD_NEW_IGW_RULES " + region_rt_name + " ####"
            if data_igw != '':
                data_igw = data_igw + "\n" + igwStr
                routetableStr[region] = routetableStr[region].replace(igwStr, data_igw)

        # On-Prem Rules
        if configure_onprem.strip() == 'y':
            v_list_having_drg = []
            for key in vcns.vcns_having_drg.keys():
                v_list_having_drg.append(key[0])
            check = vcn_name.strip(),region
            if (check in vcns.hub_vcn_names or check in vcns.spoke_vcn_names or check[0] in v_list_having_drg):
                if tempStr['lpg'] == True:
                    onpremStrlpg = "####ADD_NEW_LPG_RULES " + region_rt_name + " ####"
                    if data_onprem != '':
                        data_onprem = data_onprem + "\n" + onpremStrlpg
                        routetableStr[region] = routetableStr[region].replace(onpremStrlpg, data_onprem)
                else:
                    onpremStr = "####ADD_NEW_DRG_RULES " + region_rt_name + " ####"
                    if data_onprem != '':
                        data_onprem = data_onprem + "\n" + onpremStr
                        routetableStr[region] = routetableStr[region].replace(onpremStr, data_onprem)

        common_rt.append(region_rt_name)

    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    if (vcnInfo.onprem_destinations[0] == ""):
        print("\nonprem_destinations field is empty in VCN Info Sheet.. It will create empty route tables!!\n")

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "SubnetsVLANs")
    region_included = []

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # temporary dictionary1, dictionary2
    tempStr = {}
    tempdict = {}
    lpgrule_added = []

    compartment_var_name = ''
    destination = ''

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Create LPG Rules
    createLPGRouteRules(vcns.peering_dict)

    subnet_regions_list = df["Region"].str.lower().tolist()

    for i in df.index:
        # Get subnet data
        region = str(df.loc[i, 'Region'])
        subnet_vlan_in_excel = str(df.loc[i, 'Subnet or VLAN']).strip()

        #skip VLAN rows while create network
        if not modify_network and subnet_vlan_in_excel.lower().startswith('vlan'):
            continue
        #skip VLAN rows while running option modify network
        if modify_network and network_vlan_in_setupoci == 'network' and subnet_vlan_in_excel.lower().startswith('vlan'):
            continue

        # skip Subnet rows while running option Add/Modify/Delete VLANs
        if modify_network and network_vlan_in_setupoci == 'vlan' and subnet_vlan_in_excel.lower().startswith('subnet'):
            continue

        if (region in commonTools.endNames):
            break
        region = region.strip().lower()

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)


        vcn_name = str(df['VCN Name'][i]).strip()
        check = vcn_name.strip(), region

        if (check not in vcns.vcn_names):
            print("\nERROR!!! " + vcn_name + " specified in SubnetsVLANs tab has not been declared in VCNs tab..Exiting!")
            exit(1)

        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or
                str(df.loc[i, 'VCN Name']).lower() == 'nan' or
                str(df.loc[i, 'Display Name']).lower() == 'nan' or str(df.loc[i, 'CIDR Block']).lower() == 'nan' or
                str(df.loc[i, 'Availability Domain(AD1|AD2|AD3|Regional)']).lower() == 'nan' or
                str(df.loc[i, 'Configure SGW Route(n|object_storage|all_services)']).lower() == 'nan' or
                str(df.loc[i, 'Configure NGW Route(y|n)']).lower() == 'nan' or
                str(df.loc[i, 'Configure IGW Route(y|n)']).lower() == 'nan' or
                str(df.loc[i, 'Configure OnPrem Route(y|n)']).lower() == 'nan' or
                str(df.loc[i, 'Configure VCNPeering Route(y|n)']).lower() == 'nan'):
            print("\nERROR!!! Column Values (except DHCP Option Name, Route Table Name, Seclist Name or DNS Label) or Rows cannot be left empty in SubnetsVLANs sheet in CD3..Exiting!")
            exit(1)
        if (str(df.loc[i,'Subnet or VLAN']).strip().lower()=='subnet'):
            if str(df.loc[i, 'Type(private|public)']).lower() == 'nan' or str(df.loc[i, 'Add Default Seclist']).lower() == 'nan':
                print("\nERROR!!! Column Values - Type(private|public) and Add Default Seclist cannot be left empty for Subnet row..Exiting!")
                exit(1)


        if modify_network:
            if (df.loc[i, 'Configure SGW Route(n|object_storage|all_services)']).lower() == '-' or str( df.loc[i, 'Configure NGW Route(y|n)']).lower() == '-' or \
                str(df.loc[i, 'Configure IGW Route(y|n)']).lower() == '-' or str(df.loc[i, 'Configure OnPrem Route(y|n)']).lower() == '-' or str(df.loc[i, 'Configure VCNPeering Route(y|n)']).lower() == '-':
                if str(df.loc[i, 'Region']).lower()+"_"+commonTools.check_tf_variable(str(df.loc[i, 'VCN Name']))+"_"+commonTools.check_tf_variable(str(df.loc[i, 'Route Table Name'])) in modifiedroutetableStr[region]:
                    continue
            else:
                pass

        for columnname in dfcolumns:
            # Column value
            if (columnname != 'Rule Description'):
                columnvalue = str(df[columnname][i]).strip()
            else:
                columnvalue = str(df[columnname][i])

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Freeform and Defined Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Availability Domain(AD1|AD2|AD3|Regional)':
                columnname = 'availability_domain'
                tempdict = {'availability_domain': columnvalue}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue
                compartment_var_name = compartment_var_name.strip()
                # Added to check if compartment name is compatible with TF variable name syntax
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Configure SGW Route(n|object_storage|all_services)':
                columnname = 'configure_sgw_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_sgw_route': columnvalue}

            if columnname == 'Configure NGW Route(y|n)':
                columnname = 'configure_ngw_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_ngw_route': columnvalue}

            if columnname == 'Configure IGW Route(y|n)':
                columnname = 'configure_igw_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_igw_route': columnvalue}

            if columnname == 'Configure OnPrem Route(y|n)':
                columnname = 'configure_onprem_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_onprem_route': columnvalue}

            if columnname == 'Configure VCNPeering Route(y|n)':
                columnname = 'configure_vcnpeering_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_vcnpeering_route': columnvalue}

            if columnname == 'Route Table Name':
                if str(columnvalue).lower().strip() != 'nan' and str(columnvalue).lower().strip() != '':
                    rt_name = columnvalue.strip()
                    tempdict = {'route_table_name': rt_name}
                else:
                    rt_name = str(df.loc[i, 'Display Name']).strip()
                    tempdict = {'route_table_name': rt_name}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = columnvalue
            tempStr.update(tempdict)

        tempStr.update({'count': 1})
        if region not in region_included:
            tempStr.update({'count': 0})
            region_included.append(region)

        processSubnet(tempStr)

    createVCNRtTableString(vcns.vcn_igws.items())
    createVCNRtTableString(vcns.vcn_ngws.items())
    createVCNRtTableString(vcns.vcn_sgws.items())

    # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
    for key in vcns.hub_vcn_names:
        hub_vcn_name = key[0]

        #r = vcns.vcn_region[hub_vcn_name].strip().lower()
        r=key[1]

        compartment_var_name = vcns.vcn_compartment[hub_vcn_name,r]
        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        # String for Route Table Associated with each LPG in hub VCN peered with Spoke VCN

        srcStr = "##Add New Route Tables for " + r + " here##"
        if srcStr not in routetableStr[r]:
            routetableStr[r] = routetableStr[r] + srcStr
        tempStr['region'] = r

        lpgruleStr = createLPGRtTableString(compartment_var_name, hub_vcn_name, vcns.peering_dict, r, tempStr)
        if lpgruleStr != "" and lpgruleStr != None :
            routetableStr[r] = routetableStr[r].replace(srcStr, lpgruleStr)

    # Create Route Table associated with DRG(in VCN) for each VCN attached to DRG
    for key in vcns.vcns_having_drg.keys():
        vcn = key[0]
        if (vcn in vcns.hub_vcn_names):
            continue

        # String for Route Table Associated with DRG
        #r = vcns.vcn_region[vcn].strip().lower()
        r=key[1]
        compartment_var_name = vcns.vcn_compartment[vcn,r]

        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        srcStr = "##Add New Route Tables for " + r + " here##"
        if srcStr not in routetableStr[r]:
            routetableStr[r] = routetableStr[r] + srcStr
        tempStr['region'] = r

        drgruleStr = createVCNDRGRtTableString(compartment_var_name, vcn, vcns.peering_dict, r, tempStr, hub=0)

        if drgruleStr != "" and drgruleStr != None:
            routetableStr[r] = routetableStr[r].replace(srcStr, drgruleStr)


    # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
    for key in vcns.hub_vcn_names:
        hub_vcn_name = key[0]


        # String for Route Table Assocaited with DRG
        #r = vcns.vcn_region[hub_vcn_name].strip().lower()
        r=key[1]
        compartment_var_name = vcns.vcn_compartment[hub_vcn_name, r]
        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        srcStr = "##Add New Route Tables for " + r + " here##"
        if srcStr not in routetableStr[r]:
            routetableStr[r] = routetableStr[r] + srcStr
        tempStr['region'] = r

        drgruleStr1 = createVCNDRGRtTableString(compartment_var_name, hub_vcn_name, vcns.peering_dict, r, tempStr,hub=1)
        if drgruleStr1 != "" and drgruleStr1 != None:
            routetableStr[r] = routetableStr[r].replace(srcStr, drgruleStr1)

    # Write the contents to file
    for reg in ct.all_regions:
        outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + auto_tfvars_filename
        skeletonStr = "##Add New Route Tables for " + reg.lower() + " here##"

        # Option if Modify Network is FALSE
        if not modify_network:
            if routetableStr[reg] != '':
                routetableStr[reg] = routetableStr[reg] + "\n" + skeletonStr
                tempSkeleton[reg] = tempSkeleton[reg].replace(skeletonStr, routetableStr[reg])
                tempSkeleton[reg] = "".join([s for s in tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                oname = open(outfile, "w+")
                oname.write(tempSkeleton[reg])
                oname.close()
                print(outfile + " containing route tables has been created for region " + reg)
        else:
            # Option if Modify Network is TRUE
            processed_rt = []

            # Read the file if it exists
            modifiedroutetableStr[reg] = recursive_process_filedata(modified_network_new_rt, modifiedroutetableStr, reg, processed_rt, count=0)

            if modifiedroutetableStr[reg] != '':
                if skeletonStr not in modifiedroutetableStr[reg]:
                    last_char_index = modifiedroutetableStr[reg].rfind("}")
                    modifiedroutetableStr[reg] = modifiedroutetableStr[reg][:last_char_index] + skeletonStr+"\n"+"}" + modifiedroutetableStr[reg][last_char_index + 1:]
                tempSkeleton[reg] = modifiedroutetableStr[reg].replace(skeletonStr, routetableStr[reg])
            else:
                tempSkeleton[reg] = tempSkeleton[reg].replace(skeletonStr, routetableStr[reg] + skeletonStr)

            if tempSkeleton[reg] != '' and (reg in subnet_regions_list or reg in routetable_regions_list):
                # Backup the existing files and create new ones
                if (os.path.exists(outfile)):
                    resource = 'RTs'
                    srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                    commonTools.backup_file(srcdir, resource, prefix + auto_tfvars_filename)

                tempSkeleton[reg] = "".join([s for s in tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                oname = open(outfile, "w+")
                oname.write(tempSkeleton[reg])
                oname.close()
                print(outfile + " containing route tables has been updated for region " + reg)
            else:
                # Remove the files from other regions if there are no data
                resource = 'RTs'
                srcdir = outdir + "/" + reg + "/" + service_dir +"/"
                commonTools.backup_file(srcdir, resource, prefix + auto_tfvars_filename)
                commonTools.backup_file(srcdir, resource, prefix + '_default-routetables.auto.tfvars')

    if (fname != None):
        fname.close()


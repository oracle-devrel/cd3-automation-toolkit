#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create all the Gateways and VCN
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import re
import os
import json
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
#sys.path.append(os.getcwd() + "/../../..")
from commonTools import *

######
# Required Files
# input file containing VCN info - CD3 excel
# Create the major terraform objects - DRG, IGW, NGW, SGW, LPGs for the VCN
# Outdir
# Modify Network
# prefix
######
def parse_args():
    # Read input arguments
    parser = argparse.ArgumentParser(description='Create major-objects (VCN, IGW, NGW, DRG, LPGs etc for the VCN) terraform file')
    parser.add_argument('inputfile',help='Full Path of input file eg: cd3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument('non_gf_tenancy')
    parser.add_argument('--modify-network', default=False, action='store_true', help='modify network')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()




def create_major_objects(inputfile, outdir, prefix, non_gf_tenancy, config, modify_network=False):
    # Declare Variables
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}
    drg_tfStr = {}
    drg_attach_tfStr = {}
    igw_tfStr = {}
    vcn_tfStr = {}
    sgw_tfStr = {}
    ngw_tfStr = {}
    drg_data = {}
    drg_rt_data = {}
    drg_rd_data = {}
    lpg_tfStr = {}
    hub_lpg_tfStr = {}
    peer_lpg_tfStr = {}
    spoke_lpg_tfStr = {}
    none_lpg_tfStr  = {}
    exported_lpg_tfStr = {}
    dhcp_default_tfStr = {}
    dhcpStr = {}
    outfile_dhcp = {}
    outfile_oci_drg_data = {}
    oname_oci_drg_data = {}
    oname_def_dhcp = {}

    global dhcp_data
    auto_tfvars_filename = '_major-objects.auto.tfvars'
    dhcp_auto_tfvars_filename = '_default-dhcp.auto.tfvars'
    drg_data_tfvars_filename = '_drg-data.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)

    # Function to establish peering between LPGs
    def establishPeering(peering_dict):
        for key, value in peering_dict.items():
            #region = vcns.vcn_region[left_vcn]
            left_vcn=key[0]
            region = key[1]
            outfile = outdir + "/" + region + "/" + prefix + auto_tfvars_filename

            right_vcns = value.split(",")
            for right_vcn in right_vcns:
                if (right_vcn == ""):
                    continue
                right_vcn = right_vcn.strip()
                right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)

                try:
                    if (vcns.vcn_lpg_names[left_vcn,region][0].lower() == 'n' or vcns.vcn_lpg_names[right_vcn,region][0].lower() == 'n'):
                        print( "\nERROR!!! Cannot specify n for lpg_required field of VCN if it is part of VCN peering..Exiting!")
                        exit(1)
                except IndexError:

                    print("\nERROR!!! Insufficient LPGs declared for either " + left_vcn + " or " + right_vcn + ". Check lpg_required column in VCNs tab..Exiting!")
                    exit(1)
                searchString = """##peer_id for lpg """ + left_vcn + "_" + vcns.vcn_lpg_names[left_vcn,region][0] + "##"
                vcns.vcn_lpg_names[left_vcn,region].pop(0)
                lpg_name = vcns.vcn_lpg_names[right_vcn,region][0]
                lpg_tf_name = right_vcn + "_" + lpg_name
                lpg_tf_name = commonTools.check_tf_variable(lpg_tf_name)

                peerStr = lpg_tf_name
                vcns.vcn_lpg_names[right_vcn,region].pop(0)

                # Update file contents
                with open(outfile) as f:
                    data = f.read()
                f.close()
                updated_data = re.sub(searchString, peerStr, data)
                with open(outfile, 'w') as f:
                    f.write(updated_data)
                f.close()

    def create_drg_and_attachments(inputfile, outdir, config):
        # Declare Variables
        filename = inputfile
        configFileName = config

        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        drg_attach_skeleton = ''
        drgstr_skeleton = ''

        # Load the template file
        file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
        env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        drg_template = env.get_template('major-objects-drgs-template')
        drg_attach_template = env.get_template('major-objects-drg-attachments-template')
        drg_datasource_template = env.get_template('drg-data-source-template')
        drg_version = "DRGv2"
        drg_versions = {}
        # Get DRG version and Create oci-drg-data
        for region in drgv2.drg_names.keys():
            for drg in drgv2.drg_names[region]:
                if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
                    prevline = ""
                    with open(outdir + "/" + region + "/obj_names.safe") as f:
                        for line in f:
                            if (drg in line):
                                if prevline!= "\n":
                                    drg_version = prevline.split("::::")[1].strip()
                                break
                            prevline = line
                drg_versions[region,drg] = drg_version
                if (drg_version == "DRGv2"):
                    for drg_auto_rt_name in commonTools.drg_auto_RTs:
                        temp = {}
                        drg_auto_rt_tf_name = commonTools.check_tf_variable(drg + "_" + drg_auto_rt_name)
                        temp['drg_auto_rt_tf_name'] = drg_auto_rt_tf_name
                        temp['drg_auto_rt_name'] = drg_auto_rt_name
                        temp['drg_tf_name'] = commonTools.check_tf_variable(drg)
                        drg_rt_data[region] = drg_rt_data[region] + drg_datasource_template.render(temp)

                    for drg_auto_rd_name in commonTools.drg_auto_RDs:
                        temp = {}
                        drg_auto_rd_tf_name = commonTools.check_tf_variable(drg + "_" + drg_auto_rd_name)
                        temp['drg_auto_rd_tf_name'] = drg_auto_rd_tf_name
                        temp['drg_auto_rd_name'] = drg_auto_rd_name
                        temp['drg_tf_name'] = commonTools.check_tf_variable(drg)
                        drg_rd_data[region] = drg_rd_data[region] + drg_datasource_template.render(temp)
                drg_data[region] = drg_datasource_template.render(skeleton=True,
                                                                  data_drg_route_tables=drg_rt_data[region],
                                                                  data_drg_route_table_distributions=drg_rd_data[
                                                                      region])
        # Read cd3 using pandas dataframe
        df, col_headers = commonTools.read_cd3(filename, "DRGs")
        # Remove empty rows
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        region_included_drg = []

        # List of the column headers
        dfcolumns = df.columns.values.tolist()

        for i in df.index:
            region = str(df['Region'][i]).strip()
            if (region in commonTools.endNames):
                break
            comp_name = str(df['Compartment Name'][i]).strip()
            drg = str(df['DRG Name'][i]).strip()


            if (region.lower()=='nan' or comp_name.lower()=='nan' or drg.lower()=='nan'):
                print("\nERROR!!! Columns Region/Compartment Name/DRG Name can not be empty..Exiting!")
                exit(1)


            region = region.strip().lower()
            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            if drg not in vcns.vcns_having_drg.values():
                print("\nERROR!!! Invalid DRG Name. It should be one of the values defined in VCNs tab..Exiting!")
                exit(1)

            attached_to = str(df['Attached To'][i]).strip()
            if(attached_to.lower()!='nan'):
                attached_to = attached_to.split("::")
                if(len(attached_to)==2):
                    if attached_to[0].strip().upper() == "VCN":
                        vcn_name = attached_to[1].strip()
                        try:
                            if (vcn_name.lower() != "nan" and vcns.vcns_having_drg[vcn_name,region] != drg):
                                print("ERROR!!! VCN "+vcn_name +" in column Attached To is not as per DRG Required column of VCNs Tab..Exiting!")
                                exit()
                        except KeyError:
                            print("ERROR!!! VCN "+vcn_name+" in column Attached To is not as per VCN Name column of VCNs Tab..Exiting!")
                            exit()

        # Process Rows
        ip=1
        for i in df.index:
            region = str(df['Region'][i]).strip()
            if (region in commonTools.endNames):
                break
            region = region.strip().lower()
            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            # temporary dictionary1 and dictionary2
            tempStr = {}
            tempdict = {}
            drg_attach = {}
            drg_rt_tf_name = ''
            drg_tf_name = ''

            for columnname in dfcolumns:
                # Column value
                columnvalue = str(df[columnname][i]).strip()
                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Check for multivalued columns
                tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

                # Process Defined Tags and Freeform Tags
                if columnname.lower() in commonTools.tagColumns:
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

                if columnname == 'Compartment Name':
                    compartment_var_name = columnvalue.strip()
                    compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                    tempdict = {'compartment_tf_name': compartment_var_name}

                if columnname == "DRG Name":
                    drg_name = columnvalue
                    drg_tf_name = commonTools.check_tf_variable(drg_name)
                    tempdict['drg_tf_name'] = drg_tf_name

                if (columnname == 'Attached To'):
                    if(columnvalue.lower()=='nan' or columnvalue.lower()==''):
                        attachedto="empty"
                    else:
                        attachedto="attached"
                        columnvalues = columnvalue.split("::")
                        # for VCN attachments
                        if columnvalues[0].strip().lower() == "vcn":
                            vcn_name = columnvalues[1].strip()
                            vcn_tf_name = commonTools.check_tf_variable(vcn_name)

                            # Get DRG Attach Name
                            drg_attach_name=''
                            if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
                                with open(outdir + "/" + region + "/obj_names.safe") as f:
                                    for line in f:
                                        if ("drgattachinfo::::" + vcn_name + "::::" + drg_name in line):
                                            drg_attach_name = line.split("::::")[3].strip()
                                            break
                            if (drg_attach_name == ""):
                                drg_attach_name = drg_name + "_"+vcn_name+"_attach"

                            tempStr['drg_attach_display_name'] = drg_attach_name
                            drg_attach_tf_name = commonTools.check_tf_variable(drg_attach_name)

                            tempStr['drg_attach_tf_name'] = drg_attach_tf_name
                            tempStr['network_type'] = "VCN"
                            tempStr['network_id'] = vcn_tf_name

                            #DRG v1
                            tempStr['vcn_id'] = vcn_tf_name

                            tempStr.update(tempdict)
                            # Get VCN DRG RT table
                            vcn_drg_rt_name = ""
                            if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
                                with open(outdir + "/" + region + "/obj_names.safe") as f:
                                    for line in f:
                                        if ("drginfo::::" + vcn_name + "::::" + drg_name in line):
                                            vcn_drg_rt_name = line.split("::::")[3].strip()
                                            break
                            if (vcn_drg_rt_name == ""):
                                vcn_drg_rt_var = vcn_name + "_Route Table associated with DRG-" + drg_name
                            # Route table associated with DRG inside VCN is not existing
                            elif (vcn_drg_rt_name == "None"):
                                vcn_drg_rt_var = ""
                            else:
                                vcn_drg_rt_var = vcn_name + "_" + vcn_drg_rt_name

                            if (vcn_drg_rt_var != ""):
                                vcn_drg_rt_tf_name = commonTools.check_tf_variable(vcn_drg_rt_var)
                            else:
                                vcn_drg_rt_tf_name = ""
                            tempStr['vcn_drg_rt_tf_name'] = vcn_drg_rt_tf_name

                        # for other attachments
                        else:
                            drg_attach_name = drg_name +"_"+columnvalues[0].strip()+"_"+str(ip)+"_attach"
                            ip=ip+1
                            tempStr['drg_attach_display_name'] = drg_attach_name
                            drg_attach_tf_name = commonTools.check_tf_variable(drg_attach_name)
                            tempStr['drg_attach_tf_name'] = drg_attach_tf_name
                            tempdict['network_type'] = columnvalues[0].strip().upper()
                            # push the OCID of IP Sec or RPC or FC
                            tempStr['network_id'] = columnvalues[1].strip()

                if columnname == 'DRG RT Name':
                    #if it is Auto Generated RT(during export) dont attach any RT to DRG attachment
                    if(columnvalue in commonTools.drg_auto_RTs):
                        drg_rt_tf_name = ''
                    elif(columnvalue!=''):
                        drg_rt_tf_name = commonTools.check_tf_variable(drg_name + "_" + columnvalue)
                    tempStr['drg_rt_tf_name'] = drg_rt_tf_name

                columnname = commonTools.check_column_headers(columnname)
                tempStr[columnname] = str(columnvalue).strip()
                tempStr.update(tempdict)

            if region not in region_included_drg:
                drg_attach_skeleton = drg_attach_template.render(skeleton=True, count=0)[:-1]
                drgstr_skeleton = drg_template.render(count=0)[:-1]
                region_included_drg.append(region)

            tempStr['drg_version'] = drg_versions[region, drg_name]
            drgstr = drg_template.render(tempStr)

            if(attachedto=="attached"):
                drg_attach = drg_attach_template.render(tempStr)
            elif(attachedto=="empty"):
                drg_attach=""

            if (drgstr not in drg_tfStr[region]):
                drg_tfStr[region] = drg_tfStr[region][:-1] + drgstr #+ drg_attach
            if (drg_attach not in drg_attach_tfStr[region]):
                drg_attach_tfStr[region] = drg_attach_tfStr[region][:-1] + drg_attach
            # else:
            #     tfStr[region] = tfStr[region] + drg_attach
        for region in ct.all_regions:
            if region in region_included_drg:
                drg_attach_tfStr[region] = drg_attach_skeleton + drg_attach_tfStr[region]
                drg_tfStr[region] = drgstr_skeleton + drg_tfStr[region]

    def processVCN(tempStr):
        rt_tf_name = ''
        count_spokes = 0
        region = tempStr['region'].lower().strip()
        vcn_name = tempStr['vcn_name'].strip()
        vcn_tf_name = commonTools.check_tf_variable(vcn_name)
        vcn_drg = tempStr['drg_required'].strip()
        vcn_igw = tempStr['igw_required'].strip()
        vcn_ngw = tempStr['ngw_required'].strip()
        vcn_sgw = tempStr['sgw_required'].strip()
        vcn_lpg = tempStr['lpg_required']
        tempStr['vcn_tf_name'] = vcn_tf_name
        #vcn_lpg = tempStr['lpg_required'].strip()
        hub_spoke_none = tempStr['hub_spoke_peer_none'].strip()
        compartment_var_name = str(tempStr['compartment_name']).strip()

        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
        vcn_dns_label = tempStr['dns_label'].lower().strip()
        lpg = env.get_template('major-objects-lpgs-template')

        # Create TF object for default DHCP options
        dhcpname = vcn_name + "_Default DHCP Options for " + vcn_name
        dhcp_tf_name = commonTools.check_tf_variable(dhcpname)
        tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name, 'dhcp_tf_name': dhcp_tf_name,
                    'server_type': 'VcnLocalPlusInternet'}

        tempStr.update(tempdict)

        if vcn_igw != "n":
            # use default name
            if (vcn_igw == "y"):
                igw_name = vcn_name + "_igw"
                tempStr['igw_name'] = igw_name

            # use name provided in input
            else:
                igw_name = vcn_igw
                tempStr['igw_name'] = igw_name

            igw_tf_name = vcn_name + "_" + igw_name
            igw_tf_name = commonTools.check_tf_variable(igw_tf_name)

            tempStr['igw_tf_name'] = igw_tf_name
            tempStr.update(tempdict)

        if vcn_sgw != "n":
            # use default name
            if (vcn_sgw == "y"):
                sgw_name = vcn_name + "_sgw"
            # use name provided in input
            else:
                sgw_name = vcn_sgw
            sgw_tf_name = vcn_name + "_" + sgw_name
            sgw_tf_name = commonTools.check_tf_variable(sgw_tf_name)

            tempStr['sgw_tf_name'] = sgw_tf_name
            tempStr['sgw_name'] = sgw_name
            tempStr['sgw_required'] = tempStr['sgw_required'].lower().strip()

        if vcn_ngw != 'n':
            # use default name
            if (vcn_ngw == "y"):
                ngw_name = vcn_name + "_ngw"
            # use name provided in input
            else:
                ngw_name = vcn_ngw
            ngw_tf_name = vcn_name + "_" + ngw_name
            ngw_tf_name = commonTools.check_tf_variable(ngw_tf_name)

            tempStr['ngw_name'] = ngw_name
            tempStr['ngw_tf_name'] = ngw_tf_name
            tempStr['ngw_required'] = tempStr['ngw_required'].lower().strip()

        if (vcn_lpg != 'n'):
            count_lpg = 0

            if (hub_spoke_none.lower() == 'hub'):
                spoke_vcns = vcns.peering_dict[vcn_name,region].split(",")
                count_spokes = len(spoke_vcns)

            for lpg_name in vcns.vcn_lpg_names[vcn_name,region]:
                count_lpg = count_lpg + 1
                lpg_tf_name = vcn_name + "_" + lpg_name
                lpg_tf_name = commonTools.check_tf_variable(lpg_tf_name)
                tempStr['count_lpg'] = count_lpg
                tempStr['lpg_tf_name'] = lpg_tf_name
                tempStr['lpg_name'] = lpg_name
                tempStr['vcn_tf_name'] = vcn_tf_name
                tempStr['lpg_required'] = tempStr['lpg_required']

                rt_var = ''
                if (hub_spoke_none.lower() == 'hub' or 'peer' in hub_spoke_none.lower() ) :
                    lpg_rt_name = ""
                    if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
                        with open(outdir + "/" + region + "/obj_names.safe") as f:
                            for line in f:
                                if ("lpginfo::::" + vcn_name + "::::" + lpg_name in line):
                                    lpg_rt_name = line.split("::::")[3].strip()

                    if (lpg_rt_name != ""):
                        rt_var = vcn_name + "_" + lpg_rt_name
                    elif (count_lpg <= count_spokes):
                        rt_var = vcn_name + "_Route Table associated with LPG-" + lpg_name

                    else:
                        rt_var = ""

                    if(rt_var!=""):
                        rt_tf_name = commonTools.check_tf_variable(rt_var)
                    else:
                        rt_tf_name=""

                    tempStr['rt_tf_name'] = rt_tf_name

                    if ('hub' in hub_spoke_none.lower()):
                        hub_lpg_tfStr[region] = hub_lpg_tfStr[region] + lpg.render(tempStr)
                    elif ('peer' in hub_spoke_none.lower()):
                        peer_lpg_tfStr[region] = peer_lpg_tfStr[region] + lpg.render(tempStr)
                elif ('spoke' in hub_spoke_none.lower()):
                    spoke_lpg_tfStr[region] = spoke_lpg_tfStr[region] + lpg.render(tempStr)
                elif ('none' in hub_spoke_none.lower()):
                    none_lpg_tfStr[region] = none_lpg_tfStr[region] + lpg.render(tempStr)
                else:
                    exported_lpg_tfStr[region] = exported_lpg_tfStr[region] + lpg.render(tempStr)


        lpg_tfStr[region] = lpg.render(create_lpg_auto_vars=True,hub_lpg_details=hub_lpg_tfStr[region],peer_lpg_details=peer_lpg_tfStr[region],spoke_lpg_details=spoke_lpg_tfStr[region],exported_lpg_details=exported_lpg_tfStr[region],none_lpg_details=none_lpg_tfStr[region])

        defaultdhcp = env.get_template('major-objects-default-dhcp-template')
        dhcp_default_tfStr[region] = dhcp_default_tfStr[region][:-1] + defaultdhcp.render(tempStr)

        vcn = env.get_template('major-objects-vcns-template')
        vcn_tfStr[region] = vcn_tfStr[region][:-1] + vcn.render(tempStr)

        igws = env.get_template('major-objects-igws-template')
        igw_tfStr[region] = igw_tfStr[region][:-1] + igws.render(tempStr)

        ngws = env.get_template('major-objects-ngws-template')
        ngw_tfStr[region] = ngw_tfStr[region][:-1] + ngws.render(tempStr)

        sgws = env.get_template('major-objects-sgws-template')
        sgw_tfStr[region] = sgw_tfStr[region][:-1] + sgws.render(tempStr)

    # Get vcns object from commonTools
    vcns = parseVCNs(filename)
    drgv2 = parseDRGs(filename)

    for reg in ct.all_regions:
        tfStr[reg] = ''
        drg_tfStr[reg] = ''
        drg_attach_tfStr[reg] = ''
        igw_tfStr[reg] = ''
        lpg_tfStr[reg] = ''
        hub_lpg_tfStr[reg] = ''
        peer_lpg_tfStr[reg] = ''
        spoke_lpg_tfStr[reg] = ''
        none_lpg_tfStr[reg] = ''
        exported_lpg_tfStr[reg] = ''
        vcn_tfStr[reg] = ''
        dhcp_default_tfStr[reg] = ''
        sgw_tfStr[reg] = ''
        ngw_tfStr[reg] = ''
        dhcpStr[reg] = ''
        drg_data[reg] = ''
        drg_rt_data[reg] = ''
        drg_rd_data[reg] = ''

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "VCNs")
    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    region_included = []

    # Process VCNs
    for i in df.index:
        region = str(df['Region'][i])
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'VCN Name']).lower() == 'nan' or
                str(df.loc[i, 'CIDR Blocks']).lower() == 'nan' or str(df.loc[i, 'DRG Required']).lower() == 'nan' or str(
                    df.loc[i, 'IGW Required']).lower() == 'nan' or
                str(df.loc[i, 'NGW Required']).lower() == 'nan' or str(
                    df.loc[i, 'SGW Required']).lower() == 'nan' or str(df.loc[i, 'LPG Required']).lower() == 'nan' or
                str(df.loc[i, 'Hub/Spoke/Peer/None']).lower() == 'nan'):
            print("\nColumn Values(except dns_label) or Rows cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()
            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined Tags and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == "CIDR Blocks":
                cidr_blocks = [x.strip() for x in columnvalue.split(',')]
                # reverses the order while exporting into excel so use reverse to avoid terraform change
                if(non_gf_tenancy):
                    cidr_blocks.reverse()
                cidr_blocks = json.dumps(cidr_blocks)
                tempdict = {'cidr_blocks': cidr_blocks}

            if columnname == "DNS Label":
                # check if vcn_dns_label is not given by user in input use vcn name
                if str(columnvalue).lower() == 'nan' or str(columnvalue).lower() == '':
                    regex = re.compile('[^a-zA-Z0-9]')
                    vcn_dns = regex.sub('', df.loc[i, 'VCN Name'])
                    # truncate all digits from start of dns_label
                    index = 0
                    for c in vcn_dns:
                        if c.isdigit() == True:
                            index = index + 1
                            continue
                        else:
                            break
                    vcn_dns = vcn_dns[index:]
                    vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns
                    tempdict = {'dns_label': vcn_dns_label, 'vcn_dns': vcn_dns}
                else:
                    tempdict = {'dns_label': columnvalue.strip() }

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        tempStr.update({'count': 1})
        if region not in region_included:
            tempStr.update({'count': 0})
            region_included.append(region)

        processVCN(tempStr)

    create_drg_and_attachments(inputfile, outdir, config)

    #Write outfiles
    for reg in ct.all_regions:

        if modify_network:
            tfStr[reg] = vcn_tfStr[reg] + igw_tfStr[reg] + ngw_tfStr[reg] + sgw_tfStr[reg] + lpg_tfStr[reg] + drg_tfStr[reg] + drg_attach_tfStr[reg]
            reg_out_dir = outdir + "/" + reg

            if not os.path.exists(reg_out_dir):
                os.makedirs(reg_out_dir)

            # outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
            outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename
            outfile_dhcp[reg] = reg_out_dir + "/" + prefix + dhcp_auto_tfvars_filename
            outfile_oci_drg_data[reg] = reg_out_dir + "/" + prefix + drg_data_tfvars_filename

            srcdir = reg_out_dir + "/"
            resource = 'major-objects'
            # commonTools.backup_file(srcdir, resource, "-major-objs.tf")
            commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
            commonTools.backup_file(srcdir, resource, dhcp_auto_tfvars_filename)
            commonTools.backup_file(srcdir, resource, drg_data_tfvars_filename)

            if tfStr[reg] != '':
                oname[reg] = open(outfile[reg], "w+")
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " for major objects has been updated for region " + reg)

            if dhcp_default_tfStr[reg] != '':
                oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w+")
                oname_def_dhcp[reg].write(dhcp_default_tfStr[reg])
                oname_def_dhcp[reg].close()
                print(outfile_dhcp[reg] + " for default DHCP options for VCNs has been updated for region " + reg)

            if drg_data[reg] != '':
                oname_oci_drg_data[reg]=open(outfile_oci_drg_data[reg], "w+")
                oname_oci_drg_data[reg].write(drg_data[reg])
                oname_oci_drg_data[reg].close()
                print(outfile_oci_drg_data[reg] + " for oci-drg-data for DRGs has been updated for region " + reg)


        else:


            tfStr[reg] = vcn_tfStr[reg] + igw_tfStr[reg] + ngw_tfStr[reg] + sgw_tfStr[reg] + lpg_tfStr[reg] + drg_tfStr[reg] + drg_attach_tfStr[reg]

            reg_out_dir = outdir + "/" + reg

            if not os.path.exists(reg_out_dir):
                os.makedirs(reg_out_dir)

            srcdir = reg_out_dir + "/"
            resource = 'major-objects'

            outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename
            outfile_dhcp[reg] = reg_out_dir + "/" + prefix + dhcp_auto_tfvars_filename
            outfile_oci_drg_data[reg] = reg_out_dir + "/" + prefix + drg_data_tfvars_filename

            if drg_data[reg] != '':
                commonTools.backup_file(srcdir, resource, drg_data_tfvars_filename)

                oname_oci_drg_data[reg] = open(outfile_oci_drg_data[reg], "w+")
                oname_oci_drg_data[reg].write(drg_data[reg])
                oname_oci_drg_data[reg].close()
                print(outfile_oci_drg_data[reg] + " for oci-drg-data for DRGs has been updated for region " + reg)

            if non_gf_tenancy:
                pass
            else:
                if (dhcp_default_tfStr[reg] != ''):
                    commonTools.backup_file(srcdir, resource, dhcp_auto_tfvars_filename)

                    oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w+")
                    oname_def_dhcp[reg].write(dhcp_default_tfStr[reg])
                    oname_def_dhcp[reg].close()
                    print(outfile_dhcp[reg] + " for default DHCP options for VCNs has been created for region " + reg)

            if (tfStr[reg] != ''):
                commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

                tfStr[reg] = tfStr[reg]
                oname[reg] = open(outfile[reg], 'w+')
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " for major objects has been created for region " + reg)

    establishPeering(vcns.peering_dict)

if __name__ == '__main__':
    args = parse_args()
    create_major_objects(args.inputfile, args.outdir, prefix=args.prefix, non_gf_tenancy=args.non_gf_tenancy, modify_network=args.modify_network, config=args.config)

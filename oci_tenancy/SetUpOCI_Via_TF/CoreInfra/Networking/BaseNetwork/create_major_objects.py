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
import datetime
import shutil
import os
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../../..")
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
    parser.add_argument('--modify-network', action='store_true', help='modify network')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()




def create_major_objects(inputfile, outdir, prefix, config, modify_network=False):
    # Declare Variables
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tfStr = {}
    drg_data = {}
    dhcpStr = {}
    outfile_dhcp = {}
    outfile_oci_drg_data = {}
    oname_def_dhcp = {}
    oname_oci_drg_data = {}
    oname_datafile = {}

    global dhcp_data


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    datasource = env.get_template('data-source-template')
    defaultdhcp = env.get_template('default-dhcp-template')


    # Function to establish peering between LPGs
    def establishPeering(peering_dict):
        for left_vcn, value in peering_dict.items():
            region = vcns.vcn_region[left_vcn]
            outfile = outdir + "/" + region + "/" + prefix + '-major-objs.tf'

            right_vcns = value.split(",")

            for right_vcn in right_vcns:
                if (right_vcn == ""):
                    continue
                right_vcn = right_vcn.strip()
                right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)

                try:
                    if (vcns.vcn_lpg_names[left_vcn][0].lower() == 'n' or vcns.vcn_lpg_names[right_vcn][0].lower() == 'n'):
                        print( "\nERROR!!! Cannot specify n for lpg_required field of VCN if it is part of VCN peering..Exiting!")
                        exit(1)
                except IndexError:

                    print("\nERROR!!! Insufficient LPGs declared for either " + left_vcn + " or " + right_vcn + ". Check lpg_required column in VCNs tab..Exiting!")
                    exit(1)
                searchString = """##peer_id for lpg """ + left_vcn + "_" + vcns.vcn_lpg_names[left_vcn][0] + "##"
                vcns.vcn_lpg_names[left_vcn].pop(0)
                lpg_name = vcns.vcn_lpg_names[right_vcn][0]
                lpg_tf_name = right_vcn + "_" + lpg_name
                lpg_tf_name = commonTools.check_tf_variable(lpg_tf_name)

                peerStr = """peer_id = oci_core_local_peering_gateway.""" + lpg_tf_name + """.id"""
                vcns.vcn_lpg_names[right_vcn].pop(0)

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

        # Load the template file
        file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
        env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        drg_template = env.get_template('major-objects-drg-template')
        drg_attach_template = env.get_template('major-objects-drg-attach-template')
        drg_datasource_template = env.get_template('drg-data-source-template')

        # Create drg-oci-data
        for region in drgv2.drg_names.keys():
            for drg in drgv2.drg_names[region]:
                for drg_auto_rt_name in commonTools.drg_auto_RTs:
                    temp = {}
                    drg_auto_rt_tf_name = commonTools.check_tf_variable(drg + "_" + drg_auto_rt_name)
                    temp['drg_auto_rt_tf_name'] = drg_auto_rt_tf_name
                    temp['drg_auto_rt_name'] = drg_auto_rt_name
                    temp['drg_tf_name'] = commonTools.check_tf_variable(drg)
                    drg_data[region] = drg_data[region] + drg_datasource_template.render(temp)

                for drg_auto_rd_name in commonTools.drg_auto_RDs:
                    temp = {}
                    drg_auto_rd_tf_name = commonTools.check_tf_variable(drg + "_" + drg_auto_rd_name)
                    temp['drg_auto_rd_tf_name'] = drg_auto_rd_tf_name
                    temp['drg_auto_rd_name'] = drg_auto_rd_name
                    temp['drg_tf_name'] = commonTools.check_tf_variable(drg)
                    drg_data[region] = drg_data[region] + drg_datasource_template.render(temp)

        # Read cd3 using pandas dataframe
        df, col_headers = commonTools.read_cd3(filename, "DRGv2")
        # Remove empty rows
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)


        # List of the column headers
        dfcolumns = df.columns.values.tolist()

        for i in df.index:
            region = str(df['Region'][i]).strip()
            comp_name = str(df['Compartment Name'][i]).strip()
            drg = str(df['DRG Name'][i]).strip()


            if (region.lower()=='nan' or comp_name.lower()=='nan' or drg.lower()=='nan'):
                print("\nERROR!!! Columns Region/Compartment Name/DRG Name can not be empty..Exiting!")
                exit(1)

            if (region in commonTools.endNames):
                break
            region = region.strip().lower()
            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            if drg not in vcns.vcns_having_drg.values():
                print("\nERROR!!! Invalid DRG Name. It should be one of the values defined in VCNs tab..Exiting!")
                exit(1)

            attached_to = str(df['Attached To'][i]).strip()
            attached_to = attached_to.split("::")
            if(len(attached_to)==2):
                if attached_to[0].strip().upper() == "VCN":
                    vcn_name = attached_to[1].strip()
                    if (vcn_name.lower() != "nan" and vcns.vcns_having_drg[vcn_name,region] != drg):
                        print("ERROR!!! VCN "+vcn_name +" in column Attached To is not as per DRG Required column of VCNs Tab..Exiting!")
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
                        tempStr['network_id'] = "oci_core_vcn." + vcn_tf_name + ".id"

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

            drgstr = drg_template.render(tempStr)
            drg_attach = drg_attach_template.render(tempStr)

            if (drgstr not in tfStr[region]):
                tfStr[region] = tfStr[region] + drgstr + drg_attach
            else:
                tfStr[region] = tfStr[region] + drg_attach

    def processVCN(tempStr):
        igw = ''
        ngw = ''
        sgw = ''
        rt_tf_name = ''
        lpgdata = ''
        region = tempStr['region'].lower().strip()
        vcn_name = tempStr['vcn_name'].strip()
        vcn_tf_name = commonTools.check_tf_variable(vcn_name)
        vcn_drg = tempStr['drg_required'].strip()
        vcn_igw = tempStr['igw_required'].strip()
        vcn_ngw = tempStr['ngw_required'].strip()
        vcn_sgw = tempStr['sgw_required'].strip()
        vcn_lpg = tempStr['lpg_required'].strip()
        hub_spoke_none = tempStr['hub_spoke_peer_none'].strip()
        compartment_var_name = str(tempStr['compartment_name']).strip()

        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
        vcn_dns_label = tempStr['dns_label'].lower().strip()

        # Create TF object for default DHCP options
        dhcpname = vcn_name + "_Default DHCP Options for " + vcn_name
        dhcp_tf_name = commonTools.check_tf_variable(dhcpname)
        tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name, 'dhcp_tf_name': dhcp_tf_name,
                    'server_type': 'VcnLocalPlusInternet'}

        tempStr.update(tempdict)

        dhcp_default = defaultdhcp.render(tempStr)

        vcn = env.get_template('major-objects-vcn-template')
        vcn = vcn.render(tempStr)


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

            igw = env.get_template('major-objects-igw-template')
            igw = igw.render(tempStr)

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

            sgw = env.get_template('major-objects-sgw-template')
            sgw = sgw.render(tempStr)

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

            ngw = env.get_template('major-objects-ngw-template')
            ngw = ngw.render(tempStr)

        if (vcn_lpg != 'n'):
            count_lpg = 0

            if (hub_spoke_none == 'hub'):
                spoke_vcns = vcns.peering_dict[vcn_name].split(",")
                count_spokes = len(spoke_vcns)

            for lpg_name in vcns.vcn_lpg_names[vcn_name]:

                count_lpg = count_lpg + 1
                lpg_tf_name = vcn_name + "_" + lpg_name
                lpg_tf_name = commonTools.check_tf_variable(lpg_tf_name)

                tempStr['lpg_tf_name'] = lpg_tf_name
                tempStr['lpg_name'] = lpg_name
                tempStr['vcn_tf_name'] = vcn_tf_name
                tempStr['lpg_required'] = tempStr['lpg_required'].lower().strip()

                rt_var = ''
                if (hub_spoke_none == 'hub'):
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

                    rt_tf_name = commonTools.check_tf_variable(rt_var)

                tempStr['rt_tf_name'] = rt_tf_name

                tempStr['rt_var'] = rt_var

                lpg = env.get_template('major-objects-lpg-template')
                lpg = lpg.render(tempStr)
                lpgdata = lpgdata + lpg

        #if(drg not in tfStr[region]):
        tfStr[region] = tfStr[region] + igw + ngw + sgw + lpgdata + vcn
        #else:
        #    tfStr[region] = tfStr[region] + igw + ngw + sgw +drg_attach+ lpgdata + vcn
        dhcpStr[region] = dhcpStr[region] + dhcp_default

    # Get vcns object from commonTools
    vcns = parseVCNs(filename)
    drgv2 = parseDRGv2(filename)

    for reg in ct.all_regions:
        tfStr[reg] = ''
        dhcpStr[reg] = ''
        drg_data[reg] = ''

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "VCNs")
    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

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
                str(df.loc[i, 'CIDR Block']).lower() == 'nan' or str(df.loc[i, 'DRG Required']).lower() == 'nan' or str(
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

        processVCN(tempStr)

    create_drg_and_attachments(inputfile, outdir, config)

    #Write outfiles
    if modify_network:
        for reg in ct.all_regions:
            reg_out_dir = outdir + "/" + reg

            if not os.path.exists(reg_out_dir):
                os.makedirs(reg_out_dir)

            outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
            outfile_dhcp[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"
            outfile_oci_drg_data[reg] = reg_out_dir + "/oci-drg-data.tf"

            srcdir = reg_out_dir + "/"
            resource = 'MajorObjects'
            commonTools.backup_file(srcdir, resource, "-major-objs.tf")
            commonTools.backup_file(srcdir, resource, "/VCNs_Default_DHCP.tf")
            commonTools.backup_file(srcdir, resource, "/oci-drg-data.tf")


            oname[reg] = open(outfile[reg], "w")
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for major objects has been updated for region " + reg)

            oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w")
            oname_def_dhcp[reg].write(dhcpStr[reg])
            oname_def_dhcp[reg].close()
            print(outfile_dhcp[reg] + " containing TF for default DHCP options for VCNs has been updated for region " + reg)

            oname_oci_drg_data[reg]=open(outfile_oci_drg_data[reg], "w")
            oname_oci_drg_data[reg].write(drg_data[reg])
            oname_oci_drg_data[reg].close()
            print(outfile_oci_drg_data[reg] + " containing TF for oci-drg-data for DRGs has been updated for region " + reg)


    else:
        for reg in ct.all_regions:
            reg_out_dir = outdir + "/" + reg

            if not os.path.exists(reg_out_dir):
                os.makedirs(reg_out_dir)

            srcdir = reg_out_dir + "/"
            resource = 'MajorObjects'
            commonTools.backup_file(srcdir, resource, "-major-objs.tf")
            commonTools.backup_file(srcdir, resource, "/VCNs_Default_DHCP.tf")
            commonTools.backup_file(srcdir, resource, "/oci-drg-data.tf")

            outfile[reg] = reg_out_dir + "/" + prefix + '-major-objs.tf'
            outfile_dhcp[reg] = reg_out_dir + "/VCNs_Default_DHCP.tf"
            outfile_oci_drg_data[reg] = reg_out_dir + "/oci-drg-data.tf"

            oname_datafile[reg] = open(reg_out_dir + "/oci-data.tf", "w")
            datastr = datasource.render()
            oname_datafile[reg].write(datastr)
            print(reg_out_dir + "/oci-data.tf" + " containing TF for oci-data has been created for region " + reg)

            oname_oci_drg_data[reg] = open(outfile_oci_drg_data[reg], "w")
            oname_oci_drg_data[reg].write(drg_data[reg])
            oname_oci_drg_data[reg].close()
            print(outfile_oci_drg_data[
                      reg] + " containing TF for oci-drg-data for DRGs has been updated for region " + reg)

            if (dhcpStr[reg] != ''):
                oname_def_dhcp[reg] = open(outfile_dhcp[reg], "w")
                oname_def_dhcp[reg].write(dhcpStr[reg])
                oname_def_dhcp[reg].close()
                print(outfile_dhcp[reg] + " containing TF for default DHCP options for VCNs has been created for region " + reg)

            if (tfStr[reg] != ''):
                tfStr[reg] = tfStr[reg]
                oname[reg] = open(outfile[reg], 'w')
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " containing TF for VCN major objects has been created for region " + reg)

    establishPeering(vcns.peering_dict)

if __name__ == '__main__':
    args = parse_args()
    create_major_objects(args.inputfile, args.outdir, args.prefix, args.config, args.modify_network)

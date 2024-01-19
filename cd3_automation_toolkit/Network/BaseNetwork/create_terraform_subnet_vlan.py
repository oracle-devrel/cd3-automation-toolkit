#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Subnets
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import re
import os
sys.path.append(os.getcwd()+"/../../..")
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_subnet_vlan(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, network_vlan_in_setupoci, modify_network=False):
    filename = inputfile

    fname = None
    outfile={}
    vlan_outfile={}
    oname={}
    tfStr={}
    tfStr_vlan={}
    skeletonStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('subnet-template')
    vlan_template = env.get_template('vlan-template')
    auto_tfvars_filename = '_subnets.auto.tfvars'
    vlan_auto_tfvars_filename = '_vlans.auto.tfvars'
    region_included = []

    def processSubnet(tempStr):
        region = tempStr['region'].lower().strip()
        AD = tempStr['availability_domain'].strip()
        if (AD.strip().lower() != 'regional'):
            AD = AD.strip().upper()
            ad = ADS.index(AD)
            adString = ad
        else:
            adString = ""

        tempStr['availability_domain'] = adString

        vcn_tf_name = commonTools.check_tf_variable(tempStr['vcn_name'].strip())
        name = tempStr['display_name']

        tempStr['vcn_tf_name'] = vcn_tf_name

        display_name = name
        rt_display_name = rt_name

        tempStr['display_name'] = display_name
        tempStr['rt_display_name'] = rt_display_name

        subnet_tf_name = vcn_name + "_" + display_name
        subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)

        if rt_display_name != 'n':
            rt_tf_name = vcn_name + "_" + rt_display_name
            rt_tf_name = commonTools.check_tf_variable(rt_tf_name)
        else:
            rt_tf_name = ""

        tempStr['subnet_tf_name'] = subnet_tf_name
        tempStr['rt_tf_name'] = rt_tf_name

        sl_tf_names=[]
        seclist_names = tempStr['sl_names']
        for sl_name in seclist_names:
            sl_name = str(sl_name).strip()
            sl_display_name = str(sl_name)
            sl_tf_name = vcn_name + "_" + sl_display_name
            sl_tf_names.append(commonTools.check_tf_variable(sl_tf_name))

        seclist_ids=""
        add_default_seclist =  tempStr['add_default_seclist'].strip()

        #Attach Default Security List
        if add_default_seclist.strip() == "y":
                seclist_ids = "\"\""
                tempStr['seclist_ids'] = seclist_ids


        #Attach other security list IDs
        if( seclist_names[0]  !="n"):
            index=0
            for seclist_id in sl_tf_names:
                if(index==len(sl_tf_names)-1):
                    seclist_ids = seclist_ids + "," + "\""+commonTools.check_tf_variable(str(seclist_id))+"\""
                else:
                    seclist_ids = seclist_ids + "," + "\""+commonTools.check_tf_variable(str(seclist_id))+"\""
                index=index+1
        tempStr['seclist_ids'] = seclist_ids.lstrip(",")

        if (tempStr['dhcp_tf_name'].lower() != 'nan' and tempStr['dhcp_tf_name'] != '' and tempStr['dhcp_tf_name'] != 'n'):
            dhcp_options_id = commonTools.check_tf_variable(tempStr['dhcp_tf_name'].strip())
        else:
            dhcp_options_id = ""
        tempStr['dhcp_options_name'] = dhcp_options_id

        if tempStr['type'] == 'public':
            prohibit_public_ip_on_vnic = "false"
        else:
            prohibit_public_ip_on_vnic = "true"
        tempStr['prohibit_public_ip_on_vnic'] = prohibit_public_ip_on_vnic

        tfStr[region]= tfStr[region] +"\n"+ template.render(tempStr)


    def processVlan(tempStr):
        region = tempStr['region'].lower().strip()
        AD = tempStr['availability_domain'].strip()
        if (AD.strip().lower() != 'regional'):
            AD = AD.strip().upper()
            ad = ADS.index(AD)
            adString = ad
        else:
            adString = ""

        tempStr['availability_domain'] = adString

        vcn_name = tempStr['vcn_name'].strip()
        name = tempStr['display_name']
        display_name = name
        rt_display_name = rt_name

        tempStr['display_name'] = display_name
        tempStr['rt_display_name'] = rt_display_name

        vlan_tf_name = vcn_name + "_" + display_name
        vlan_tf_name = commonTools.check_tf_variable(vlan_tf_name)
        tempStr['vlan_tf_name'] = vlan_tf_name


        '''
        nsg_names = tempStr['nsg_names']
        for nsg_name in nsg_names:
            nsg_name = str(nsg_name).strip()
            nsg_display_name = str(nsg_name)
        '''

        tfStr_vlan[region]= tfStr_vlan[region] +"\n"+ vlan_template.render(tempStr)

    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "SubnetsVLANs")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in ct.all_regions:
        tfStr[reg] = ''
        skeletonStr[reg] = ''
        tfStr_vlan[reg] = ''

    # temporary dictionary1, dictionary2
    tempStr = {}
    tempdict = {}

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        region=str(df.loc[i,'Region'])

        if (region in commonTools.endNames):
            break

        region=region.strip().lower()

        compartment_var_name = df.loc[i, 'Compartment Name']
        vcn_name=str(df['VCN Name'][i]).strip()
        check = vcn_name.strip(), region

        if (check not in vcns.vcn_names):
            print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
            exit(1)

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                        df.loc[i, 'VCN Name']).lower() == 'nan' or str(df.loc[i, 'Display Name']).lower() == 'nan' or str(df.loc[i, 'CIDR Block']).lower() == 'nan'):
            print("\nColumn Values Region, Compartment Name, VCN Name, Display Name and CIDR Block cannot be left empty in SubnetsVLANs sheet in CD3..exiting...")
            exit(1)


        if (str(df.loc[i, 'Configure IGW Route(y|n)']).lower() == 'nan' or str(df.loc[i, 'Configure NGW Route(y|n)']).lower() == 'nan' or str(
                        df.loc[i, 'Configure SGW Route(n|object_storage|all_services)']).lower() == 'nan' or str(df.loc[i, 'Configure OnPrem Route(y|n)']).lower() == 'nan' or str(
                        df.loc[i,'Configure VCNPeering Route(y|n)']).lower() == 'nan'):
            print("\nColumn Values Configure IGW/SGW/On-Prem/VCN route cannot be left empty in SubnetsVLANs sheet in CD3..exiting...")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process the Freefrorm and Defined Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Availability Domain(AD1|AD2|AD3|Regional)':
                columnname = 'availability_domain'
                tempdict = {'availability_domain': columnvalue}


            if columnname == 'Add Default Seclist':
                if columnvalue.lower() == 'nan':
                    columnvalue = 'y'

            if columnname == 'DHCP Option Name':
                columnname = 'dhcp_options_name'
                if str(columnvalue).strip().lower() != '' and str(columnvalue).strip().lower() != 'n':
                    dhcp = df.loc[i,'VCN Name'].strip() +"_" + columnvalue
                    dhcp = commonTools.check_tf_variable(dhcp)
                    tempdict = {'dhcp_tf_name': dhcp,'dhcp_options_name' : columnvalue}
                else:
                    tempdict = {'dhcp_tf_name': columnvalue, 'dhcp_options_name': columnvalue}

            if columnname == 'DNS Label':
                dnslabel = columnvalue.strip()
                # check if subnet_dns_label is not given by user in input use subnet name
                if (str(dnslabel).lower() == 'nan' or str(dnslabel).lower() == ''):
                    regex = re.compile('[^a-zA-Z0-9]')
                    subnet_dns = regex.sub('', df.loc[i,'Display Name'])
                    # truncate all digits from start of dns_label
                    index = 0
                    for c in subnet_dns:
                        if c.isdigit() == True:
                            index = index + 1
                            continue
                        else:
                            break
                    subnet_dns = subnet_dns[index:]
                    dnslabel = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns
                    tempdict = {'dns_label': dnslabel, 'subnet_dns': subnet_dns}
                elif dnslabel.lower() == 'n':
                    dnslabel = ''
                    tempdict = {'dns_label': dnslabel}
                else:
                    tempdict = {'dns_label': dnslabel}

            if columnname == 'Route Table Name':
                rt_name = columnvalue
                if (str(rt_name).lower() == 'nan' or str(rt_name).lower() == ''):
                    # route table name not provided; use subnet name as route table name
                    rt_name = str(df.loc[i,'Display Name']).strip()
                    tempdict = {'rt_name': rt_name}
                else:
                    rt_name = columnvalue.strip()
                    tempdict = {'rt_name': rt_name}
                tempStr.update(tempdict)

            sl_names = []
            if columnname == 'Seclist Names':
                if str(columnvalue).lower() == 'nan' or str(columnvalue).lower() == '':
                    # seclist name not provided; use subnet name as seclist name
                    sl_names.append(df.loc[i,'Display Name'].strip())
                    tempdict = {'sl_names': sl_names}
                else:
                    sl_names = columnvalue.split(",")
                    tempdict = {'sl_names': sl_names}

                tempStr.update(tempdict)

            if columnname == 'NSGs':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg = ""
                    nsg_str = ""

                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg = "\"" + NSGs[k].strip() + "\""
                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    tempdict = {'nsg_ids': nsg_str}
                    tempStr.update(tempdict)
                else:
                    tempdict = {'nsg_ids': ''}
                    tempStr.update(tempdict)

            if columnname == 'Type(private|public)':
                columnname = 'type'
                columnvalue = columnvalue.lower()

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        subnet_vlan_in_excel = str(df.loc[i,'Subnet or VLAN']).strip()

        if network_vlan_in_setupoci=="network" and subnet_vlan_in_excel.lower().startswith('subnet'):
            processSubnet(tempStr)
        elif network_vlan_in_setupoci=="vlan" and subnet_vlan_in_excel.lower().startswith('vlan'):
            vlan_details = subnet_vlan_in_excel.split("::")
            if len(vlan_details)==2:
                vlan_tag = vlan_details[1]
            else:
                vlan_tag = ""
            tempdict = {'vlan_tag': vlan_tag}
            tempStr.update(tempdict)
            processVlan(tempStr)

    if fname != None:
        fname.close()

    if len(service_dir) != 0:
        service_dir_network = service_dir['network']
        service_dir_vlan=service_dir['vlan']
    else:
        service_dir_network = ""
        service_dir_vlan = ""
    if modify_network:
            #resource = 'subnets'
            if(network_vlan_in_setupoci=='network'):
                for reg in ct.all_regions:
                    reg_out_dir = outdir + "/" + reg + "/" + service_dir_network
                    if not os.path.exists(reg_out_dir):
                        os.makedirs(reg_out_dir)

                    srcdir = reg_out_dir + "/"

                    commonTools.backup_file(srcdir, 'subnets', prefix + auto_tfvars_filename)
                    outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename
                    srcStr = "##Add New Subnets for " + reg + " here##"
                    # Create Skeleton Template
                    if tfStr[reg] != '':
                        skeletonStr[reg] = template.render(tempStr, skeleton=True, count=0, region=reg)
                        tfStr[reg] = skeletonStr[reg].replace(srcStr, tfStr[reg] + "\n" + srcStr)
                        tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                        oname[reg] = open(outfile[reg], "w")
                        oname[reg].write(tfStr[reg])
                        oname[reg].close()
                        print(outfile[reg] + " for Subnets has been updated for region " + reg)

            #  resource = 'vlans'
            if (network_vlan_in_setupoci == 'vlan'):
                for reg in ct.all_regions:
                    reg_out_dir = outdir + "/" + reg + "/" + service_dir_vlan
                    if not os.path.exists(reg_out_dir):
                        os.makedirs(reg_out_dir)

                    srcdir = reg_out_dir + "/"

                    commonTools.backup_file(srcdir, 'vlans', prefix + vlan_auto_tfvars_filename)
                    vlan_outfile[reg] = reg_out_dir + "/" + prefix + vlan_auto_tfvars_filename
                    srcStr = "##Add New VLANs for " + reg + " here##"
                    # Create Skeleton Template
                    if tfStr_vlan[reg] != '':

                        skeletonStr[reg] = vlan_template.render(tempStr, skeleton=True, count=0, region=reg)
                        tfStr_vlan[reg] = skeletonStr[reg].replace(srcStr, tfStr_vlan[reg] + "\n" + srcStr)

                        tfStr_vlan[reg] = "".join([s for s in tfStr_vlan[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                        oname[reg] = open(vlan_outfile[reg], "w")
                        oname[reg].write(tfStr_vlan[reg])
                        oname[reg].close()
                        print(vlan_outfile[reg] + " for VLANs has been created for region " + reg)


    elif not modify_network:
        # resource = 'subnets'
        if (network_vlan_in_setupoci == 'network'):
            for reg in ct.all_regions:
                reg_out_dir = outdir + "/" + reg + "/" + service_dir_network
                if not os.path.exists(reg_out_dir):
                        os.makedirs(reg_out_dir)

                srcdir = reg_out_dir + "/"
                commonTools.backup_file(srcdir, 'subnets', prefix + auto_tfvars_filename)

                outfile[reg] = reg_out_dir + "/" +  "/"+prefix + auto_tfvars_filename

                # Create Skeleton Template
                if tfStr[reg] != '':
                    skeletonStr[reg] = template.render(tempStr, skeleton=True, count=0, region=reg)
                    srcStr = "##Add New Subnets for " + reg + " here##"
                    tfStr[reg] = skeletonStr[reg].replace(srcStr, tfStr[reg] + "\n" + srcStr)

                    tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                    oname[reg] = open(outfile[reg], 'w')
                    oname[reg].write(tfStr[reg])
                    oname[reg].close()
                    print(outfile[reg] + " for Subnets has been created for region " + reg)
        #  resource = 'vlans'
        if (network_vlan_in_setupoci == 'vlan'):
            for reg in ct.all_regions:
                reg_out_dir = outdir + "/" + reg + "/" + service_dir_vlan
                if not os.path.exists(reg_out_dir):
                    os.makedirs(reg_out_dir)

                srcdir = reg_out_dir + "/"

                commonTools.backup_file(srcdir, 'vlans', prefix + vlan_auto_tfvars_filename)
                vlan_outfile[reg] = reg_out_dir + "/" + prefix + vlan_auto_tfvars_filename            # Create Skeleton Template
                if tfStr_vlan[reg] != '':
                    skeletonStr[reg] = vlan_template.render(tempStr, skeleton=True, count=0, region=reg)
                    srcStr = "##Add New VLANs for " + reg + " here##"
                    tfStr_vlan[reg] = skeletonStr[reg].replace(srcStr, tfStr_vlan[reg] + "\n" + srcStr)

                    tfStr_vlan[reg] = "".join(
                        [s for s in tfStr_vlan[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                    oname[reg] = open(vlan_outfile[reg], "w")
                    oname[reg].write(tfStr_vlan[reg])
                    oname[reg].close()
                    print(vlan_outfile[reg] + " for VLANs has been created for region " + reg)

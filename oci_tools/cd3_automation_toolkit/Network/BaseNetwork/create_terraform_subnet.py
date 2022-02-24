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
import argparse
import shutil
import datetime
import os
sys.path.append(os.getcwd()+"/../../..")
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######

def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description='Takes in a list of subnet names with format \"name,subnet CIDR,Availability Domain, Public|Private subnet,dhcp-options\". '
                                     'Create terraform files for subnets.')
    parser.add_argument('inputfile', help='Full Path of input file. eg  cd3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument('--modify-network', action='store_true', help='modify network: true or false')
    parser.add_argument('--configFileName', default=DEFAULT_LOCATION, help='Config file name')
    args = parser.parse_args()


#If input is CD3
def create_terraform_subnet(inputfile, outdir, prefix, config, modify_network=False):
    filename = inputfile
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)


    fname = None
    outfile={}
    oname={}
    tfStr={}
    skeletonStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('module-subnet-template')
    auto_tfvars_filename = '_subnets.auto.tfvars'
    region_included = []

    def processSubnet(tempStr):
        region = tempStr['region'].lower().strip()
        subnet = tempStr['cidr_block']
        AD = tempStr['availability_domain'].strip()
        if (AD.strip().lower() != 'regional'):
            AD = AD.strip().upper()
            ad = ADS.index(AD)
            ad_name_int = ad + 1
            ad_name = str(ad_name_int)
            adString = ad
        else:
            ad_name = ""
            adString = ""

        tempStr['availability_domain'] = adString

        vcn_tf_name = commonTools.check_tf_variable(tempStr['vcn_name'].strip())
        name = tempStr['subnet_name']
        tempStr['vcn_tf_name'] = vcn_tf_name
        if (vcnInfo.subnet_name_attach_cidr == 'y'):
                if (str(ad_name) != ''):
                        name1 = name + "-ad" + str(ad_name)
                        namert = rt_name + "-ad" + str(ad_name)
                else:
                        name1 = name
                        namert = rt_name

                display_name = name1 + "-" + subnet
                rt_display_name=namert+ "-" + subnet

        else:
                display_name = name
                rt_display_name=rt_name

        tempStr['display_name'] = display_name
        tempStr['rt_display_name'] = rt_display_name


        sl_tf_names=[]
        seclist_names = tempStr['sl_names']
        if (vcnInfo.subnet_name_attach_cidr == 'y'):
                for sl_name in seclist_names:
                        sl_name=str(sl_name).strip()
                        if (str(ad_name) != ''):
                                namesl = str(sl_name) + "-ad" + str(ad_name)
                        else:
                                namesl = str(sl_name)
                        sl_display_name = namesl + "-" + subnet
                        sl_tf_name=vcn_name+"_"+sl_display_name
                        sl_tf_names.append(commonTools.check_tf_variable(sl_tf_name))
        else:
                for sl_name in seclist_names:
                        sl_name=str(sl_name).strip()
                        sl_display_name=str(sl_name)
                        sl_tf_name = vcn_name + "_" + sl_display_name
                        sl_tf_names.append(commonTools.check_tf_variable(sl_tf_name))

        subnet_tf_name=vcn_name+"_"+display_name
        subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)
        if rt_display_name != 'n':
            rt_tf_name = vcn_name+"_"+rt_display_name
            rt_tf_name = commonTools.check_tf_variable(rt_tf_name)
        else:
            rt_tf_name = ""


        tempStr['subnet_tf_name'] = subnet_tf_name
        tempStr['rt_tf_name'] = rt_tf_name

        seclist_ids=""
        add_default_seclist =  tempStr['add_default_seclist'].strip()

        #Attach Default Security List
        if add_default_seclist.strip() == "y":
                seclist_ids = "\""+vcn_tf_name+"\""
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
            dhcp_options_id = vcn_tf_name
        tempStr['dhcp_options_name'] = dhcp_options_id

        if tempStr['type'] == 'public':
            prohibit_public_ip_on_vnic = "false"
        else:
            prohibit_public_ip_on_vnic = "true"
        tempStr['prohibit_public_ip_on_vnic'] = prohibit_public_ip_on_vnic

        tfStr[region]= tfStr[region] +"\n"+ template.render(tempStr)

    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Subnets")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in ct.all_regions:
        tfStr[reg] = ''
        skeletonStr[reg] = ''

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

        if (vcn_name.strip() not in vcns.vcn_names):
            print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
            exit(1)

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                        df.loc[i, 'VCN Name']).lower() == 'nan' or str(df.loc[i, 'Subnet Name']).lower() == 'nan' or str(df.loc[i, 'CIDR Block']).lower() == 'nan'):
            print("\nColumn Values Region, Compartment Name, VCN Name, Subnet Name and CIDR Block cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        if (str(df.loc[i,'Availability Domain(AD1|AD2|AD3|Regional)']).lower =='nan' or str(
                        df.loc[i, 'Type(private|public)']).lower() == 'nan' or str(df.loc[i,'Add Default Seclist']).lower() == 'nan'):
            print("\nColumn Values Add Default Seclist, Availability Domain and Type cannot be left empty in VCNs sheet in CD3..exiting...")
            exit(1)

        if (str(df.loc[i, 'Configure IGW Route(y|n)']).lower() == 'nan' or str(df.loc[i, 'Configure NGW Route(y|n)']).lower() == 'nan' or str(
                        df.loc[i, 'Configure SGW Route(n|object_storage|all_services)']).lower() == 'nan' or str(df.loc[i, 'Configure OnPrem Route(y|n)']).lower() == 'nan' or str(
                        df.loc[i,'Configure VCNPeering Route(y|n)']).lower() == 'nan'):
            print("\nColumn Values Configure IGW/SGW/On-Prem/VCN route cannot be left empty in VCNs sheet in CD3..exiting...")
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
                columnname = 'dhcp_option_name'
                if str(columnvalue).strip().lower() != '' and str(columnvalue).strip().lower() != 'n':
                    dhcp = df.loc[i,'VCN Name'].strip() +"_" + columnvalue
                    dhcp = commonTools.check_tf_variable(dhcp)
                    tempdict = {'dhcp_tf_name': dhcp,'dhcp_option_name' : columnvalue}
                else:
                    tempdict = {'dhcp_tf_name': columnvalue, 'dhcp_option_name': columnvalue}

            if columnname == 'DNS Label':
                dnslabel = columnvalue.strip()
                # check if subnet_dns_label is not given by user in input use subnet name
                if (str(dnslabel).lower() == 'nan' or str(dnslabel).lower() == ''):
                    regex = re.compile('[^a-zA-Z0-9]')
                    subnet_dns = regex.sub('', df.loc[i,'Subnet Name'])
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
                    rt_name = str(df.loc[i,'Subnet Name']).strip()
                    tempdict = {'rt_name': rt_name}
                else:
                    rt_name = columnvalue.strip()
                    tempdict = {'rt_name': rt_name}
                tempStr.update(tempdict)

            sl_names = []
            if columnname == 'Seclist Names':
                if str(columnvalue).lower() == 'nan' or str(columnvalue).lower() == '':
                    # seclist name not provided; use subnet name as seclist name
                    sl_names.append(df.loc[i,'Subnet Name'].strip())
                    tempdict = {'sl_names': sl_names}
                else:
                    sl_names = columnvalue.split(",")
                    tempdict = {'sl_names': sl_names}

                tempStr.update(tempdict)

            if columnname == 'Type(private|public)':
                columnname = 'type'
                columnvalue = columnvalue.lower()

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        processSubnet(tempStr)

    if fname != None:
        fname.close()

    if modify_network:
        for reg in ct.all_regions:
            reg_out_dir = outdir + "/" + reg
            if not os.path.exists(reg_out_dir):
                    os.makedirs(reg_out_dir)

            srcdir = reg_out_dir + "/"
            resource = 'Subnets'
            commonTools.backup_file(srcdir, resource, prefix + auto_tfvars_filename)

            outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

            # Create Skeleton Template
            if tfStr[reg] != '':
                skeletonStr[reg] = template.render(tempStr, skeleton=True, count=0, region=reg)
                srcStr = "##Add New Subnets for " + reg + " here##"
                tfStr[reg] = skeletonStr[reg].replace(srcStr, tfStr[reg] + "\n" + srcStr)

                oname[reg] = open(outfile[reg], "w")
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " for Subnets has been updated for region " + reg)

    elif not modify_network:
        for reg in ct.all_regions:
            reg_out_dir = outdir + "/" + reg
            if not os.path.exists(reg_out_dir):
                    os.makedirs(reg_out_dir)

            srcdir = reg_out_dir + "/"
            resource = 'Subnets'
            commonTools.backup_file(srcdir, resource, prefix + auto_tfvars_filename)
            outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

            # Create Skeleton Template
            if tfStr[reg] != '':
                skeletonStr[reg] = template.render(tempStr, skeleton=True, count=0, region=reg)
                srcStr = "##Add New Subnets for " + reg + " here##"
                tfStr[reg] = skeletonStr[reg].replace(srcStr, tfStr[reg] + "\n" + srcStr)

                oname[reg] = open(outfile[reg], 'w')
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " for Subnets has been created for region " + reg)

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_subnet(args.inputfile, args.outdir, args.prefix, args.config, modify_network=args.modify_network)

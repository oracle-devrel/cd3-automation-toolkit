#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Security List
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import re
import os
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + '/../../..')
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, Modify Network AND outdir
######
def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description='Creates a terraform sec list resource with name for each subnet'
                                                 'identified in the subnet input file.  This creates open egress (0.0.0.0/0) and '
                                                 'All protocols within subnet ingress rules.  This also opens ping between peered VCNs'
                                                 ' and ping from On-Prem to hub VCN based on the input property add_ping_sec_rules_vcnpeering '
                                                 'and add_ping_sec_rules_onprem respectively. Any other rules should be put in manually.')
    parser.add_argument('inputfile', help='Full Path of input file. eg cd3 excel file')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument('--modify-network', action='store_true', help="modify networking")
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


# If the input is CD3
def create_terraform_seclist(inputfile, outdir, prefix, config, modify_network=False):
    def purge(dir, pattern):
        for f in os.listdir(dir):
            if re.search(pattern, f):
                print("Purge ....." + os.path.join(dir, f))
                os.remove(os.path.join(dir, f))


    filename = inputfile
    modify_network = str(modify_network)
    configFileName = config

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    fname = None
    oname = None
    secrulefiles = {}
    ADS = ["AD1", "AD2", "AD3"]

    #Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('seclist-template')
    secrule = env.get_template('sec-rule-template')

    def processSubnet(tempStr):

        tempStr['region'].lower().strip()
        subnet_cidr = tempStr['cidr_block'].strip()

        # Seclist name specifiied as 'n' - dont create any seclist

        if tempStr['seclist_names'].lower() == 'n':
            return

        if (tempStr['availability_domain'].strip().lower() != 'regional'):
            AD = tempStr['availability_domain'].strip().upper()
            ad = ADS.index(AD)
            ad_name_int = ad + 1
            ad_name = str(ad_name_int)
        else:
            ad_name = ""

        vcn_name = tempStr['vcn_name']
        vcn_tf_name = commonTools.check_tf_variable(tempStr['vcn_name'])
        tempStr['vcn_tf_name'] = vcn_tf_name

        index = 0
        seclist_names = tempStr['sl_names']

        for sl_name in seclist_names:
            sl_name = sl_name.strip()

            # check if subnet cidr needs to be attached
            if (vcnInfo.subnet_name_attach_cidr == 'y'):
                if (str(ad_name) != ''):
                    name1 = sl_name + "-ad" + str(ad_name)
                else:
                    name1 = sl_name
                display_name = name1 + "-" + tempStr['cidr_block']
            else:
                display_name = sl_name
            tempStr['display_name'] = display_name

            sl_tf_name = vcn_name+ "_" + display_name
            sl_tf_name = commonTools.check_tf_variable(sl_tf_name)
            tempStr['seclist_tf_name'] = sl_tf_name


            if (sl_tf_name + "_seclist.tf" in secrulefiles[region]):
                secrulefiles[region].remove(sl_tf_name + "_seclist.tf")
            outfile = outdir + "/" + region + "/" + sl_tf_name + "_seclist.tf"

            # If Modify Network is set to true
            if (os.path.exists(outfile) and modify_network == 'true'):
                continue

            # If same seclist name is used for subsequent subnets
            if (index == 0 and os.path.exists(outfile) and modify_network == 'false'):
                tempStr['rule_type'] = "ingress"
                tempStr['source'] = subnet_cidr
                tempStr['protocol_code'] = 'all'
                tempStr['isstateless'] = "false"

                Str = secrule.render(tempStr)

                with open(outfile, 'r+') as file:
                    filedata = file.read()
                file.close()

                # Replace the target string
                textToSearch = "####ADD_NEW_SEC_RULES####" + vcn_tf_name + "_" + sl_tf_name
                Str = Str + "\n" + textToSearch

                filedata = filedata.replace(textToSearch, Str)
                oname = open(outfile, "w")
                oname.write(filedata)
                oname.close()
                continue

            # New Seclist
            oname = open(outfile, "w")
            tempStr['index'] = index

            tempSecList = template.render(tempStr)
            if index != 0:
                tempSecList=tempSecList +"\n"
            elif (index == 0):
                secrule_data = ''
                rule_type = ['ingress','egress']
                for rule in rule_type:
                    tempStr['destination'] = '0.0.0.0/0'
                    tempStr['protocol_code'] = 'all'
                    tempStr['source'] = subnet_cidr
                    tempStr['rule_type'] = rule
                    tempStr['isstateless'] = "false"
                    secrule_data = secrule_data + secrule.render(tempStr)
                textToSearch = "####ADD_NEW_SEC_RULES####" + vcn_tf_name + "_" + sl_tf_name
                secrule_data = secrule_data + textToSearch
                tempSecList = tempSecList.replace(textToSearch,secrule_data)
            oname.write(tempSecList)
            oname.close()
            print(outfile + " containing TF for seclist has been created for region " + region)
            index = index + 1

    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Purge existing routetable files
    if (modify_network == 'false'):
        for reg in ct.all_regions:
            purge(outdir+"/"+reg, "_seclist.tf")
            secrulefiles.setdefault(reg, [])

    # Get existing list of secrule table files
    if (modify_network == 'true'):
        for reg in ct.all_regions:
            secrulefiles.setdefault(reg, [])
            lisoffiles = os.listdir(outdir + "/" + reg)
            for file in lisoffiles:
                if "_seclist.tf" in file:
                    secrulefiles[reg].append(file)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Subnets")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Start processing each subnet
    for i in df.index:
        region = df.loc[i, 'Region']
        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1, dictionary2, string  and list
        tempStr = {}
        tempdict = {}
        sl_names = []
        compartment_var_name = ''

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i,'VCN Name']).lower() == 'nan':
            print("\nThe values for Region, Compartment Name and VCN Name cannot be left empty in Subnets Tab. Please enter a value and try again !!")
            exit()

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process the Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue
            vcn_name = str(df.loc[i,'VCN Name'].strip())

            if (vcn_name.strip() not in vcns.vcn_names):
                print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
                exit(1)

            if columnname == 'Availability Domain(AD1|AD2|AD3|Regional)':
                columnname = 'availability_domain'
                columnvalue = columnvalue.strip()

            if columnname == 'Seclist Names':
                columnvalue = columnvalue.strip()
                if columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    sl_names = columnvalue.split(",")
                else:
                    sl_names.append(str(df.loc[i,'Subnet Name']).strip())
                compartment_var_name = compartment_var_name.strip()
                tempdict = {'compartment_tf_name' : compartment_var_name, 'sl_names' : sl_names}

            #Added to check if compartment name is compatible with TF variable name syntax
            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = columnvalue
            tempStr.update(tempdict)

        processSubnet(tempStr)

    # remove any extra sec list files (not part of latest cd3)
    for reg in ct.all_regions:
        if(len(secrulefiles[reg])!=0):
            print("\nATTENION!!! Below SecLists are not attached to any subnet; If you want to delete any of them, remove the TF file!!!")
        for remaining_sl_file in secrulefiles[reg]:
            print(outdir + "/" + reg + "/" + remaining_sl_file)

            # print("\nRemoving "+outdir + "/" + reg + "/"+remaining_sl_file)
            # os.remove(outdir + "/" + reg + "/"+remaining_sl_file)
            # secrulefiles[reg].remove(remaining_sl_file)

    if (fname != None):
        fname.close()

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_seclist(args.inputfile, args.outdir, args.prefix, args.config, args.modify_network)

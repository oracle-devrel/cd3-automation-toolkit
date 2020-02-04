#!/usr/bin/python3
##### Author : Suruchi ###
##### Oracle Consulting ####



######
# Required Files
# Properties File: vcn-info.properties"
# Code will read input subnet file name for each vcn from properties file
# Subnets file will contain info about each subnet. Seclists will be created based on the inputs in properties file
# Outfile
######

import sys
import argparse
import configparser
import re
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." +  os.path.join(dir, f))
            os.remove(os.path.join(dir, f))

parser = argparse.ArgumentParser(description="Creates a terraform sec list resource with name for each subnet"
                                             "identified in the subnet input file.  This creates open egress (0.0.0.0/0) and "
                                             "All protocols within subnet ingress rules.  This also opens ping between peered VCNs"
                                             " and ping from On-Prem to hub VCN based on the input property add_ping_sec_rules_vcnpeering "
                                             "and add_ping_sec_rules_onprem respectively. Any other rules should be put in manually.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir",help="Output directory")
parser.add_argument("--modify_network", help="modify: true or false", required=False)


if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

filename=args.inputfile
outdir = args.outdir
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"

common_seclist_names={}
fname = None
oname=None
secrulefiles={}
tempStr = ""
ADS = ["AD1", "AD2", "AD3"]

def processSubnet(region,vcn_name,AD,seclists_per_subnet,name,seclist_name,compartment_var_name):

    j = 0
    if (AD.strip().lower() != 'regional'):
        AD = AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    if(seclist_name==''):
        slname=vcn_name+"_"+name+ "_seclist.tf"
    else:
        slname = vcn_name+"_"+ seclist_name + "_seclist.tf"

    if (slname in secrulefiles[region]):
        secrulefiles[region].remove(slname)

    outfile = outdir + "/" + region + "/" + slname

    # If Modify Network is set to true
    if (os.path.exists(outfile) and modify_network == 'true'):
        return

    # If same seclist name is used for subsequent subnets
    if(os.path.exists(outfile) and modify_network == 'false'):
        Str= """
                        ingress_security_rules {
                            protocol = "all"
                            source = \"""" + subnet + """"
                        }
                        
                        ####ADD_NEW_SEC_RULES####1
                    """
        with open(outfile, 'r+') as file:
            filedata = file.read()
        file.close()
        # Replace the target string
        textToSearch="####ADD_NEW_SEC_RULES####1"
        filedata = filedata.replace(textToSearch, Str)
        oname = open(outfile, "w")
        oname.write(filedata)
        oname.close()
        return

    #New Seclist
    oname = open(outfile, "w")
    while j < seclists_per_subnet:
        #seclist name not provided; use subnetname as seclistname
        if(seclist_name==''):
            seclistname = name + "-" + str(j + 1)
            if (str(ad_name) != ''):
                name1 = seclistname + "-ad" + str(ad_name)
            else:
                name1 = seclistname

            #check if subnet cidr needs to be attached
            if (vcnInfo.subnet_name_attach_cidr == 'y'):
                display_name = name1 + "-" + subnet
            else:
                display_name = seclistname
        #seclist name provided
        else:
            seclistname = seclist_name + "-" + str(j + 1)
            #no need to attach subnet cidr to display name
            display_name=seclistname


        tempStr = """
        resource "oci_core_security_list" \"""" + vcn_name+"_"+seclistname + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            display_name = \"""" + display_name.strip() + "\""

        if j + 1 > 1:
            tempStr = tempStr + """

                        ####ADD_NEW_SEC_RULES####""" + str(j + 1) + """
        }
        """
        else:
            tempStr = tempStr + """
                        ingress_security_rules {
                            protocol = "all"
                            source = \"""" + subnet + """"
                        }
                        egress_security_rules {
                            destination = "0.0.0.0/0"
                            protocol = "all"
                        }

                        ####ADD_NEW_SEC_RULES####""" + str(j + 1) + """
                    }
                    """
        oname.write(tempStr)
        j = j + 1
    oname.close()
    print(outfile + " containing TF for seclist has been created for region " + region)

#If input is CD3 excel file
if('.xls' in filename):
    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)
    for reg in vcnInfo.all_regions:
        common_seclist_names[reg] = []

    # Purge existing routetable files
    if (modify_network == 'false'):
        for reg in vcnInfo.all_regions:
            purge(outdir+"/"+reg, "_seclist.tf")
            secrulefiles.setdefault(reg, [])

    # Get existing list of secrule table files
    if (modify_network == 'true'):
        for reg in vcnInfo.all_regions:
            secrulefiles.setdefault(reg, [])
            lisoffiles = os.listdir(outdir + "/" + reg)
            for file in lisoffiles:
                if "_seclist.tf" in file:
                    secrulefiles[reg].append(file)


    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    df.dropna(how='all')

    #Start processing each subnet
    for i in df.index:
        region = df.iat[i, 0]
        if (region in commonTools.endNames):
            break
        compartment_var_name = df.iat[i, 1]
        vcn_name = str(df['vcn_name'][i]).strip()
        if (vcn_name.strip() not in vcns.vcn_names):
            print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
            exit(1)
        region = region.strip().lower()


        # Get subnet data
        name = df.iat[i, 3]
        name=name.strip()
        subnet = df.iat[i, 4]
        subnet=subnet.strip()
        AD = df.iat[i, 5]
        AD=AD.strip()
        seclist_name = df.iat[i, 9]
        if (str(seclist_name).lower() != 'nan'):
            seclist_name=seclist_name.strip()
        else:
            seclist_name=''
        compartment_var_name=compartment_var_name.strip()

        common_seclist_name=df.iat[i,10]
        if(str(common_seclist_name).lower() !='nan'):
            if (vcn_name+"_"+common_seclist_name not in common_seclist_names[region]):
                common_seclist_names[region].append(vcn_name+"_"+common_seclist_name)
                out_common_file=outdir+"/"+region+"/"+vcn_name+"_"+common_seclist_name+"_seclist.tf"
                if(vcn_name+"_"+common_seclist_name+"_seclist.tf" in secrulefiles[region]):
                    secrulefiles[region].remove(vcn_name+"_"+common_seclist_name+"_seclist.tf")
                if (not os.path.exists(out_common_file) or modify_network == 'false'):
                    oname_common=open(out_common_file,"w")
                    data="""
        resource "oci_core_security_list" \"""" + vcn_name+"_"+common_seclist_name.strip() + "-1" """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            display_name = \"""" + common_seclist_name.strip() + "-1" """"
            ####ADD_NEW_SEC_RULES####1
        }
        """
                    oname_common.write(data)

                    print(out_common_file + " containing TF for seclist has been created for region " + region)
                    oname_common.close()

        seclists_per_subnet = df.iat[i, 11]
        if (str(seclists_per_subnet).lower() == 'nan'):
            seclists_per_subnet = '1'
        try:
            seclists_per_subnet = int(seclists_per_subnet)
        except:
            print("\nERROR!!! Make sure to enter numeric value(without any extra spaces) in sec_list_per_subnet column of Subnets tab..Exiting!")
            exit(1)

        processSubnet(region,vcn_name,AD,seclists_per_subnet,name,seclist_name,compartment_var_name)


    # remove any extra route table files (not part of latest cd3)
    for reg in vcnInfo.all_regions:
        for remaining_sl_file in secrulefiles[reg]:
            print("\nRemoving "+outdir + "/" + reg + "/"+remaining_sl_file)
            os.remove(outdir + "/" + reg + "/"+remaining_sl_file)
            secrulefiles[reg].remove(remaining_sl_file)

# If CD3 excel file is not given as input
elif('.properties' in filename):
        # Get VCN Info from VCN_INFO section
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(args.inputfile)
        sections = config.sections()

        # Get Global Properties from Default Section
        all_regions = config.get('Default', 'regions')
        all_regions = all_regions.split(",")
        all_regions = [x.strip().lower() for x in all_regions]
        if (subnet_add == 'false'):
            for reg in all_regions:
                purge(outdir + "/" + reg, "_seclist.tf")
        subnet_name_attach_cidr = config.get('Default', 'subnet_name_attach_cidr')
        drg_destinations = config.get('Default', 'drg_subnet')
        if(drg_destinations==''):
            print("\ndrg_subnet should not be left empty.. It will create empty route tables")
        else:
            drg_destinations = drg_destinations.split(",")


        vcns = config.options('VCN_INFO')
        for vcn_name in vcns:
                vcn_lpg_rules.setdefault(vcn_name, '')

        #Create sec rules as per Section VCN_PEERING
        peering_dict = dict(config.items('VCN_PEERING'))
        ocs_vcn_cidr=peering_dict['ocs_vcn_cidr']
        peering_dict.pop('ocs_vcn_lpg_ocid')
        add_ping_sec_rules_vcnpeering=peering_dict['add_ping_sec_rules_vcnpeering']
        add_ping_sec_rules_onprem=peering_dict['add_ping_sec_rules_onprem']
        peering_dict.pop('add_ping_sec_rules_vcnpeering')
        peering_dict.pop('add_ping_sec_rules_onprem')
        peering_dict.pop('ocs_vcn_cidr')


        if(add_ping_sec_rules_vcnpeering.strip().lower()=='y'):
            createLPGSecRules(peering_dict)

        for vcn_name in vcns:
            vcn_data = config.get('VCN_INFO', vcn_name)
            vcn_data = vcn_data.split(',')
            region = vcn_data[0].strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                exit(1)
            vcn_drg=vcn_data[2].strip().lower()
            hub_spoke_none = vcn_data[6].strip().lower()
            vcn_subnet_file = vcn_data[7].strip().lower()
            if os.path.isfile(vcn_subnet_file) == False:
                print("input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping SecList TF creation for this VCN.")
                continue
            sps = vcn_data[9].strip().lower()
            seclists_per_subnet = int(sps)


            fname = open(vcn_subnet_file,"r")

            #Read subnet file
            for line in fname:
                    i = 0
                    if not line.startswith('#') and line !='\n':
                            [compartment_var_name, name, sub, AD, pubpvt, dhcp, rt_name,seclist_name,common_seclist_name,SGW, NGW, IGW,dns_label] = line.split(',')
                            linearr = line.split(",")
                            compartment_var_name = linearr[0].strip()
                            name = linearr[1].strip()
                            subnet = linearr[2].strip()
                            if (vcn_name+"_"+common_seclist_name.strip().lower() != '' and common_seclist_name not in common_seclist_names):
                                common_seclist_names[region].append(vcn_name+"_"+common_seclist_name)
                                out_common_file = outdir + "/" + region + "/" + vcn_name+"_"+common_seclist_name + "_seclist.tf"
                                oname_common = open(out_common_file, "w")
                                data = """
                                                resource "oci_core_security_list" \"""" + vcn_name+"_"+common_seclist_name.strip() + "-1" """"{
                                                    compartment_id = "${var.""" + compartment_var_name + """}"
                                                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
                                                    display_name = \"""" + common_seclist_name.strip() + "-1" """"
                                                    ####ADD_NEW_SEC_RULES####1
                                                }
                                                """
                                oname_common.write(data)
                                print(
                                    out_common_file + " containing TF for seclist has been created for region " + region)
                                oname_common.close()

                            processSubnet(region, vcn_name, AD, seclists_per_subnet, name, seclist_name.strip(),subnet_name_attach_cidr,compartment_var_name)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit(1)


if(fname!=None):
    fname.close()

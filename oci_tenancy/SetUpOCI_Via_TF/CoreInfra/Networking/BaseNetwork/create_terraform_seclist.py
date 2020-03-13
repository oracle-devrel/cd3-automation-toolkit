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

fname = None
oname=None
secrulefiles={}
tempStr = ""
ADS = ["AD1", "AD2", "AD3"]

def processSubnet(region,vcn_name,AD,seclist_names,compartment_var_name):
    #Seclist name specifiied as 'n' - dont create any seclist
    if(seclist_names[0]=="n"):
        return

    if (AD.strip().lower() != 'regional'):
        AD = AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    vcn_tf_name=commonTools.tfname.sub("-",vcn_name)

    index=0
    for sl_name in seclist_names:
        sl_name=sl_name.strip()

        # check if subnet cidr needs to be attached
        if (vcnInfo.subnet_name_attach_cidr == 'y'):
            if (str(ad_name) != ''):
                name1 = sl_name + "-ad" + str(ad_name)
            else:
                name1 = sl_name
            display_name = name1 + "-" + subnet
        else:
            display_name = sl_name

        sl_tf_name = commonTools.tfname.sub("-",display_name)

        if (vcn_tf_name +"_"+sl_tf_name+"_seclist.tf" in secrulefiles[region]):
            secrulefiles[region].remove(vcn_tf_name +"_"+sl_tf_name+"_seclist.tf")
        outfile = outdir + "/" + region + "/" + vcn_tf_name +"_"+sl_tf_name+"_seclist.tf"

        # If Modify Network is set to true
        if (os.path.exists(outfile) and modify_network == 'true'):
            continue

        # If same seclist name is used for subsequent subnets
        if(index==0 and os.path.exists(outfile) and modify_network == 'false'):
            Str= """
                            ingress_security_rules {
                                protocol = "all"
                                source = \"""" + subnet + """"
                            }
                            
                        ####ADD_NEW_SEC_RULES####"""+vcn_tf_name+"_"+sl_tf_name

            with open(outfile, 'r+') as file:
                filedata = file.read()
            file.close()
            # Replace the target string
            textToSearch="####ADD_NEW_SEC_RULES####"+vcn_tf_name+"_"+sl_tf_name
            filedata = filedata.replace(textToSearch, Str)
            oname = open(outfile, "w")
            oname.write(filedata)
            oname.close()
            continue

        #New Seclist
        oname = open(outfile, "w")

        tempStr = """
        resource "oci_core_security_list" \"""" + vcn_tf_name+"_"+sl_tf_name + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
            display_name = \"""" + display_name.strip() + "\""

        if index!=0:
            tempStr = tempStr + """
            ####ADD_NEW_SEC_RULES####""" + vcn_tf_name+"_"+sl_tf_name  + """
        }
        """
        elif(index==0):
            tempStr = tempStr + """
                        ingress_security_rules {
                            protocol = "all"
                            source = \"""" + subnet + """"
                        }
                        egress_security_rules {
                            destination = "0.0.0.0/0"
                            protocol = "all"
                        }

                        ####ADD_NEW_SEC_RULES####""" + vcn_tf_name+"_"+sl_tf_name + """
                    }
                    """
        oname.write(tempStr)
        oname.close()
        print(outfile + " containing TF for seclist has been created for region " + region)
        index=index+1

#If input is CD3 excel file
if('.xls' in filename):
    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

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
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

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
        seclist_names = df.iat[i, 9]
        sl_names=[]
        if (str(seclist_names).lower() != 'nan'):
            sl_names=seclist_names.split(",")
        else:
            # seclist not provided; use subnet name as seclist name
            sl_names.append(name)
        compartment_var_name=compartment_var_name.strip()


        processSubnet(region,vcn_name,AD,sl_names,compartment_var_name)


    # remove any extra sec list files (not part of latest cd3)
    for reg in vcnInfo.all_regions:
        if(len(secrulefiles[reg])!=0):
            print("\nATTENION!!! Below SecLists are not attached to any subnet; If you want to delete any of them, remove the TF file!!!")
        for remaining_sl_file in secrulefiles[reg]:
            print(outdir + "/" + reg + "/"+remaining_sl_file)
            #print("\nRemoving "+outdir + "/" + reg + "/"+remaining_sl_file)
            #os.remove(outdir + "/" + reg + "/"+remaining_sl_file)
            #secrulefiles[reg].remove(remaining_sl_file)

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

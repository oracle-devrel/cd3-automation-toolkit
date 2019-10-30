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
import os
import argparse
import configparser
import re
import pandas as pd

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
parser.add_argument("--subnet_add", help="Add new subnet: true or false", required=False)


if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

filename=args.inputfile
outdir = args.outdir
if args.subnet_add is not None:
    subnet_add = str(args.subnet_add)
else:
    subnet_add = "false"

common_seclist_names=[]
fname = None
oname=None

#create VCN LPG rules
vcn_lpg_rules = {}
peering_dict = dict()

tempStr = ""
ADS = ["AD1", "AD2", "AD3"]

def createLPGSecRules(peering_dict):
    global vcn_lpg_rules
    for left_vcn,value in peering_dict.items():
        right_vcns=value.split(",")
        for right_vcn in right_vcns:
                if(right_vcn=='ocs_vcn'):
                    # Build rule for VCN on left for OCS VCN on right
                    ruleStr = """
        ingress_security_rules {
                protocol = "1"
                source = \"""" + ocs_vcn_cidr + """"
                }
        """
                    vcn_lpg_rules[left_vcn] = vcn_lpg_rules[left_vcn] + ruleStr

                else:
                    #Build rule for VCN on left
                    ruleStr = """
        ingress_security_rules {
                protocol = "1"
                source = "${oci_core_vcn.""" + right_vcn + """.cidr_block}"
                }
        """
                    vcn_lpg_rules[left_vcn]=vcn_lpg_rules[left_vcn]+ruleStr

                    #Build rule for VCNs on right
                    ruleStr = """
        ingress_security_rules {
                protocol = "1"
                source = "${oci_core_vcn.""" + left_vcn + """.cidr_block}"
                }
        """
                    vcn_lpg_rules[right_vcn] = vcn_lpg_rules[right_vcn] + ruleStr


def processSubnet(region,vcn_name,AD,seclists_per_subnet,name,seclist_name,subnet_name_attach_cidr,compartment_var_name):

    j = 0
    if (AD.strip().lower() != 'regional'):
        AD = AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    if(seclist_name==''):
        outfile=outdir+"/"+region+"/"+name+ "_seclist.tf"
    else:
        outfile = outdir + "/" + region + "/" + seclist_name + "_seclist.tf"

    #Same seclist used for subnets
    if(os.path.exists(outfile)):
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

            #check if subnet codr needs to be attached
            if (subnet_name_attach_cidr == 'y'):
                display_name = name1 + "-" + subnet
            else:
                display_name = seclistname
        #seclist name provided
        else:
            seclistname = seclist_name + "-" + str(j + 1)
            #no need to attach subnet cidr to display name
            display_name=seclistname


        tempStr = """
        resource "oci_core_security_list" \"""" + seclistname + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            display_name = \"""" + display_name.strip() + "\""

        if j + 1 > 1:
            tempStr = tempStr + """

                        ####ADD_NEW_SEC_RULES####""" + str(j + 1) + """
        }
        """
        else:
            if (vcn_lpg_rules[vcn_name] != ""):
                tempStr = tempStr + vcn_lpg_rules[vcn_name]

            if (add_ping_sec_rules_onprem == 'y'):
                if (hub_spoke_none == 'hub' or vcn_drg != 'n' or hub_spoke_none == 'spoke'):
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            tempStr = tempStr + """
                        ingress_security_rules {
                            protocol = "1"
                            source = \"""" + drg_destination.strip() + """"
                        }
                        """

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

endNames = {'<END>', '<end>'}
#If input is CD3 excel file
if('.xls' in filename):
        NaNstr = 'NaN'
        df_vcn = pd.read_excel(filename, sheet_name='VCNs',skiprows=1)
        df_vcn.dropna(how='all')

        df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
        # Get Property Values

        properties = df_info['Property']
        values = df_info['Value']

        all_regions = str(values[7]).strip()
        all_regions = all_regions.split(",")
        all_regions = [x.strip().lower() for x in all_regions]

        # Purge existing sec list files
        if (subnet_add == 'false'):
            for reg in all_regions:
                purge(outdir+"/"+reg, "_seclist.tf")

        drg_destinations = str(values[0]).strip()
        if (drg_destinations.lower() == NaNstr.lower()):
            print("\ndrg_subnet should not be left empty.. It will create empty route tables")
            drg_destinations = ''
        drg_destinations = drg_destinations.split(",")

        add_ping_sec_rules_onprem = str(values[5]).strip()
        if (add_ping_sec_rules_onprem.lower() == NaNstr.lower()):
            add_ping_sec_rules_onprem = 'n'

        add_ping_sec_rules_vcnpeering = str(values[6]).strip()
        if (add_ping_sec_rules_vcnpeering.lower() == NaNstr.lower()):
            add_ping_sec_rules_vcnpeering = 'n'

        subnet_name_attach_cidr = str(values[4]).strip()
        if (subnet_name_attach_cidr.lower() == NaNstr.lower()):
            subnet_name_attach_cidr = 'n'

        for j in df_info.index:
            if (j > 8):
                peering_dict[properties[j]] = values[j]


        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        for i in df_vcn.index:
                region = df_vcn['Region'][i]
                if (region in endNames):
                    break
                region = region.strip().lower()
                if region not in all_regions:
                    print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
                    exit(1)

                vcn_name=df_vcn['vcn_name'][i]
                vcn_lpg_rules.setdefault(vcn_name, '')

        if (add_ping_sec_rules_vcnpeering.strip().lower() == 'y'):
            createLPGSecRules(peering_dict)

        df_vcn.set_index("vcn_name", inplace=True)
        df_vcn.head()
        df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
        df.dropna(how='all')

        #Start processing each subnet
        for i in df.index:
            # Get VCN data
            compartment_var_name = df.iat[i, 0]
            if (compartment_var_name in endNames):
                break
            vcn_name = df['vcn_name'][i]
            vcn_data = df_vcn.loc[vcn_name]
            region=vcn_data['Region']
            region=region.strip().lower()
            vcn_drg = vcn_data['drg_required']
            hub_spoke_none = vcn_data['hub_spoke_none']
            sps = vcn_data['sec_list_per_subnet']

            # Get subnet data
            name = df.iat[i, 2]
            name=name.strip()
            subnet = df.iat[i, 3]
            subnet=subnet.strip()
            AD = df.iat[i, 4]
            AD=AD.strip()
            seclist_name = df.iat[i, 8]
            if (str(seclist_name).lower() != 'nan'):
                seclist_name=seclist_name.strip()
            else:
                seclist_name=''
            compartment_var_name=compartment_var_name.strip()

            seclists_per_subnet = int(sps)
            common_seclist_name=df.iat[i,9]
            if(str(common_seclist_name).lower() !=NaNstr.lower() and common_seclist_name not in common_seclist_names):
                common_seclist_names.append(common_seclist_name)
                out_common_file=outdir+"/"+region+"/"+common_seclist_name+"_seclist.tf"
                oname_common=open(out_common_file,"w")
                data="""
        resource "oci_core_security_list" \"""" + common_seclist_name.strip() + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            display_name = \"""" + common_seclist_name.strip() + """"
            ####ADD_NEW_SEC_RULES####1
        }
        """
                oname_common.write(data)
                print(out_common_file + " containing TF for seclist has been created for region " + region)
                oname_common.close()

            processSubnet(region,vcn_name,AD,seclists_per_subnet,name,seclist_name,subnet_name_attach_cidr,compartment_var_name)

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
                            if (common_seclist_name.strip().lower() != '' and common_seclist_name not in common_seclist_names):
                                common_seclist_names.append(common_seclist_name)
                                out_common_file = outdir + "/" + region + "/" + common_seclist_name + "_seclist.tf"
                                oname_common = open(out_common_file, "w")
                                data = """
                                                resource "oci_core_security_list" \"""" + common_seclist_name.strip() + """"{
                                                    compartment_id = "${var.""" + compartment_var_name + """}"
                                                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
                                                    display_name = \"""" + common_seclist_name.strip() + """"
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
    exit()


if(fname!=None):
    fname.close()

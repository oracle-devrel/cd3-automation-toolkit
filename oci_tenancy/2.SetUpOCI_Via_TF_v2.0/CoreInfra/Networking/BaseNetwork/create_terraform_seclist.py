#!/bin/python
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

parser = argparse.ArgumentParser(description="Creates a terraform sec list resource with name \"name-cidr\" for each subnet"
                                             "identified in the subnet input file.  This creates open egress (0.0.0.0/0) and "
                                             "All protocols within subnet ingress rules.  This also opens ping between peered VCNs"
                                             " and ping from On-Prem to hub VCN based on the input property add_ping_sec_rules_vcnpeering "
                                             "and add_ping_sec_rules_onprem respectively. Any other rules should be put in manually.")
parser.add_argument("inputfile", help="Full Path of input file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir",help="Output directory")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

filename=args.inputfile
outdir = args.outdir
fname = None
oname = None

ash_dir=outdir+"/ashburn"
phx_dir=outdir+"/phoenix"

if not os.path.exists(ash_dir):
        os.makedirs(ash_dir)

if not os.path.exists(phx_dir):
        os.makedirs(phx_dir)



# Purge existing sec list files
purge(ash_dir, "_seclist.tf")
purge(phx_dir, "_seclist.tf")

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


def processSubnet(region,vcn_name,AD,seclists_per_subnet,name,subnet_name_attach_cidr,compartment_var_name):

    j = 0
    if (AD.strip().lower() != 'regional'):
        AD = AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    print(' seclist file name  ************************** ' + name + '_seclist.tf')
    while j < seclists_per_subnet:
        if(region=='ashburn'):
            oname = open(ash_dir + "/" + name + "_seclist.tf", "a")
        elif(region=='phoenix'):
            oname = open(phx_dir + "/" + name + "_seclist.tf", "a")

        # seclistname = name + str(ad_name) + "-" + str(j + 1)
        seclistname = name + "-" + str(j + 1)

        if (str(ad_name) != ''):
            name1 = seclistname + "-ad" + str(ad_name)
        else:
            name1 = seclistname

        if (subnet_name_attach_cidr == 'y'):
            # display_name = seclistname + "-" + subnet
            display_name = name1 + "-" + subnet
        else:
            # display_name = name + "-" + str(j + 1)
            display_name = seclistname

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
                if (hub_spoke_none == 'hub' or vcn_drg == 'y' or hub_spoke_none == 'spoke'):
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


endNames = {'<END>', '<end>'}
#If input is CD3 excel file
if('.xlsx' in filename):
        NaNstr = 'NaN'
        df_vcn = pd.read_excel(filename, sheet_name='VCNs',skiprows=1)
        df_vcn.dropna(how='all')

        df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
        # Get Property Values

        properties = df_info['Property']
        values = df_info['Value']

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
            if (j > 7):
                peering_dict[properties[j]] = values[j]


        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        for i in df_vcn.index:
                region = df_vcn['Region'][i]
                if (region in endNames):
                    break
                vcn_name=df_vcn['vcn_name'][i]
                vcn_lpg_rules.setdefault(vcn_name, '')

        if (add_ping_sec_rules_vcnpeering.strip().lower() == 'y'):
            createLPGSecRules(peering_dict)

        # Start processing as per vcn and subnet file info from VCN_INFO section
        df_vcn.set_index("vcn_name", inplace=True)
        df_vcn.head()
        df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
        df.dropna(how='all')
        for i in df.index:
            # Get VCN data
            compartment_var_name = df.iat[i, 0]
            if (compartment_var_name in endNames):
                break
            vcn_name = df['vcn_name'][i]
            vcn_data = df_vcn.loc[vcn_name]
            region=vcn_data['Region']
            region=region.strip().lower()
            vcn_drg = vcn_data['drg_required(y|n)']
            hub_spoke_none = vcn_data['hub_spoke_none']
            sps = vcn_data['sec_list_per_subnet']

            # Get subnet data
            name = df.iat[i, 2]
            name=name.strip()
            subnet = df.iat[i, 3]
            subnet=subnet.strip()
            AD = df.iat[i, 4]
            AD=AD.strip()
            compartment_var_name=compartment_var_name.strip()

            seclists_per_subnet = int(sps)

            processSubnet(region,vcn_name,AD,seclists_per_subnet,name,subnet_name_attach_cidr,compartment_var_name)

# If CD3 excel file is not given as input
elif('.csv' in filename):
        # Get VCN Info from VCN_INFO section
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(args.propsfile)
        sections = config.sections()

        # Get Global Properties from Default Section
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
            region=region.strip().lower()
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
                            [compartment_var_name, name, sub, AD, pubpvt, dhcp, SGW, NGW, IGW] = line.split(',')
                            linearr = line.split(",")
                            compartment_var_name = linearr[0].strip()
                            name = linearr[1].strip()
                            subnet = linearr[2].strip()
                            processSubnet(region, vcn_name, AD, seclists_per_subnet, name, subnet_name_attach_cidr,compartment_var_name)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()


if(fname!=None):
    fname.close()
if(oname!=None):
    oname.close()
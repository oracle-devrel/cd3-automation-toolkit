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
parser.add_argument("--propsfile", help="Full Path of properties file. eg vcn-info.properties in example folder")
parser.add_argument("--outdir",help="Output directory")
parser.add_argument("--omcs",help="Input Fileis of pattern \"name-cidr\" ",action="store_true")
parser.add_argument("--inputCD3", help="input CD3 excel file", required=False)

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

excel=''
if(args.inputCD3 is not None):
    excel=args.inputCD3
outdir = args.outdir
fname = None
oname = None


config = configparser.RawConfigParser()
config.optionxform = str
config.read(args.propsfile)
sections=config.sections()

# Purge existing sec list files
purge(outdir, "_seclist.tf")

#Get Global Properties from Default Section
subnet_name_attach_cidr = config.get('Default','subnet_name_attach_cidr')
drg_destinations = config.get('Default', 'drg_subnet')
drg_destinations=drg_destinations.split(",")

#create VCN LPG rules
vcn_lpg_rules = {}

# If CD3 excel file is given as input
if(excel!=''):
        df_vcn = pd.read_excel(excel, sheet_name='VCNs')

        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        for i in df_vcn.index:
                vcn_name=df_vcn['vcn_name'][i]
                vcn_lpg_rules.setdefault(vcn_name, '')
# If CD3 excel file is not given as input
else:
        # Get VCN Info from VCN_INFO section
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
    ruleStr=""
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


tempStr = ""
ADS = ["AD1", "AD2", "AD3"]

#Start processing as per vcn and subnet file info from VCN_INFO section
# If CD3 excel file is given as input
if(excel!=''):
    df_vcn.set_index("vcn_name", inplace=True)
    df_vcn.head()
    df = pd.read_excel(excel, sheet_name='Subnets')
    for i in df.index:
            #Get VCN data
            vcn_name=df['vcn_name'][i]
            vcn_data = df_vcn.loc[vcn_name]
            vcn_drg = vcn_data['drg_required(y|n)']
            hub_spoke_none=vcn_data['hub_spoke_none']
            sps=vcn_data['sec_list_per_subnet']

            #Get subnet data
            name = df.iat[i, 2]
            subnet = df.iat[i, 3]
            AD = df.iat[i, 4]
            compartment_var_name = df.iat[i, 0]

            seclists_per_subnet = int(sps)
            j=0
            if (AD.strip() != 'Regional'):
                ad = ADS.index(AD)
                ad_name_int = ad + 1
                ad_name = str(ad_name_int)
            else:
                ad_name = ""
            print(' seclist file name  ************************** ' + name + '_seclist.tf')
            while j < seclists_per_subnet:
                oname = open(outdir + "/" + name + "_seclist.tf", "a")
                #seclistname = name + str(ad_name) + "-" + str(j + 1)
                seclistname = name  + "-" + str(j + 1)
                if (subnet_name_attach_cidr == 'y'):
                    display_name = seclistname + "-" + subnet
                else:
                    display_name = name + "-" + str(j + 1)

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
                    source = \"""" + drg_destination + """"
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
                #------------------------------------------------------------
                ####ADD_NEW_SEC_RULES####""" + str(j + 1) + """
            }
            """
                oname.write(tempStr)
                j = j + 1


# If CD3 excel file is not given as input
else:
    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        vcn_drg=vcn_data[1].strip().lower()
        hub_spoke_none = vcn_data[5].strip().lower()
        vcn_subnet_file = vcn_data[6].strip().lower()
        if os.path.isfile(vcn_subnet_file) == False:
            print("input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping SecList TF creation for this VCN.")
            continue
        sps = vcn_data[8].strip().lower()
        seclists_per_subnet = int(sps)

        fname = open(vcn_subnet_file,"r")

        #Read subnet file
        for line in fname:
                i = 0
                if not line.startswith('#') and line !='\n':
                        if args.omcs :
                                name_sub,AD,pubpvt,dhcp,SGW,NGW,IGW = line.split(',')
                                subnet = name_sub.rsplit("-",1)[1].strip()
                                name = name_sub.rsplit("-",1)[0].strip()
                        else:
                                [compartment_var_name, name, sub, AD, pubpvt, dhcp, SGW, NGW, IGW] = line.split(',')
                                linearr = line.split(",")
                                compartment_var_name = linearr[0].strip()
                                name = linearr[1].strip()
                                subnet = linearr[2].strip()
                        if (AD.strip() != 'Regional'):
                                ad = ADS.index(AD)
                                ad_name_int = ad + 1
                                ad_name = str(ad_name_int)
                        else:
                                ad_name = ""
                        print(' seclist file name  ************************** '+name+'_seclist.tf')
                        while i < seclists_per_subnet :
                                oname = open(outdir +"/" +name+"_seclist.tf","a")
                                seclistname = name + str(ad_name) + "-" +  str(i+1)

                                if (subnet_name_attach_cidr == 'y'):
                                    display_name = seclistname + "-" + subnet
                                else:
                                    display_name = name + "-" + str(i + 1)

                                tempStr = """
resource "oci_core_security_list" \"""" + seclistname +  """"{
    compartment_id = "${var.""" + compartment_var_name + """}"
    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
    display_name = \""""  + display_name.strip() + "\""


                                if i+1 > 1 :
                                        tempStr  = tempStr + """
       
        ####ADD_NEW_SEC_RULES####""" + str(i+1) + """
        }
        """
                                else :
                                        if(vcn_lpg_rules[vcn_name]!=""):
                                            tempStr=tempStr+vcn_lpg_rules[vcn_name]
                                        if(add_ping_sec_rules_onprem=='y'):
                                            if(hub_spoke_none=='hub' or vcn_drg=='y' or hub_spoke_none=='spoke'):
                                                for drg_destination in drg_destinations:
                                                    if(drg_destination!=''):
                                                        tempStr=tempStr+"""
                ingress_security_rules {
                    protocol = "1"
                    source = \"""" + drg_destination + """"
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
                #------------------------------------------------------------
                ####ADD_NEW_SEC_RULES####""" + str(i+1) + """
}
"""
                                oname.write(tempStr)
                                i = i + 1
if(fname!=None):
    fname.close()
if(oname!=None):
    oname.close()
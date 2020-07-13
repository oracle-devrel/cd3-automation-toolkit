#!/usr/bin/python3
# Author: Shruthi Subramanian
#shruthi.subramanian@oracle.com
import argparse
import re
import pandas as pd
import os
import sys
import ipaddr
import oci
import logging
import ipaddress
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *


parser = argparse.ArgumentParser(description="CD3 Validator")
parser.add_argument("cd3file", help="Full Path of CD3 file")
parser.add_argument("--configFileName", help="Path to config file")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.cd3file
if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    configFileName = ""
    config = oci.config.from_file()

ct = commonTools()
ct.get_subscribedregions(configFileName)
ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

compartment_ids={}
vcn_ids = {}
vcn_cidrs = {}
vcn_compartment_ids = {}

logging.addLevelName(60,"custom")
logging.basicConfig(filename="cd3Validator.log",filemode="w",format="%(asctime)s - %(message)s",level=60)
logger=logging.getLogger("cd3Validator")

def get_vcn_ids(compartment_ids,config):
    #Fetch the VCN ID
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        vnc = VirtualNetworkClient(config)
        for comp_id in compartment_ids.values():
            vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns,compartment_id=comp_id)
            for vcn in vcn_list.data:
                #if(vcn.lifecycle_state == 'ACTIVE'):
                vcn_ids[vcn.display_name]=vcn.id
    return vcn_ids

#Checks for special characters in dns_label name
def checklabel(lable,count):
    present=False
    lable = str(lable)
    if (lable == "Nan") or (lable == "") or (lable == "NaN") or (lable == "nan"):
        pass
    else:
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if (regex.search(lable) == None):
            pass
        else:
            logging.log(60,"ROW " + str(count+2) + " : dns_label value has special characters")
            present = True
    return present

#Shows LPG Peering that will be established based on hub_spoke_peer_none column
def showPeering(vcnsob,oci_vcn_lpgs):
    present=False
    #Check if the LPGs are sufficient for creating the peers.
    for left_vcn, value in vcnsob.peering_dict.items():
        right_vcns = value.split(",")
        for right_vcn in right_vcns:
            if(right_vcn==""):
                continue
            right_vcn=right_vcn.strip()
            try:
                if(vcnsob.vcn_lpg_names[left_vcn][0].lower()=='n' or vcnsob.vcn_lpg_names[right_vcn][0].lower()=='n'):
                    logging.log(60,"ERROR!!! Cannot specify n for lpg_required field for either "+left_vcn +" or "+ right_vcn+ "; Since they are part of VCN peering")
                    present = True
                    continue
            except IndexError:
                logging.log(60,"ERROR!!! Insufficient LPGs declared for either "+left_vcn + " or "+right_vcn + ". Check lpg_required column for both VCNs in VCNs tab")
                present = True
                continue
            left_vcn_lpg=vcnsob.vcn_lpg_names[left_vcn][0]
            vcnsob.vcn_lpg_names[left_vcn].pop(0)
            right_vcn_lpg=vcnsob.vcn_lpg_names[right_vcn][0]
            vcnsob.vcn_lpg_names[right_vcn].pop(0)
            logging.log(60,left_vcn_lpg + " of VCN " + left_vcn + " peers with " + right_vcn_lpg + " of VCN " + right_vcn)

            '''
            if(left_vcn in oci_vcn_lpgs.keys()):
                if(left_vcn_lpg in oci_vcn_lpgs[left_vcn]):
                    #logging.log(60,"ERROR!!! "+left_vcn_lpg +" for vcn "+left_vcn+" already exists in OCI. Use another name")
                    present=True
            if(right_vcn in oci_vcn_lpgs.keys()):
                if(right_vcn_lpg in oci_vcn_lpgs[right_vcn]):
                    #logging.log(60,"ERROR!!! " + right_vcn_lpg + " for vcn "+right_vcn+"  already exists in OCI. Use another name")
                    present =True
            '''
    return present

# Checks for duplicates
def checkIfDuplicates(listOfElems):
    setOfElems = set()
    for elem in listOfElems:
        if elem in setOfElems:
            return elem
        else:
            setOfElems.add(elem)
    return False


#Checks if the CIDRs overlap for each VCN and Subnet mentioned in excelsheet
def validate_cidr(cidr_list, cidrs_dict):
    cidroverlap_check=False
    cidrdup_check=False

    for i in range(0,len(cidr_list)):
        if (cidr_list[i] == ""):
            continue
        cidr1 = ipaddr.IPNetwork(cidr_list[i])

        for j in range(i+1,len(cidr_list)):
            if (cidr_list[j] == ""):
                continue

            cidr2 = ipaddr.IPNetwork(cidr_list[j])
            # Check for Duplicate CIDRs
            if(str(cidr1)==str(cidr2)):
                logging.log(60, "ROW " + str(j + 3) + " : Duplicate CIDR value " + str(cidr2) + " with ROW " + str(i + 3))
                cidrdup_check = True
                continue

            # Check for Overlapping CIDRs
            bool=cidr1.overlaps(cidr2)
            if(bool==True):
                logging.log(60, "ROW " + str(j+3) + " : Overlapping CIDR value " + str(cidr2) + " with ROW " + str(i + 3)+ " CIDR value "+str(cidr1))
                cidroverlap_check=True

    if (cidroverlap_check == True or cidrdup_check==True):
        return True
    else:
        return False

#Fetch the dhcp list and vcn cidrs for cross validation of values
def fetch_dhcplist_vcn_cidrs(filename):
    # Read the Subnets tab from excel
    df = pd.read_excel(filename, sheet_name='DHCP', skiprows=1)
    #Drop null values
    df = df.dropna(how='all')
    #Reset index
    df = df.reset_index(drop=True)

    # Get a list of dhcp options name
    dhcplist = df['dhcp_option_name'].tolist()

    # Read the Subnets tab from excel
    dfv = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    #Drop null values
    dfv = dfv.dropna(how='all')
    #Reset index
    dfv = dfv.reset_index(drop=True)

    cidr_list = []
    vcn_cidrs = {}
    # List of the column headers
    dfcolumns = dfv.columns.values.tolist()

    #Loop through each row
    for i in dfv.index:
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dfv.loc[i, columnname]).strip()
            if columnname == "vcn_cidr":
                # Collect CIDR List for validating
                if str(columnvalue).lower() == "nan":
                    cidr_list.append("")
                else:
                    cidr_list.append(str(columnvalue))
                    vcn_cidrs.update({str(dfv.loc[i,'vcn_name']) : str(columnvalue) })

    return dhcplist,vcn_cidrs

#Check if subnets tab is compliant
def validate_subnets(filename,comp_ids,vcnobj):

    # Read the Subnets tab from excel
    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    #Drop null values
    df = df.dropna(how='all')
    #Reset index
    df = df.reset_index(drop=True)

    # Counter to fetch the row number
    count = 0

    cidr_list = []
    cidrs_dict = {}
    subnet_dnsdup_check=False
    subnet_dnswrong_check=False
    subnet_empty_check=False
    subnet_wrong_check=False
    subnet_comp_check=False
    subnet_reg_check=False
    subnet_vcn_check=False
    subnet_dhcp_check = False
    subnet_vcn_cidr_check = False
    subnet_dns=[]
    subnetname_list=[]
    vcn_list=[]

    logging.log(60,"Start Null or Wrong value check in each row-----------------")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    #Fetch the dhcp list and VCN CIDR List for cross validation
    list = fetch_dhcplist_vcn_cidrs(filename)
    dhcplist = list[0]
    vcncidrlist = list[1]

    #Loop through each row
    for i in df.index:
        count = count + 1
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if (str(df[df.columns[0]][i]) in commonTools.endNames):
            logging.log(60,"Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            break

        # Check for invalid Region
        region = str(df[df.columns[0]][i])
        if (region.lower()!="nan" and region.lower() not in ct.all_regions):
            logging.log(60, "ROW " + str(i + 3) + " : Region " + region + " is not subscribed to tenancy")
            subnet_reg_check = True

        #Check for invalid compartment name
        comp_name = str(df[df.columns[1]][i])
        try:
            comp_id = comp_ids[comp_name]
        except KeyError:
            logging.log(60,"ROW "+str(i+3) + " : Compartment " + comp_name + " doesnot exist in OCI")
            subnet_comp_check=True

        #Check for invalid VCN name
        vcn_name=str(df[df.columns[2]][i])
        if(vcn_name.lower()!="nan" and vcn_name not in vcnobj.vcn_names):
            logging.log(60,"ROW "+str(i+3) + " : VCN "+vcn_name+" not part of VCNs Tab")
            subnet_vcn_check=True

        # Check if the dns_label field has special characters or is duplicate
        dns_value=str(df[str(df.columns[16])][i])
        dns_subnetname=str(df[str(df.columns[3])][i])
        dns_vcn=str(df[str(df.columns[2])][i])

        if (dns_value.lower() == "nan"):
            subnet_dns.append("")
        else:
            if (dns_vcn not in vcn_list):
                vcn_list.append(dns_vcn)
                if (dns_subnetname not in subnetname_list):
                    subnetname_list.append(dns_subnetname)
                    if (dns_value not in subnet_dns):
                        subnet_dns.append(dns_value)
            else:
                if (dns_value not in subnet_dns):
                    subnet_dns.append(dns_value)
                else:
                    logging.log(60,"ROW " + str(i + 3) + " : Duplicate dns_label value " + dns_value + " for subnet " + str(dns_subnetname) + " of vcn " + str(dns_vcn))
                    subnet_dns.append(dns_value)
                    subnet_dnsdup_check = True

            '''
            if (dns_value not in subnet_dns):
                subnet_dns.append(dns_value)
                subnetname_list.append(dns_subnetname)
            else:
                logging.log(60, "ROW " + str(i + 3) + " : Duplicate dns_label value " + dns_value +" with ROW "+str(subnet_dns.index(dns_value)+3))
                subnet_dns.append(dns_value)
                subnet_dnsdup_check = True
            '''
            subnet_dnswrong_check = checklabel(dns_value, count)

        # Check if the Service and Internet gateways are set appropriately; if not display the message;
        sgw_value=str(df[str(df.columns[11])][i])
        igw_value = str(df[str(df.columns[13])][i])
        if(igw_value.lower()!="nan" and sgw_value.lower()!="nan"):
            if (igw_value.lower() == "y" and sgw_value.lower() == "all_services"):
                logging.log(60,"ROW " + str(count+2) + " : Internet Gateway target cannot be used together with Service Gateway target for All Services in the same routing table. Change either the value of SGW or IGW configure route !!")
                subnet_wrong_check = True

        # Collect CIDR List for validating
        if str(df[df.columns[4]][i]).lower() == "nan":
            cidr_list.append("")
            continue
        else:
            cidr_list.append(str(df[df.columns[4]][i]))

        # Check for null values and display appropriate message
        for j in df.keys():
            if (str(df[j][i]) == "NaN" or str(df[j][i]) == "nan" or str(df[j][i]) == ""):
                #only dhcp_option_name, route table name, seclist_names and dns_label columns can be empty
                if j == str(df.columns[16]) or j == str(df.columns[7]) or j == str(df.columns[8]) or j == str(df.columns[9]):
                    pass
                else:
                    logging.log(60,"ROW " + str(count+2) + " : Empty value at column " +j)
                    subnet_empty_check = True

        #Lop through Columns and cross validate - 1. Subnets and VCN CIDRs and 2. Subnet and DHCP Options
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df.loc[i, columnname]).strip()

            #Execute this portion of code only when called from DHCP function;(List cannot be empty)
            if dhcplist !=[]:
                if columnname == "dhcp_option_name\n(Leave blank if default dhcp option needs to be used)":
                    if columnvalue in dhcplist:
                        pass
                    else:
                        if columnvalue == 'nan':
                            continue
                        logging.log(60, "ROW " + str(i + 3) + " : Value \"" + columnvalue + "\" in column \"dhcp_option_name\" is not declared in DHCP tab.")
                        subnet_dhcp_check = True

            #Execute if list is []; list is empty when called from VCN function
            if columnname == "subnet_cidr":
                if columnvalue == "nan":
                    continue
                columnvalue = ipaddress.ip_network(columnvalue)

                for vcns in vcncidrlist:
                    vcncidrlist[vcns] = str(vcncidrlist[vcns]).strip()
                    vcn_cidr = ipaddress.ip_network(vcncidrlist[vcns])
                    if df.loc[i, 'vcn_name'] == vcns:
                        if columnvalue.subnet_of(vcn_cidr):
                            pass
                        else:
                            logging.log(60, "ROW " + str(i + 3) + " : Subnet CIDR - " + str(columnvalue) + "  does not fall under VCN CIDR - "+str(vcn_cidr))
                            subnet_vcn_cidr_check = True

    if (subnet_reg_check == True or subnet_vcn_check == True or subnet_comp_check == True or subnet_empty_check == True or subnet_dnswrong_check == True or subnet_wrong_check == True or subnet_dnsdup_check == True or subnet_dhcp_check == True and subnet_vcn_cidr_check == True):
        print("Null or Wrong value Check failed!!")
        subnet_check=True
    else:
        subnet_check=False
    logging.log(60, "End Null or Wrong value Check in each row------------------\n")

    logging.log(60,"Start Subnet CIDRs Check---------------------------------")
    subnet_cidr_check = validate_cidr(cidr_list,cidrs_dict)
    if (subnet_cidr_check == True):
        print("Subnet CIDRs Check failed!!")
    logging.log(60, "End Subnet CIDRs Check---------------------------------\n")

    return subnet_check,subnet_cidr_check


#Check if VCNs tab is compliant
def validate_vcns(filename,comp_ids,vcnobj):#,vcn_cidrs,vcn_compartment_ids):

    vcn_ids = get_vcn_ids(comp_ids, config)

    #Read the VCNs tab from excel
    df = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    # Drop null values
    df = df.dropna(how='all')
    # Reset index
    df = df.reset_index(drop=True)

    #Counter to fetch the row number
    count = 0
    cidr_list = []
    cidrs_dict = {}

    vcn_empty_check=False
    vcn_dnswrong_check=False
    #vcn_dnsdup_check=False
    vcn_comp_check=False
    vcn_reg_check=False
    vcn_vcnname_check=False

    vcn_check=False

    logging.log(60,"Start Null or Wrong value Check in each row---------------")
    vcn_dns=[]
    vcn_names=[]

    #Loop through each row
    for i in df.index:
        count = count + 1

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df[df.columns[0]][i]) in commonTools.endNames:
            logging.log(60,"Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            break

        # Check for invalid Region
        region=str(df[df.columns[0]][i])
        if(region.lower()!="nan" and region.lower() not in ct.all_regions):
            logging.log(60, "ROW " + str(i + 3) + " : Region " + region + " is not subscribed to tenancy")
            vcn_reg_check=True

        #Check for invalid Compartment Name
        comp_name = str(df[df.columns[1]][i])
        try:
            comp_id=comp_ids[comp_name]
        except KeyError:
            logging.log(60,"ROW "+str(i+3)+" : Compartment " + comp_name + " doesnot exist in OCI")
            vcn_comp_check=True

        #Check for invalid(duplicate) vcn name
        vcn_name=str(df[str(df.columns[2])][i])
        if(vcn_name.lower()=='nan'):
            vcn_names.append("")
        else:
            if(vcn_name not in vcn_names):
                vcn_names.append(vcn_name)
            else:
                logging.log(60, "ROW " + str(i + 3) + " : Duplicate vcn_name value " + vcn_name + " with ROW " + str(vcn_names.index(vcn_name) + 3))
                vcn_names.append(vcn_name)
                vcn_vcnname_check=True


        # Check if the dns_label field has special characters # duplicates for vcn dns_label allowed
        dns_value = str(df[str(df.columns[10])][i])
        if (dns_value.lower() == "nan"):
            vcn_dns.append("")
        else:
            """if (dns_value not in vcn_dns):
                vcn_dns.append(dns_value)
            else:
                logging.log(60, "ROW " + str(i + 3) + " : Duplicate dns_label value " + dns_value +" with ROW "+str(vcn_dns.index(dns_value)+3))
                vcn_dns.append(dns_value)
                vcn_dnsdup_check = True
            """
            vcn_dnswrong_check = checklabel(dns_value, count)

        # Collect CIDR List for validating
        if str(df[df.columns[3]][i]).lower() == "nan":
            cidr_list.append("")
        else:
            cidr_list.append(str(df[df.columns[3]][i]))
            cidrs_dict.update({str(df[df.columns[3]][i]): str(df[df.columns[2]][i])})

        #Check for null values and display appropriate message
        for j in df.keys():
            if (str(df[j][i]) == "NaN" or str(df[j][i]) == "nan" or str(df[j][i]) == ""):
                if j == str(df.columns[10]):
                    continue
                else:
                    logging.log(60,"ROW " + str(count+2) + " : Empty value at column " + j)
                    vcn_empty_check = True


    if (vcn_vcnname_check==True or vcn_reg_check == True or vcn_comp_check == True or vcn_empty_check == True or vcn_dnswrong_check == True): # or vcn_dnsdup_check == True):
        print("Null or Wrong value Check failed!!")
        vcn_check = True
    logging.log(60, "End Null or Wrong value Check in each row---------------\n")

    logging.log(60,"Start VCN CIDRs Check--------------------------------------")
    vcn_cidr_check = validate_cidr(cidr_list, cidrs_dict)
    if(vcn_cidr_check==True):
        print("VCN CIDRs Check failed!!")
    logging.log(60, "End VCN CIDRs Check--------------------------------------\n")

    logging.log(60,"Start LPG Peering Check---------------------------------------------")
    logging.log(60,"Current Status of LPGs in OCI for each VCN listed in VCNs tab:")
    oci_vcn_lpgs={}


    #Loop through each row
    for i in df.index:
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df[df.columns[0]][i]) in commonTools.endNames:
            break

        region = str(df[df.columns[0]][i]).lower().strip()

        #Fetches current LPGs for each VCN and show its status
        comp_name = str(df[df.columns[1]][i]).strip()
        vcn_name = str(df[df.columns[2]][i]).strip()

        try:
            comp_id=comp_ids[comp_name]
        except KeyError:
            continue
        try:
            vcn_id=vcn_ids[vcn_name]
        except KeyError:
            lpg = vcnobj.vcn_lpg_names[vcn_name][0]
            if (lpg != 'n'):
                logging.log(60,"ROW "+str(i+3)+" : VCN " + vcn_name + " doesnot exist in OCI. VCN and its LPGs "+str(vcnobj.vcn_lpg_names[vcn_name]) +" will be created new")
            else:
                logging.log(60,"ROW "+str(i+3)+" : VCN " + vcn_name + " doesnot exist in OCI. VCN will be created new")
            continue

        oci_vcn_lpgs[vcn_name]=[]
        vcn_lpg_str=""

        config.__setitem__("region", ct.region_dict[region])
        vnc = oci.core.VirtualNetworkClient(config)
        lpg_list=vnc.list_local_peering_gateways(compartment_id=comp_id,vcn_id=vcn_id)

        if(len(lpg_list.data)==0):
            logging.log(60,"ROW "+str(i+3)+" : LPGs for VCN "+vcn_name+ " in OCI-  None")
        else:
            for lpg in lpg_list.data:
                oci_vcn_lpgs[vcn_name].append(lpg.display_name)
                vcn_lpg_str=lpg.display_name + " : " + lpg.peering_status+", "+vcn_lpg_str
            logging.log(60,"ROW "+str(i+3)+" : LPGs for VCN " + vcn_name + " in OCI-  "+vcn_lpg_str)


    logging.log(60,"####### Below is the LPG peering as per CD3 data: Please verify !! ##########")
    #Show the peering details of each lpg in Hub,Spoke or Peer VCNs
    vcn_peer_check = showPeering(vcnobj,oci_vcn_lpgs)
    if (vcn_peer_check == True):
        print("Please verify LPG Peering Status in log file !!")
    logging.log(60,"\nPlease go through \"CD3 Modification Procedure\" of confluence page for information on correct order of lpg entries for non-greenfield tenancies")
    logging.log(60,"Link: https://confluence.oraclecorp.com/confluence/display/NAC/Support+for+Non-GreenField+Tenancies")


    logging.log(60,"End LPG Peering Check---------------------------------------------\n")

    return vcn_check,vcn_cidr_check,vcn_peer_check

#Checks if the fields in DHCP tab are compliant
def validate_dhcp(filename,comp_ids,vcnobj):
    #Read DHCP tab from excel
    df = pd.read_excel(filename, sheet_name='DHCP', skiprows=1)
    #Drop null values
    df = df.dropna(how='all')
    #Reset index
    df = df.reset_index(drop=True)

    empty = ['', 'Nan', 'NaN', 'nan']
    dhcp_empty_check=False
    dhcp_wrong_check=False
    dhcp_comp_check=False
    dhcp_vcn_check=False
    dhcp_reg_check=False

    # Counter to fetch the row number
    count = 0

    logging.log(60,"Start Null or Wrong value Check in each row----------------")
    for i in df.index:
        count = count + 1

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df[df.columns[0]][i]) in commonTools.endNames:
            logging.log(60,"Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            break

        # Check for invalid Region
        region = str(df[df.columns[0]][i])

        if (region.lower()!="nan" and region.lower() not in ct.all_regions):
            logging.log(60, "ROW " + str(i + 3) + " : Region " + region + " is not subscribed to tenancy")
            dhcp_reg_check = True

        #Check for invalid compartment name
        comp_name = str(df[df.columns[1]][i])
        try:
            comp_id = comp_ids[comp_name]
        except KeyError:
            logging.log(60,"ROW "+str(i+3) + " : Compartment " + comp_name + " doesnot exist in OCI")
            dhcp_comp_check=True

        # Check for invalid VCN name
        vcn_name = str(df[df.columns[2]][i])
        if (vcn_name.lower()!="nan" and vcn_name not in vcnobj.vcn_names):
            logging.log(60, "ROW " + str(i + 3) + " : VCN "+vcn_name+" not part of VCNs Tab")
            dhcp_vcn_check = True

        for j in df.keys():
            #Check the customer_dns_servers column; if empty return error based on the value in server_type column
            if j == str(df.columns[6]):
                if str(df[df.columns[6]][i]) in empty:
                    if str(df[df.columns[4]][i]) == "CustomDnsServer":
                        logging.log(60,"ROW  " + str(count+2) + ": 'custom_dns_servers' column cannot be empty if server type is 'CustomDnsServer'")
                        dhcp_wrong_check = True
                    elif str(df[df.columns[4]][i]) == "VcnLocalPlusInternet":
                        continue
            else:
                #Check if there are any field that is empty; display appropriate message
                if str(df[j][i]) in empty and j != str(df.columns[5]):
                    logging.log(60,"ROW " + str(count+2) + " : Empty value at column " + j)
                    dhcp_empty_check = True
                    
    logging.log(60,"End Null or Wrong value Check in each row-----------------\n")
    if (dhcp_reg_check==True or dhcp_vcn_check==True or dhcp_wrong_check == True or dhcp_comp_check==True or dhcp_empty_check==True): # or subnet_dhcp_check == True):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def main():
    #CD3 Validation begins here for Sunbnets, VCNs and DHCP tabs
    #Flag to check if for errors
    vcnobj = parseVCNs(filename)

    logging.log(60,"============================= Verifying VCNs Tab ==========================================\n")
    print("\nProcessing VCNs Tab..")
    vcn_check,vcn_cidr_check,vcn_peer_check = validate_vcns(filename, ct.ntk_compartment_ids, vcnobj)

    logging.log(60,"============================= Verifying Subnets Tab ==========================================\n")
    print("\nProcessing Subnets Tab..")
    subnet_check,subnet_cidr_check = validate_subnets(filename,ct.ntk_compartment_ids,vcnobj)

    logging.log(60,"============================= Verifying DHCP Tab ==========================================\n")
    print("\nProcessing DHCP Tab..")
    dhcp_check = validate_dhcp(filename,ct.ntk_compartment_ids,vcnobj)

    #Prints the final result; once the validation is complete
    if vcn_check == True or vcn_cidr_check == True or vcn_peer_check == True or subnet_check == True or subnet_cidr_check == True or dhcp_check == True:
        logging.log(60,"=======")
        logging.log(60,"Summary:")
        logging.log(60,"=======")
        logging.log(60,"ERROR: Make appropriate changes to CD3 Values as per above Errors and try again !!!")
        print("\n\nSummary:")
        print("=======")
        print("Errors Found!!! Please check cd3Validator.log for details before proceeding!!")
        exit(1)
    elif vcn_check == False and vcn_cidr_check == False and vcn_peer_check == False and subnet_check == False and subnet_cidr_check == False and dhcp_check == False:
        logging.log(60,"=======")
        logging.log(60,"Summary:")
        logging.log(60,"=======")
        logging.log(60,"There are no errors in CD3. Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed !!!")
        print("\n\nSummary:")
        print("=======")
        print("There are no errors in CD3. Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed !!!")
        exit(0)

if __name__ == '__main__':

    #Execution of the code begins here
    main()
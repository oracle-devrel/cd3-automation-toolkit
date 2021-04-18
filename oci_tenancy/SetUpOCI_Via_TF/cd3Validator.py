#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help you to validate the entries in CD3 sheet for - VCN, DHCP and Subnets Tabs
# CD3 Validator for Networking Objects
#
# Author: Shruthi Subramanian
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import argparse
import re
import pandas as pd
import os
import sys
import oci
import logging
import ipaddress
from functools import partial
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
from commonTools import *


CD3_LOG_LEVEL = 60
logging.addLevelName(CD3_LOG_LEVEL, "custom")
logging.basicConfig(filename="cd3Validator.log", filemode="w", format="%(asctime)s - %(message)s", level=60)
logger = logging.getLogger("cd3Validator")
log = partial(logger.log, CD3_LOG_LEVEL)

ct = commonTools()
compartment_ids = {}
vcn_ids = {}
vcn_cidrs = {}
vcn_compartment_ids = {}


def get_vcn_ids(compartment_ids, config):
    # Fetch the VCN ID
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        vnc = VirtualNetworkClient(config)
        for comp_id in compartment_ids.values():
            vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=comp_id)
            for vcn in vcn_list.data:
                # if(vcn.lifecycle_state == 'ACTIVE'):
                vcn_ids[vcn.display_name] = vcn.id
    return vcn_ids


# Checks for special characters in dns_label name
def checklabel(lable, count):
    present = False
    lable = str(lable).strip()
    if (lable == "Nan") or (lable == "") or (lable == "NaN") or (lable == "nan"):
        pass
    else:
        regex = re.compile('[@_!#$%^&* ()<>?/\|}{~:]')
        if (regex.search(lable) == None):
            pass
        else:
            log(f'ROW {count+2} : DNS Label value has special characters')
            present = True
    return present


# Shows LPG Peering that will be established based on hub_spoke_peer_none column
def showPeering(vcnsob, oci_vcn_lpgs):
    present = False
    # Check if the LPGs are sufficient for creating the peers.
    for left_vcn, value in vcnsob.peering_dict.items():
        right_vcns = value.split(",")
        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            right_vcn = right_vcn.strip()
            try:
                if (vcnsob.vcn_lpg_names[left_vcn][0].lower() == 'n' or vcnsob.vcn_lpg_names[right_vcn][0].lower() == 'n'):
                    log(f'ERROR!!! Cannot specify n for LPG Required field for either {left_vcn} or {right_vcn}; Since they are part of VCN peering')
                    present = True
                    continue
            except IndexError:
                log(f'ERROR!!! Insufficient LPGs declared for either {left_vcn} or {right_vcn}. Check LPG Required column for both VCNs in VCNs tab')
                present = True
                continue
            left_vcn_lpg = vcnsob.vcn_lpg_names[left_vcn][0]
            vcnsob.vcn_lpg_names[left_vcn].pop(0)
            right_vcn_lpg = vcnsob.vcn_lpg_names[right_vcn][0]
            vcnsob.vcn_lpg_names[right_vcn].pop(0)
            log(f'{left_vcn_lpg} of VCN {left_vcn} peers with {right_vcn_lpg} of VCN {right_vcn}')

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


# Checks if the CIDRs overlap for each VCN and Subnet mentioned in excelsheet
def validate_cidr(cidr_list, cidrs_dict):
    cidroverlap_check = False
    cidrdup_check = False
    cidr_check = False

    for i in range(0, len(cidr_list)):
        try:
            ipaddress.ip_network(cidr_list[i])
        except ValueError:
            log(f'Row  {str(i+3)} Field CIDR Block {cidr_list[i]} is invalid. CIDR range has host bits set.')
            cidr_check = True

    for i in range(0, len(cidr_list)):
        if (cidr_list[i] == ""):
            continue
        try:
            cidr1 = ipaddress.ip_network(cidr_list[i])
        except ValueError:
            continue

        for j in range(i + 1, len(cidr_list)):
            if (cidr_list[j] == ""):
                continue
            try:
                cidr2 = ipaddress.ip_network(cidr_list[j])
            except ValueError:
                continue
            # Check for Duplicate CIDRs
            if (str(cidr1) == str(cidr2)):
                log(f'ROW {j+3} : Duplicate CIDR value {cidr2} with ROW {i+3}')
                cidrdup_check = True
                continue

            # Check for Overlapping CIDRs
            if cidr1.overlaps(cidr2):
                log(f'ROW {str(j+3)} : Overlapping CIDR value {str(cidr2)} with ROW {str(i+3)} CIDR value {str(cidr1)}')
                cidroverlap_check = True
    return any([cidroverlap_check, cidrdup_check, cidr_check])


# Fetch the dhcp list and vcn cidrs for cross validation of values
def fetch_dhcplist_vcn_cidrs(filename):
    # Read the Subnets tab from excel
    df = pd.read_excel(filename, sheet_name='DHCP', skiprows=1)
    # Drop null values
    df = df.dropna(how='all')
    # Reset index
    df = df.reset_index(drop=True)

    # Get a list of dhcp options name
    dhcplist = df['DHCP Option Name'].tolist()

    # Read the Subnets tab from excel
    dfv = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    # Drop null values
    dfv = dfv.dropna(how='all')
    # Reset index
    dfv = dfv.reset_index(drop=True)

    cidr_list = []
    vcn_cidrs = {}
    # List of the column headers
    dfcolumns = dfv.columns.values.tolist()

    # Loop through each row
    for i in dfv.index:
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dfv.loc[i, columnname]).strip()
            if columnname == "CIDR Block":
                # Collect CIDR List for validating
                if str(columnvalue).strip().lower() == "nan":
                    cidr_list.append("")
                else:
                    cidr_list.append(str(columnvalue))
                    vcn_cidrs.update({str(dfv.loc[i, 'VCN Name']): str(columnvalue)})
    return dhcplist, vcn_cidrs


# Check if subnets tab is compliant
def validate_subnets(filename, comp_ids, vcnobj):
    # Read the Subnets tab from excel
    df, col_headers = commonTools.read_cd3(filename, "Subnets")

    # Drop null values
    df = df.dropna(how='all')
    # Reset index
    df = df.reset_index(drop=True)

    # Counter to fetch the row number
    count = 0

    cidr_list = []
    cidrs_dict = {}
    subnet_dnsdup_check = False
    subnet_dnswrong_check = False
    subnet_empty_check = False
    subnet_wrong_check = False
    subnet_comp_check = False
    subnet_reg_check = False
    subnet_vcn_check = False
    subnet_dhcp_check = False
    subnet_vcn_cidr_check = False
    subnet_dns_length = False
    subnet_dns = []
    subnetname_list = []
    vcn_list = []

    log("Start Null or Wrong value check in each row-----------------")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Fetch the dhcp list and VCN CIDR List for cross validation
    list = fetch_dhcplist_vcn_cidrs(filename)
    dhcplist = list[0]
    vcncidrlist = list[1]

    # Loop through each row
    for i in df.index:
        count = count + 1
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if (str(df.loc[i, 'Region']) in commonTools.endNames):
            log('Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!')
            break

        # Check for invalid Region
        region = str(df.loc[i, 'Region'])
        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy')
            subnet_reg_check = True

        # Check for invalid compartment name
        comp_name = str(df.loc[i, 'Compartment Name'])
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI')
                dhcp_comp_check = True

        # Check for invalid VCN name
        vcn_name = str(df.loc[i, 'VCN Name'])
        if (vcn_name.lower() != "nan" and vcn_name not in vcnobj.vcn_names):
            log(f'ROW {i+3} : VCN {vcn_name} not part of VCNs Tab')
            subnet_vcn_check = True

        # Check if the dns_label field has special characters or if it has greater than 15 characters or is duplicate
        dns_value = str(df.loc[i, 'DNS Label'])
        dns_subnetname = str(df.loc[i, 'Subnet Name'])
        dns_vcn = str(df.loc[i, 'VCN Name'])

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
                    log(f'ROW {i+3} : Duplicate DNS Label value "{dns_value}" for subnet "{dns_subnetname}" of vcn "{dns_vcn}"')
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

        if (len(dns_value) > 15):
            log(f'ROW {i+3} : DNS Label value "{dns_value}" for subnet "{dns_subnetname}" of vcn "{dns_vcn}" has more alphanumeric characters than the allowed maximum limit of 15.')
            subnet_dns_length = True

        # Check if the Service and Internet gateways are set appropriately; if not display the message;
        sgw_value = str(df.loc[i, 'Configure SGW Route(n|object_storage|all_services)'])
        igw_value = str(df.loc[i, 'Configure IGW Route(y|n)'])
        if (igw_value.lower() != "nan" and sgw_value.lower() != "nan"):
            if (igw_value.lower() == "y" and sgw_value.lower() == "all_services"):
                log(f'ROW {count + 2} : Internet Gateway target cannot be used together with Service Gateway target for All Services in the same routing table. Change either the value of SGW or IGW configure route !!')
                subnet_wrong_check = True

        # Collect CIDR List for validating
        if str(df.loc[i, 'CIDR Block']).lower() == "nan":
            cidr_list.append("")
            continue
        else:
            cidr_list.append(str(df.loc[i, 'CIDR Block']))

        # Check for null values and display appropriate message
        labels = ['DNS Label', 'DHCP Option Name', 'Route Table Name', 'Seclist Names']
        for j in df.keys():
            if (str(df[j][i]) == "NaN" or str(df[j][i]) == "nan" or str(df[j][i]) == ""):
                # only dhcp_option_name, route table name, seclist_names and dns_label columns can be empty
                if j in labels or commonTools.check_column_headers(j) in commonTools.tagColumns:
                    pass
                else:
                    log(f'ROW {count+2} : Empty value at column {j}')
                    subnet_empty_check = True

        # Lop through Columns and cross validate - 1. Subnets and VCN CIDRs and 2. Subnet and DHCP Options
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df.loc[i, columnname]).strip()

            # Execute this portion of code only when called from DHCP function;(List cannot be empty)
            if dhcplist != []:
                if columnname == "DHCP Option Name":
                    if columnvalue in dhcplist or columnvalue == 'n':
                        pass
                    else:
                        if columnvalue == 'nan':
                            continue
                        log(f'ROW {i + 3} : Value "{columnvalue}" in column "DHCP Option Name" is not declared in DHCP tab.')
                        subnet_dhcp_check = True

            # Execute if list is []; list is empty when called from VCN function
            if columnname == "CIDR Block":
                if columnvalue == "nan":
                    continue
                try:
                    columnvalue = ipaddress.ip_network(columnvalue)
                except ValueError:
                    continue

                for vcns in vcncidrlist:
                    vcncidrlist[vcns] = str(vcncidrlist[vcns]).strip()
                    try:
                        vcn_cidr = ipaddress.ip_network(vcncidrlist[vcns])
                    except ValueError:
                        continue
                    if df.loc[i, 'VCN Name'] == vcns:
                        if columnvalue.subnet_of(vcn_cidr):
                            pass
                        else:
                            log(f'ROW {i+3} : Subnet CIDR - {columnvalue} does not fall under VCN CIDR - {vcn_cidr}')
                            subnet_vcn_cidr_check = True

    if any([subnet_reg_check, subnet_vcn_check, subnet_comp_check, subnet_empty_check, subnet_dnswrong_check, subnet_wrong_check, subnet_dnsdup_check, subnet_dns_length, subnet_dhcp_check, subnet_vcn_cidr_check]):
        print("Null or Wrong value Check failed!!")
        subnet_check = True
    else:
        subnet_check = False
    log("End Null or Wrong value Check in each row------------------\n")

    log("Start Subnet CIDRs Check---------------------------------")
    subnet_cidr_check = validate_cidr(cidr_list, cidrs_dict)
    if (subnet_cidr_check == True):
        print("Subnet CIDRs Check failed!!")
    log("End Subnet CIDRs Check---------------------------------\n")

    return subnet_check, subnet_cidr_check


# Check if VCNs tab is compliant
def validate_vcns(filename, comp_ids, vcnobj, config):  # ,vcn_cidrs,vcn_compartment_ids):
    vcn_ids = get_vcn_ids(comp_ids, config)

    # Read the VCNs tab from excel
    df, col_headers = commonTools.read_cd3(filename, "VCNs")

    # Drop null values
    df = df.dropna(how='all')
    # Reset index
    df = df.reset_index(drop=True)

    # Counter to fetch the row number
    count = 0
    cidr_list = []
    cidrs_dict = {}

    vcn_empty_check = False
    vcn_dnswrong_check = False
    # vcn_dnsdup_check=False
    vcn_comp_check = False
    vcn_reg_check = False
    vcn_vcnname_check = False
    vcn_dns_length =  False

    vcn_check = False

    log("Start Null or Wrong value Check in each row---------------")
    vcn_dns = []
    vcn_names = []

    # Loop through each row
    for i in df.index:
        count = count + 1

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df.loc[i, 'Region']) in commonTools.endNames:
            log("Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            break

        # Check for invalid Region
        region = str(df.loc[i, 'Region'])
        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy')
            vcn_reg_check = True

        # Check for invalid Compartment Name
        comp_name = str(df.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3}  : Compartment {comp_name} + does not exist in OCI')
                vcn_comp_check = True

        # Check for invalid(duplicate) vcn name
        vcn_name = str(df.loc[i, 'VCN Name'])
        if (vcn_name.lower() == 'nan'):
            vcn_names.append("")
        else:
            if (vcn_name not in vcn_names):
                vcn_names.append(vcn_name)
            else:
                log(f'ROW {i+3} : Duplicate VCN Name value {vcn_name}  with ROW {vcn_names.index(vcn_name) + 3}')
                vcn_names.append(vcn_name)
                vcn_vcnname_check = True

        # Check if the dns_label field has special characters # duplicates for vcn dns_label allowed # dns length not more than 15 characters
        dns_value = str(df.loc[i, 'DNS Label'])
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

        if (len(dns_value) > 15):
            log(f'ROW {i+3} : DNS Label value {dns_value} has more alphanumeric characters than the allowed maximum limit of 15.')
            vcn_dns_length = True

        # Collect CIDR List for validating
        if str(df.loc[i, 'CIDR Block']).lower() == "nan":
            cidr_list.append("")
        else:
            cidr_list.append(str(df.loc[i, 'CIDR Block']))
            cidrs_dict.update({str(df.loc[i, 'CIDR Block']): str(df.loc[i, 'VCN Name'])})

        # Check for null values and display appropriate message
        for j in df.keys():
            if (str(df[j][i]) == "NaN" or str(df[j][i]) == "nan" or str(df[j][i]) == ""):
                if j == 'DNS Label' or commonTools.check_column_headers(j) in commonTools.tagColumns:
                    continue
                else:
                    log(f'ROW {count+2} : Empty value at column {j}')
                    vcn_empty_check = True

    if any([vcn_vcnname_check, vcn_reg_check, vcn_comp_check, vcn_empty_check, vcn_dnswrong_check, vcn_dns_length]):  # or vcn_dnsdup_check == True):
        print("Null or Wrong value Check failed!!")
        vcn_check = True
    log("End Null or Wrong value Check in each row---------------\n")

    log("Start VCN CIDRs Check--------------------------------------")
    vcn_cidr_check = validate_cidr(cidr_list, cidrs_dict)
    if (vcn_cidr_check == True):
        print("VCN CIDRs Check failed!!")
    log("End VCN CIDRs Check--------------------------------------\n")

    log("Start LPG Peering Check---------------------------------------------")
    log("Current Status of LPGs in OCI for each VCN listed in VCNs tab:")
    oci_vcn_lpgs = {}

    # Loop through each row
    for i in df.index:
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df.loc[i, 'Region']) in commonTools.endNames:
            break

        region = str(df.loc[i, 'Region']).lower().strip()

        # Fetches current LPGs for each VCN and show its status
        comp_name = str(df.loc[i, 'Compartment Name']).strip()
        vcn_name = str(df.loc[i, 'VCN Name']).strip()

        try:
            comp_id = comp_ids[comp_name]
        except KeyError:
            continue
        try:
            vcn_id = vcn_ids[vcn_name]
        except KeyError:
            lpg = vcnobj.vcn_lpg_names[vcn_name][0]
            if (lpg != 'n'):
                log(f'ROW {i+3} : VCN {vcn_name} does not exist in OCI. VCN and its LPGs {vcnobj.vcn_lpg_names[vcn_name]} will be created new')
            else:
                log(f'ROW {i+3} : VCN {vcn_name} does not exist in OCI. VCN will be created new')
            continue

        oci_vcn_lpgs[vcn_name] = []
        vcn_lpg_str = ""

        config.__setitem__("region", ct.region_dict[region])
        vnc = oci.core.VirtualNetworkClient(config)

        lpg_list = vnc.list_local_peering_gateways(compartment_id=comp_id, vcn_id=vcn_id)

        if (len(lpg_list.data) == 0):
            log(f'ROW {i+3} : LPGs for VCN {vcn_name} in OCI-  None')
        else:
            for lpg in lpg_list.data:
                oci_vcn_lpgs[vcn_name].append(lpg.display_name)
                vcn_lpg_str = lpg.display_name + " : " + lpg.peering_status + ", " + vcn_lpg_str
            log(f'ROW {i + 3} : LPGs for VCN {vcn_name} in OCI- {vcn_lpg_str}')

    log("####### Below is the LPG peering as per CD3 data: Please verify !! ##########")
    # Show the peering details of each lpg in Hub,Spoke or Peer VCNs
    vcn_peer_check = showPeering(vcnobj, oci_vcn_lpgs)
    if (vcn_peer_check == True):
        print("Please verify LPG Peering Status in log file !!")
    log("\nPlease go through \"CD3 Modification Procedure\" of confluence page for information on correct order of lpg entries for non-greenfield tenancies")
    log("Link: https://confluence.oraclecorp.com/confluence/display/NAC/Support+for+Non-GreenField+Tenancies")

    log("End LPG Peering Check---------------------------------------------\n")

    return vcn_check, vcn_cidr_check, vcn_peer_check


# Checks if the fields in DHCP tab are compliant
def validate_dhcp(filename, comp_ids, vcnobj):
    # Read DHCP tab from excel
    df, col_headers = commonTools.read_cd3(filename, "DHCP")

    # Drop null values
    df = df.dropna(how='all')
    # Reset index
    df = df.reset_index(drop=True)

    empty = ['', 'Nan', 'NaN', 'nan']
    dhcp_empty_check = False
    dhcp_wrong_check = False
    dhcp_comp_check = False
    dhcp_vcn_check = False
    dhcp_reg_check = False

    # Counter to fetch the row number
    count = 0

    log("Start Null or Wrong value Check in each row----------------")
    for i in df.index:
        count = count + 1

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df.loc[i, 'Region']) in commonTools.endNames:
            log("Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            break

        # Check for invalid Region
        region = str(df.loc[i, 'Region'])

        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy')
            dhcp_reg_check = True

        # Check for invalid compartment name
        comp_name = str(df.loc[i, 'Compartment Name'])
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI')
                dhcp_comp_check = True

        # Check for invalid VCN name
        vcn_name = str(df.loc[i, 'VCN Name'])
        if (vcn_name.lower() != "nan" and vcn_name not in vcnobj.vcn_names):
            log(f'ROW {i+3}: VCN {vcn_name} not part of VCNs Tab')
            dhcp_vcn_check = True

        for j in df.keys():
            # Check the customer_dns_servers column; if empty return error based on the value in server_type column
            if j == 'Custom DNS Server':
                if str(df.loc[i, 'Custom DNS Server']) in empty:
                    if str(df.loc[i, 'Server Type(VcnLocalPlusInternet|CustomDnsServer)']) == "CustomDnsServer":
                        log(f'ROW {count+2} : "Custom DNS Server" column cannot be empty if server type is "CustomDnsServer"')
                        dhcp_wrong_check = True
                    elif str(df.loc[i, 'Server Type(VcnLocalPlusInternet|CustomDnsServer)']) == "VcnLocalPlusInternet":
                        continue
            else:
                # Check if there are any field that is empty; display appropriate message
                if str(df[j][i]).strip() in empty and j != 'Search Domain' and commonTools.check_column_headers(
                        j) not in commonTools.tagColumns:
                    log(f'ROW {count+2}  : Empty value at column {j}')
                    dhcp_empty_check = True

    log("End Null or Wrong value Check in each row-----------------\n")
    if any([dhcp_reg_check, dhcp_vcn_check, dhcp_wrong_check, dhcp_comp_check, dhcp_empty_check]):  # or subnet_dhcp_check == True):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_cd3(filename, configFileName):
    # CD3 Validation begins here for Sunbnets, VCNs and DHCP tabs
    # Flag to check if for errors
    config = oci.config.from_file(file_location=configFileName)
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)
    vcnobj = parseVCNs(filename)

    log("============================= Verifying VCNs Tab ==========================================\n")
    print("\nProcessing VCNs Tab..")
    vcn_check, vcn_cidr_check, vcn_peer_check = validate_vcns(filename, ct.ntk_compartment_ids, vcnobj, config)

    log("============================= Verifying Subnets Tab ==========================================\n")
    print("\nProcessing Subnets Tab..")
    subnet_check, subnet_cidr_check = validate_subnets(filename, ct.ntk_compartment_ids, vcnobj)

    log("============================= Verifying DHCP Tab ==========================================\n")
    print("\nProcessing DHCP Tab..")
    dhcp_check = validate_dhcp(filename, ct.ntk_compartment_ids, vcnobj)

    # Prints the final result; once the validation is complete
    if any([vcn_check, vcn_cidr_check, vcn_peer_check, subnet_check, subnet_cidr_check, dhcp_check]):
        log("=======")
        log("Summary:")
        log("=======")
        log("ERROR: Make appropriate changes to CD3 Values as per above Errors and try again !!!")
        print("\n\nSummary:")
        print("=======")
        print("Errors Found!!! Please check cd3Validator.log for details before proceeding!!")
        exit(1)
    else:
        log("=======")
        log("Summary:")
        log("=======")
        log("There are no errors in CD3. Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed !!!")
        print("\n\nSummary:")
        print("=======")
        print("There are no errors in CD3. Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed !!!")
        exit(0)


def parse_args():
    parser = argparse.ArgumentParser(description="CD3 Validator")
    parser.add_argument("cd3file", help="Full Path of CD3 file")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Path to config file")
    return parser.parse_args()

if __name__ == '__main__':
    # Execution of the code begins here
    filename = args.cd3file
    configFileName = args.configFileName
    validate_cd3(filename, configFileName)

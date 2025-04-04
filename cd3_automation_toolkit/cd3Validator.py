#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help you to validate the entries in CD3 sheet for - VCN, DHCP and Subnets Tabs
# CD3 Validator for Networking Objects
#
# Author: Shruthi Subramanian
# Oracle Consulting
# Modified (TF Upgrade): CD3 Developers at Oracle
#

import logging
import ipaddress
import os
from functools import partial
import inspect
from oci.core.virtual_network_client import VirtualNetworkClient
from commonTools import *

'''
def get_vcn_ids(compartment_ids, config):
    # Fetch the VCN ID
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        vnc = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        for comp_id in compartment_ids.values():
            vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=comp_id)
            for vcn in vcn_list.data:
                # if(vcn.lifecycle_state == 'ACTIVE'):
                vcn_ids[vcn.display_name] = vcn.id
    return vcn_ids

# Shows LPG Peering that will be established based on hub_spoke_peer_none column
def showPeering(vcnsob):
    present = False
    # Check if the LPGs are sufficient for creating the peers.
    for key, value in vcnsob.peering_dict.items():
        left_vcn=key[0]
        region=key[1]
        right_vcns = value.split(",")
        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            right_vcn = right_vcn.strip()
            try:
                if (vcnsob.vcn_lpg_names[left_vcn,region][0].lower() == 'n' or vcnsob.vcn_lpg_names[right_vcn,region][0].lower() == 'n'):
                    log(f'ERROR!!! Cannot specify n for "LPG Required" field for either {left_vcn} or {right_vcn}; Since they are part of VCN peering.')
                    present = True
                    continue
            except IndexError:
                log(f'ERROR!!! Insufficient LPGs declared for either {left_vcn} or {right_vcn}. Check LPG Required column for both VCNs in VCNs tab.')
                present = True
                continue
            left_vcn_lpg = vcnsob.vcn_lpg_names[left_vcn,region][0]
            vcnsob.vcn_lpg_names[left_vcn,region].pop(0)
            right_vcn_lpg = vcnsob.vcn_lpg_names[right_vcn,region][0]
            vcnsob.vcn_lpg_names[right_vcn,region].pop(0)
            log(f'{left_vcn_lpg} of VCN {left_vcn} peers with {right_vcn_lpg} of VCN {right_vcn}.')

    return present

'''

# Check for unique values across two sheets
def compare_values(list_to_check,value_to_check,index):
    if (value_to_check not in list_to_check):
        if 'Availability Domain(AD1|AD2|AD3)' in index[1]:
            log(f'ROW {index[0] + 3} : Invalid value for column "{index[1]}".')
        else:
            log(f'ROW {index[0] + 3} : Invalid value for column "{index[1]}". {value_to_check} does not exist in {index[2]} tab.')
        return True
    return False

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
            log(f'ROW {count+2} : "DNS Label" value has special characters.')
            present = True
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
def validate_cidr(cidr_list):
    cidroverlap_check = False
    cidrdup_check = False
    cidr_check = False

    for i in range(0, len(cidr_list)):
        try:
            rowN = cidr_list[i][1]
            ipaddress.ip_network(cidr_list[i][0])
        except ValueError:
            log(f'Row {str(rowN)} Field "CIDR Block" {cidr_list[i]} is invalid. CIDR range has host bits set.')
            cidr_check = True

    for i in range(0, len(cidr_list)):
        if (cidr_list[i][0] == ""):
            continue
        try:
            cidr1 = ipaddress.ip_network(cidr_list[i][0])
            rowI = cidr_list[i][1]
        except ValueError:
            continue

        for j in range(i + 1, len(cidr_list)):
            if (cidr_list[j][0] == ""):
                continue
            try:
                cidr2 = ipaddress.ip_network(cidr_list[j][0])
                rowJ = cidr_list[j][1]
            except ValueError:
                continue
            # Check for Duplicate CIDRs
            if (str(cidr1) == str(cidr2)):
                log(f'ROW {rowJ} : Duplicate CIDR value {cidr2} with ROW {rowI}.')
                cidrdup_check = True
                continue

            # Check for Overlapping CIDRs
            if cidr1.overlaps(cidr2):
                log(f'ROW {str(j+3)} : Overlapping CIDR value {str(cidr2)} with ROW {str(i+3)} CIDR value {str(cidr1)}.')
                cidroverlap_check = True
    return any([cidroverlap_check, cidrdup_check, cidr_check])

#validate NSGs columns for services - Instances, FSS etc
def validate_nsgs_column(i,region,columnvalue,subnet_name,subnetobj,vcn_nsg_list):
    vcn_nsg_check = False
    vcn_name = None
    key = region,subnet_name
    try:
        vcn_name = subnetobj.vcn_subnet_map[key][1]
    except Exception as e:
        pass

    NSGs = columnvalue.split(",")
    for nsg in NSGs:
        nsg = region + "_" + str(vcn_name) + "_" + nsg
        # Cross check the NSG names in Instances and NSGs sheet
        vcn_nsg_check = compare_values(vcn_nsg_list.tolist(), nsg, [i, 'NSGs', 'NSGs'])
    return vcn_nsg_check


# Fetch the dhcp list and vcn cidrs for cross validation of values
def fetch_vcn_cidrs(filename):
    vcn_cidrs = {}
    # List of the column headers
    dfv = data_frame(filename, 'VCNs')
    dfcolumns = dfv.columns.values.tolist()

    # Loop through each row
    for i in dfv.index:
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dfv.loc[i, columnname]).strip()
            if columnname == "CIDR Blocks":
                # Collect CIDR List for validating
                if str(columnvalue).lower() == "nan":
                    pass
                else:
                    vcn_cidrs.update({(str(dfv.loc[i, 'VCN Name']).strip(), str(dfv.loc[i, 'Region']).strip().lower()): str(columnvalue)})
    return vcn_cidrs


# Check if subnets tab is compliant
def validate_subnets(filename, comp_ids, vcnobj):

    # Counter to fetch the row number
    count = 0

    cidr_list = []
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
    dhcplist = []

    log("Start Null or Wrong value check in each row-----------------")

    dfsub = data_frame(filename, 'SubnetsVLANs')
    dfdhcp = data_frame(filename, 'DHCP')
    # List of the column headers
    dfcolumns = dfsub.columns.values.tolist()

    # Fetch the dhcp list and VCN CIDR List for cross validation
    vcncidrlist = fetch_vcn_cidrs(filename)

    # Get a list of dhcp options name from DHCP tab
    for d in dfdhcp.index:
        vcn_name = str(dfdhcp.loc[d, 'VCN Name']).strip()
        dhcp_name = str(dfdhcp.loc[d, 'DHCP Option Name']).strip()
        dhcplist.append(vcn_name+"_"+dhcp_name)

    # Loop through each row
    for i in dfsub.index:
        subnet_or_vlan = (str(dfsub.loc[i, 'Subnet or VLAN']).strip()).split("::")[0]
        count = count + 1
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if (str(dfsub.loc[i, 'Region']).strip() in commonTools.endNames):
            break

        # Check for invalid Region
        region = str(dfsub.loc[i, 'Region']).strip()

        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            subnet_reg_check = True

        # Check for invalid compartment name
        comp_name = str(dfsub.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                subnet_comp_check = True

        # Check for invalid VCN name
        vcn_name = str(dfsub.loc[i, 'VCN Name']).strip()
        entry=vcn_name,region.lower()
        if (vcn_name.lower() != "nan" and entry not in vcnobj.vcn_names):
            log(f'ROW {i+3} : VCN {vcn_name} not part of VCNs Tab.')
            subnet_vcn_check = True

        # Check if the dns_label field has special characters or if it has greater than 15 characters or is duplicate
        dns_value = str(dfsub.loc[i, 'DNS Label']).strip()
        if dns_value.lower() != 'n':
            dns_subnetname = str(dfsub.loc[i, 'Display Name']).strip()
            dns_vcn = str(dfsub.loc[i, 'VCN Name']).strip()

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
                        log(f'ROW {i+3} : Duplicate "DNS Label" value "{dns_value}" for subnet "{dns_subnetname}" of vcn "{dns_vcn}".')
                        subnet_dns.append(dns_value)
                        #subnet_dnsdup_check = True
                subnet_dnswrong_check = checklabel(dns_value, count)

            if (len(dns_value) > 15):
                log(f'ROW {i+3} : "DNS Label" value "{dns_value}" for subnet "{dns_subnetname}" of vcn "{dns_vcn}" has more alphanumeric characters than the allowed maximum limit of 15.')
                subnet_dns_length = True

        # Check if the Service and Internet gateways are set appropriately; if not display the message;
        sgw_value = str(dfsub.loc[i, 'Configure SGW Route(n|object_storage|all_services)']).strip()
        igw_value = str(dfsub.loc[i, 'Configure IGW Route(y|n)']).strip()
        if (igw_value.lower() != "nan" and sgw_value.lower() != "nan"):
            if (igw_value.lower() == "y" and sgw_value.lower() == "all_services"):
                log(f'ROW {count + 2} : Internet Gateway target cannot be used together with Service Gateway target for All Services in the same routing table. Change either the value of SGW or IGW configure route !!')
                subnet_wrong_check = True

        #Check if DHCP Option Name specified in Subnets Tab is specified/declared correctly in DHCP Tab
        check_dhcp=0
        subnet_dhcp_name = ""
        if(str(dfsub.loc[i, 'DHCP Option Name']).strip().lower()!="n" and str(dfsub.loc[i, 'DHCP Option Name']).strip()!="nan"):
            subnet_dhcp_name = str(dfsub.loc[i, 'VCN Name']).strip()+"_"+str(dfsub.loc[i, 'DHCP Option Name']).strip()
            check_dhcp=1

        if dhcplist != [] and check_dhcp == 1 and subnet_dhcp_name!="":
            if subnet_dhcp_name in dhcplist:
                pass
            else:
                log(f'ROW {i + 3} : Value "{subnet_dhcp_name}" in column "DHCP Option Name" is not declared in DHCP tab.')
                subnet_dhcp_check = True

        # Collect CIDR List for validating
        if str(dfsub.loc[i, 'CIDR Block']).strip().lower() == "nan":
            entry=("",i+3)
            cidr_list.append(entry)
            continue
        else:
            entry = (str(dfsub.loc[i, 'CIDR Block']).strip(), i+3)
            cidr_list.append(entry)

        # Check for null values and display appropriate message
        labels = ['DNS Label', 'DHCP Option Name', 'Route Table Name', 'Seclist Names','NSGs']
        for j in dfsub.keys():
            if (str(dfsub[j][i]).strip() == "NaN" or str(dfsub[j][i]).strip() == "nan" or str(dfsub[j][i]).strip() == ""):
                # only dhcp_option_name, route table name, seclist_names and dns_label columns can be empty
                if j in labels or commonTools.check_column_headers(j) in commonTools.tagColumns:
                    pass
                else:
                    if j == "Type(private|public)" and subnet_or_vlan.lower() == "vlan":
                        continue
                    log(f'ROW {count+2} : Empty value at column "{j}".')
                    subnet_empty_check = True

        # Check if subnet CIDR mentioned is valid for the VCN of the subnet
        subnet_cidr = str(dfsub.loc[i, 'CIDR Block']).strip()
        if subnet_cidr != "nan" or subnet_cidr!="":
            try:
                subnet_cidr = ipaddress.ip_network(subnet_cidr)
            except ValueError:
                continue

            correct=0
            vcn = str(dfsub.loc[i, 'VCN Name']).strip()
            region = str(dfsub.loc[i, 'Region']).strip().lower()
            cidr=vcncidrlist[(vcn,region)]
            if("," in cidr):
                for x in cidr.split(','):
                    x=x.strip()
                    try:
                        vcn_cidr = ipaddress.ip_network(x)
                    except ValueError:
                        continue
                    if subnet_cidr.subnet_of(vcn_cidr):
                        correct=1
                        break
            else:
                try:
                    vcn_cidr = ipaddress.ip_network(cidr)
                except ValueError:
                    continue
                if subnet_cidr.subnet_of(vcn_cidr):
                    correct=1
            if(correct==0):
                log(f'ROW {i + 3} : Subnet CIDR - {subnet_cidr} does not fall under VCN CIDR - {vcncidrlist[(vcn,region)]}.')
                subnet_vcn_cidr_check = True

    if any([subnet_reg_check, subnet_vcn_check, subnet_comp_check, subnet_empty_check, subnet_dnswrong_check, subnet_wrong_check, subnet_dnsdup_check, subnet_dns_length, subnet_dhcp_check, subnet_vcn_cidr_check]):
        print("Null or Wrong value Check failed!!")
        subnet_check = True
    else:
        subnet_check = False
    log("End Null or Wrong value Check in each row------------------\n")

    log("Start Subnet CIDRs Check---------------------------------")
    subnet_cidr_check = validate_cidr(cidr_list)
    if (subnet_cidr_check == True):
        print("Subnet CIDRs Check failed!!")
    log("End Subnet CIDRs Check---------------------------------\n")

    return subnet_check, subnet_cidr_check


# Check if VCNs tab is compliant
def validate_vcns(filename, comp_ids, vcnobj):# config):  # ,vcn_cidrs,vcn_compartment_ids):
    #vcn_ids = get_vcn_ids(comp_ids, config)

    dfv = data_frame(filename, 'VCNs')

    # Counter to fetch the row number
    count = 0
    cidr_list = []

    vcn_empty_check = False
    vcn_dnswrong_check = False
    vcn_comp_check = False
    vcn_reg_check = False
    vcn_vcnname_check = False
    vcn_dns_length =  False
    vcn_peer_check = False

    vcn_check = False

    log("Start Null or Wrong value Check in each row---------------")
    vcn_dns = []
    vcn_names = []

    # Loop through each row
    for i in dfv.index:
        count = count + 1

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(dfv.loc[i, 'Region']).strip() in commonTools.endNames:
            break

        # Check for invalid Region
        region = str(dfv.loc[i, 'Region']).strip()
        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            vcn_reg_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfv.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                vcn_comp_check = True

        # Check for invalid(duplicate) vcn name
        vcn_name = str(dfv.loc[i, 'VCN Name']).strip()
        if (vcn_name.lower() == 'nan'):
            vcn_names.append("")
        else:
            entry = vcn_name, region.lower()
            if (entry not in vcn_names):
                vcn_names.append(entry)
            else:
                log(f'ROW {i+3} : Duplicate "VCN Name" value {vcn_name}  with ROW {vcn_names.index(vcn_name) + 3}.')
                vcn_names.append(vcn_name)
                vcn_vcnname_check = True

        # Check if the dns_label field has special characters # duplicates for vcn dns_label allowed # dns length not more than 15 characters
        dns_value = str(dfv.loc[i, 'DNS Label']).strip()
        if (dns_value.lower() == "nan"):
            vcn_dns.append("")
        else:
            vcn_dnswrong_check = checklabel(dns_value, count)

        if (len(dns_value) > 15):
            log(f'ROW {i+3} : "DNS Label" value {dns_value} has more alphanumeric characters than the allowed maximum limit of 15.')
            vcn_dns_length = True

        # Collect CIDR List for validating
        if str(dfv.loc[i, 'CIDR Blocks']).strip().lower() == "nan":
            entry=("",i+3)
            cidr_list.append(entry)
        else:
            for x in str(dfv.loc[i, 'CIDR Blocks']).strip().split(','):
                x=x.strip()
                entry=(x,i+3)
                cidr_list.append(entry)

        # Check for null values and display appropriate message
        for j in dfv.keys():
            if (str(dfv[j][i]).strip() == "NaN" or str(dfv[j][i]).strip() == "nan" or str(dfv[j][i]).strip() == ""):
                if j == 'DNS Label' or commonTools.check_column_headers(j) in commonTools.tagColumns:
                    continue
                else:
                    log(f'ROW {count+2} : Empty value at column "{j}".')
                    vcn_empty_check = True

    if any([vcn_vcnname_check, vcn_reg_check, vcn_comp_check, vcn_empty_check, vcn_dnswrong_check, vcn_dns_length]):  # or vcn_dnsdup_check == True):
        print("Null or Wrong value Check failed!!")
        vcn_check = True
    log("End Null or Wrong value Check in each row---------------\n")

    log("Start VCN CIDRs Check--------------------------------------")
    vcn_cidr_check = validate_cidr(cidr_list)
    if (vcn_cidr_check == True):
        print("VCN CIDRs Check failed!!")
    log("End VCN CIDRs Check--------------------------------------\n")

    '''
    log("Start LPG Peering Check---------------------------------------------")
    log("Current Status of LPGs in OCI for each VCN listed in VCNs tab:")
    oci_vcn_lpgs = {}

    # Loop through each row
    for i in dfv.index:
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(dfv.loc[i, 'Region']).strip() in commonTools.endNames:
            break

        region = str(dfv.loc[i, 'Region']).lower().strip()

        # Fetches current LPGs for each VCN and show its status
        comp_name = str(dfv.loc[i, 'Compartment Name']).strip()
        vcn_name = str(dfv.loc[i, 'VCN Name']).strip()

        try:
            comp_id = comp_ids[comp_name]
        except KeyError:
            continue
        try:
            vcn_id = vcn_ids[vcn_name]
        except KeyError:
            lpg = vcnobj.vcn_lpg_names[vcn_name,region][0]
            if (lpg != 'n'):
                log(f'ROW {i+3} : VCN {vcn_name} does not exist in OCI. VCN and its LPGs {vcnobj.vcn_lpg_names[vcn_name,region]} will be created new.')
            else:
                log(f'ROW {i+3} : VCN {vcn_name} does not exist in OCI. VCN will be created new.')
            continue

        oci_vcn_lpgs[vcn_name] = []
        vcn_lpg_str = ""

        config.__setitem__("region", ct.region_dict[region])
        vnc = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

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
    vcn_peer_check = showPeering(vcnobj)
    if (vcn_peer_check == True):
        print("Please verify LPG Peering Status in log file !!")
    log("\nPlease go through \"CD3 Modification Procedure\" of confluence page for information on correct order of lpg entries for non-greenfield tenancies.")
    log("Link: https://confluence.oraclecorp.com/confluence/display/NAC/Support+for+Non-GreenField+Tenancies")

    log("End LPG Peering Check---------------------------------------------\n")
    '''

    return vcn_check, vcn_cidr_check, vcn_peer_check


# Checks if the fields in DHCP tab are compliant
def validate_dhcp(filename, comp_ids, vcnobj):
    dfdhcp = data_frame(filename, 'DHCP')
    empty = ['', 'Nan', 'NaN', 'nan']
    dhcp_empty_check = False
    dhcp_wrong_check = False
    dhcp_comp_check = False
    dhcp_vcn_check = False
    dhcp_reg_check = False

    # Counter to fetch the row number
    count = 0

    log("Start Null or Wrong value Check in each row----------------")
    for i in dfdhcp.index:
        count = count + 1

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(dfdhcp.loc[i, 'Region']).strip() in commonTools.endNames:
            break

        # Check for invalid Region
        region = str(dfdhcp.loc[i, 'Region']).strip()

        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            dhcp_reg_check = True

        # Check for invalid compartment name
        comp_name = str(dfdhcp.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                dhcp_comp_check = True

        # Check for invalid VCN name
        vcn_name = str(dfdhcp.loc[i, 'VCN Name']).strip()
        entry=vcn_name,region.lower()

        if (vcn_name.lower() != "nan" and entry not in vcnobj.vcn_names):
            log(f'ROW {i+3} : VCN {vcn_name} not part of VCNs Tab.')
            dhcp_vcn_check = True

        for j in dfdhcp.keys():
            # Check the customer_dns_servers column; if empty return error based on the value in server_type column
            if j == 'Custom DNS Server':
                if str(dfdhcp.loc[i, 'Custom DNS Server']).strip() in empty:
                    if str(dfdhcp.loc[i, 'Server Type(VcnLocalPlusInternet|CustomDnsServer)']).strip() == "CustomDnsServer":
                        log(f'ROW {count+2} : "Custom DNS Server" column cannot be empty if server type is "CustomDnsServer".')
                        dhcp_wrong_check = True
                    elif str(dfdhcp.loc[i, 'Server Type(VcnLocalPlusInternet|CustomDnsServer)']).strip() == "VcnLocalPlusInternet":
                        continue
            else:
                # Check if there are any field that is empty; display appropriate message
                if str(dfdhcp[j][i]).strip() in empty and j != 'Search Domain' and commonTools.check_column_headers(
                        j) not in commonTools.tagColumns:
                    log(f'ROW {count+2}  : Empty value at column {j}.')
                    dhcp_empty_check = True

    log("End Null or Wrong value Check in each row-----------------\n")
    if any([dhcp_reg_check, dhcp_vcn_check, dhcp_wrong_check, dhcp_comp_check, dhcp_empty_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False



# Checks if the fields in DRGv2 tab are compliant
def validate_drgv2(filename, comp_ids, vcnobj):
    dfdrgv2 = data_frame(filename, 'DRGs')
    drgv2_empty_check = False
    drgv2_invalid_check = False
    drgv2_comp_check = False
    drgv2_drg_check = False
    drgv2_vcn_check = False
    drgv2_format_check = False

    for i in dfdrgv2.index:
        region = str(dfdrgv2.loc[i, 'Region']).strip().lower()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            drgv2_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            drgv2_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfdrgv2.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            drgv2_empty_check = True
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                drgv2_comp_check = True

        # Check for invalid DRG name
        drg_name=str(dfdrgv2.loc[i, 'DRG Name']).strip()
        if drg_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "DRG Name".')
            drgv2_empty_check = True
        if drg_name not in vcnobj.vcns_having_drg.values() and "ocid1.drg.oc" not in drg_name:
            log(f'ROW {i + 3}: DRG Name {drg_name} not part of VCNs Tab.')
            drgv2_drg_check = True

        attached_to=str(dfdrgv2.loc[i, 'Attached To']).strip()
        if(attached_to.lower()=='' or attached_to.lower()=='nan'):
            pass
        else:
            if "::" not in attached_to:
                log(f'ROW {i + 3} : Wrong value at column Attached To - {attached_to}. Valid format is <ATTACH_TYPE>::<ATTACH_ID>')
                drgv2_format_check = True
            else:
                attached_to=attached_to.split("::")
                if(len(attached_to)< 2 and len(attached_to) > 3):
                    log(f'ROW {i + 3} : Wrong value at column Attached To - {attached_to}. Valid format is <ATTACH_TYPE>::<ATTACH_ID>')
                    drgv2_format_check = True
                elif attached_to[0].strip().upper()=="VCN":
                    vcn_name = attached_to[1].strip()

                    try:
                        if (vcn_name.lower() != "nan" and vcnobj.vcns_having_drg[vcn_name,region]!=drg_name) and "ocid1.drg.oc" not in drg_name:
                            log(f'ROW {i + 3}: VCN {vcn_name} in column Attached To is not as per DRG Required column of VCNs Tab.')
                            drgv2_vcn_check = True
                    except KeyError:
                        log(f'ROW {i + 3}: VCN {vcn_name} in column Attached To is not as per VCN Name column of VCNs Tab.')
                        drgv2_vcn_check = True


        rd_name=str(dfdrgv2.loc[i, 'Import DRG Route Distribution Name']).strip()
        rd_name_stmts = str(dfdrgv2.loc[i, 'Import DRG Route Distribution Statements']).strip()

        if(rd_name.lower()=='nan' and rd_name_stmts.lower()!='nan'):
            log(f"ROW {i + 3} : column 'Import DRG Route Distribution Statements' cannot have value if column 'Import DRG Route Distribution Name' is null")
            drgv2_format_check = True
        if rd_name_stmts.lower()!='nan':
            if "::" not in rd_name_stmts:
                log(f'ROW {i + 3} : Wrong value at column Import DRG Route Distribution Statements. Valid format is <matchtype>::<type|ocid>::<priority>')
                drgv2_format_check = True
            else:
                rd_name_stmts = rd_name_stmts.split("\n")
                for rd_name_stmt in rd_name_stmts:
                    if rd_name_stmt!="":
                        rd_name_stmt=rd_name_stmt.split("::")
                        if(len(rd_name_stmt)!=3):
                            log(f'ROW {i + 3} : Wrong value at column Import DRG Route Distribution Statements. Valid format is <matchtype>::<type|ocid>::<priority>')
                            drgv2_format_check = True

    if any([drgv2_empty_check,drgv2_invalid_check,drgv2_comp_check,drgv2_drg_check,drgv2_vcn_check,drgv2_format_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_dns(filename,comp_ids):
    mandat_val_check = False
    dns_empty_check = False
    vcn_name_check = False
    subnet_check = False
    nsg_check = False
    endpoint_type_check = False
    dfdns = data_frame(filename, 'DNS-Views-Zones-Records')
    dfdnscolumns = dfdns.columns.values.tolist()
    dfres = data_frame(filename, 'DNS-Resolvers')
    dfrescolumns = dfres.columns.values.tolist()
    log(f'Checking for DNS-Views-Zones-Records')
    for i in dfdns.index:
        region = str(dfdns.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            mandat_val_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            mandat_val_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfdns.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            mandat_val_check = True
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} does not exist in OCI.')
                mandat_val_check = True

        view_name = str(dfdns.loc[i, 'View Name']).strip()
        if view_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "View Name".')
            mandat_val_check = True
        zone_name = str(dfdns.loc[i, 'Zone']).strip()
        domain_name = str(dfdns.loc[i, 'Domain']).strip()
        rtype = str(dfdns.loc[i, 'RType']).strip()
        rdata = str(dfdns.loc[i, 'RDATA']).strip()
        ttl = str(dfdns.loc[i, 'TTL']).strip()
        nan_count = 0
        for item in [domain_name,rtype,rdata,ttl]:
            if item.lower() == 'nan':
                nan_count +=1
        if nan_count in [1,2,3]:
            log(f'ROW {i + 3} : one or more of the required( Domain, RType, RDATA and TTL) parameter is missing for a record creation')
            mandat_val_check = True

        if 'nan' not in [domain_name.lower(),rtype.lower(),rdata.lower(),ttl.lower()] and zone_name.lower() == 'nan':
            log(f'ROW {i + 3} : Zone name can not be null')
            mandat_val_check = True

        # Add Existing Zone check
        # Add Existing Domain check
    log(f'Checking for DNS-Resolvers')
    for i in dfres.index:
        region = str(dfres.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            mandat_val_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            mandat_val_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfres.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            mandat_val_check = True
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} doesnot exist in OCI.')
                mandat_val_check = True
        vcn_name = str(dfres.loc[i, 'VCN Name']).strip()
        if vcn_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "VCN Name".')
            vcn_name_check = True

        e_name = str(dfres.loc[i, 'Endpoint Display Name']).strip()
        e_s_name = str(dfres.loc[i, 'Endpoint Subnet Name']).strip()
        e_type = str(dfres.loc[i, 'Endpoint Type:IP Address']).strip()
        e_n = str(dfres.loc[i, 'Endpoint NSGs']).strip()
        if e_name.lower() != 'nan' and (e_s_name.lower() == 'nan' or e_type.lower() == 'nan'):
            log(f'ROW {i + 3} : Please validate Endpoint Subnet, Endpoint Type:IP Address for Endpoint {e_name}. It can not be null')
            mandat_val_check = True

        if (e_s_name.lower() != 'nan' or e_type.lower() != 'nan' or e_n.lower() != 'nan') and e_name.lower() == 'nan':
            log(f'ROW {i + 3} : Endpoint name can not be null if other Endpoint parameters are passed.')
            mandat_val_check = True

        v_detail = str(dfres.loc[i, 'Associated Private Views']).strip()
        if v_detail != 'nan':
            try:
                v_comp = v_detail.split('@')[0]
                v_name = v_detail.split('@')[1]
            except KeyError:
                log(f'ROW {i+3} : Incorrect format for Associated Private Views')
                mandat_val_check = True
            try:
                v_comp = commonTools.check_tf_variable(v_comp)
                comp_id = comp_ids[v_comp]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {v_comp} does not exist in OCI.')
                mandat_val_check = True

        # Add Endpoint listener/forwarder Ip check with respect to subnet
        # Add subnet/vcn existence check
        # Endpoint NSG check

    if any([mandat_val_check, dns_empty_check, vcn_name_check, subnet_check, nsg_check, endpoint_type_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False
def validate_instances(filename,comp_ids,subnetobj,vcn_subnet_list,vcn_nsg_list):
    inst_empty_check = False
    inst_invalid_check = False
    inst_comp_check = False
    vcn_subnet_check = False
    vcn_nsg_check= False

    dfinst = data_frame(filename, 'Instances')
    dfcolumns = dfinst.columns.values.tolist()

    for i in dfinst.index:
        region = str(dfinst.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            inst_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i+3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            inst_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfinst.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Compartment Name".')
            inst_empty_check = True
        else:
            try:
                comp_name=commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                inst_comp_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dfinst.loc[i, columnname]).strip()
            if (columnname == 'Availability Domain(AD1|AD2|AD3)'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column "Availability Domain".')
                    inst_empty_check = True
                elif columnvalue.upper() not in ["AD1", "AD2", "AD3"]:
                    log(f'ROW {i+3} : Wrong value at column "Availability Domain" - {columnvalue}.')
                    inst_invalid_check = True

            if columnname == 'Fault Domain':
                if columnvalue.lower() != 'nan' and columnvalue not in ["FAULT-DOMAIN-1", "FAULT-DOMAIN-2", "FAULT-DOMAIN-3"]:
                    log(f'ROW {i+3} : Wrong value at column Fault Domain - {columnvalue}.')
                    inst_invalid_check = True

            if columnname == 'SSH Key Var Name':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column SSH Key Var Name. Instance will be launched without any ssh key. Ignore for Windows.')
                    print("Warning! ROW " + str(i + 3) + " : Empty value at column 'SSH Key Var Name'. Instance will be launched without any ssh key. Ignore for Windows.")

            if columnname == 'Pub Address':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column "Pub Address".')
                    inst_empty_check = True
                elif columnvalue.lower()!='true' and columnvalue.lower()!='false':
                    log(f'ROW {i+3} : Wrong value at column "Pub Address" - {columnvalue}.')
                    inst_invalid_check = True

            if columnname == 'Display Name':
                if columnvalue.lower()=='nan':
                    log(f'ROW {i+3} : Empty value at column "Display Name"')
                    inst_empty_check = True

            if columnname == 'Network Details':
                if columnvalue.lower()=='nan':
                    log(f'ROW {i+3} : Empty value at column "Network Details"')
                    inst_empty_check = True
                else:
                    # Cross check the VCN names in Instances and VCNs sheet
                    #vcn_subnet_check = compare_values(vcn_subnet_list.tolist(), columnvalue,[i, 'Subnet Name', 'SubnetsVLANs'])
                    if ("::" not in columnvalue):
                        vcn_subnet_check = True


            if columnname == 'Source Details':
                if columnvalue.lower()== 'nan':
                    log(f'ROW {i+3} : Empty value at column "Source Details".')
                    inst_empty_check = True

                elif (not columnvalue.startswith("image::") and not columnvalue.startswith("bootVolume::") and not columnvalue.startswith("ocid1.image.oc") and not columnvalue.startswith("ocid1.bootvolume.oc")):
                    log(f'ROW {i+3} : Wrong value at column Source Details - {columnvalue}. Valid format is image::<var_name> or bootVolume::<var_name>.')
                    inst_invalid_check = True

            if columnname == 'Shape':
                if columnvalue.lower()=='nan':
                    log(f'ROW {i+3} : Empty value at column "Shape".')
                    inst_empty_check = True

                elif "Flex" in columnvalue:
                    if "::" not in columnvalue:
                        log(f'ROW {i+3} : Wrong value at column Shape - {columnvalue}. Valid format for Flex Shapes is VM.Standard.E3.Flex::<ocpus>.')
                        inst_invalid_check = True
                    else:
                        shape = columnvalue.split("::")
                        if len(shape)!=2:
                            log(f'ROW {i+3} : Wrong value at column Shape - {columnvalue}.Valid format for Flex Shapes is VM.Standard.E3.Flex::<ocpus>.')
                            inst_invalid_check = True


            #if vcn_subnet_check==False and columnname == "NSGs":
            #    subnet_name = str(dfinst.loc[i, "Display Name"]).strip()
            #    if(columnvalue!='nan'):
            #        vcn_nsg_check = validate_nsgs_column(i,region,columnvalue,subnet_name,subnetobj,vcn_nsg_list)

    if any([inst_empty_check, inst_comp_check, inst_invalid_check, vcn_subnet_check,vcn_nsg_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_blockvols(filename,comp_ids):
    bvs_empty_check = False
    bvs_invalid_check = False
    bvs_comp_check = False
    instance_name_check = False
    bv_ad_check = False
    ADS = ["AD1","AD2","AD3"]
    dfvol = data_frame(filename, 'BlockVolumes')
    dfinst = data_frame(filename, 'Instances')
    values_list = dfinst['Display Name'].tolist()
    inst_ad_list = dfinst['Display Name']+'_'+dfinst['Availability Domain(AD1|AD2|AD3)']
    dfcolumns = dfvol.columns.values.tolist()
    for i in dfvol.index:
        region = str(dfvol.loc[i, 'Region']).strip().lower()

        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            bvs_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i+3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            bvs_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfvol.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Compartment Name".')
            bvs_empty_check = True
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} doesnot exist in OCI.')
                bvs_comp_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dfvol.loc[i, columnname]).strip()

            # Check if values are entered for mandatory fields - to create volumes
            if columnname == 'Block Name':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column "Block Name".')
                    bvs_empty_check = True
            if columnname == 'VPUs per GB':
                if columnvalue.lower() != 'nan':
                    if columnvalue.isnumeric():
                        if int(columnvalue) < 10 or int(columnvalue) > 120 or int(columnvalue) % 10 != 0:
                            log(f'ROW {i+3} : Wrong value at column "VPUs per GB". Must be integer between 10 to 120 and multiple of 10.')
                            bvs_invalid_check = True
                    else:
                        log(f'ROW {i + 3} : Wrong value at column "VPUs per GB". Must be integer between 10 to 120 and multiple of 10.')
                        bvs_invalid_check = True
            if columnname == 'Size In GBs':
                if columnvalue.lower() != 'nan':
                    if columnvalue.isnumeric():
                        if int(columnvalue) < 50 or int(columnvalue) > 31744:
                            log(f'ROW {i+3} : Wrong value at column "Size In GBs". Must be integer between 50 to 31744')
                            bvs_invalid_check = True
                    else:
                        log(f'ROW {i + 3} : Wrong value at column "Size In GBs". Must be integer between 50 to 31744')
                        bvs_invalid_check = True
            if (columnname == 'Availability Domain(AD1|AD2|AD3)'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column "Availability Domain".')
                    bvs_empty_check = True
                elif columnvalue.upper() not in ["AD1", "AD2", "AD3"]:
                    log(f'ROW {i+3} : Wrong value at column "Availability Domain" - {columnvalue}.')
                    bvs_invalid_check = True
            if (columnname == 'Attach Type(iscsi|paravirtualized)'):
                if columnvalue.lower()!='nan' and columnvalue!="iscsi" and columnvalue!="paravirtualized":
                    log(f'ROW {i+3} :  Wrong value at column "Attach Type" - {columnvalue}.')
                    bvs_invalid_check = True
            if commonTools.check_column_headers(columnname) == 'kms_key_id':
                if columnvalue.lower() != 'nan' and (not columnvalue.strip().startswith("ocid1.key.oc")):
                    log(f'ROW {i+3} : Kms Key ID is not in correct format.')
                    bvs_invalid_check = True
            if commonTools.check_column_headers(columnname) == 'kms_key_id' and columnvalue.lower() != 'nan' and str(dfvol.loc[i, 'Block Volume Replica (Region::AD::Name)']).strip().lower() != 'nan':
                log(f'ROW {i + 3} : Volume replication is not supported along with volume encryption with Customer Managed Keys.')
                bvs_invalid_check = True
            if columnname == 'Block Volume Replica (Region::AD::Name)':
                if columnvalue.lower() != 'nan' and columnvalue.lower() != '' and "::" not in columnvalue.strip():
                    log(f'ROW {i + 3} : Block Volume Replicas Availability Domain not in correct format. Check column "' +columnname+"\"")
                    bvs_invalid_check = True
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '' and "::" in columnvalue.strip():
                    block_volume_replicas_ads = columnvalue.strip().split("::")
                    block_volume_replicas_region = (block_volume_replicas_ads[0]).lower()
                    block_volume_replicas_ad = (block_volume_replicas_ads[1]).upper()
                    if block_volume_replicas_region not in ct.all_regions or block_volume_replicas_ad not in ADS:
                        log(f'ROW {i + 3} : Volume replication Region is not subscribed to tenancy or toolkit is not yet configured to be used for this region or AD is not present in destination region. Check column "' +columnname+"\"")
                        bvs_invalid_check = True
                    elif block_volume_replicas_region == str(dfvol.loc[i, 'Region']).strip().lower() and block_volume_replicas_ad == str(dfvol.loc[i, 'Availability Domain(AD1|AD2|AD3)']).strip().upper():
                        log(f'ROW {i + 3} : Replication Region and AD can not be same as Volume Region and AD. Check column "' +columnname+"\"")
                        bvs_invalid_check = True
            if columnname == 'Source Details':
                if columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if not (columnvalue.strip().startswith("ocid1.volume.oc") or columnvalue.strip().startswith(
                            "ocid1.volumebackup.oc") or columnvalue.strip().startswith(
                        "ocid1.blockvolumereplica.oc") or columnvalue.strip().startswith(
                        "volumeBackup::") or columnvalue.strip().startswith(
                        "volume::") or columnvalue.strip().startswith("blockVolumeReplica::")):
                        log(f'ROW {i + 3} : Source Details not in correct format. Check column "' +columnname+"\"")
                        bvs_invalid_check = True
            if columnname == 'Autotune Type':
                if columnvalue.lower() != 'nan' and columnvalue.lower() != '' and columnvalue.strip().upper() not in ["BOTH","PERFORMANCE_BASED","DETACHED_VOLUME"]:
                    log(f'ROW {i + 3} : Value must be either PERFORMANCE_BASED or DETACHED_VOLUME or BOTH. Check column "' +columnname+"\"")
                    bvs_invalid_check = True
                elif columnvalue.strip().upper() == "BOTH" or columnvalue.strip().upper() == "PERFORMANCE_BASED":
                    if "Max VPUS Per GB" in dfcolumns:
                        if str(dfvol.loc[i, 'Max VPUS Per GB']).strip().lower() == 'nan':
                            log(f'ROW {i + 3} : For Autotune Type PERFORMANCE_BASED or BOTH column "Max VPUS Per GB" can not be left blank.')
                            bvs_invalid_check = True
                    else:
                        log(f'ROW {i + 3} : For Autotune Type PERFORMANCE_BASED or BOTH column "Max VPUS Per GB" must be present in sheet and can not be left blank.')
                        bvs_invalid_check = True

        if str(dfvol.loc[i, 'Attached To Instance']).strip().lower() != 'nan' and str(
                dfvol.loc[i, 'Attach Type(iscsi|paravirtualized)']).strip().lower() != 'nan' and str(
                dfvol.loc[i, 'Device']).strip().lower() != 'nan' and not (re.match("/dev/oracleoci/oraclevd[b-z]$", str(
                dfvol.loc[i, 'Device']).strip().lower()) or re.match("/dev/oracleoci/oraclevda[a-g]$", str(
                dfvol.loc[i, 'Device']).strip().lower())):
            log(f'ROW {i + 3} : Wrong value at column "Device".')
            bvs_invalid_check = True
        elif (str(dfvol.loc[i, 'Attached To Instance']).strip().lower() == 'nan' or str(
                dfvol.loc[i, 'Attach Type(iscsi|paravirtualized)']).strip().lower() == 'nan') and str(
                dfvol.loc[i, 'Device']).strip().lower() != 'nan':
            log(f'ROW {i + 3} : Wrong value at column "Device".Attached To Instance and Attach Type can not be left blank')
            bvs_invalid_check = True
        # Check if values are entered for mandatory fields - to attach volumes to instances
        if str(dfvol.loc[i, 'Attached To Instance']).strip().lower() != 'nan' and str(dfvol.loc[i, 'Attach Type(iscsi|paravirtualized)']).strip().lower() == 'nan':
            log(f'ROW {i+3} : Field "Attach Type" is empty if you want to attach  the volume to instance {dfvol.loc[i,"Attached To Instance"]}.')
            bvs_invalid_check = True
        elif str(dfvol.loc[i, 'Attach Type(iscsi|paravirtualized)']).strip().lower() != 'nan' and str(
                dfvol.loc[i, 'Attached To Instance']).strip().lower() == 'nan':
            log(f'ROW {i+3} : Field "Attached To Instance" is empty for Attachment Type {dfvol.loc[i,"Attach Type(iscsi|paravirtualized)"]}.')
            bvs_invalid_check = True

        if(str(dfvol.loc[i, 'Attached To Instance']).strip().lower() != 'nan' and str(dfvol.loc[i, 'Attach Type(iscsi|paravirtualized)']).strip().lower() != 'nan'):
            # Cross check the instance names in Instances and Block Volumes sheet
            instance_name_check = compare_values([x for x in values_list],str(dfvol.loc[i, 'Attached To Instance']),[i, 'Attached To Instance', 'Instances'])

            # Cross check the ADs in Instances and Block Volumes sheet
            bv_ad_check = compare_values([str(x).lower() for x in inst_ad_list.tolist()],str(dfvol.loc[i, 'Attached To Instance']).lower()+'_'+str(dfvol.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower(),[i, 'Availability Domain(AD1|AD2|AD3)', 'Instances'])

    if any([bvs_empty_check, bvs_comp_check, bvs_invalid_check, instance_name_check, bv_ad_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_fss(filename,comp_ids,subnetobj,vcn_subnet_list,vcn_nsg_list):
    fss_empty_check = False
    fss_invalid_check = False
    fss_comp_check = False
    vcn_subnet_check = False
    vcn_nsg_check= False

    df_fss = data_frame(filename, 'FSS')
    dfcolumns = df_fss.columns.values.tolist()

    for i in df_fss.index:
        region = str(df_fss.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        comp_name = str(df_fss.loc[i, 'Compartment Name']).strip()
        ad_name = str(df_fss.loc[i, 'Availability Domain(AD1|AD2|AD3)']).strip()
        mt_name = str(df_fss.loc[i, 'MountTarget Name']).strip()
        mt_subnet_name = str(df_fss.loc[i, 'Network Details']).strip()
        my_list = [region, comp_name.lower(),ad_name.lower(),mt_name.lower(),mt_subnet_name.lower()]

        if all(j == 'nan' for j in my_list):
            pass
        elif 'nan' in my_list:
            log(f'ROW {i + 3} : Empty value for any of the columns "Region", "Compartment Name", "Availability Domain(AD1|AD2|AD3)", "MountTarget Name", "Network Details"')
            fss_empty_check = True

        if region!='nan' and region not in ct.all_regions:
            log(f'ROW {i+3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            fss_invalid_check = True

        # Check for invalid Compartment Name
        if comp_name.lower()!='nan':
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} doesnot exist in OCI.')
                fss_comp_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df_fss.loc[i, columnname]).strip()
            if (columnname == 'Availability Domain(AD1|AD2|AD3)'):
                if columnvalue.lower()!='nan' and columnvalue.upper() not in ["AD1", "AD2", "AD3"]:
                    log(f'ROW {i+3} : Wrong value at column "Availability Domain" - {columnvalue}.')
                    fss_invalid_check = True

            if columnname == 'Network Details':
                # Cross check the VCN names in Instances and VCNs sheet
                if(columnvalue!='nan'):
                    # vcn_subnet_check = compare_values(vcn_subnet_list.tolist(), columnvalue,[i, 'Display Name <vcn-name_subnet-name>', 'SubnetsVLANs'])
                    if ("::" not in columnvalue):
                        vcn_subnet_check = True

            #if vcn_subnet_check==False and columnname == "NSGs":
            #    subnet_name = str(df_fss.loc[i, "MountTarget SubnetName"]).strip()
            #    if (columnvalue != 'nan'):
            #        vcn_nsg_check = validate_nsgs_column(i,region,columnvalue,subnet_name,subnetobj,vcn_nsg_list)

    if any([fss_empty_check, fss_comp_check, fss_invalid_check, vcn_subnet_check,vcn_nsg_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False



def validate_compartments(filename):

    comp_empty_check = False
    comp_invalid_check = False
    parent_comp_check= False
    # Read the Compartments tab from excel
    dfcomp = data_frame(filename,'Compartments')

    for i in dfcomp.index:
        region = str(dfcomp.loc[i, 'Region']).strip().lower()
        parent_comp = str(dfcomp.loc[i, 'Parent Compartment']).strip().split("::")[-1]

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            comp_empty_check = True
        elif region!=ct.home_region:
            log(f'ROW {i+3} : Region specified is not the Home Region.')
            comp_invalid_check = True
        if str(dfcomp.loc[i, 'Name']).strip().lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Name".')
            comp_empty_check = True
        if(str(dfcomp.loc[i, 'Name']).strip() == parent_comp):
            log(f'ROW {i + 3} : Name cannot be same as Parent Compartment Name')
            comp_invalid_check = True


    if (comp_empty_check == True or parent_comp_check == True or comp_invalid_check == True):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_groups(filename):
    groups_empty_check = False
    groups_invalid_check = False
    # Read the Groups tab from excel
    dfg = data_frame(filename, 'Groups')

    for i in dfg.index:
        region = str(dfg.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            groups_empty_check = True
        elif region!=ct.home_region:
            log(f'ROW {i+3} : Region specified is not the Home Region.')
            groups_invalid_check = True
        if str(dfg.loc[i, 'Name']).strip().lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Name".')
            groups_empty_check = True
    if groups_empty_check == True or groups_invalid_check == True:
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_policies(filename,comp_ids):
    policies_empty_check = False
    policies_comp_check = False
    policies_invalid_check = False

    # Read the Policies tab from excel
    dfp = data_frame(filename,'Policies')

    for i in dfp.index:
        region = str(dfp.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        # Check for invalid Compartment Name
        comp_name = str(dfp.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} doesnot exist in OCI.')
                policies_comp_check = True

        #Check for Null Values
        if str(dfp.loc[i, 'Region']).strip().lower()!='nan' and str(dfp.loc[i, 'Region']).strip().lower()!=ct.home_region:
            log(f'ROW {i+3} : Region specified is not the Home Region.')
            policies_invalid_check = True

        if str(dfp.loc[i, 'Region']).strip().lower() != 'nan' and str(
                dfp.loc[i, 'Name']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Compartment Name']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Policy Statements']).strip().lower() != 'nan':
            log(f'ROW {i+3} : Empty value at column "Name" and "Compartment Name".')
            policies_empty_check = True
        if str(dfp.loc[i, 'Region']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Name']).strip().lower() != 'nan' and str(
                dfp.loc[i, 'Compartment Name']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Policy Statements']).strip().lower() != 'nan':
            log(f'ROW {i+3} : Empty value at column "Region" and "Compartment Name".')
            policies_empty_check = True

        if str(dfp.loc[i, 'Region']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Name']).strip().lower() != 'nan' and str(
                dfp.loc[i, 'Compartment Name']).strip().lower() != 'nan' and str(
                dfp.loc[i, 'Policy Statements']).strip().lower() != 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            policies_empty_check = True

        if str(dfp.loc[i, 'Region']).strip().lower() != 'nan' and str(
                dfp.loc[i, 'Name']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Compartment Name']).strip().lower() != 'nan' and str(
                dfp.loc[i, 'Policy Statements']).strip().lower() != 'nan':
            log(f'ROW {i+3} : Empty value at column "Name".')
            policies_empty_check = True

        if str(dfp.loc[i, 'Policy Statements']).strip().lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Policy Statements".')
            policies_empty_check = True

        if str(dfp.loc[i, 'Compartment Name']).strip().lower() == 'nan' and str(dfp.loc[i, 'Policy Statements']).strip().lower() != 'nan' and str(
            dfp.loc[i, 'Name']).strip().lower() != 'nan':
            log(f'ROW {i+3} : Empty value at column "Compartment Name".')
            policies_empty_check = True

        if str(dfp.loc[i, 'Region']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Name']).strip().lower() == 'nan' and str(
                dfp.loc[i, 'Compartment Name']).strip().lower() != 'nan' and str(
            dfp.loc[i, 'Policy Statements']).strip().lower() != 'nan':
            log(f'ROW {i+3} : Empty value at column "Region" and "Name".')
            policies_empty_check = True

        statement = str(dfp.loc[i, 'Policy Statements']).strip().lower()
        '''
        words = statement.split()
        if ('to' in words):
            verb = words[words.index('to') + 1]
            if verb not in ['inspect', 'read', 'use', 'manage']:
                log(f'ROW {i + 3} : Invalid verb used in Policy Statement')
                policies_invalid_check = True
        '''


    if policies_empty_check == True or policies_comp_check == True or policies_invalid_check == True:
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_tags(filename,comp_ids):

    tag_empty_check = False
    tag_invalid_check = False
    tag_comp_check  = False

    # Read the Compartments tab from excel
    dftag = data_frame(filename,'Tags')

    for i in dftag.index:
        region = str(dftag.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            tag_empty_check = True
        elif region!=ct.home_region:
            log(f'ROW {i+3} : Region specified is not the Home Region.')
            tag_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dftag.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan' or comp_name == '':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            tag_empty_check = True
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} doesnot exist in OCI.')
                tag_comp_check = True

        # List of the column headers
        dfcolumns = dftag.columns.values.tolist()

        for columnname in dfcolumns:
            columnvalue = str(dftag[columnname][i])
            # Column value
            if columnname == "Tag Description":
                columnvalue = columnvalue.lower()
                if str(dftag.loc[i, 'Tag Keys']).strip().lower() != 'nan':
                    if columnvalue == '' or columnvalue == 'nan':
                        log(f'ROW {i + 3} : Empty value at column  "Tag Description".')
                        tag_empty_check = True
            if columnname == "Namespace Description":
                columnvalue = columnvalue.lower()
                if columnvalue == '' or columnvalue == 'nan':
                    log(f'ROW {i + 3} : Empty value at column  "Namespace Description".')
                    tag_empty_check = True

            if columnname == 'Tag Namespace':
                columnvalue = str(columnvalue).strip()
                if columnvalue == '' or columnvalue == 'nan':
                    log(f'ROW {i + 3} : Empty value at column "Tag Namespace".')
                    tag_empty_check = True

                if ' ' in columnvalue or '.' in columnvalue:
                    log(f'ROW {i+3} : Spaces and Periods are not allowed in Tag Namespaces.')
                    tag_invalid_check = True
                if columnvalue.lower().startswith('oci') or columnvalue.lower().startswith('orcl'):
                    log(f'ROW {i + 3} : Tag Namespaces cannot start with oci or orcl')
                    tag_invalid_check = True

            if columnname == 'Tag Keys':
                columnvalue = str(columnvalue).strip()
                # if columnvalue == '' or columnvalue == 'nan':
                #     log(f'ROW {i + 3} : Empty value at column "Tag Keys".')
                #     tag_empty_check = True

                if ' ' in columnvalue or '.' in columnvalue:
                    log(f'ROW {i+3} : Spaces and Periods are not allowed in Tag Keys.')
                    tag_invalid_check = True
                if columnvalue.lower().startswith('oci') or columnvalue.lower().startswith('orcl'):
                    log(f'ROW {i + 3} : Tag Definition Names cannot start with oci or orcl')
                    tag_invalid_check = True

    if (tag_empty_check == True or  tag_invalid_check == True or tag_comp_check == True):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_budgets(filename,comp_ids):
    budget_check_result = []


    # Read the Compartments tab from excel
    dfbudget = data_frame(filename, 'Budgets')

    for i in dfbudget.index:
        region = str(dfbudget.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region!='nan' and region != ct.home_region:
            log(f'ROW {i + 3} : It should be Home Region of the tenancy')
            budget_check_result.append(False)
        name = str(dfbudget.loc[i, 'Name']).strip().lower()
        desc = str(dfbudget.loc[i, 'Description']).strip()
        scope = str(dfbudget.loc[i, 'Scope']).strip().lower().lower()
        target = str(dfbudget.loc[i, 'Target']).strip()
        schedule = str(dfbudget.loc[i, 'Schedule']).strip().lower().lower()
        amount = str(dfbudget.loc[i, 'Amount']).strip().lower()
        start_day = str(dfbudget.loc[i, 'Start Day']).strip()
        start_date = str(dfbudget.loc[i, 'Budget Start Date']).strip().lower()
        end_date = str(dfbudget.loc[i, 'Budget End Date']).strip().lower()
        rules = str(dfbudget.loc[i, 'Alert Rules']).strip().lower()
        recipients = str(dfbudget.loc[i, 'Alert Recipients']).strip()
        message = str(dfbudget.loc[i, 'Alert Message']).strip()

        if rules == 'nan' and (region == 'nan' or name == 'nan' or scope == 'nan' or schedule == 'nan' or amount == 'nan'):
            log(f'ROW {i + 3} : Empty value at one of the columns "Region/Name/Scope/Schedule/Amount.')
            budget_check_result.append(False)
        if schedule == "single_use" and (start_date == 'nan' or end_date == 'nan'):
            log(f'ROW {i + 3} : Start Date and End Date are mandatory for Single Use Schedule.')
            budget_check_result.append(False)

        if schedule == "month" and start_day == 'nan':
            log(f'ROW {i + 3} : \"Start Day\" is mandatory for MONTH Schedule.')
            budget_check_result.append(False)

        if rules != 'nan' and len(rules.split("::")) < 2:
            log(f'ROW {i + 3} : \"Alert Rules\" format is not correct".')
            budget_check_result.append(False)
        if recipients != 'nan':
            recipients=recipients.split(",")
            for rec in recipients:
                if "@" not in rec:
                    log(f'ROW {i + 3} : \"Alert Recipients\" format is not correct.')
                    budget_check_result.append(False)

    if budget_check_result and False in budget_check_result:
        return False
    else:
        return True


def validate_buckets(filename, comp_ids):
    # Initialize the flag to False for each bucket
    buckets_empty_check = False
    buckets_invalid_check = False
    buckets_comp_check = False
    bucket_reg_check = False
    bucket_name_check = False

    # Read the Compartments tab from excel
    dfbuckets = data_frame(filename, 'Buckets')

    for i in dfbuckets.index:
        region = str(dfbuckets.loc[i, 'Region']).strip().lower()
        lifecycle_all_columns = ['Lifecycle Policy Name', 'Lifecycle Target and Action',
                                       'Lifecycle Policy Enabled', 'Lifecycle Rule Period','Lifecyle Exclusion Patterns','Lifecyle Inclusion Patterns','Lifecyle Inclusion Prefixes']

        lifecycle_mandatory_columns = ['Lifecycle Policy Name','Lifecycle Target and Action','Lifecycle Policy Enabled','Lifecycle Rule Period']
        lifecycle_input = False
        for columns in lifecycle_all_columns:
            column_value = str(dfbuckets.loc[i, columns]).strip().lower()
            if column_value != 'nan':
                lifecycle_input = True
                data_column = columns
        if lifecycle_input == True:
            for columns in lifecycle_mandatory_columns:
                column_value = str(dfbuckets.loc[i, columns]).strip().lower()
                if column_value == 'nan':
                    log(f'ROW {i + 3} : {columns} cannot be empty as column {data_column} has data.')
                    buckets_invalid_check = True


        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            buckets_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            bucket_reg_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfbuckets.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan' or comp_name == '':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            buckets_empty_check = True
        else:
            try:
                comp_name = commonTools.check_tf_variable(comp_name)
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} does not exist in OCI.')
                buckets_comp_check = True

        # Check for invalid Bucket Name
        bucket_name = str(dfbuckets.loc[i, 'Bucket Name']).strip()
        if bucket_name.lower() == 'nan' or bucket_name == '':
            log(f'ROW {i + 3} : Empty value at column "Bucket Name".')
            buckets_empty_check = True
        else:
            if re.match("^[A-Za-z0-9_.-]*$", bucket_name.lower()):
                bucket_name_check = False
            else:
                bucket_name_check = True
                log(f'ROW {i + 3} : "Bucket Name" can only contain letters (upper or lower case), numbers, hyphens, underscores, and periods.')


        # List of the column headers
        dfcolumns = dfbuckets.columns.values.tolist()

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dfbuckets.loc[i, columnname]).strip()

            if columnname == 'Storage Tier':
                if columnvalue.lower() not in ['standard','archive']:
                    log(f'ROW {i + 3} : Value of "Storage Tier" can be only either "Standard" or "Archive".')
                    buckets_invalid_check = True
                elif columnvalue.lower() == 'archive':
                    auto_tiering_index = dfcolumns.index('Auto Tiering')
                    if auto_tiering_index != -1 and str(dfbuckets.loc[i, 'Auto Tiering']).strip().lower() == 'enabled':
                        log(f'ROW {i + 3} : Auto Tiering cannot be "Enabled" when Storage Tier is "Archive".')
                        buckets_invalid_check = True

            if columnname == 'Auto Tiering':
                if columnvalue.lower() not in ['enabled','disabled']:
                    log(f'ROW {i + 3} : Value of "Auto Tiering" can be only either "Enabled" or "Disabled".')
                    buckets_invalid_check = True

            # Check for the Object Versioning column
            if columnname == 'Object Versioning':
                if columnvalue.lower() not in ['enabled', 'disabled']:
                    log(f'ROW {i + 3} : Value of "Object Versioning" can only be "Enabled" or "Disabled".')
                    buckets_invalid_check = True

            if columnname == 'Emit Object Events':
                if columnvalue.lower() not in ['enabled','disabled']:
                    log(f'ROW {i + 3} : Value of "Emit Object Events" can be only either "Enabled" or "Disabled".')
                    buckets_invalid_check = True


            if columnname == 'Visibility':
                if columnvalue.lower() not in ['private','public']:
                    log(f'ROW {i + 3} : Value of "Visibility" can be only either "Private" or "Public".')
                    buckets_invalid_check = True

            # Check for valid destination region for enabling the replication policy
            if columnname == 'Replication Policy' and columnvalue != "nan":
                columnvalue = columnvalue.split("::")
                if len(columnvalue) == 3:
                    replication_policy_name = columnvalue[0]
                    destination_region = columnvalue[1].lower()
                    destination_bucket_name = columnvalue[2]
                    if replication_policy_name.strip() and destination_bucket_name.strip():
                        if destination_region in ct.region_dict:
                            destination_region = ct.region_dict[destination_region]
                        else:
                            log(f'ROW {i + 3} : The "Destination_region" of replication policy is not a valid region.')
                            buckets_invalid_check = True
                    else:
                        log(f'ROW {i + 3} : The replication policy format is incorrect or policy name/destination bucket is empty.')
                        buckets_invalid_check = True
                else:
                    log(f'ROW {i + 3} : The replication policy format is incorrect.')
                    buckets_invalid_check = True

            # Get the current time
            current_time = datetime.datetime.utcnow()
            #Check for the retention policy details
            if columnname == 'Retention Rules':
                if columnvalue == "nan":
                    continue
                rule_values = columnvalue.split("\n")
                if rule_values and str(dfbuckets.loc[i, 'Object Versioning']).strip().lower() == 'enabled':
                    log(f'ROW {i + 3} : Retention policy cannot be created when Object Versioning is enabled.')
                    buckets_invalid_check = True

                elif rule_values and str(dfbuckets.loc[i, 'Object Versioning']).strip().lower() == 'disabled':
                    retention_rules = []
                    for rule in rule_values:
                        rule_components = rule.split("::")
                        if len(rule_components) >= 1:
                            retention_rule_display_name = rule_components[0]
                            time_unit = None
                            time_amount = None
                            time_rule_locked = None

                            if len(rule_components) >= 2:
                                if rule_components[1].lower() == 'indefinite':
                                    time_amount = None
                                else:
                                    time_amount = rule_components[1]
                                    if not time_amount.isdigit():
                                        log(f'ROW {i + 3} : "time_amount" of retention rule is not in valid format. It should be an "integer" or "indefinite".')
                                        buckets_invalid_check = True
                                        continue
                                    else:
                                        time_amount = int(time_amount)

                            if len(rule_components) >= 3:
                                time_unit = rule_components[2].upper()
                                if time_unit not in ('DAYS', 'YEARS'):
                                    log(f'ROW {i + 3} : "time_unit" of retention rule is not in valid format. It should be either DAYS or YEARS.')
                                    buckets_invalid_check = True
                                else:
                                    # If time_unit is valid, set the flag to True for processing time_rule_locked
                                    process_time_rule_locked = True

                            if len(rule_components) == 4 and process_time_rule_locked:
                                time_rule_locked = rule_components[3]
                                if time_rule_locked:
                                    if time_rule_locked.endswith(".000Z"):
                                        time_rule_locked = time_rule_locked[:-5] + "Z"
                                    elif not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*Z",time_rule_locked):
                                        # Convert from "dd-mm-yyyy" to "YYYY-MM-DDThh:mm:ssZ" format
                                        if re.match(r"\d{2}-\d{2}-\d{4}", time_rule_locked):
                                            try:
                                                datetime_obj = datetime.datetime.strptime(time_rule_locked, "%d-%m-%Y")
                                                time_rule_locked = datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                                            except ValueError:
                                                log(f'ROW {i + 3} : "time_rule_locked" of retention rule is not in valid format. It should be in the format "dd-mm-yyyy".')
                                                buckets_invalid_check = True
                                                continue
                                        else:
                                            log(f'ROW {i + 3} : "time_rule_locked" of retention rule is not in valid format. It should be in the format "dd-mm-yyyy".')
                                            buckets_invalid_check = True
                                            continue
                                    # Parse the time_rule_locked into a datetime object
                                    try:
                                        if len(time_rule_locked.split(".")) > 1:
                                            time_rule_locked_datetime = datetime.datetime.strptime(time_rule_locked,
                                                                                                   "%Y-%m-%dT%H:%M:%S.%fZ"
                                                                                                   )
                                        else:
                                            time_rule_locked_datetime = datetime.datetime.strptime(time_rule_locked, "%Y-%m-%dT%H:%M:%SZ")
                                    except ValueError:
                                        log(f'ROW {i + 3} : "time_rule_locked" of retention rule is not in valid format. It should be in the format "YYYY-MM-DDThh:mm:ssZ".')
                                        buckets_invalid_check = True
                                        continue

                                    # Calculate the difference between current time and time_rule_locked
                                    time_difference = time_rule_locked_datetime - current_time

                                    # Check if the difference is less than 14 days
                                    if time_difference.days < 14:
                                        log(f'ROW {i + 3} : "time_rule_locked" of retention rule must be more than 14 days from the current time.')
                                        buckets_invalid_check = True
                                else:
                                    # No action is required since time_rule_locked is optional
                                    log(f'ROW {i + 3} : "time_rule_locked" is optional and skipped.')

            # Check for the Lifecycle Policy Details
            if lifecycle_input == True:
                # Define the valid options for the "Lifecycle Target and Action" column
                valid_options = [
                    'objects::ARCHIVE',
                    'objects::INFREQUENT_ACCESS',
                    'objects::Delete',
                    'previous-object-versions::Archive',
                    'previous-object-versions::Delete',
                    'multipart-uploads::Abort'
                ]

                # Check if "Lifecycle Target and Action" is empty
                if columnname == 'Lifecycle Target and Action':
                    if columnvalue != 'nan' and columnvalue not in valid_options:
                        log(f'ROW {i + 3} : Invalid value in "Lifecycle Target and Action" column. '
                            f'Allowed options are: {", ".join(valid_options)}.')
                        buckets_invalid_check = True

                # Check if "Lifecycle Policy Enabled" is empty
                if columnname == 'Lifecycle Policy Enabled':
                    if columnvalue != 'nan' and columnvalue.lower() not in ['true', 'false']:
                      log(f'ROW {i + 3} : "Lifecycle Policy Enabled" must be either "TRUE" or "FALSE".')
                      buckets_invalid_check = True

                # Check if "Lifecycle Rule Period" is empty
                if columnname == 'Lifecycle Rule Period':
                    # Merge the checks for "Lifecycle Rule Period"
                    if columnvalue != 'nan':
                        columnvalue = columnvalue.upper()
                        columnvalue = columnvalue.split("::")
                        if len(columnvalue) == 2:
                            time_amount = columnvalue[0]
                            time_unit = columnvalue[1].lower()
                            # Check that time_amount is an integer
                            if not time_amount.isdigit():
                                log(f'ROW {i + 3} : Invalid time unit. "Lifecycle Rule Period" must be an integer value.')
                                buckets_invalid_check = True

                            # Check that time_unit is either "DAYS" or "YEARS"
                            if time_unit not in ['days','years']:
                                log(f'ROW {i + 3} : Invalid time amount. "Lifecycle Rule Period" must be "DAYS" or "YEARS".')
                                buckets_invalid_check = True

                        else:
                            log(f'ROW {i + 3} : Invalid format for  "Lifecycle Rule Period" ')
                            buckets_invalid_check = True

    if (buckets_empty_check == True or buckets_invalid_check == True or buckets_comp_check == True or bucket_reg_check == True or bucket_name_check == True):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


#validate_kms
def validate_kms(filename,comp_ids):

    dfkms = data_frame(filename, 'KMS')
    kms_invalid_check = False
    prev_vault_type = ""

    for i in dfkms.index:
        region = str(dfkms.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            pass
        elif region != 'nan' and region not in ct.all_regions:
            log(f'ROW {i + 3} : Either "Region" {region} is not subscribed to tenancy or toolkit is not yet configured to be used for this region.')
            kms_invalid_check = True

        vault_compartment_name = str(dfkms.loc[i, 'Vault Compartment Name']).strip()
        vault_display_name = str(dfkms.loc[i, 'Vault Display Name']).strip()
        replica_region = str(dfkms.loc[i, 'Replica Region']).strip().lower()
        key_compartment_name = str(dfkms.loc[i, 'Key Compartment Name']).strip()
        key_display_name = str(dfkms.loc[i, 'Key Display Name']).strip()
        protection_mode = str(dfkms.loc[i, 'Protection mode']).strip()
        algorithm = str(dfkms.loc[i, 'Algorithm']).strip()
        length_in_bits = dfkms.loc[i,'Length in bits']
        curve_id = str(dfkms.loc[i, 'Curve Id']).strip()
        auto_rotation = dfkms.loc[i, 'Auto rotation']
        rotation_interval_in_days = dfkms.loc[i, 'Rotation interval in days']

        current_vault_type = str(dfkms.loc[i, 'Vault type'])
        if current_vault_type != 'nan':
            vault_type = current_vault_type
            if vault_type.lower() not in ['default', 'virtual_private']:
                log(f'ROW {i + 3}: Invalid Vault_type!!. Vault type should be either "DEFAULT" or "VIRTUAL_PRIVATE". ')
                kms_invalid_check = True
            prev_vault_type = vault_type

        else:
            vault_type = prev_vault_type

        if (str(dfkms.loc[i, 'Vault Compartment Name']).strip() != 'nan' or str(dfkms.loc[i, 'Vault Display Name']).strip()!= 'nan' or str(dfkms.loc[i, 'Vault type']) != 'nan'):

           # Check Vault Compartment name
            if vault_compartment_name == 'nan' or vault_compartment_name == '':
                log(f'ROW {i + 3} : Empty value at column "Vault Compartment Name".')
                pass
            else:
                try:
                    vault_comp_name = commonTools.check_tf_variable(vault_comp_name)
                    comp_id = comp_ids[vault_compartment_name]
                except KeyError:
                    log(f'ROW {i+3} : Compartment {vault_compartment_name} does not exist in OCI.')
                    kms_invalid_check = True

            # Check Vault display name
            if vault_display_name == 'nan' or vault_display_name == '':
                log(f'ROW {i + 3} : Empty value at column "Vault Display Name".')
                kms_invalid_check = True
            else:
                if re.match("^[A-Za-z0-9_-]{1,100}$", vault_display_name.lower()):
                    pass
                else:
                    kms_invalid_check = True
                    log(f'ROW {i + 3} : "Vault Name" can only contain letters (upper or lower case), numbers, hyphens and underscores.')

           # Check Replica region
            if replica_region == region:
                log(f'ROW {i+3}: Replica region cannot be same as the primary Vault region')
                kms_invalid_check = True
            elif (replica_region in commonTools.endNames):
                break
            elif replica_region == 'nan':
                pass
            elif replica_region != 'nan' and replica_region not in ct.all_regions:
                log(f'ROW {i + 3} : "Replica Region" {replica_region} is either not subscribed to tenancy or toolkit is not yet configured to be used for this region')
                kms_invalid_check = True


        #Check Keys columns
        if (key_compartment_name != 'nan' or key_display_name != 'nan'):
            #Check for empty values
            if (key_compartment_name == 'nan' or  key_display_name == 'nan' or  protection_mode == 'nan' or algorithm == 'nan' or str(length_in_bits) == 'nan') :
                log(f'ROW {i + 3} : Empty values found at one or more places in these columns: Key Compartment Name/ Key Display Name/ Protection mode/ Algorithm/ Length in bits')
                kms_invalid_check = True

            else:
                # Check Key Compartment name
                if key_compartment_name != 'nan' or key_compartment_name != '':
                    try:
                        key_compartment_name = commonTools.check_tf_variable(key_compartment_name)
                        comp_id = comp_ids[key_compartment_name]
                    except KeyError:
                        log(f'ROW {i + 3} : Compartment {key_compartment_name} does not exist in OCI.')
                        kms_invalid_check = True

                # Check key display name
                if key_display_name == 'nan' or key_display_name == '':
                    log(f'ROW {i + 3} : Empty value at column "Key Display Name".')
                    kms_invalid_check = True
                else:
                    if re.match("^[A-Za-z0-9_-]{1,100}$", key_display_name.lower()):
                        pass
                    else:
                        kms_invalid_check = True
                        log(f'ROW {i + 3} : "Key Name" can only contain letters (upper or lower case), numbers, hyphens and underscores.')

                # Check Protection mode
                if protection_mode.lower() not in ['software', 'hsm']:
                    log(f'ROW {i + 3} : Invalid value for protection mode. It should be either "software" or "hsm"')
                    kms_invalid_check = True

                # Check Algorithm
                if algorithm.lower() not in ['aes', 'rsa', 'ecdsa']:
                    log(f'ROW {i + 3} : Invalid value for Algorithm. It should be either "aes", "rsa" or "ecdsa"')
                    kms_invalid_check = True

                # Check Length in bits
                if algorithm.lower() == "aes" and length_in_bits not in [128, 192, 256]:
                    log(f'ROW {i + 3} : Invalid length for "{algorithm}".')
                    kms_invalid_check = True
                elif algorithm.lower() == "rsa" and length_in_bits not in [2048, 3072, 4096]:
                    log(f'ROW {i + 3} : Invalid length for "{algorithm}".')
                    kms_invalid_check = True
                elif algorithm.lower() == "ecdsa" and length_in_bits not in [256, 384, 521]:
                    log(f'ROW {i + 3} : Invalid length for "{algorithm}".')
                    kms_invalid_check = True

                # Check Curve Id
                if (algorithm.lower() == "aes" or algorithm.lower() == "rsa") and curve_id != 'nan':
                    log(f'ROW {i + 3} : Curve id is only valid for ECDSA keys')
                    kms_invalid_check = True
                elif (algorithm.lower() == "ecdsa" and curve_id not in ['NIST_P256', 'NIST_P384', 'NIST_P521']):
                    log(f'ROW {i + 3} : Invalid curve id. It should be either "NIST_P256", "NIST_P384" or "NIST_P521."')
                    kms_invalid_check = True

                elif (algorithm.lower() == "ecdsa" and curve_id in ['NIST_P256', 'NIST_P384', 'NIST_P521']):
                    if int(re.search(r'\d+', curve_id).group()) != int(length_in_bits):
                        log(f'ROW {i + 3} : Invalid curve id for the length specified.')
                        kms_invalid_check = True

                # Check Auto rotation and rotation interval
                if (vault_type.lower() == 'default' and auto_rotation is True) or (vault_type.lower() == 'default' and str(rotation_interval_in_days) != 'nan'):
                    log(f'ROW {i + 3} : Auto rotation or Rotation interval can only be set for virtual_private vaults.')
                    kms_invalid_check = True
                elif vault_type.lower() == "virtual_private":
                    if (auto_rotation is True) and str(rotation_interval_in_days) == 'nan':
                        log(f'ROW {i + 3} : Rotation interval in days value cannot be empty if auto_rotation is enabled')
                        kms_invalid_check = True
                    if ((auto_rotation is False) or str(auto_rotation) == 'nan') and str(rotation_interval_in_days) != 'nan':
                        log(f'ROW {i + 3} : Rotation interval cannot be specified if auto rotation is not enabled.')
                        kms_invalid_check = True
                    if str(rotation_interval_in_days) != 'nan' and not (60 <= int(rotation_interval_in_days) <= 365):
                        log(f'ROW {i + 3} : Invalid Rotation interval. Value should be between 60-365.')
                        kms_invalid_check = True

    if kms_invalid_check == True:
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_cd3(choices, filename, var_file, prefix, outdir, ct1): #config1, signer1, ct1):
    CD3_LOG_LEVEL = 60
    logging.addLevelName(CD3_LOG_LEVEL, "custom")
    file=prefix+"_cd3Validator.log"
    resource = "cd3validator"
    customer_tenancy_dir = outdir
    commonTools.backup_file(customer_tenancy_dir,resource,file)
    logging.basicConfig(filename=customer_tenancy_dir+"/"+file, filemode="w", format="%(asctime)s - %(message)s", level=60, force = True)
    logger = logging.getLogger("cd3Validator")
    global log
    log = partial(logger.log, CD3_LOG_LEVEL)
    final_check = []

    global ct #, config, signer
    ct=ct1
    #config=config1
    #signer =signer1
    global compartment_ids
    compartment_ids = {}
    global vcn_ids
    vcn_ids = {}
    global vcn_cidrs
    vcn_cidrs = {}
    global vcn_compartment_ids
    vcn_compartment_ids = {}

    comp_check = False
    groups_check = False
    policies_check = False
    vcn_check = False
    vcn_cidr_check = False
    vcn_peer_check = False
    subnet_check = False
    subnet_cidr_check = False
    dhcp_check = False
    drgv2_check = False
    bvs_check = False
    tags_check = False
    fss_check = False
    instances_check = False
    dns_check = False
    buckets_check = False
    budgets_check = False
    kms_check = False

    errors = False

    if not os.path.exists(filename):
        print("\nCD3 excel sheet not found at "+filename +"\nExiting!!")
        exit(1)

    #ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)
    #print("Getting Compartments OCIDs...")
    all_comp_ocids = ct.get_compartment_map(var_file,'Validator')

    vcnobj = parseVCNs(filename)
    subnetobj = parseSubnets(filename)

    dfsub = data_frame(filename, 'SubnetsVLANs')
    vcn_subnet_list = dfsub['VCN Name'].astype(str)+'_'+dfsub['Display Name']

    dfnsg = data_frame(filename, 'NSGs')
    vcn_nsg_list = dfnsg['Region'].astype(str).str.lower() + '_' + dfnsg['VCN Name'].astype(str) + '_' + dfnsg['NSG Name']

    val_net=False
    for options in choices:
        if ('Validate Compartments' in options[0]):
            log("============================= Verifying Compartments Tab ==========================================\n")
            print("\nValidating Compartments Tab..")
            comp_check = validate_compartments(filename)
            errors = comp_check
        if ('Validate Groups' in options[0]):
            log("\n============================= Verifying Groups Tab ==========================================\n")
            print("\nValidating Groups Tab..")
            groups_check = validate_groups(filename)
            errors =  groups_check
        if ('Validate Policies' in options[0]):
            log("\n============================= Verifying Policies Tab ==========================================\n")
            print("\nValidating Policies Tab..")
            policies_check = validate_policies(filename,all_comp_ocids)
            errors =  policies_check
        if ('Validate Tags' in options[0]):
            log("\n============================= Verifying Tags Tab ==========================================\n")
            print("\nValidating Tags Tab..")
            tags_check = validate_tags(filename,all_comp_ocids)
            errors = tags_check

        if ('Validate Budgets' in options[0]):
            log("\n============================= Verifying Budgets Tab ==========================================\n")
            print("\nValidating Budgets Tab..")
            budgets_check = validate_budgets(filename,all_comp_ocids)
            errors = budgets_check
            final_check.append(budgets_check)

        if ('Validate KMS' in options[0]):
            log("\n============================= Verifying KMS Tab ==========================================\n")
            print("\nValidating KMS Tab..")
            kms_check = validate_kms(filename,all_comp_ocids)
            errors = kms_check


        # CD3 Validation begins here for Network
        if ('Validate Network(VCNs, SubnetsVLANs, DHCP, DRGs)' in options[0]):
            val_net=True

            log("\n============================= Verifying VCNs Tab ==========================================\n")
            log("\n====================== Note: LPGs will not be verified ====================================\n")
            print("\nValidating VCNs Tab..")
            print("NOTE: LPGs will not be verified")
            vcn_check, vcn_cidr_check, vcn_peer_check = validate_vcns(filename, all_comp_ocids, vcnobj) #, config)

            log("============================= Verifying SubnetsVLANs Tab ==========================================\n")
            print("\nValidating SubnetsVLANs Tab..")
            subnet_check, subnet_cidr_check = validate_subnets(filename, all_comp_ocids, vcnobj)

            log("============================= Verifying DHCP Tab ==========================================\n")
            print("\nValidating DHCP Tab..")
            dhcp_check = validate_dhcp(filename, all_comp_ocids, vcnobj)

            log("============================= Verifying DRGs Tab ==========================================\n")
            print("\nValidating DRGs Tab..")
            drgv2_check = validate_drgv2(filename, all_comp_ocids, vcnobj)

            if any([vcn_check, vcn_cidr_check, vcn_peer_check, subnet_check, subnet_cidr_check, dhcp_check, drgv2_check]):
                errors = True

        if ('Validate DNS' in options[0]):
            log("\n============================= Verifying DNS Tabs ==========================================\n")
            print("\nValidating DNS Tab..")
            dns_check = validate_dns(filename,all_comp_ocids)
            errors = dns_check

        if ('Validate Instances' in options[0]):
            log("\n============================= Verifying Instances Tab ==========================================\n")
            print("\nValidating Instances Tab..")
            instances_check = validate_instances(filename,all_comp_ocids,subnetobj,vcn_subnet_list,vcn_nsg_list)
            errors = instances_check

        if ('Validate Block Volumes' in options[0]):
            log("\n============================= Verifying BlockVolumes Tab ==========================================\n")
            print("\nValidating BlockVolumes Tab..")
            bvs_check = validate_blockvols(filename,all_comp_ocids)
            errors = bvs_check

        if ('Validate FSS' in options[0]):
            log("\n============================= Verifying FSS Tab ==========================================\n")
            print("\nValidating FSS Tab..")
            fss_check = validate_fss(filename,all_comp_ocids,subnetobj,vcn_subnet_list,vcn_nsg_list)
            errors = fss_check

        if ('Validate Buckets' in options[0]):
            log("\n============================= Verifying Buckets Tab ==========================================\n")
            print("\nValidating Buckets Tab..")
            buckets_check = validate_buckets(filename,all_comp_ocids)
            errors = buckets_check

            # Prints the final result; once the validation is complete
    if any([comp_check, groups_check, policies_check, tags_check, instances_check, dns_check, bvs_check,fss_check, vcn_check, vcn_cidr_check, vcn_peer_check, subnet_check, subnet_cidr_check, dhcp_check, drgv2_check,buckets_check, kms_check]) or False in final_check:
        log("=======")
        log("Summary:")
        log("=======")
        log("ERROR: Make appropriate changes to CD3 Values as per above Errors and try again !!!")
        if inspect.stack()[1].function == 'validate_cd3':
            print("\n\nSummary:")
            print("=======")
        print("Errors Found!!!")

    elif ('q' not in choices and 'm' not in choices):
        log("=======")
        log("Summary:")
        log("=======")
        log("There are no syntax errors in CD3. Proceed with TF Generation.\n")
        if(val_net == True):
            log("Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed with TF !!!")
        if inspect.stack()[1].function == 'validate_cd3':
            print("\n\nSummary:")
            print("=======")
        print("There are no syntax errors in CD3. Proceed with TF Generation.\n")
        if(val_net == True):
            print("Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed !!!")
        # exit(0)
    elif('q' in choices):
        exit(1)
    else:
        print("Invalid Choice....Exiting!!")
        exit(1)

    if inspect.stack()[1].function == 'validate_cd3' or errors:
        print("Please check the log file at " + customer_tenancy_dir + "/" + file + "\n")

    del(log)
    del(logger)
    return errors


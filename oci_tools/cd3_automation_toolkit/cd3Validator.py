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
import logging
import ipaddress
from collections import namedtuple
from functools import partial
from oci.core.virtual_network_client import VirtualNetworkClient
from commonTools import *


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
            ipaddress.ip_network(cidr_list[i][0])
            rowN= cidr_list[i][1]
        except ValueError:
            log(f'Row  {str(rowN)} Field "CIDR Block" {cidr_list[i]} is invalid. CIDR range has host bits set.')
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

    dfsub = data_frame(filename, 'Subnets')
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
        count = count + 1
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if (str(dfsub.loc[i, 'Region']).strip() in commonTools.endNames):
            break

        # Check for invalid Region
        region = str(dfsub.loc[i, 'Region']).strip()

        if (region.lower() != "nan" and region.lower() not in ct.all_regions):
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy.')
            subnet_reg_check = True

        # Check for invalid compartment name
        comp_name = str(dfsub.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
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
        dns_subnetname = str(dfsub.loc[i, 'Subnet Name']).strip()
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
                    subnet_dnsdup_check = True
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
        labels = ['DNS Label', 'DHCP Option Name', 'Route Table Name', 'Seclist Names']
        for j in dfsub.keys():
            if (str(dfsub[j][i]).strip() == "NaN" or str(dfsub[j][i]).strip() == "nan" or str(dfsub[j][i]).strip() == ""):
                # only dhcp_option_name, route table name, seclist_names and dns_label columns can be empty
                if j in labels or commonTools.check_column_headers(j) in commonTools.tagColumns:
                    pass
                else:
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
                    x.strip()
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
def validate_vcns(filename, comp_ids, vcnobj, config):  # ,vcn_cidrs,vcn_compartment_ids):
    vcn_ids = get_vcn_ids(comp_ids, config)

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
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy.')
            vcn_reg_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfv.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
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
                x.strip()
                entry=(x,i+3)
                cidr_list.append(entry)

        # Check for null values and display appropriate message
        for j in dfv.keys():
            if (str(dfv[j][i]).strip() == "NaN" or str(dfv[j][i]).strip() == "nan" or str(dfv[j][i]).strip() == ""):
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
    vcn_cidr_check = validate_cidr(cidr_list)
    if (vcn_cidr_check == True):
        print("VCN CIDRs Check failed!!")
    log("End VCN CIDRs Check--------------------------------------\n")

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
    vcn_peer_check = showPeering(vcnobj)
    if (vcn_peer_check == True):
        print("Please verify LPG Peering Status in log file !!")
    log("\nPlease go through \"CD3 Modification Procedure\" of confluence page for information on correct order of lpg entries for non-greenfield tenancies.")
    log("Link: https://confluence.oraclecorp.com/confluence/display/NAC/Support+for+Non-GreenField+Tenancies")

    log("End LPG Peering Check---------------------------------------------\n")

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
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy.')
            dhcp_reg_check = True

        # Check for invalid compartment name
        comp_name = str(dfdhcp.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            pass
        else:
            try:
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
            log(f'ROW {i + 3} : Region {region} is not subscribed to tenancy.')
            drgv2_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfdrgv2.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            drgv2_empty_check = True
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                drgv2_comp_check = True

        # Check for invalid DRG name
        drg_name=str(dfdrgv2.loc[i, 'DRG Name']).strip()
        if drg_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "DRG Name".')
            drgv2_empty_check = True
        if drg_name not in vcnobj.vcns_having_drg.values():
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
                if(len(attached_to)!=2):
                    log(f'ROW {i + 3} : Wrong value at column Attached To - {attached_to}. Valid format is <ATTACH_TYPE>::<ATTACH_ID>')
                    drgv2_format_check = True
                elif attached_to[0].strip().upper()=="VCN":
                    vcn_name = attached_to[1].strip()

                    try:
                        if (vcn_name.lower() != "nan" and vcnobj.vcns_having_drg[vcn_name,region]!=drg_name):
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
            log(f'ROW {i+3} : "Region" {region} is not subscribed for tenancy.')
            inst_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfinst.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Compartment Name".')
            inst_empty_check = True
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} doesnot exist in OCI.')
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
                    log(f'ROW {i+3} : Empty value at column Display Name')
                    inst_empty_check = True

            if columnname == 'Subnet Name':
                if columnvalue.lower()=='nan':
                    log(f'ROW {i+3} : Empty value at column Subnet Name.')
                    inst_empty_check = True
                else:
                    # Cross check the VCN names in Instances and VCNs sheet
                    vcn_subnet_check = compare_values(vcn_subnet_list.tolist(), columnvalue,[i, 'Subnet Name <vcn-name_subnet-name>', 'Subnets'])

            if columnname == 'Source Details':
                if columnvalue.lower()== 'nan':
                    log(f'ROW {i+3} : Empty value at column "Source Details".')
                    inst_empty_check = True

                elif (not columnvalue.startswith("image::") and not columnvalue.startswith("bootVolume::")):
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
                        shape= columnvalue.split("::")
                        if len(shape)!=2:
                            log(f'ROW {i+3} : Wrong value at column Shape - {columnvalue}.Valid format for Flex Shapes is VM.Standard.E3.Flex::<ocpus>.')
                            inst_invalid_check = True

            if vcn_subnet_check==False and columnname == "NSGs":
                subnet_name = str(dfinst.loc[i, "Subnet Name"]).strip()
                if(columnvalue!='nan'):
                    vcn_nsg_check = validate_nsgs_column(i,region,columnvalue,subnet_name,subnetobj,vcn_nsg_list)

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
            log(f'ROW {i+3} : Region {region} is not subscribed to tenancy.')
            bvs_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dfvol.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Compartment Name".')
            bvs_empty_check = True
        else:
            try:
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
        mt_subnet_name = str(df_fss.loc[i, 'MountTarget SubnetName']).strip()
        my_list = [region, comp_name.lower(),ad_name.lower(),mt_name.lower(),mt_subnet_name.lower()]

        if all(j == 'nan' for j in my_list):
            pass
        elif 'nan' in my_list:
            log(f'ROW {i + 3} : Empty value for any of the columns "Region", "Compartment Name", "Availability Domain(AD1|AD2|AD3)", "MountTarget Name", "MountTarget SubnetName"')
            fss_empty_check = True

        if region!='nan' and region not in ct.all_regions:
            log(f'ROW {i+3} : "Region" {region} is not subscribed for tenancy.')
            fss_invalid_check = True

        # Check for invalid Compartment Name
        if comp_name.lower()!='nan':
            try:
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

            if columnname == 'MountTarget SubnetName':
                # Cross check the VCN names in Instances and VCNs sheet
                if(columnvalue!='nan'):
                    vcn_subnet_check = compare_values(vcn_subnet_list.tolist(), columnvalue,[i, 'Subnet Name <vcn-name_subnet-name>', 'Subnets'])

            if vcn_subnet_check==False and columnname == "NSGs":
                subnet_name = str(df_fss.loc[i, "MountTarget SubnetName"]).strip()
                if (columnvalue != 'nan'):
                    vcn_nsg_check = validate_nsgs_column(i,region,columnvalue,subnet_name,subnetobj,vcn_nsg_list)

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
            log(f'ROW {i+3} : Empty value at column Name')
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
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} doesnot exist in OCI.')
                tag_comp_check = True

        # List of the column headers
        dfcolumns = dftag.columns.values.tolist()

        for columnname in dfcolumns:
            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(dftag[columnname][i])
            else:
                columnvalue = str(dftag[columnname][i]).strip()

            if columnname == 'Tag Namespace':
                columnvalue = str(columnvalue).strip()
                if columnvalue == '' or columnvalue == 'nan':
                    log(f'ROW {i + 3} : Empty value at column "Tag Namespace".')
                    tag_empty_check = True

                if ' ' in columnvalue or '.' in columnvalue:
                    log(f'ROW {i+3} : Spaces and Periods are not allowed in Tag Namespaces.')
                    tag_invalid_check = True

            if columnname == 'Tag Keys':
                columnvalue = str(columnvalue).strip()
                # if columnvalue == '' or columnvalue == 'nan':
                #     log(f'ROW {i + 3} : Empty value at column "Tag Keys".')
                #     tag_empty_check = True

                if ' ' in columnvalue or '.' in columnvalue:
                    log(f'ROW {i+3} : Spaces and Periods are not allowed in Tag Keys.')
                    tag_invalid_check = True

    if (tag_empty_check == True or  tag_invalid_check == True or tag_comp_check == True):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_cd3(filename, prefix, outdir,choices, configFileName):
    CD3_LOG_LEVEL = 60
    logging.addLevelName(CD3_LOG_LEVEL, "custom")
    file=prefix+"_cd3Validator.log"
    resource = "cd3validator"
    customer_tenancy_dir = outdir
    commonTools.backup_file(customer_tenancy_dir,resource,file)
    logging.basicConfig(filename=customer_tenancy_dir+"/"+file, filemode="w", format="%(asctime)s - %(message)s", level=60)
    logger = logging.getLogger("cd3Validator")
    global log
    log = partial(logger.log, CD3_LOG_LEVEL)

    global ct
    ct = commonTools()
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

    if not os.path.exists(filename):
        print("\nCD3 excel sheet not found at "+filename +"\nExiting!!")
        exit()
    config = oci.config.from_file(file_location=configFileName)
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    vcnobj = parseVCNs(filename)
    subnetobj = parseSubnets(filename)

    dfsub = data_frame(filename, 'Subnets')
    vcn_subnet_list = dfsub['VCN Name'].astype(str)+'_'+dfsub['Subnet Name']

    dfnsg = data_frame(filename, 'NSGs')
    vcn_nsg_list = dfnsg['Region'].astype(str).str.lower() + '_' + dfnsg['VCN Name'].astype(str) + '_' + dfnsg['NSG Name']

    val_net=False
    for options in choices:
        if ('Validate Compartments' in options[0]):
            log("============================= Verifying Compartments Tab ==========================================\n")
            print("\nProcessing Compartments Tab..")
            comp_check = validate_compartments(filename)
        if ('Validate Groups' in options[0]):
            log("\n============================= Verifying Groups Tab ==========================================\n")
            print("\nProcessing Groups Tab..")
            groups_check = validate_groups(filename)
        if ('Validate Policies' in options[0]):
            log("\n============================= Verifying Policies Tab ==========================================\n")
            print("\nProcessing Policies Tab..")
            policies_check = validate_policies(filename,ct.ntk_compartment_ids)
        if ('Validate Tags' in options[0]):
            log("\n============================= Verifying Tags Tab ==========================================\n")
            print("\nProcessing Tags Tab..")
            tags_check = validate_tags(filename,ct.ntk_compartment_ids)
        # CD3 Validation begins here for Network
        if ('Validate Network(VCNs, Subnets, DHCP, DRGs)' in options[0]):
            val_net=True

            log("\n============================= Verifying VCNs Tab ==========================================\n")
            print("\nProcessing VCNs Tab..")
            vcn_check, vcn_cidr_check, vcn_peer_check = validate_vcns(filename, ct.ntk_compartment_ids, vcnobj, config)

            log("============================= Verifying Subnets Tab ==========================================\n")
            print("\nProcessing Subnets Tab..")
            subnet_check, subnet_cidr_check = validate_subnets(filename, ct.ntk_compartment_ids, vcnobj)

            log("============================= Verifying DHCP Tab ==========================================\n")
            print("\nProcessing DHCP Tab..")
            dhcp_check = validate_dhcp(filename, ct.ntk_compartment_ids, vcnobj)

            log("============================= Verifying DRGs Tab ==========================================\n")
            print("\nProcessing DRGs Tab..")
            drgv2_check = validate_drgv2(filename, ct.ntk_compartment_ids, vcnobj)

        if ('Validate Instances' in options[0]):
            log("\n============================= Verifying Instances Tab ==========================================\n")
            print("\nProcessing Instances Tab..")
            instances_check = validate_instances(filename,ct.ntk_compartment_ids,subnetobj,vcn_subnet_list,vcn_nsg_list)

        if ('Validate Block Volumes' in options[0]):
            log("\n============================= Verifying BlockVolumes Tab ==========================================\n")
            print("\nProcessing BlockVolumes Tab..")
            bvs_check = validate_blockvols(filename,ct.ntk_compartment_ids)

        if ('Validate FSS' in options[0]):
            log("\n============================= Verifying FSS Tab ==========================================\n")
            print("\nProcessing FSS Tab..")
            fss_check = validate_fss(filename,ct.ntk_compartment_ids,subnetobj,vcn_subnet_list,vcn_nsg_list)


    # Prints the final result; once the validation is complete
    if any([comp_check, groups_check, policies_check, tags_check, instances_check, bvs_check,fss_check, vcn_check, vcn_cidr_check, vcn_peer_check, subnet_check, subnet_cidr_check, dhcp_check, drgv2_check]):
        log("=======")
        log("Summary:")
        log("=======")
        log("ERROR: Make appropriate changes to CD3 Values as per above Errors and try again !!!")
        print("\n\nSummary:")
        print("=======")
        print("Errors Found!!!")
    elif ('q' not in choices and 'm' not in choices):
        log("=======")
        log("Summary:")
        log("=======")
        log("There are no errors in CD3. Please proceed with TF Generation\n")
        if(val_net == True):
            log("Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed with TF !!!")
        print("\n\nSummary:")
        print("=======")
        print("There are no errors in CD3. Please proceed with TF Generation\n")
        if(val_net == True):
            print("Verify LPG's Peering Check Status once in the log file. Otherwise You are good to proceed !!!")
        # exit(0)
    elif('q' in choices):
        exit(1)
    else:
        print("Invalid Choice....Exiting!!")
        exit(1)
    print("Please check the log file at "+customer_tenancy_dir+"/"+file+"\n")


def parse_args():
    parser = argparse.ArgumentParser(description="CD3 Validator")
    parser.add_argument("cd3file", help="Full Path of CD3 file")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='customer name/prefix for all file names')
    parser.add_argument("validate_cd3file", help="Validate Options; comma seperated")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Path to config file")
    return parser.parse_args()

if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    filename = args.cd3file
    configFileName = args.config
    outdir  = args.outdir
    prefix = args.prefix
    validate_options = args.validate_cd3file
    validate_cd3(filename, prefix,outdir,validate_options, configFileName)


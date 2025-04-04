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

import logging
import ipaddress
from functools import partial
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.vault import VaultsClient
from oci.key_management import KmsVaultClient
from commonTools import *
import re

"""def get_vcn_ids(compartment_ids, config):
    # Fetch the VCN ID
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        vnc = VirtualNetworkClient(config)
        for comp_id in compartment_ids.values():
            if comp_id == 'ocid1.compartment.oc1..aaaaaaaaeifixpi24fbexw5xwidb7wy23rsnxs5pg6qj5da':
                vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=comp_id, lifecycle_state="AVAILABLE")
                for vcn in vcn_list.data:
                    # if(vcn.lifecycle_state == 'ACTIVE'):
                    vcn_ids[vcn.display_name] = vcn.id
    return vcn_ids

def get_subnet_list(compartment_ids, config):
    # Fetch the subnet List
    subnet_names = []
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        vnc = VirtualNetworkClient(config)
        for comp_id in compartment_ids.values():
            if comp_id == 'ocid1.compartment.oc1..aaaaaaaaeifixpi24fbexwhnsohftxam34s5xwidb7wy23rsnxs5pg6qj5da':
                vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=comp_id, lifecycle_state="AVAILABLE")
                for vcn in vcn_list.data:
                    # if(vcn.lifecycle_state == 'ACTIVE'):
                    vcn_name = vcn.display_name
                    for comp_id_again in compartment_ids.values():
                        if comp_id_again == 'ocid1.compartment.oc1..aaaaaaaaeifixpi24fbexwhnsohftxam34s5xwidb7wy23rsnxs5pg6qj5da':
                            Subnets = oci.pagination.list_call_get_all_results(vnc.list_subnets, compartment_id=comp_id_again, vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                            for subnet in Subnets.data:
                                subnet_names.append(region + '_' + vcn_name + '_' + subnet.display_name)
    return subnet_names

def get_secret_list(compartment_ids, config):
    # Fetch the Secret List
    secret_list1 = []
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        secret = VaultsClient(config)
        vault = KmsVaultClient(config)
        for comp_id in compartment_ids.values():
            if comp_id == 'ocid1.compartment.oc1..aaaaaaaaeifixpi24fbexwhnsohftxam34s5xwidb7wy23rsnxs5pg6qj5da':
                secrets = oci.pagination.list_call_get_all_results(secret.list_secrets, compartment_id=comp_id, lifecycle_state="ACTIVE")
                for secret1 in secrets.data:
                    vault_id1 = secret1.vault_id
                    vaults = vault.get_vault(vault_id=vault_id1)
                    secret_list1.append(region + '::' + vaults.data.display_name + '::' + secret1.secret_name)
    return secret_list1"""

def validate_vault_secret(i,region1,cmp1,columnvalue,comp_ids,config,signer, ct):
    vault_secret_check = False
    secret_list = []
    config.__setitem__("region", ct.region_dict[region1])
    secret = VaultsClient(config=config,signer=signer)
    vault = KmsVaultClient(config=config,signer=signer)
    vault_value_check = region1 + "::" + columnvalue
    vcmp_id = comp_ids[cmp1]
    secrets1 = oci.pagination.list_call_get_all_results(secret.list_secrets, compartment_id=vcmp_id, lifecycle_state="ACTIVE")
    for secret1 in secrets1.data:
        vault_id1 = secret1.vault_id
        vaults = vault.get_vault(vault_id=vault_id1)
        secret_list.append(region1 + '::' + vaults.data.display_name + '::' + secret1.secret_name)
    vault_secret_check = compare_values(secret_list, vault_value_check, [i, 'vault', 'OCI', columnvalue])
    return vault_secret_check

def validate_vcn_subnet(i,region2,cmp2,columnvalue,comp_ids,config,signer, ct):
    vcn_subnet_check = False
    vcn_subnet_list = []
    config.__setitem__("region", ct.region_dict[region2])
    vnc = VirtualNetworkClient(config=config,signer=signer)
    vcn_subnet_value_check = region2 + '::' + columnvalue
    ncmp_id = comp_ids[cmp2]
    vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=ncmp_id, lifecycle_state="AVAILABLE")
    for vcn in vcn_list.data:
        vcn_name = vcn.display_name
        Subnets = oci.pagination.list_call_get_all_results(vnc.list_subnets, compartment_id=ncmp_id, vcn_id=vcn.id, lifecycle_state="AVAILABLE")
        for subnet in Subnets.data:
            vcn_subnet_list.append(region2 + '::' + vcn_name + '::' + subnet.display_name)
    vcn_subnet_check = compare_values(vcn_subnet_list, vcn_subnet_value_check, [i, 'vcn', 'OCI', columnvalue])
    return vcn_subnet_check

def validate_vcn_nsg(i,region2,cmp2,nsg1,comp_ids,config,signer, ct):
    vcn_nsg_check = False
    vcn_nsg_list = []
    config.__setitem__("region", ct.region_dict[region2])
    vnc = VirtualNetworkClient(config=config,signer=signer)
    vcn_nsg_value_check = nsg1
    sendvalue = nsg1.split('_')
    sendvalue1 = sendvalue[1] + '_' + sendvalue[2]
    ncmp_id = comp_ids[cmp2]
    vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=ncmp_id, lifecycle_state="AVAILABLE")
    for vcn in vcn_list.data:
        vcn_name = vcn.display_name
        Nsgs = oci.pagination.list_call_get_all_results(vnc.list_network_security_groups, compartment_id=ncmp_id, vcn_id=vcn.id, lifecycle_state="AVAILABLE")
        for nsg in Nsgs.data:
            vcn_nsg_list.append(region2 + '_' + vcn_name + '_' + nsg.display_name)
    vcn_nsg_check = compare_values(vcn_nsg_list, vcn_nsg_value_check, [i, 'nsg', 'OCI', sendvalue1])
    return vcn_nsg_check

"""def get_nsg_list(compartment_ids, config):
    # Fetch the subnet List
    nsg_names = []
    for region in ct.all_regions:
        config.__setitem__("region", ct.region_dict[region])
        vnc = VirtualNetworkClient(config)
        for comp_id in compartment_ids.values():
            if comp_id == 'ocid1.compartment.oc1..aaaaaaaaeifixpi24fbexwhnsohftxam34s5xwidb7wy23rsnxs5pg6qj5da':
                vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, compartment_id=comp_id, lifecycle_state="AVAILABLE")
                for vcn in vcn_list.data:
                    # if(vcn.lifecycle_state == 'ACTIVE'):
                    vcn_name = vcn.display_name
                    for comp_id_again in compartment_ids.values():
                        if comp_id_again == 'ocid1.compartment.oc1..aaaaaaaaeifixpi24fbexwhnsohftxam34s5xwidb7wy23rsnxs5pg6qj5da':
                            Nsgs = oci.pagination.list_call_get_all_results(vnc.list_network_security_groups, compartment_id=comp_id_again, vcn_id=vcn.id, lifecycle_state="AVAILABLE")
                            for nsg in Nsgs.data:
                                nsg_names.append(region + '_' + vcn_name + '_' + nsg.display_name)
    return nsg_names"""

def compare_values(list_to_check, value_to_check, index):
    if (value_to_check not in list_to_check):
        if len(index) == 4:
            if index[3].lower() != 'nan':
                if index[1].lower() == 'vault':
                    value1 = index[3].split("::")
                    log(f'ROW {index[0] + 3} : Invalid value for column "Vault Secret Id".  Secret "{value1[1]}" or vault "{value1[0]}" does not exist in "{index[2]}".')
                elif index[1].lower() == 'vcn':
                    value1 = index[3].split("_")
                    log(f'ROW {index[0] + 3} : Invalid value for column "Subnet Name".  Subnet "{value1[1]}" or VCN "{value1[0]}" does not exist in "{index[2]}".')
                elif index[1].lower() == 'nsg':
                    value1 = index[3].split("_")
                    log(f'ROW {index[0] + 3} : Invalid value for column "NSGs".  NSG "{value1[1]}" for "{value1[0]}" does not exist in "{index[2]}".')
                else:
                    value_to_check = value_to_check.split("::")
                    log(f'ROW {index[0] + 3} : Invalid value for column "{index[1]}". {index[3]} "{value_to_check[1]}" for policy "{value_to_check[0]}" does not exist in "{index[2]}" tab.')
        else:
            log(f'ROW {index[0] + 3} : Invalid value for column "{index[1]}" "{value_to_check}" does not exist in "{index[2]}" tab.')
        return True
    return False
# Checks for duplicates
def checkIfDuplicates(listOfElems):
    setOfElems = set()
    for elem in listOfElems:
        if elem in setOfElems:
            return elem
        else:
            setOfElems.add(elem)
    return False


def validate_Firewall(filename,comp_ids,fwpolicy,config,signer, ct):
    fw_empty_check = False
    fw_invalid_check = False
    fw_comp_check = False
    fw_subnet_check = []
    fw_nsg_check = []
    fw_policycheck = False

    dffirewall = data_frame(filename, 'Firewall')
    dfcolumns = dffirewall.columns.values.tolist()

    for i in dffirewall.index:
        region = str(dffirewall.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i+3} : Empty value at column "Region".')
            fw_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i+3} : "Region" {region} is not subscribed for tenancy.')
            fw_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dffirewall.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i+3} : Empty value at column "Compartment Name".')
            fw_empty_check = True
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i+3} : Compartment {comp_name} does not exist in OCI.')
                fw_comp_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffirewall.loc[i, columnname]).strip()

            if (columnname == 'Availability Domain(AD1|AD2|AD3|Regional)'):
                if columnvalue.lower() != 'nan' and columnvalue.upper() not in ["AD1", "AD2", "AD3","REGIONAL"]:
                    log(f'ROW {i+3} : Wrong value at column "Availability Domain" - {columnvalue}.')
                    fw_invalid_check = True

            if columnname == 'IPv4 Address':
                if columnvalue.lower() != 'nan':
                    try:
                        ipaddress.ip_address(columnvalue)
                    except ValueError:
                        log(f'ROW {i+3} : Wrong value at column "IPv4 Address" - {columnvalue}.')
                        fw_invalid_check = True

            if columnname == 'Firewall Name':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column Firewall Name')
                    fw_empty_check = True

            if columnname == 'Subnet Name':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column Subnet Name.')
                    fw_empty_check = True
                else:
                    # Cross check the VCN names in Firewall sheet with OCI.
                    subnetname = region + '::' + columnvalue
                    region2 = str(dffirewall.loc[i, 'Region']).strip().lower()
                    cmp2 = str(dffirewall.loc[i, 'Network Compartment Name']).strip()
                    fw_subnet_check.append(validate_vcn_subnet(i, region2, cmp2, columnvalue, comp_ids,config,signer, ct))

            if columnname == 'Firewall Policy':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i+3} : Empty value at column Policy Name.')
                    fw_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fw_policycheck = compare_values(fwpolicy.tolist(), columnvalue, [i, 'Policy Name', 'Firewall-Policy'])

            if not any(fw_subnet_check) and columnname == "NSGs":
                if(columnvalue!='nan'):
                    NSGs = columnvalue.split(",")
                    nsg_sub_name = str(dffirewall.loc[i, 'Subnet Name']).strip().split("::")
                    nsg_vcn_name = nsg_sub_name[0]
                    for nsg in NSGs:
                        nsg = region + "_" + str(nsg_vcn_name) + "_" + nsg
                        fw_nsg_check.append(validate_vcn_nsg(i, region2, cmp2, nsg, comp_ids,config,signer, ct))

    if any([fw_empty_check, fw_comp_check, fw_invalid_check, fw_policycheck]) or any(fw_subnet_check) or any(fw_nsg_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_FirewallPolicy(filename, ct):
    comp_ids = ct.ntk_compartment_ids
    fwpolicy_empty_check = False
    fwpolicy_comp_check = False
    fwpolicy_invalid_check = False

    dffwpolicy = data_frame(filename, 'Firewall-Policy')
    dfcolumns = dffwpolicy.columns.values.tolist()

    for i in dffwpolicy.index:
        region = str(dffwpolicy.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicy_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicy_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dffwpolicy.loc[i, 'Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Compartment Name".')
            fwpolicy_empty_check = True
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} does not exist in OCI.')
                fwpolicy_comp_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicy.loc[i, columnname]).strip()
            if (columnname == 'Policy Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicy_invalid_check = True

    if any([fwpolicy_empty_check, fwpolicy_comp_check, fwpolicy_invalid_check]):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_names(var_name):
    pattern = re.compile('[^a-zA-Z0-9_-]')
    # x=pattern.match(var_name)
    x = re.search(pattern, var_name)
    if x != None:
        return True
    else:
        return False


def validate_FirewallPolicyApplist(filename, fwpolicy_list,ct):
    fwpolicyapp_empty_check = False
    fwpolicyapp_invalid_check = False
    fwpolicyapp_check = []
    fwpolicyapp_appg_length = False
    fwpolicyapp_appg_mistake = False
    dffwpolicyapplist = data_frame(filename, 'Firewall-Policy-ApplicationList')
    dfcolumns = dffwpolicyapplist.columns.values.tolist()

    for i in dffwpolicyapplist.index:
        region = str(dffwpolicyapplist.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicyapp_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicyapp_invalid_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicyapplist.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Firewall Policy.')
                    fwpolicyapp_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicyapp_check.append(compare_values(fwpolicy_list.tolist(), columnvalue, [i, 'Firewall Policy', 'Firewall-Policy']))
            if (columnname == 'Application List'):
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 28):
                        log(f'ROW {i + 3} : Application List name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 28.')
                        fwpolicyapp_appg_length = True
                    if(validate_names(columnvalue)==True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in Application List Name')
                        fwpolicyapp_invalid_check == True

            if (columnname == 'Applications'):
                if columnvalue.lower() != 'nan':
                    allapps = columnvalue.split("\n")
                    for apps in allapps:
                        apps = apps.split("::")
                        mistake = '[A-Za-z0-9]:[A-Za-z0-9]'
                        for app in apps:
                            if re.search(mistake,app):
                                log(f'ROW {i + 3} : Applications value "{apps}" have only one : as a seperator. Re-run validation after fixing it')
                                fwpolicyapp_appg_mistake = True
                        if len(apps) < 3 or len(apps) > 4:
                            log(f'ROW {i + 3} : Applications value "{apps}" does not have all/correct required details')
                            fwpolicyapp_invalid_check = True
                        else:
                            if (len(apps[0]) > 28):
                                log(f'ROW {i + 3} : Application name "{apps[0]}" has more alphanumeric characters than the allowed maximum limit of 28.')
                                fwpolicyapp_appg_length = True
                            if (validate_names(apps[0]) == True):
                                log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Applications Name')
                                fwpolicyapp_invalid_check == True

                            if (apps[1] not in ['ICMP','ICMP_V6']):
                                log(f'ROW {i + 3} : Application type "{apps[1]}" is not the correct value.')
                                fwpolicyapp_invalid_check = True
                            if fwpolicyapp_appg_mistake == False:
                                if (int(apps[2]) not in range(0, 255)):
                                    log(f'ROW {i+3} : ICMP type "{apps[2]}" is not the correct value, it should be between 0-255.')
                                    fwpolicyapp_invalid_check = True
                                if len(apps) == 4:
                                    if (int(apps[3]) not in range(0, 255)):
                                        log(f'ROW {i + 3} : ICMP code "{apps[3]}" is not the correct vale, it should be between 0-255.')
                                        fwpolicyapp_invalid_check = True
    if any([fwpolicyapp_empty_check, fwpolicyapp_invalid_check, fwpolicyapp_appg_length, fwpolicyapp_appg_mistake]) or any(fwpolicyapp_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_FirewallPolicyServicelist(filename, fwpolicy_list,ct):
    fwpolicyservice_empty_check = False
    fwpolicyservice_invalid_check = False
    fwpolicyservice_check = []
    fwpolicyservice_serviceg_length = False
    fwpolicyservice_serviceg_mistake = False
    dffwpolicyservicelist = data_frame(filename, 'Firewall-Policy-ServiceList')
    dfcolumns = dffwpolicyservicelist.columns.values.tolist()

    for i in dffwpolicyservicelist.index:
        region = str(dffwpolicyservicelist.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicyservice_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicyservice_invalid_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicyservicelist.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicyservice_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicyservice_check.append(compare_values(fwpolicy_list.tolist(), columnvalue, [i, 'Firewall Policy', 'Firewall-Policy']))
            if (columnname == 'Service List'):
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 28):
                        log(f'ROW {i + 3} : Service List name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 28.')
                        fwpolicyservice_serviceg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Service List Name')
                        fwpolicyservice_invalid_check == True
            if (columnname == 'Services'):
                if columnvalue.lower() != 'nan':
                    allservices = columnvalue.split("\n")
                    for services in allservices:
                        services = services.split("::")
                        mistake = '[A-Za-z0-9]:[A-Za-z0-9]'
                        for app in services:
                            if re.search(mistake, app):
                                log(f'ROW {i + 3} : Services value "{services}" have only one : as a seperator. Re-run validation after fixing it')
                                fwpolicyservice_serviceg_mistake = True
                        if len(services) < 3 or len(services) > 3:
                            log(f'ROW {i + 3} : Services value "{services}" does not have all/correct required details')
                            fwpolicyservice_invalid_check = True
                        else:
                            if (len(services[0]) > 28):
                                log(f'ROW {i + 3} : Service name "{services[0]}" has more alphanumeric characters than the allowed maximum limit of 28.')
                                fwpolicyservice_serviceg_length = True
                            if (validate_names(services[0]) == True):
                                log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Services Name')
                                fwpolicyservice_invalid_check == True

                            if (services[1] not in ['TCP_SERVICE', 'UDP_SERVICE']):
                                log(f'ROW {i + 3} : Service type "{services[1]}" is not the correct value.')
                                fwpolicyservice_invalid_check = True
                            if (services[2] != 'nan'):
                                ports = services[2].split(",")
                                for port in ports:
                                    port_miss = '^([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-5][0-9][0-9][0-9][0-9]|[6][0-5][0-2][0-9][0-9]|[6][5][3][0-2][0-5])[-]([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-5][0-9][0-9][0-9][0-9]|[6][0-5][0-2][0-9][0-9]|[6][5][3][0-2][0-5])$'
                                    if not re.search(port_miss, port):
                                        log(f'ROW {i + 3} : Port info "{port}" in "{services[0]}" is not valid. It should be in format "min_port-max_port" and maximum port range is 65325')
                                        fwpolicyservice_invalid_check = True

    if any([fwpolicyservice_empty_check, fwpolicyservice_invalid_check, fwpolicyservice_serviceg_length, fwpolicyservice_serviceg_mistake]) or any(fwpolicyservice_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_FirewallPolicyUrllist(filename, fwpolicy_list,ct):
    fwpolicyurl_empty_check = False
    fwpolicyurl_invalid_check = False
    fwpolicyurl_check = []
    fwpolicyurl_urlg_length = False
    fwpolicyurl_urlg_mistake = False
    dffwpolicyUrllist = data_frame(filename, 'Firewall-Policy-UrlList')
    dfcolumns = dffwpolicyUrllist.columns.values.tolist()

    for i in dffwpolicyUrllist.index:
        region = str(dffwpolicyUrllist.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicyurl_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicyurl_invalid_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicyUrllist.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicyurl_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicyurl_check.append(compare_values(fwpolicy_list.tolist(), columnvalue, [i, 'Policy Name', 'Firewall-Policy']))
            if (columnname == 'List Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column List Name.')
                    fwpolicyurl_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 28):
                        log(f'ROW {i + 3} : URL List Name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 28.')
                        fwpolicyurl_urlg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the URL List Name')
                        fwpolicyurl_invalid_check == True
            if (columnname == 'URL List'):
                if columnvalue.lower() != 'nan':
                    allurls = columnvalue.split("\n")
                    for urls in allurls:
                        validurl = '^(?!:\/\/)(?=.{1,255}$)((.{1,63}\.){1,127}(?![0-9]*$)[a-z0-9-]+\.?)$'
                        if not re.search(validurl,urls):
                            fwurllistname = str(dffwpolicyUrllist.loc[i, 'List Name']).strip()
                            log(f'ROW {i + 3} : URL "{urls}" in URL List "{fwurllistname}" is not a valid URL')
                            fwpolicyurl_invalid_check = True
    if any([fwpolicyurl_empty_check, fwpolicyurl_invalid_check, fwpolicyurl_urlg_length, fwpolicyurl_urlg_mistake]) or any(fwpolicyurl_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_FirewallPolicyAddress(filename, fwpolicy_list,ct):
    fwpolicyaddress_empty_check = False
    fwpolicyaddress_invalid_check = False
    fwpolicyaddress_check = []
    fwpolicyaddress_addressg_length = False
    fwpolicyaddress_addressg_mistake = False
    dffwpolicyAddress = data_frame(filename, 'Firewall-Policy-AddressList')
    dfcolumns = dffwpolicyAddress.columns.values.tolist()

    for i in dffwpolicyAddress.index:
        region = str(dffwpolicyAddress.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicyaddress_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicyaddress_invalid_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicyAddress.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicyaddress_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicyaddress_check.append(compare_values(fwpolicy_list.tolist(), columnvalue,[i, 'Policy Name', 'Firewall-Policy']))
            if (columnname == 'List Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column List Name.')
                    fwpolicyaddress_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 28):
                        log(f'ROW {i + 3} : url List name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 28.')
                        fwpolicyaddress_addressg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Address List Name')
                        fwpolicyaddress_invalid_check == True
            if (columnname == 'Address Type'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Address Type.')
                    fwpolicyaddress_empty_check = True
                if (columnvalue not in ['IP', 'FQDN']):
                    log(f'ROW {i + 3} : Address type "{columnvalue}" is not the correct value, it should be IP or FQDN.')
                    fwpolicyaddress_invalid_check = True
            if (columnname == 'Address List'):
                if columnvalue.lower() != 'nan':
                    alladdress = columnvalue.split(",")
                    for address in alladdress:
                        try:
                            ipaddress.ip_address(address)
                        except ValueError:
                            try:
                                ipaddress.ip_network(address)
                            except ValueError:
                                log(f'ROW {i + 3} : IP address "{address}" is not a valid IP or Network')
                                fwpolicyaddress_invalid_check = True
    if any([fwpolicyaddress_empty_check, fwpolicyaddress_invalid_check, fwpolicyaddress_addressg_length, fwpolicyaddress_addressg_mistake]) or any(fwpolicyaddress_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_FirewallPolicySecrets(filename, fwpolicy_list, config,signer, ct):
    comp_ids = ct.ntk_compartment_ids
    fwpolicysecret_empty_check = False
    fwpolicysecret_invalid_check = False
    fwpolicysecret_check = []
    fwpolicysecret_secret_length = False
    fwpolicysecret_comp_check = False
    fwpolicysecret_vault_check = []
    dffwpolicysecret = data_frame(filename, 'Firewall-Policy-Secret')
    dfcolumns = dffwpolicysecret.columns.values.tolist()

    for i in dffwpolicysecret.index:
        region = str(dffwpolicysecret.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicysecret_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicysecret_invalid_check = True

        # Check for invalid Compartment Name
        comp_name = str(dffwpolicysecret.loc[i, 'Vault Compartment Name']).strip()
        if comp_name.lower() == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Vault Compartment Name".')
            fwpolicysecret_empty_check = True
        else:
            try:
                comp_id = comp_ids[comp_name]
            except KeyError:
                log(f'ROW {i + 3} : Compartment {comp_name} does not exist in OCI.')
                fwpolicysecret_comp_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicysecret.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicysecret_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicysecret_check.append(compare_values(fwpolicy_list.tolist(), columnvalue, [i, 'Policy Name', 'Firewall-Policy']))
            if (columnname == 'Secret Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Secret Name.')
                    fwpolicysecret_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 58):
                        log(f'ROW {i + 3} : Secret name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 58.')
                        fwpolicysecret_secret_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Secret Name')
                        fwpolicysecret_invalid_check == True
            if (columnname == 'Secret Source'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Secret Source.')
                    fwpolicysecret_empty_check = True
                if (columnvalue not in ['OCI_VAULT']):
                    log(f'ROW {i + 3} : Secret Source "{columnvalue}" is not the correct value, it should be OCI_VAULT.')
                    fwpolicysecret_invalid_check = True
            if (columnname == 'Secret Type'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Secret Type.')
                    fwpolicysecret_empty_check = True
                if (columnvalue not in ['SSL_FORWARD_PROXY', 'SSL_INBOUND_INSPECTION']):
                    log(f'ROW {i + 3} : Secret Type "{columnvalue}" is not the correct value, it should be SSL_INBOUND_INSPECTION/SSL_FORWARD_PROXY.')
                    fwpolicysecret_invalid_check = True
            if columnname == 'Vault Secret Id':
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Vault Secret Id.')
                    fwpolicysecret_empty_check = True
                else:
                    # Cross-check vault and secret against OCI. .
                    mistake = '[A-Za-z0-9]:[A-Za-z0-9]'
                    if re.search(mistake, columnvalue):
                        log(f'ROW {i + 3} : Vault Secret id "{columnvalue}" have only one : as a seperator. Re-run validation after fixing it')
                        fwpolicysecret_invalid_check = True
                    else:
                        region1 = str(dffwpolicysecret.loc[i, 'Region']).strip().lower()
                        cmp1 = str(dffwpolicysecret.loc[i, 'Vault Compartment Name']).strip()
                        secretname = region1 + '::' + columnvalue
                        fwpolicysecret_vault_check.append(validate_vault_secret(i,region1,cmp1,columnvalue,comp_ids,config,signer, ct))
            if (columnname == 'Version Number'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Version Number.')
                    fwpolicysecret_empty_check = True
                else:
                    if (int(columnvalue) not in range(0, 255)):
                        log(f'ROW {i + 3} : Secret Version Number "{columnvalue}" is not the correct value.')
                        fwpolicysecret_invalid_check = True
    if any([fwpolicysecret_empty_check, fwpolicysecret_invalid_check, fwpolicysecret_secret_length, fwpolicysecret_comp_check]) or any(fwpolicysecret_vault_check) or any(fwpolicysecret_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_FirewallPolicyDecryption(filename, fwpolicy_list,ct):
    fwpolicydecrypt_empty_check = False
    fwpolicydecrypt_invalid_check = False
    fwpolicydecrypt_check = []
    fwpolicydecrypt_nameg_length = False
    dffwpolicydecrypt = data_frame(filename, 'Firewall-Policy-DecryptProfile')
    dfcolumns = dffwpolicydecrypt.columns.values.tolist()

    for i in dffwpolicydecrypt.index:
        region = str(dffwpolicydecrypt.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicydecrypt_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicydecrypt_invalid_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicydecrypt.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicydecrypt_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicydecrypt_check.append(compare_values(fwpolicy_list.tolist(), columnvalue,[i, 'Firewall Policy', 'Firewall-Policy']))
            if (columnname == 'Decryption Profile Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Decryption Profile Name.')
                    fwpolicydecrypt_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 63) or (len(columnvalue) < 2):
                        log(f'ROW {i + 3} : Decryption Profile Name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 63.')
                        fwpolicydecrypt_nameg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Decryption Profile Name')
                        fwpolicydecrypt_invalid_check == True
            if (columnname == 'Decryption Profile Type'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Decryption Profile Type.')
                    fwpolicydecrypt_empty_check = True
                if (columnvalue not in ['SSL_FORWARD_PROXY', 'SSL_INBOUND_INSPECTION']):
                    log(f'ROW {i + 3} : Decryption Profile Type "{columnvalue}" is not the correct value, it should be SSL_INBOUND_INSPECTION/SSL_FORWARD_PROXY.')
                    fwpolicydecrypt_invalid_check = True
            if (columnname in ['are certificate extensions restricted', 'is auto include alt name',
                               'is expired certificate blocked', 'is out of capacity blocked',
                               'is revocation status timeout blocked', 'is unknown revocation status blocked',
                               'is unsupported cipher blocked', 'is unsupported version blocked',
                               'is untrusted issuer blocked']):
                if columnvalue.lower() != 'nan' and columnvalue not in ['True', 'False']:
                    log(f'ROW {i + 3} : The value for "{columnname}" is not TRUE/FALSE.')
                    fwpolicydecrypt_invalid_check = True

    if any([fwpolicydecrypt_empty_check, fwpolicydecrypt_invalid_check, fwpolicydecrypt_nameg_length]) or any(fwpolicydecrypt_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_FirewallPolicyDecryptionRule(filename, fwpolicy_list, fulladdreslist, fullsercretslist, fulldecryptlist,ct):
    fwpolicydecryptrule_empty_check = False
    fwpolicydecryptrule_invalid_check = False
    fwpolicydecryptrule_check = []
    fwpolicydecryptrule_nameg_length = False
    fwpolicydecryptrulesa_check = []
    fwpolicydecryptruleda_check = []
    fwpolicydecryptrulesn_check = []
    fwpolicydecryptruledp_check = []
    fwpolicydecryptrulepost_check = []

    dffwpolicydecryptrule = data_frame(filename, 'Firewall-Policy-DecryptRule')
    dfcolumns = dffwpolicydecryptrule.columns.values.tolist()

    dffwdecryptrule = data_frame(filename, 'Firewall-Policy-DecryptRule')
    dffwdecryptrule_list = dffwdecryptrule['Rule Name'].astype(str)
    dffwdecryptrulepolicy_list = dffwdecryptrule['Firewall Policy'].astype(str)
    fulldecryptrulelist = dffwdecryptrulepolicy_list + '::' + dffwdecryptrule_list

    for i in dffwpolicydecryptrule.index:
        region = str(dffwpolicydecryptrule.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicydecryptrule_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicydecryptrule_invalid_check = True
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicydecryptrule.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicydecryptrule_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicydecryptrule_check.append(compare_values(fwpolicy_list.tolist(), columnvalue,[i, 'Policy Name', 'Firewall-Policy']))
            if (columnname == 'Rule Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Rule Name.')
                    fwpolicydecryptrule_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 63) or (len(columnvalue) < 2):
                        log(f'ROW {i + 3} : Decryption Profile Name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 63.')
                        fwpolicydecryptrule_nameg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Decryption Rule Name')
                        fwpolicydecryptrule_invalid_check == True
            if (columnname == 'Source Address'):
                if columnvalue.lower() != 'nan':
                    sa_list = columnvalue.split(",")
                    for eachsa in sa_list:
                        fwpolicyname = str(dffwpolicydecryptrule.loc[i, 'Firewall Policy']).strip()
                        finalsalist = fwpolicyname + '::' + eachsa
                        fwpolicydecryptrulesa_check.append(compare_values(fulladdreslist.tolist(), finalsalist, [i, 'Source Address', 'Firewall-Policy-Address', 'Address list']))
            if (columnname == 'Destination Address'):
                if columnvalue.lower() != 'nan':
                    da_list = columnvalue.split(",")
                    for eachda in da_list:
                        fwpolicyname = str(dffwpolicydecryptrule.loc[i, 'Firewall Policy']).strip()
                        finaldalist = fwpolicyname + '::' + eachda
                        fwpolicydecryptruleda_check.append(compare_values(fulladdreslist.tolist(), finaldalist, [i, 'Destination Address','Firewall-Policy-Address', 'Address list']))
            if (columnname == 'Secret Name'):
                if columnvalue.lower() != 'nan':
                    fwpolicyname = str(dffwpolicydecryptrule.loc[i, 'Firewall Policy']).strip()
                    finalsnlist = fwpolicyname + '::' + columnvalue
                    fwpolicydecryptrulesn_check.append(compare_values(fullsercretslist.tolist(), finalsnlist, [i, 'Secret Name', 'Firewall-Policy-Secrets', 'Secret name']))
            if (columnname == 'Decryption Profile'):
                if columnvalue.lower() != 'nan':
                    fwpolicyname = str(dffwpolicydecryptrule.loc[i, 'Firewall Policy']).strip()
                    finaldplist = fwpolicyname + '::' + columnvalue
                    fwpolicydecryptruledp_check.append(compare_values(fulldecryptlist.tolist(), finaldplist, [i, 'Decryption Profile', 'Firewall-Policy-Decryptprofile', 'Decryption Profile name']))
            if (columnname == 'Action'):
                if (columnvalue not in ['NO_DECRYPT', 'DECRYPT']):
                    log(f'ROW {i + 3} : Action "{columnvalue}" is not a valid option, it should be either NO_DECRYPT/DECRYPT.')
                    fwpolicydecryptrule_invalid_check = True

            if (columnname == 'Position'):
                if columnvalue.lower() != 'nan':
                    post = columnvalue.split('::')
                    if len(post) != 2:
                        log(f'ROW {i + 3} : Position value in "{post}" does not have all/correct required details')
                        fwpolicydecryptrule_invalid_check = True
                    else:
                        if (post[0] not in ['before_rule', 'after_rule']):
                            log(f'ROW {i + 3} : Position condition in "{post[0]}" is not a valid option, it should be either before_rule/after_rule')
                        if post[1].lower() != 'nan':
                            fwpolicyname = str(dffwpolicydecryptrule.loc[i, 'Firewall Policy']).strip()
                            finalrulepost = fwpolicyname + '::' + post[1]
                            fwpolicydecryptrulepost_check.append(compare_values(fulldecryptrulelist.tolist(), finalrulepost, [i, 'Firewall Policy', 'Firewall-Policy-DecryptionRule', 'Post']))

    if any([fwpolicydecryptrule_empty_check, fwpolicydecryptrule_invalid_check, fwpolicydecryptrule_nameg_length]) or any(fwpolicydecryptrule_check) or any(fwpolicydecryptrulesa_check) or any(fwpolicydecryptruleda_check) or any(fwpolicydecryptrulesn_check) or any(fwpolicydecryptruledp_check) or any(fwpolicydecryptrulepost_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False


def validate_FirewallPolicyTunnelInspectRule(filename, fwpolicy_list, fulladdreslist, ct):
    fwpolicytunnelinspectrule_empty_check = False
    fwpolicytunnelinspectrule_invalid_check = False
    fwpolicytunnelinspectrule_check = []
    fwpolicytunnelinspectrule_nameg_length = False
    fwpolicytunnelinspectrulesa_check = []
    fwpolicytunnelinspectruleda_check = []
    fwpolicytunnelinspectrulepost_check = []

    dffwpolicytunnelinspectrule = data_frame(filename, 'Firewall-Policy-TunnelInspect')
    dfcolumns = dffwpolicytunnelinspectrule.columns.values.tolist()

    dffwtunnleinspectrule = data_frame(filename, 'Firewall-Policy-TunnelInspect')
    dffwtunnleinspectrule_list = dffwtunnleinspectrule['Rule Name'].astype(str)
    dffwtunnleinspectrulepolicy_list = dffwtunnleinspectrule['Firewall Policy'].astype(str)
    fulltunnelinspectrulelist = dffwtunnleinspectrulepolicy_list + '::' + dffwtunnleinspectrule_list

    for i in dffwpolicytunnelinspectrule.index:
        region = str(dffwpolicytunnelinspectrule.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicytunnelinspectrule_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicytunnelinspectrule_invalid_check = True
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicytunnelinspectrule.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Policy Name.')
                    fwpolicytunnelinspectrule_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicytunnelinspectrule_check.append(
                        compare_values(fwpolicy_list.tolist(), columnvalue, [i, 'Policy Name', 'Firewall-Policy']))
            if (columnname == 'Rule Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Rule Name.')
                    fwpolicytunnelinspectrule_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 63) or (len(columnvalue) < 2):
                        log(f'ROW {i + 3} : Tunnel inspection rule Name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 63.')
                        fwpolicytunnelinspectrule_nameg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Tunnel inspection Rule Name')
                        fwpolicytunnelinspectrule_invalid_check == True
            if (columnname == 'Source Address'):
                if columnvalue.lower() != 'nan':
                    sa_list = columnvalue.split(",")
                    for eachsa in sa_list:
                        fwpolicyname = str(dffwpolicytunnelinspectrule.loc[i, 'Firewall Policy']).strip()
                        finalsalist = fwpolicyname + '::' + eachsa
                        fwpolicytunnelinspectrulesa_check.append(compare_values(fulladdreslist.tolist(), finalsalist,[i, 'Source Address','Firewall-Policy-Address','Address list']))
            if (columnname == 'Destination Address'):
                if columnvalue.lower() != 'nan':
                    da_list = columnvalue.split(",")
                    for eachda in da_list:
                        fwpolicyname = str(dffwpolicytunnelinspectrule.loc[i, 'Firewall Policy']).strip()
                        finaldalist = fwpolicyname + '::' + eachda
                        fwpolicytunnelinspectruleda_check.append(compare_values(fulladdreslist.tolist(), finaldalist,[i, 'Destination Address','Firewall-Policy-Address','Address list']))
            if (columnname == 'Action'):
                if (columnvalue not in ['INSPECT', 'INSPECT_AND_CAPTURE_LOG', 'Inspect', 'Inspect_And_Capture_Log', 'inspect', 'inspect_and_capture_log','Inspect_and_capture_log']):
                    log(f'ROW {i + 3} : Action "{columnvalue}" is not a valid option, it should be either INSPECT/INSPECT_AND_CAPTURE_LOG.')
                    fwpolicytunnelinspectrule_invalid_check = True

            if (columnname == 'Position'):
                if columnvalue.lower() != 'nan':
                    post = columnvalue.split('::')
                    if len(post) != 2:
                        log(f'ROW {i + 3} : Position value in "{post}" does not have all/correct required details')
                        fwpolicytunnelinspectrule_invalid_check = True
                    else:
                        if (post[0] not in ['before_rule', 'after_rule']):
                            log(f'ROW {i + 3} : Position condition in "{post[0]}" is not a valid option, it should be either before_rule/after_rule')
                        if post[1].lower() != 'nan':
                            fwpolicyname = str(dffwpolicytunnelinspectrule.loc[i, 'Firewall Policy']).strip()
                            finalrulepost = fwpolicyname + '::' + post[1]
                            fwpolicytunnelinspectrulepost_check.append(
                                compare_values(fulltunnelinspectrulelist.tolist(), finalrulepost,[i, 'Position', 'Firewall-Policy-TunnelInspect', 'Rule name']))

    if any([fwpolicytunnelinspectrule_empty_check, fwpolicytunnelinspectrule_invalid_check,
            fwpolicytunnelinspectrule_nameg_length]) or any(fwpolicytunnelinspectrule_check) or any(
            fwpolicytunnelinspectrulesa_check) or any(fwpolicytunnelinspectruleda_check) or  any(
            fwpolicytunnelinspectrulepost_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_FirewallPolicySecurityRule(filename, fwpolicy_list, fulladdreslist, fullservicelist, fullappslist, fullurlslist,ct):
    fwpolicysecurityrule_empty_check = False
    fwpolicysecurityrule_invalid_check = False
    fwpolicysecurityrule_check = []
    fwpolicysecurityrule_nameg_length = False
    fwpolicysecurityrulesa_check = []
    fwpolicysecurityruleda_check = []
    fwpolicysecurityrulesl_check = []
    fwpolicysecurityruleal_check = []
    fwpolicysecurityruleul_check = []
    fwpolicysecurityrule_action_mistake = False
    fwpolicysecurityrulepost_check = []
    dffwpolicysecurityrule = data_frame(filename, 'Firewall-Policy-SecRule')
    dfcolumns = dffwpolicysecurityrule.columns.values.tolist()

    dffwsecurityrule = data_frame(filename, 'Firewall-Policy-SecRule')
    dffwsecurityrule_list = dffwsecurityrule['Rule Name'].astype(str)
    dffwsecurityrulepolicy_list = dffwsecurityrule['Firewall Policy'].astype(str)
    fullsecurityrulelist = dffwsecurityrulepolicy_list + '::' + dffwsecurityrule_list

    for i in dffwpolicysecurityrule.index:
        region = str(dffwpolicysecurityrule.loc[i, 'Region']).strip().lower()
        # Encountered <End>
        if (region in commonTools.endNames):
            break
        if region == 'nan':
            log(f'ROW {i + 3} : Empty value at column "Region".')
            fwpolicysecurityrule_empty_check = True
        elif region not in ct.all_regions:
            log(f'ROW {i + 3} : "Region" {region} is not subscribed for tenancy.')
            fwpolicysecurityrule_invalid_check = True

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(dffwpolicysecurityrule.loc[i, columnname]).strip()
            if (columnname == 'Firewall Policy'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Firewall Policy.')
                    fwpolicysecurityrule_empty_check = True
                else:
                    # Cross check the Policy names in Firewall Policy sheet with OCI.
                    fwpolicysecurityrule_check.append(compare_values(fwpolicy_list.tolist(), columnvalue,[i, 'Policy Name', 'Firewall-Policy']))
            if (columnname == 'Rule Name'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Rule Name.')
                    fwpolicysecurityrule_empty_check = True
                if columnvalue.lower() != 'nan':
                    if (len(columnvalue) > 63) or (len(columnvalue) < 2):
                        log(f'ROW {i + 3} : Security Rule Name "{columnvalue}" has more alphanumeric characters than the allowed maximum limit of 63.')
                        fwpolicysecurityrule_nameg_length = True
                    if (validate_names(columnvalue) == True):
                        log(f'ROW {i + 3} : Only alphabets, digits, - and _ are allowed in the Security Rule Name')
                        fwpolicysecurityrule_invalid_check == True
            if (columnname == 'Source Address'):
                if columnvalue.lower() != 'nan':
                    sa_list = columnvalue.split(",")
                    for eachsa in sa_list:
                        fwpolicyname = str(dffwpolicysecurityrule.loc[i, 'Firewall Policy']).strip()
                        finalsalist = fwpolicyname + '::' + eachsa
                        fwpolicysecurityrulesa_check.append(compare_values(fulladdreslist.tolist(), finalsalist,[i, 'Source Address', 'Firewall-Policy-Address', 'Address list']))
            if (columnname == 'Destination Address'):
                if columnvalue.lower() != 'nan':
                    da_list = columnvalue.split(",")
                    for eachda in da_list:
                        fwpolicyname = str(dffwpolicysecurityrule.loc[i, 'Firewall Policy']).strip()
                        finaldalist = fwpolicyname + '::' + eachda
                        fwpolicysecurityruleda_check.append(compare_values(fulladdreslist.tolist(), finaldalist,[i, 'Destination Address','Firewall-Policy-Address', 'Address list']))
            if (columnname == 'Service List'):
                if columnvalue.lower() != 'nan':
                    sl_list = columnvalue.split(",")
                    for eachsl in sl_list:
                        fwpolicyname = str(dffwpolicysecurityrule.loc[i, 'Firewall Policy']).strip()
                        finalsllist = fwpolicyname + '::' + eachsl
                        fwpolicysecurityrulesl_check.append(compare_values(fullservicelist.tolist(), finalsllist,[i, 'Service List','Firewall-Policy-Servicelist', 'Service list']))
            if (columnname == 'Application List'):
                if columnvalue.lower() != 'nan':
                    al_list = columnvalue.split(",")
                    for eachal in al_list:
                        fwpolicyname = str(dffwpolicysecurityrule.loc[i, 'Firewall Policy']).strip()
                        finalallist = fwpolicyname + '::' + eachal
                        fwpolicysecurityruleal_check.append(compare_values(fullappslist.tolist(), finalallist, [i, 'Application List','Firewall-Policy-Applicationlist', 'Application list']))
            if (columnname == 'Url List'):
                if columnvalue.lower() != 'nan':
                    ul_list = columnvalue.split(",")
                    for eachul in ul_list:
                        fwpolicyname = str(dffwpolicysecurityrule.loc[i, 'Firewall Policy']).strip()
                        finalullist = fwpolicyname + '::' + eachul
                        fwpolicysecurityruleul_check.append(compare_values(fullurlslist.tolist(), finalullist,[i, 'Url List', 'Firewall-Policy-urllist', 'Ur listl']))
            if (columnname == 'Action'):
                if columnvalue.lower() == 'nan':
                    log(f'ROW {i + 3} : Empty value at column Action.')
                    fwpolicysecurityrule_empty_check = True
                else:
                    act = columnvalue.split('::')
                    if len(act) == 1:
                        mistake = '[A-Za-z0-9]:[A-Za-z0-9]'
                        if re.search(mistake, act[0]):
                            log(f'ROW {i + 3} : Action value "{act[0]}" have only one : as a seperator. Re-run validation after fixing it')
                            fwpolicysecurityrule_action_mistake = True
                        elif (act[0] not in ['ALLOW', 'DROP', 'REJECT', 'Allow', 'allow', 'Drop', 'drop', 'reject', 'Reject']):
                            log(f'ROW {i + 3} : Action value in "{act[0]}" is not valid. It can be one of the following "ALLOW/DROP/REJECT"')
                            fwpolicysecurityrule_invalid_check = True
                    elif len(act) == 2:
                        if (act[0] not in ['INSPECT', 'Inspect', 'inspect']):
                            log(f'ROW {i + 3} : Action"{columnvalue}" is not a valid option. It should be either "INSPECT".')
                            fwpolicysecurityrule_invalid_check = True
                        if (act[0].upper() in ['INSPECT']):
                            if(act[1] not in ['INTRUSION_DETECTION', 'INTRUSION_PREVENTION', 'Intrusion_Detection', 'intrusion_detection', 'Intrusion_detection', 'Intrusion_Prevention', 'intrusion_prevention', 'Intrusion_prevention' ]):
                                log(f'ROW {i + 3} : Inspection"{columnvalue}" is not a valid option. It should be either "INTRUSION_DETECTION/INTRUSION_PREVENTION".')
                                fwpolicysecurityrule_invalid_check = True
                    else:
                        log(f'ROW {i + 3} : "{columnvalue}" is not a valid option for Security rule Action.')
                        fwpolicysecurityrule_invalid_check = True
            if (columnname == 'Position'):
                if columnvalue.lower() != 'nan':
                    post = columnvalue.split('::')
                    if len(post) != 2:
                        log(f'ROW {i + 3} : Position value in "{post}" does not have all/correct required details')
                        fwpolicysecurityrule_invalid_check = True
                    else:
                        if post[0] not in ['before_rule', 'after_rule']:
                            log(f'ROW {i + 3} : Position condition in "{post[0]}" is not a valid option, it should be either before_rule/after_rule')
                        if post[1].lower() != 'nan':
                            fwpolicyname = str(dffwpolicysecurityrule.loc[i, 'Firewall Policy']).strip()
                            finalrulepost = fwpolicyname + '::' + post[1]
                            fwpolicysecurityrulepost_check.append(compare_values(fullsecurityrulelist.tolist(), finalrulepost,[i, 'Position', 'Firewall-Policy-Secrule', 'Rule name']))

    if any([fwpolicysecurityrule_empty_check, fwpolicysecurityrule_invalid_check, fwpolicysecurityrule_nameg_length, fwpolicysecurityrule_action_mistake]) or any(fwpolicysecurityruleal_check) or any(fwpolicysecurityruleul_check) or any(fwpolicysecurityrulepost_check) or any(fwpolicysecurityrulesl_check) or any(fwpolicysecurityruleda_check) or any(fwpolicysecurityrulesa_check) or any(fwpolicysecurityrule_check):
        print("Null or Wrong value Check failed!!")
        return True
    else:
        return False

def validate_compartments(filename,ct):

    comp_empty_check = False
    comp_invalid_check = False
    parent_comp_check= False
    # Read the Compartments tab from excel
    dfcomp = data_frame(filename ,'Compartments')

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


def validate_firewall_cd3(filename, var_file, prefix, outdir, config,signer,ct):
    CD3_LOG_LEVEL = 60
    logging.addLevelName(CD3_LOG_LEVEL, "custom")
    file = prefix+"_cd3FirewallValidator.log"
    resource = "cd3Firewallvalidator"
    customer_tenancy_dir = outdir
    commonTools.backup_file(customer_tenancy_dir,resource,file)
    logging.basicConfig(filename=customer_tenancy_dir+"/"+file, filemode="w", format="%(asctime)s - %(message)s", level=60)
    logger = logging.getLogger("cd3FirewallValidator")
    global log
    log = partial(logger.log, CD3_LOG_LEVEL)


    global compartment_ids
    compartment_ids = {}
    global vcn_ids
    vcn_ids = {}
    global subnet_names
    subnet_names = []
    global nsg_names
    nsg_names = []
    global vcn_cidrs
    vcn_cidrs = {}
    global vcn_compartment_ids
    vcn_compartment_ids = {}

    Firewall_check = False
    fw_policy_check = False
    fw_policyapp_check = False
    fw_policyservice_check = False
    fw_policyurl_check = False
    fw_policyaddress_check = False
    fw_policysecrets_check = False
    fw_policydecryption_check = False
    fw_policydecryptionrule_check = False
    fw_policysecurityrule_check = False

    if not os.path.exists(filename):
        print("\nCD3 excel sheet not found at "+filename +"\nExiting!!")
        exit()

    #ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)
    print("Getting Compartments OCIDs...")
    ct.get_compartment_map(var_file,'Validator')

    dffwpolicy = data_frame(filename, 'Firewall-Policy')
    fwpolicy_list = dffwpolicy['Policy Name'].astype(str)

    dffwaddress = data_frame(filename, 'Firewall-Policy-AddressList')
    dffwaddress_list = dffwaddress['List Name'].astype(str)
    dffwaddresspolicy_list = dffwaddress['Firewall Policy'].astype(str)
    fulladdreslist = dffwaddresspolicy_list + '::' + dffwaddress_list

    dffwservice = data_frame(filename, 'Firewall-Policy-ServiceList')
    dffwservice_list = dffwservice['Service List'].astype(str)
    dffwservicepolicy_list = dffwservice['Firewall Policy'].astype(str)
    fullservicelist = dffwservicepolicy_list + '::' + dffwservice_list

    dffwapps = data_frame(filename, 'Firewall-Policy-ApplicationList')
    dffwapps_list = dffwapps['Application List'].astype(str)
    dffwappspolicy_list = dffwapps['Firewall Policy'].astype(str)
    fullappslist = dffwappspolicy_list + '::' + dffwapps_list

    dffwurls = data_frame(filename, 'Firewall-Policy-UrlList')
    dffwurls_list = dffwurls['List Name'].astype(str)
    dffwurlspolicy_list = dffwurls['Firewall Policy'].astype(str)
    fullurlslist = dffwurlspolicy_list + '::' + dffwurls_list

    dffwsecrets = data_frame(filename, 'Firewall-Policy-Secret')
    dffwsecrets_list = dffwsecrets['Secret Name'].astype(str)
    dffwsecrestspolicy_list = dffwsecrets['Firewall Policy'].astype(str)
    fullsecretslist = dffwsecrestspolicy_list + '::' + dffwsecrets_list

    dffwdecrypt = data_frame(filename, 'Firewall-Policy-DecryptProfile')
    dffwdecrypt_list = dffwdecrypt['Decryption Profile Name'].astype(str)
    dffwdecryptpolicy_list = dffwdecrypt['Firewall Policy'].astype(str)
    fulldecryptlist = dffwdecryptpolicy_list + '::' + dffwdecrypt_list

    log("\n============================= Verifying Firewall Tab ==========================================\n")
    print("\nProcessing Firewall Tab..")
    Firewall_check = validate_Firewall(filename, ct.ntk_compartment_ids, fwpolicy_list,config,signer, ct)
    log("\n============================= Verifying Firewall-Policy Tab ==========================================\n")
    print("\nProcessing Firewall-Policy Tab..")
    fw_policy_check = validate_FirewallPolicy(filename, ct)
    log("\n============================= Verifying Firewall-Policy-ApplicationList Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-Applicationlist Tab..")
    fw_policyapp_check = validate_FirewallPolicyApplist(filename, fwpolicy_list,ct)
    log("\n============================= Verifying Firewall-Policy-ServiceList Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-Servicelist Tab..")
    fw_policyservice_check = validate_FirewallPolicyServicelist(filename, fwpolicy_list,ct)
    log("\n============================= Verifying Firewall-Policy-urlList Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-urllist Tab..")
    fw_policyurl_check = validate_FirewallPolicyUrllist(filename, fwpolicy_list,ct)
    log("\n============================= Verifying Firewall-Policy-AddressList Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-Address Tab..")
    fw_policyaddress_check = validate_FirewallPolicyAddress(filename, fwpolicy_list,ct)
    log("\n============================= Verifying Firewall-Policy-Secret Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-Secrets Tab..")
    fw_policysecrets_check = validate_FirewallPolicySecrets(filename, fwpolicy_list, config,signer, ct)
    log("\n============================= Verifying Firewall-Policy-DecryptProfile Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-Decryptprofile Tab..")
    fw_policydecryption_check = validate_FirewallPolicyDecryption(filename, fwpolicy_list,ct)
    log("\n============================= Verifying Firewall-Policy-DecryptRule Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-DecryptRule Tab..")
    fw_policydecryptionrule_check = validate_FirewallPolicyDecryptionRule(filename, fwpolicy_list, fulladdreslist, fullsecretslist, fulldecryptlist,ct)
    log("\n============================= Verifying Firewall-Policy-SecRule Tab ==========================================\n")
    print("\nProcessing Firewall-Policy-Secrules Tab..")
    fw_policysecurityrule_check = validate_FirewallPolicySecurityRule(filename, fwpolicy_list, fulladdreslist, fullservicelist, fullappslist, fullurlslist,ct)
    print("\nProcessing Firewall-Policy-TunnelInspect Tab..")
    fw_policytunnelinspect_check = validate_FirewallPolicyTunnelInspectRule(filename, fwpolicy_list, fulladdreslist, ct)
    # Prints the final result; once the validation is complete
    if any([Firewall_check, fw_policy_check, fw_policyapp_check, fw_policyurl_check, fw_policyservice_check, fw_policyaddress_check, fw_policysecrets_check, fw_policydecryption_check, fw_policydecryptionrule_check, fw_policysecurityrule_check, fw_policytunnelinspect_check]):
        log("=======")
        log("Summary:")
        log("=======")
        log("ERROR: Make appropriate changes to CD3 Values as per above Errors and try again !!!")
        print("\n\nSummary:")
        print("=======")
        print("Errors Found!!!")
        print("Please check the log file at " + customer_tenancy_dir + "/" + file + "\n")
        return "Error"
    else:
        log("=======")
        log("Summary:")
        log("=======")
        log("There are no errors in CD3. Please proceed with TF Generation\n")
        print("\n\nSummary:")
        print("=======")
        print("There are no errors in CD3. Please proceed with TF Generation\n")
        return "No Error"



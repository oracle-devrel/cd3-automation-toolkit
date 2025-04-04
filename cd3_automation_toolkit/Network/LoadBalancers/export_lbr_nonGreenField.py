#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export LBR Components
#
# Author: Shruthi Subramanian
# Oracle Consulting
#
import sys
import oci
import os
import subprocess as sp

from oci.certificates import CertificatesClient
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.load_balancer.load_balancer_client import LoadBalancerClient

sys.path.append(os.getcwd() + "/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}


def cookie_headers(values_for_column, session_persistence, excel_header_map):
    for headers in values_for_column:
        if headers == 'Cookie Name':
            if (session_persistence.__getattribute__(commonTools.check_column_headers(headers))):
                values_for_column[headers].append(
                    str(session_persistence.__getattribute__(commonTools.check_column_headers(headers))))
            else:
                values_for_column[headers].append("")

        if headers == 'Cookie Path':
            try:
                value = str(session_persistence.__getattribute__(excel_header_map[headers]))
                if value.lower() == 'none':
                    value = ""
                values_for_column[headers].append(value)
            except AttributeError as e:
                values_for_column[headers].append("")

        if headers == "Disable Fallback(TRUE|FALSE)":
            if (session_persistence.__getattribute__(excel_header_map[headers])):
                value = str(session_persistence.__getattribute__(excel_header_map[headers]))
                if value.lower() == 'none':
                    value = ""
                values_for_column[headers].append(value)
            else:
                values_for_column[headers].append("")
    return values_for_column


def common_headers(region, headers, values_for_column, eachlbr, excel_header_map, lbr_compartment_name):
    if headers == 'Region':
        values_for_column[headers].append(str(region))
    elif headers == 'Compartment Name':
        values_for_column[headers].append(str(lbr_compartment_name))
    else:
        if headers in excel_header_map.keys():
            try:
                value = str(eachlbr.__getattribute__(excel_header_map[headers]))
                if value.lower() == "none":
                    value = ""
                values_for_column[headers].append(str(value))
            except AttributeError as e:
                pass
    return values_for_column


def print_certs(obj, reg, outdir, service_dir):
    cname = ""
    pname = ""

    ca_certificate = obj.ca_certificate
    public_certificate = obj.public_certificate

    # print(obj.certificate_name, outdir, reg)

    if str(ca_certificate).lower() != "none":
        cname = outdir + "/" + str(reg).lower() + "/" + service_dir + "/" + str(
            obj.certificate_name) + "-ca-certificate.cert"
        ca_cert = open(cname, "w")
        ca_cert.write(ca_certificate)
        ca_cert.close()

    if str(public_certificate).lower() != "none":
        pname = outdir + "/" + str(reg).lower() + "/" + service_dir + "/" + str(
            obj.certificate_name) + "-public_certificate.cert"
        public_cert = open(pname, "w")
        public_cert.write(public_certificate)
        public_cert.close()

    cert_name = obj.certificate_name
    ca_cert = str(cname)  # .replace("\\", "\\\\")
    public_cert = str(pname)  # .replace("\\", "\\\\")

    return cert_name, ca_cert, public_cert


def insert_values(values_for_column, oci_objs, sheet_dict, region, comp_name, display_name, minimum_bandwidth_in_mbps,
                  maximum_bandwidth_in_mbps, subnets, nsgs, reserved_ip, hostnames, cert_name, ca_cert,
                  passphrase, privatekey, public_cert, cipher_name, cipher_suites):
    for col_header in values_for_column.keys():
        if col_header == 'Region':
            values_for_column[col_header].append(str(region))
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(comp_name)
        elif col_header == 'LBR Name':
            values_for_column[col_header].append(display_name)
        elif col_header == "Network Details":
            values_for_column[col_header].append(subnets)
        elif (col_header == "NSGs"):
            values_for_column[col_header].append(nsgs)
        elif (col_header == "Reserved IP (Y|N|OCID)"):
            values_for_column[col_header].append(reserved_ip)
        elif (col_header == 'LBR Hostname(Name:Hostname)'):
            values_for_column[col_header].append(hostnames)
        elif col_header == 'Certificate Name':
            values_for_column[col_header].append(cert_name)
        elif col_header == 'CA Cert':
            values_for_column[col_header].append(ca_cert)
        elif col_header == 'Passphrase':
            values_for_column[col_header].append(passphrase)
        elif col_header == 'Private Key':
            values_for_column[col_header].append(privatekey)
        elif col_header == 'Public Cert':
            values_for_column[col_header].append(public_cert)
        elif col_header == 'Cipher Suite Name':
            values_for_column[col_header].append(cipher_name)
        elif col_header == 'Ciphers':
            values_for_column[col_header].append(cipher_suites)
        elif col_header == 'Minimum Bandwidth In Mbps (Flexible shapes only)':
            values_for_column[col_header].append(minimum_bandwidth_in_mbps)
        elif col_header == 'Maximum Bandwidth In Mbps (Flexible shapes only)':
            values_for_column[col_header].append(maximum_bandwidth_in_mbps)
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(oci_objs[0], col_header, values_for_column)
        else:
            values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def print_lbr_hostname_certs(region, ct, outdir, values_for_column_lhc, lbr, LBRs, lbr_compartment_name, export_tags, network,
                             service_dir):
    for eachlbr in LBRs.data:

        # Fetch LBR Name
        display_name = eachlbr.display_name

        # Tags filter
        defined_tags = eachlbr.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)
        # None of Tags from export_tags exist on this instance; Dont export this instance
        if check == False:
            continue

        # Filter out the LBs provisioned by oke
        eachlbr_defined_tags = eachlbr.defined_tags
        if 'Oracle-Tags' in eachlbr_defined_tags.keys():
            if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Fetch reserved IP address
        reserved_ip = ""
        if eachlbr.ip_addresses != []:
            for ips in eachlbr.ip_addresses:
                if str(ips.reserved_ip) == "null" or str(ips.reserved_ip) == "None":
                    reserved_ip = "N"
                else:
                    reserved_ip = ips.reserved_ip.id

        # Fetch Network Compartment Name
        # Fetch Compartment Name
        lbr_comp_id = eachlbr.compartment_id
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if lbr_comp_id == comp_id and lbr_comp_id not in comp_done_ids:
                lbr_compartment_name = comp_name
                comp_done_ids.append(lbr_comp_id)

        # Fetch hostname
        hostname_name_list = ''
        if (eachlbr.hostnames):
            for hostname in eachlbr.hostnames:
                hostname_info = lbr.get_hostname(eachlbr.id, hostname).data
                value = hostname_info.name + ":" + hostname_info.hostname
                hostname_name_list = hostname_name_list + ',' + value
            if (hostname_name_list != "" and hostname_name_list[0] == ','):
                hostname_name_list = hostname_name_list.lstrip(',')

        # Fetch NSGs
        nsg_detail = ""
        # if eachlbr.network_security_group_ids:
        for nsg_id in eachlbr.network_security_group_ids:
            # for nsgs in NSGs.data:
            #   id = nsgs.id
            #    if nsg_ids == id:
            #        nsg_name = nsgs.display_name + "," + nsg_name
            nsg_info = network.get_network_security_group(nsg_id).data
            nsg_name = nsg_info.display_name
            nsg_detail = nsg_name + "," + nsg_detail
        if (nsg_detail != ""):
            nsg_detail = nsg_detail[:-1]

        nsg_name = nsg_detail

        # Fetch Subnets
        subnet_name_list = ""
        if eachlbr.subnet_ids:
            for subnet_id in eachlbr.subnet_ids:
                subnet_info = network.get_subnet(subnet_id=subnet_id)
                subnet_name = subnet_info.data.display_name
                vcn_id = subnet_info.data.vcn_id
                vcn_info = network.get_vcn(vcn_id=vcn_id)
                vcn_name = vcn_info.data.display_name

                ntk_compartment_id = network.get_vcn(subnet_info.data.vcn_id).data.compartment_id  # compartment-id
                network_compartment_name = lbr_compartment_name
                for comp_name, comp_id in ct.ntk_compartment_ids.items():
                    if comp_id == ntk_compartment_id:
                        network_compartment_name = comp_name

                vs = network_compartment_name + "@" + vcn_name + "::" + subnet_name
                subnet_name_list = subnet_name_list + ',' + vs
                if (subnet_name_list != "" and subnet_name_list[0] == ','):
                    subnet_name_list = subnet_name_list.lstrip(',')
        else:
            subnet_name_list = ""

        maximum_bandwidth_in_mbps = ""
        minimum_bandwidth_in_mbps = ""
        if eachlbr.shape_details:
            maximum_bandwidth_in_mbps = eachlbr.shape_details.maximum_bandwidth_in_mbps
            minimum_bandwidth_in_mbps = eachlbr.shape_details.minimum_bandwidth_in_mbps

        # Loops for fetching Certificates and Cipher Suites
        ciphers = eachlbr.ssl_cipher_suites
        certs = eachlbr.certificates
        cert_ct = 0
        cipher_ct = 0
        no_of_certs = ''
        no_of_ciphers = ''
        cipher_list = []
        certificate_list = []

        if (not certs and not ciphers):
            oci_objs = [eachlbr]
            insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, lbr_compartment_name, display_name,
                          minimum_bandwidth_in_mbps, maximum_bandwidth_in_mbps, subnet_name_list, nsg_name, reserved_ip,
                          hostname_name_list, '', '', '', '', '', '', '')

        elif (not certs and ciphers):
            oci_objs = [eachlbr, ciphers]

            # Only Ciphers
            for ciphers, details in (eachlbr.ssl_cipher_suites).items():
                cipher_suites = ''
                suites_list = details.ciphers
                for suites in suites_list:
                    cipher_suites = cipher_suites + "," + suites
                    if (cipher_suites != "" and cipher_suites[0] == ','):
                        cipher_suites = cipher_suites.lstrip(',')
                cipher_name = ciphers

                cipher_ct = cipher_ct + 1

                if (cipher_ct == 1):
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, lbr_compartment_name,
                                  display_name, minimum_bandwidth_in_mbps, maximum_bandwidth_in_mbps, subnet_name_list,
                                  nsg_name, reserved_ip, hostname_name_list, '', '', '', '', '', cipher_name,
                                  cipher_suites)
                else:
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '', '', '', '', '', '', '',
                                  '', '', '', '', '', cipher_name, cipher_suites)

        elif (certs and not ciphers):
            oci_objs = [eachlbr, certs]

            for certificates, details in certs.items():
                # Get cert info
                cert_name, ca_cert, public_cert = print_certs(details, region, outdir, service_dir)

                cert_ct = cert_ct + 1
                if (cert_ct == 1):
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, lbr_compartment_name,
                                  display_name, minimum_bandwidth_in_mbps, maximum_bandwidth_in_mbps, subnet_name_list,
                                  nsg_name, reserved_ip, hostname_name_list, cert_name, ca_cert, '', '', public_cert,
                                  '', '')
                else:
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '', '', '', '', '', '', '',
                                  cert_name, ca_cert, '', '', public_cert, '', '')

        elif (certs and ciphers):
            oci_objs = [eachlbr, certs, ciphers]

            # Check the number of certs and ciphers; consider largest count for loop
            for certificates, cert_details in certs.items():
                certificate_list.append(certificates)
                no_of_certs = len(certificate_list)

            for cipher, cipher_details in ciphers.items():
                cipher_list.append(cipher_details.name)
                no_of_ciphers = len(cipher_list)

            # If number of ciphers are greater than that of certs; loop through ciphers
            if no_of_ciphers > no_of_certs:
                i = 0
                if i == no_of_ciphers:
                    break
                else:
                    for cipher, cipher_details in ciphers.items():
                        cipher_suites = ''
                        suites_list = cipher_details.ciphers
                        for suites in suites_list:
                            cipher_suites = cipher_suites + "," + suites
                            if (cipher_suites != "" and cipher_suites[0] == ','):
                                cipher_suites = cipher_suites.lstrip(',')
                        cipher_name = cipher_details.name
                        j = 0
                        for cert, cert_details in certs.items():
                            if i == j:
                                # Insert values of certs and cipher till they are equal
                                cert_name, ca_cert, public_cert = print_certs(cert_details, region, outdir, service_dir)

                                if i != 0:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '',
                                                  '', '', '', '', '',
                                                  '', cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                                else:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region,
                                                  lbr_compartment_name, display_name, minimum_bandwidth_in_mbps,
                                                  maximum_bandwidth_in_mbps, subnet_name_list, nsg_name, reserved_ip,
                                                  hostname_name_list, cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                            elif i >= no_of_certs and j == no_of_certs - 1:
                                # Insert additional values of cipher; as count of cipher is more
                                insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '', '', '', '',
                                              '', '', '', '', '', '', '', '', cipher_name, cipher_suites)
                            else:
                                pass
                            j = j + 1
                        i = i + 1

            # If number of certs are greater than that of ciphers; loop through certs
            if no_of_certs > no_of_ciphers:
                i = 0
                if i == no_of_certs:
                    break
                else:
                    for cert, cert_details in certs.items():
                        # Fetch Cert values
                        cert_name, ca_cert, public_cert = print_certs(cert_details, region, outdir, service_dir)
                        j = 0
                        for cipher, cipher_details in ciphers.items():
                            cipher_suites = ''
                            if i == j:
                                suites_list = cipher_details.ciphers
                                for suites in suites_list:
                                    cipher_suites = cipher_suites + "," + suites
                                    if (cipher_suites != "" and cipher_suites[0] == ','):
                                        cipher_suites = cipher_suites.lstrip(',')
                                cipher_name = cipher_details.name
                                if i != 0:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '', '',
                                                  '', '', '', '',
                                                  '', cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                                else:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region,
                                                  lbr_compartment_name, display_name, minimum_bandwidth_in_mbps,
                                                  maximum_bandwidth_in_mbps, subnet_name_list, nsg_name, reserved_ip,
                                                  hostname_name_list, cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                            elif i >= no_of_ciphers and j == no_of_ciphers - 1:
                                # Insert additional values of certs; as count of certs is more
                                insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '', '', '', '',
                                              '', '', '', cert_name, ca_cert, '', '', public_cert, '', '')
                            else:
                                pass
                            j = j + 1
                        i = i + 1

            # if both are equal, loop through one of them as main; other as secondary
            elif no_of_certs == no_of_ciphers:
                i = 0
                if i == no_of_ciphers:
                    break
                else:
                    for cipher, cipher_details in ciphers.items():
                        cipher_suites = ''
                        suites_list = cipher_details.ciphers
                        for suites in suites_list:
                            cipher_suites = cipher_suites + "," + suites
                            if (cipher_suites != "" and cipher_suites[0] == ','):
                                cipher_suites = cipher_suites.lstrip(',')
                        cipher_name = cipher_details.name
                        j = 0
                        for cert, cert_details in certs.items():
                            if i == j:
                                cert_name, ca_cert, public_cert = print_certs(cert_details, region, outdir, service_dir)
                                if i != 0:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '', '', '', '',
                                                  '', '', '', '',
                                                  '', cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                                else:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region,
                                                  lbr_compartment_name, display_name, minimum_bandwidth_in_mbps,
                                                  maximum_bandwidth_in_mbps, subnet_name_list, nsg_name, reserved_ip,
                                                  hostname_name_list, cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                            j = j + 1
                        i = i + 1
    return values_for_column_lhc


def print_backendset_backendserver(region, ct, values_for_column_bss, lbr, LBRs, lbr_compartment_name,export_tags):
    certs = CertificatesClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)

    for eachlbr in LBRs.data:

        # Tags filter
        defined_tags = eachlbr.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)
        # None of Tags from export_tags exist on this instance; Dont export this instance
        if check == False:
            continue

        # Filter out the LBs provisioned by oke
        eachlbr_defined_tags = eachlbr.defined_tags
        if 'Oracle-Tags' in eachlbr_defined_tags.keys():
            if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Loop through Backend Sets

        # Fetch Compartment Name
        lbr_comp_id = eachlbr.compartment_id
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if lbr_comp_id == comp_id and lbr_comp_id not in comp_done_ids:
                lbr_compartment_name = comp_name
                comp_done_ids.append(lbr_comp_id)

        for backendsets in eachlbr.__getattribute__('backend_sets'):
            backend_list = ""
            backup_list = ""
            backendset_details = lbr.get_backend_set(eachlbr.__getattribute__('id'), backendsets).data
            certificate_list = ''
            hc = ''
            # Process the Backend Server and Backup server details
            for backends in backendset_details.__getattribute__('backends'):
                if str(backends.__getattribute__('name')).lower() != "none":
                    backend_value = str(backends.__getattribute__('name'))
                    backend_list = backend_list + "," +  backend_value
                if (backend_list != "" and backend_list[0] == ','):
                    backend_list = backend_list.lstrip(',')

                if str(backends.__getattribute__('backup')).lower() == 'true':
                    backup_value = backends.ip_address
                    backup_list = backup_list + ',' + backup_value
                if (backup_list != "" and backup_list[0] == ','):
                    backup_list = backup_list.lstrip(',')
            # Process columns related to Session Cookies
            lb_cookie_session_persistence_configuration = backendset_details.__getattribute__(
                'lb_cookie_session_persistence_configuration')
            session_persistence_configuration = backendset_details.__getattribute__('session_persistence_configuration')

            if str(lb_cookie_session_persistence_configuration).lower() != 'none':
                lb_session = 'LB'
                values_for_column_bss['Cookie Session(n|LB|Backend Server)'].append(lb_session)
                values_for_column_bss = cookie_headers(values_for_column_bss,
                                                       lb_cookie_session_persistence_configuration, sheet_dict_bss)

            elif str(session_persistence_configuration).lower() != 'none':
                lb_session = 'Backend Server'
                values_for_column_bss['Cookie Session(n|LB|Backend Server)'].append(lb_session)
                values_for_column_bss = cookie_headers(values_for_column_bss, session_persistence_configuration,
                                                       sheet_dict_bss)

            else:
                lb_session = 'n'
                values_for_column_bss['Cookie Session(n|LB|Backend Server)'].append(lb_session)
                values_for_column_bss['Cookie Name'].append("")
                values_for_column_bss['Cookie Path'].append("")
                values_for_column_bss['Disable Fallback(TRUE|FALSE)'].append("")

            # Get Health Checker
            hc = lbr.get_health_checker(eachlbr.__getattribute__('id'), backendsets).data

            for col_headers in values_for_column_bss:
                headers_lower = commonTools.check_column_headers(col_headers)

                # Process Columns that are common across LBR sheets - Region, Compartment Name and LBR Name
                if col_headers in sheet_dict_common.keys():
                    values_for_column_bss = common_headers(region, col_headers, values_for_column_bss, eachlbr,
                                                           sheet_dict_common, lbr_compartment_name)

                # Process the Tag  Columns
                elif headers_lower in commonTools.tagColumns:
                    values_for_column_bss = commonTools.export_tags(eachlbr, col_headers, values_for_column_bss)

                elif col_headers == 'SSL Protocols':
                    protocols_list = ''
                    certificate_list = backendset_details.ssl_configuration
                    if str(certificate_list).lower() == 'none':
                        values_for_column_bss[col_headers].append("")
                    else:
                        for protocols in certificate_list.protocols:
                            protocols_list = protocols_list + "," + protocols
                        if (protocols_list != "" and protocols_list[0] == ','):
                            protocols_list = protocols_list.lstrip(',')
                        values_for_column_bss[col_headers].append(protocols_list)

                # Process the Backend Set and Backend Server  Columns
                elif col_headers in sheet_dict_bss.keys():
                    if col_headers == "Backend Policy(LEAST_CONNECTIONS|ROUND_ROBIN|IP_HASH)":
                        policy = backendset_details.__getattribute__(sheet_dict_bss[col_headers])
                        values_for_column_bss['Backend Policy(LEAST_CONNECTIONS|ROUND_ROBIN|IP_HASH)'].append(
                            str(policy))

                    elif 'Backend HealthCheck' in col_headers:
                        values_for_column_bss[col_headers].append(hc.__getattribute__(sheet_dict_bss[col_headers]))

                    elif col_headers == "Backend ServerComp@ServerName:Port":
                        values_for_column_bss[col_headers].append(backend_list)

                    elif col_headers == "Backend Set Name":
                        values_for_column_bss[col_headers].append(backendsets)

                    elif col_headers == "Certificate Name or OCID":
                        if str(backendset_details.ssl_configuration).lower() != "none":
                            certificate_list = backendset_details.ssl_configuration
                            if certificate_list.certificate_ids != []:
                                certificates = ""
                                for certificate_ids in certificate_list.certificate_ids:
                                    certificates = certificates + "," + certificate_ids
                                values_for_column_bss[col_headers].append(
                                    str(certificate_list.certificate_ids).lstrip(","))
                            elif certificate_list.certificate_name != "" and str(
                                    certificate_list.certificate_name).lower() != "none":
                                values_for_column_bss[col_headers].append(certificate_list.certificate_name)
                            else:
                                values_for_column_bss[col_headers].append("")
                        else:
                            values_for_column_bss[col_headers].append("")


                    elif col_headers == "Trusted Certificate Authority IDs":
                        ca_cert_list = ""
                        if certificate_list.trusted_certificate_authority_ids != []:
                            for certs in certificate_list.trusted_certificate_authority_ids:
                                ca_cert_list = ca_cert_list + "," + certs
                            values_for_column_bss[col_headers].append(ca_cert_list.lstrip(','))
                        else:
                            values_for_column_bss[col_headers].append("")

                    elif col_headers == 'Backup <Backend Server Name>':
                        values_for_column_bss[col_headers].append(backup_list)

                    elif col_headers == 'UseSSL(y|n)':
                        value = 'y'
                        if str(backendset_details.__getattribute__('ssl_configuration')).lower() == 'none':
                            value = 'n'
                        values_for_column_bss[col_headers].append(value)

                    elif "Cookie" in col_headers or "Fallback" in col_headers:
                        continue

                    else:
                        oci_objs = [backendset_details, eachlbr, hc, certificate_list]
                        values_for_column_bss = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_bss,
                                                                                 values_for_column_bss)
                else:

                    if "Cookie" not in col_headers:
                        # Process the remaining  Columns
                        oci_objs = [backendset_details, eachlbr, hc, certificate_list]
                        values_for_column_bss = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_bss,
                                                                                 values_for_column_bss)

    return values_for_column_bss


def print_listener(region, ct, values_for_column_lis, LBRs, lbr_compartment_name,export_tags):
    for eachlbr in LBRs.data:
        sslcerts = None

        # Tags filter
        defined_tags = eachlbr.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)
        # None of Tags from export_tags exist on this instance; Dont export this instance
        if check == False:
            continue

        # Filter out the LBs provisioned by oke
        eachlbr_defined_tags = eachlbr.defined_tags
        if 'Oracle-Tags' in eachlbr_defined_tags.keys():
            if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Fetch Compartment Name
        lbr_comp_id = eachlbr.compartment_id
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if lbr_comp_id == comp_id and lbr_comp_id not in comp_done_ids:
                lbr_compartment_name = comp_name
                comp_done_ids.append(lbr_comp_id)

        # Loop through listeners
        for listeners, values in eachlbr.__getattribute__('listeners').items():
            for col_headers in values_for_column_lis.keys():
                headers_lower = commonTools.check_column_headers(col_headers)

                # If value of Certificate Name is needed, check in ssl_configuration attribute
                if col_headers == 'Certificate Name or OCID':
                    sslcerts = values.__getattribute__(sheet_dict_lis['UseSSL (y|n)'])
                    if str(sslcerts).lower() != "none":
                        if sslcerts.__getattribute__('certificate_name') != "" and str(
                                sslcerts.__getattribute__('certificate_name')).lower() != "none":
                            values_for_column_lis[col_headers].append(sslcerts.__getattribute__('certificate_name'))
                        elif sslcerts.certificate_ids != []:
                            certificates = ""
                            for certificate_ids in sslcerts.certificate_ids:
                                certificates = certificates + "," + certificate_ids
                            values_for_column_lis[col_headers].append(certificates.lstrip(","))
                        else:
                            values_for_column_lis[col_headers].append("")
                    else:
                        values_for_column_lis[col_headers].append("")

                elif col_headers == "Trusted Certificate Authority IDs":
                    ca_cert_list = ""
                    if str(sslcerts).lower() != "none":
                        if sslcerts.trusted_certificate_authority_ids != []:
                            for certs in sslcerts.trusted_certificate_authority_ids:
                                ca_cert_list = ca_cert_list + "," + certs
                            values_for_column_lis[col_headers].append(ca_cert_list.lstrip(','))
                        else:
                            values_for_column_lis[col_headers].append("")
                    else:
                        values_for_column_lis[col_headers].append("")

                elif col_headers == 'SSL Protocols':
                    protocols_list = ''
                    if str(sslcerts).lower() == 'none':
                        values_for_column_lis[col_headers].append("")
                    else:
                        for protocols in sslcerts.protocols:
                            protocols_list = protocols_list + "," + protocols
                        if (protocols_list != "" and protocols_list[0] == ','):
                            protocols_list = protocols_list.lstrip(',')
                        values_for_column_lis[col_headers].append(protocols_list)

                # Process Columns that are common across LBR sheets - Region, Compartment Name and LBR Name
                elif col_headers in sheet_dict_common.keys():
                    values_for_column_lis = common_headers(region, col_headers, values_for_column_lis, eachlbr,
                                                           sheet_dict_common, lbr_compartment_name)

                # Process the Tag Columns
                elif headers_lower in commonTools.tagColumns:
                    values_for_column_lis = commonTools.export_tags(eachlbr, col_headers, values_for_column_lis)

                # Process the Listerner Columns
                elif col_headers in sheet_dict_lis.keys():
                    if col_headers == 'Rule Set Names':
                        rule_str = ""
                        if values.__getattribute__(sheet_dict_lis[col_headers]) != []:
                            for rule in values.__getattribute__(sheet_dict_lis[col_headers]):
                                rule_str = rule_str + "," + rule
                            if (rule_str != "" and rule_str[0] == ','):
                                rule_str = rule_str.lstrip(',')
                        values_for_column_lis[col_headers].append(rule_str)

                    elif col_headers == 'UseSSL (y|n)':
                        if str(values.__getattribute__(sheet_dict_lis[col_headers])).lower() != "none":
                            values_for_column_lis[col_headers].append("y")
                        else:
                            values_for_column_lis[col_headers].append("n")

                    elif col_headers == "LBR Hostnames (Name)":
                        hostnames = ""
                        if values.__getattribute__(sheet_dict_lis[col_headers]):
                            for eachhostname in values.__getattribute__(sheet_dict_lis[col_headers]):
                                hostnames = hostnames + "," + eachhostname
                            if (hostnames != "" and hostnames[0] == ','):
                                hostnames = hostnames.lstrip(',')
                        values_for_column_lis[col_headers].append(hostnames)

                    elif col_headers == 'Idle Time Out (in Seconds)':
                        connection_config = values.__getattribute__('connection_configuration')
                        values_for_column_lis[col_headers].append(
                            connection_config.__getattribute__(sheet_dict_lis[col_headers]))

                    else:
                        oci_objs = [values, eachlbr, sslcerts]
                        values_for_column_lis = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_lis,
                                                                                 values_for_column_lis)

                else:
                    oci_objs = [eachlbr, values, sslcerts]
                    values_for_column_lis = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_lis,
                                                                             values_for_column_lis)

    return values_for_column_lis


def print_rule(region, ct, values_for_column_rule, LBRs, lbr_compartment_name,export_tags):
    for eachlbr in LBRs.data:

        # Tags filter
        defined_tags = eachlbr.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)
        # None of Tags from export_tags exist on this instance; Dont export this instance
        if check == False:
            continue

        # Filter out the LBs provisioned by oke
        eachlbr_defined_tags = eachlbr.defined_tags
        if 'Oracle-Tags' in eachlbr_defined_tags.keys():
            if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Fetch Compartment Name
        lbr_comp_id = eachlbr.compartment_id
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if lbr_comp_id == comp_id and lbr_comp_id not in comp_done_ids:
                lbr_compartment_name = comp_name
                comp_done_ids.append(lbr_comp_id)

        for rulesets, values in eachlbr.__getattribute__('rule_sets').items():
            for eachitem in values.items:
                for col_headers in values_for_column_rule.keys():
                    headers_lower = commonTools.check_column_headers(col_headers)

                    if col_headers in sheet_dict_common.keys():
                        values_for_column_rule = common_headers(region, col_headers, values_for_column_rule, eachlbr,
                                                                sheet_dict_common, lbr_compartment_name)

                    elif col_headers == 'Rule Set Name':
                        values_for_column_rule[col_headers].append(rulesets)

                    elif col_headers in sheet_dict_rule.keys():
                        try:
                            if 'Redirect' in col_headers:
                                uri_details = eachitem.redirect_uri
                                if str(uri_details.port).lower() == 'none':
                                    uri_details.port = ''
                                if str(uri_details.host).lower() == 'none':
                                    uri_details.host = ''
                                if str(uri_details.path).lower() == 'none':
                                    uri_details.path = ''
                                if str(uri_details.protocol).lower() == 'none':
                                    uri_details.protocol = ''
                                if str(uri_details.query).lower() == 'none':
                                    uri_details.query = ''

                                if 'Host:Port' in col_headers:
                                    value = uri_details.host + ":" + str(uri_details.port)
                                    values_for_column_rule[col_headers].append(value)

                                if 'Protocol:Path' in col_headers:
                                    value = uri_details.protocol + ":" + uri_details.path
                                    values_for_column_rule[col_headers].append(value)

                                if 'Query' in col_headers:
                                    values_for_column_rule[col_headers].append(uri_details.query)

                            else:
                                value = str(eachitem.__getattribute__(sheet_dict_rule[col_headers]))
                                if value.lower() == 'none':
                                    value = ""
                                values_for_column_rule[col_headers].append(value)

                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")
                            pass

                    elif col_headers == 'Allowed Methods':
                        allowed_method = ''
                        if eachitem.action == "CONTROL_ACCESS_USING_HTTP_METHODS":
                            for method in eachitem.__getattribute__(headers_lower):
                                allowed_method = allowed_method + ",\"" + method + "\""

                            if (allowed_method != "" and allowed_method[0] == ','):
                                allowed_method = allowed_method.lstrip(',')

                        values_for_column_rule[col_headers].append(allowed_method)

                    elif 'Attribute' in col_headers:
                        try:
                            for attributes in eachitem.conditions:
                                values_for_column_rule[col_headers].append(attributes.__getattribute__(headers_lower))
                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")

                    elif 'Operator' in col_headers:
                        try:
                            for attributes in eachitem.conditions:
                                values_for_column_rule[col_headers].append(attributes.__getattribute__(headers_lower))
                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")

                    elif col_headers == "Suffix or Prefix (suffix:<value>|prefix:<value>)":
                        combined_suffix = ''
                        combined_prefix = ''
                        try:
                            suffix_val = eachitem.suffix
                            if suffix_val != "" and suffix_val != 'nan' and suffix_val != None:
                                combined_suffix = "suffix:" + suffix_val
                            prefix_val = eachitem.prefix
                            if prefix_val != "" and prefix_val != 'nan' and prefix_val != None:
                                combined_prefix = "prefix:" + prefix_val
                            combination = combined_suffix + "," + combined_prefix
                            values_for_column_rule[col_headers].append(combination)
                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")
                            pass
                    else:
                        oci_objs = [eachlbr, eachitem]
                        values_for_column_rule = commonTools.export_extra_columns(oci_objs, col_headers,
                                                                                  sheet_dict_rule,
                                                                                  values_for_column_rule)

    return values_for_column_rule


def print_prs(region, ct, values_for_column_prs, LBRs, lbr_compartment_name,export_tags):
    for eachlbr in LBRs.data:

        # Tags filter
        defined_tags = eachlbr.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)
        # None of Tags from export_tags exist on this instance; Dont export this instance
        if check == False:
            continue

        # Filter out the LBs provisioned by oke
        eachlbr_defined_tags = eachlbr.defined_tags
        if 'Oracle-Tags' in eachlbr_defined_tags.keys():
            if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Fetch Compartment Name
        lbr_comp_id = eachlbr.compartment_id
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if lbr_comp_id == comp_id and lbr_comp_id not in comp_done_ids:
                lbr_compartment_name = comp_name
                comp_done_ids.append(lbr_comp_id)
        for prs, values in eachlbr.__getattribute__('path_route_sets').items():
            for path_routes in values.__getattribute__('path_routes'):
                for col_headers in values_for_column_prs.keys():
                    headers_lower = commonTools.check_column_headers(col_headers)

                    if col_headers in sheet_dict_common.keys():
                        values_for_column_prs = common_headers(region, col_headers, values_for_column_prs, eachlbr,
                                                               sheet_dict_common, lbr_compartment_name)
                    elif col_headers == 'Match Type':
                        try:
                            key = path_routes.__getattribute__('path_match_type')
                            match_type = key.match_type
                            values_for_column_prs[col_headers].append(match_type)
                        except AttributeError as e:
                            values_for_column_prs[col_headers].append("")

                    elif col_headers in sheet_dict_prs.keys():
                        values_for_column_prs[col_headers].append(values.__getattribute__(sheet_dict_prs[col_headers]))

                    else:
                        # Process the remaining  Columns
                        oci_objs = [eachlbr, values, path_routes]
                        values_for_column_prs = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_prs,
                                                                                 values_for_column_prs)

    return values_for_column_prs


def print_routing_policies(region, ct, values_for_column_rp, LBRs, lbr_compartment_name,export_tags):
    for eachlbr in LBRs.data:

        # Tags filter
        defined_tags = eachlbr.defined_tags
        tags_list = []
        for tkey, tval in defined_tags.items():
            for kk, vv in tval.items():
                tag = tkey + "." + kk + "=" + vv
                tags_list.append(tag)

        if export_tags == []:
            check = True
        else:
            check = any(e in tags_list for e in export_tags)
        # None of Tags from export_tags exist on this instance; Dont export this instance
        if check == False:
            continue

        # Filter out the LBs provisioned by OKE
        eachlbr_defined_tags = eachlbr.defined_tags
        if 'Oracle-Tags' in eachlbr_defined_tags.keys():
            if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                if 'ocid1.cluster' in created_by:
                    continue

        # Retrieve the routing policies for the load balancer
        routing_policies = eachlbr.routing_policies

        # Fetch the compartment name
        lbr_comp_id = eachlbr.compartment_id
        comp_done_ids = []
        for comp_name, comp_id in ct.ntk_compartment_ids.items():
            if lbr_comp_id == comp_id and lbr_comp_id not in comp_done_ids:
                lbr_compartment_name = comp_name
                comp_done_ids.append(lbr_comp_id)

        # Retrieve the values for the routing policies
        for rp, values in eachlbr.__getattribute__('routing_policies').items():
            for col_headers in values_for_column_rp.keys():
                headers_lower = commonTools.check_column_headers(col_headers)

                if col_headers in sheet_dict_common.keys():
                    values_for_column_rp = common_headers(region, col_headers, values_for_column_rp, eachlbr,
                                                          sheet_dict_common, lbr_compartment_name)
                elif col_headers == 'LBR Name':
                    values_for_column_rp[col_headers].append(eachlbr.display_name)

                elif col_headers == 'Routing Policy Name':
                    values_for_column_rp[col_headers].append(values.__getattribute__('name'))

                elif col_headers == "Rules":
                    rules = []
                    for rule in values.rules:
                        if hasattr(rule, 'actions') and rule.actions and hasattr(rule.actions[0], 'backend_set_name'):
                            backend_set_name = rule.actions[0].backend_set_name
                        else:
                            backend_set_name = None

                        name = rule.name.strip("\n")
                        condition = rule.condition.strip("\n")
                        backend_set_name = backend_set_name.strip("\n")
                        rule_str = f"{name}::{condition}::{backend_set_name}"
                        rules.append(rule_str)
                    rules_string = "\n".join(rules)
                    values_for_column_rp[col_headers].append(rules_string)

                elif col_headers in sheet_dict_rp.keys():
                    values_for_column_rp[col_headers].append(
                        values.__getattribute__(sheet_dict_rp[col_headers]))

                else:
                    # Process the remaining  Columns
                    oci_objs = [eachlbr, values]
                    values_for_column_rp = commonTools.export_extra_columns(oci_objs, col_headers,
                                                                            sheet_dict_rp,
                                                                                    values_for_column_rp)

    return values_for_column_rp


# Execution of the code begins here
def export_lbr(inputfile, outdir, service_dir, config1, signer1, ct, export_compartments, export_regions,export_tags):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global values_for_column_lhc
    global values_for_column_bss
    global values_for_column_lis
    global values_for_column_rule
    global values_for_column_prs
    global values_for_column_rp
    global sheet_dict_common
    global sheet_dict_lhc
    global sheet_dict_bss
    global sheet_dict_lis
    global sheet_dict_rule
    global sheet_dict_prs
    global sheet_dict_rp
    global listener_to_cd3
    global config, signer,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    signer = signer1
    config = config1

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    # Read CD3
    df, values_for_column_lhc = commonTools.read_cd3(cd3file, "LB-Hostname-Certs")
    df, values_for_column_bss = commonTools.read_cd3(cd3file, "LB-BackendSet-BackendServer")
    df, values_for_column_lis = commonTools.read_cd3(cd3file, "LB-Listener")
    df, values_for_column_rule = commonTools.read_cd3(cd3file, "LB-RuleSet")
    df, values_for_column_prs = commonTools.read_cd3(cd3file, "LB-PathRouteSet")
    df, values_for_column_rp = commonTools.read_cd3(cd3file, "LB-RoutingPolicy")

    # Get dict for columns from Excel_Columns
    sheet_dict_common = ct.sheet_dict["Common-LBR-Headers"]
    sheet_dict_lhc = ct.sheet_dict["LB-Hostname-Certs"]
    sheet_dict_bss = ct.sheet_dict["LB-BackendSet-BackendServer"]
    sheet_dict_lis = ct.sheet_dict["LB-Listener"]
    sheet_dict_rule = ct.sheet_dict["LB-RuleSet"]
    sheet_dict_prs = ct.sheet_dict["LB-PathRouteSet"]
    sheet_dict_rp = ct.sheet_dict["LB-RoutingPolicy"]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- LB-Hostname-Certs, LB-BackendSet-BackendServer, LB-Listener, LB-RuleSet, LB-PathRouteSet, LB-RoutingPolicy will be overwritten during export process!!!\n")

    # Fetch LBR Details
    print("\nFetching details of Load Balancer...")

    # Create backups
    file_name = 'import_commands_lbr.sh'
    resource = 'import_lbr'
    total_resources=0

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name

        if os.path.exists(script_file):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, file_name)

        importCommands[reg] = ''

        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        lbr = LoadBalancerClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        network = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                signer=signer)
        region = reg.capitalize()

        for compartment_name in export_compartments:
            LBRs = oci.pagination.list_call_get_all_results(lbr.list_load_balancers,
                                                            compartment_id=ct.ntk_compartment_ids[compartment_name],
                                                            lifecycle_state="ACTIVE")
            values_for_column_lhc = print_lbr_hostname_certs(region, ct, outdir, values_for_column_lhc, lbr, LBRs,
                                                             compartment_name, export_tags, network, service_dir)
            values_for_column_lis = print_listener(region, ct, values_for_column_lis, LBRs, compartment_name,export_tags)
            values_for_column_bss = print_backendset_backendserver(region, ct, values_for_column_bss, lbr, LBRs,
                                                                   compartment_name,export_tags)
            values_for_column_rule = print_rule(region, ct, values_for_column_rule, LBRs, compartment_name,export_tags)
            values_for_column_prs = print_prs(region, ct, values_for_column_prs, LBRs, compartment_name,export_tags)
            values_for_column_rp = print_routing_policies(region, ct, values_for_column_rp, LBRs, compartment_name,export_tags)


            for eachlbr in LBRs.data:
                # Tags filter
                defined_tags = eachlbr.defined_tags
                tags_list = []
                for tkey, tval in defined_tags.items():
                    for kk, vv in tval.items():
                        tag = tkey + "." + kk + "=" + vv
                        tags_list.append(tag)

                if export_tags == []:
                    check = True
                else:
                    check = any(e in tags_list for e in export_tags)
                # None of Tags from export_tags exist on this instance; Dont export this instance
                if check == False:
                    continue

                total_resources += 1

                # Filter out the LBs provisioned by oke
                eachlbr_defined_tags = eachlbr.defined_tags
                if 'Oracle-Tags' in eachlbr_defined_tags.keys():
                    if 'CreatedBy' in eachlbr_defined_tags['Oracle-Tags'].keys():
                        created_by = eachlbr_defined_tags['Oracle-Tags']['CreatedBy']
                        if 'ocid1.cluster' in created_by:
                            continue


                lbr_info = eachlbr
                lbr_display_name = lbr_info.display_name
                tf_name = commonTools.check_tf_variable(lbr_display_name)
                tf_resource = f'module.load-balancers[\\"{tf_name}\\"].oci_load_balancer_load_balancer.load_balancer'
                if tf_resource not in state["resources"]:
                    importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {lbr_info.id}'

                for certificates in eachlbr.certificates:
                    cert_tf_name = commonTools.check_tf_variable(certificates)
                    tf_resource = f'module.certificates[\\"{tf_name}_{cert_tf_name}_cert\\"].oci_load_balancer_certificate.certificate'
                    if tf_resource not in state["resources"]:
                        importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/certificates/{certificates}'

                for hostnames in eachlbr.hostnames:
                    hostname_tf_name = commonTools.check_tf_variable(hostnames)
                    tf_resource = f'module.hostnames[\\"{tf_name}_{hostname_tf_name}_hostname\\"].oci_load_balancer_hostname.hostname'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/hostnames/{hostnames}'

                for listeners in eachlbr.listeners:
                    listener_tf_name = commonTools.check_tf_variable(listeners)
                    tf_resource = f'module.listeners[\\"{tf_name}_{listener_tf_name}\\"].oci_load_balancer_listener.listener'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/listeners/{listeners}'

                for backendsets, values in eachlbr.backend_sets.items():
                    backendsets_tf_name = commonTools.check_tf_variable(backendsets)
                    tf_resource = f'module.backend-sets[\\"{tf_name}_{backendsets_tf_name}\\"].oci_load_balancer_backend_set.backend_set'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/backendSets/{backendsets}'

                    cnt = 0
                    for keys in values.backends:
                        cnt = cnt + 1
                        backendservers_name = keys.name
                        backendservers_tf_name = commonTools.check_tf_variable(keys.ip_address + "-" + str(keys.port))
                        tf_resource = f'module.backends[\\"{tf_name}_{backendsets_tf_name}_{backendservers_tf_name}\\"].oci_load_balancer_backend.backend'
                        if tf_resource not in state["resources"]:
                            importCommands[
                                reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/backendSets/{backendsets}/backends/{backendservers_name}'

                for pathroutes in eachlbr.path_route_sets:
                    pathroutes_tf_name = commonTools.check_tf_variable(pathroutes)
                    tf_resource = f'module.path-route-sets[\\"{tf_name}_{pathroutes_tf_name}\\"].oci_load_balancer_path_route_set.path_route_set'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/pathRouteSets/{pathroutes}'

                for routing_policy in eachlbr.routing_policies:
                    routing_policy_tf_name = commonTools.check_tf_variable(routing_policy)
                    tf_resource = f'module.routing-policies[\\"{tf_name}_{routing_policy_tf_name}\\"].oci_load_balancer_load_balancer_routing_policy.load_balancer_routing_policy'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/routingPolicies/{routing_policy}'

                for routerules in eachlbr.rule_sets:
                    routerules_tf_name = commonTools.check_tf_variable(routerules)
                    tf_resource = f'module.rule-sets[\\"{tf_name}_{routerules_tf_name}\\"].oci_load_balancer_rule_set.rule_set'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/ruleSets/{routerules}'

                for ciphers in eachlbr.ssl_cipher_suites:
                    ciphers_tf_name = commonTools.check_tf_variable(ciphers)
                    tf_resource = f'module.cipher-suites[\\"{tf_name}_{ciphers_tf_name}\\"].oci_load_balancer_ssl_cipher_suite.ssl_cipher_suite'
                    if tf_resource not in state["resources"]:
                        importCommands[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" loadBalancers/{lbr_info.id}/sslCipherSuites/{ciphers}'

    commonTools.write_to_cd3(values_for_column_lhc, cd3file, "LB-Hostname-Certs")
    commonTools.write_to_cd3(values_for_column_bss, cd3file, "LB-BackendSet-BackendServer")
    commonTools.write_to_cd3(values_for_column_lis, cd3file, "LB-Listener")
    commonTools.write_to_cd3(values_for_column_rule, cd3file, "LB-RuleSet")
    commonTools.write_to_cd3(values_for_column_prs, cd3file, "LB-PathRouteSet")
    commonTools.write_to_cd3(values_for_column_rp, cd3file, "LB-RoutingPolicy")

    print("{0} LBRs exported into CD3.\n".format(total_resources))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if importCommands[reg] != "":
            init_commands = f'\n######### Writing import for Load Balancer Objects #########\n\n#!/bin/bash\n{tf_or_tofu} init'
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])

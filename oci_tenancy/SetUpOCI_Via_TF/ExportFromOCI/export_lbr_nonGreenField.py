#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export LBR Components
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import argparse
import sys
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.load_balancer.load_balancer_client import LoadBalancerClient
import os
sys.path.append(os.getcwd()+"/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}

def cookie_headers(values_for_column, session_persistence, excel_header_map):
    for headers in values_for_column:
        if headers == 'Cookie Name':
            if (session_persistence.__getattribute__(commonTools.check_column_headers(headers))):
                values_for_column[headers].append(str(session_persistence.__getattribute__(commonTools.check_column_headers(headers))))
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

def common_headers(region, headers, values_for_column, eachlbr, excel_header_map, ntk_compartment_name):
    if headers == 'Region':
        values_for_column[headers].append(str(region))
    elif headers == 'Compartment Name':
        values_for_column[headers].append(str(ntk_compartment_name))
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

def print_certs(obj, reg, outdir):

    cname = ""
    pname = ""

    ca_certificate = obj.ca_certificate
    public_certificate = obj.public_certificate

    #print(obj.certificate_name, outdir, reg)

    if str(ca_certificate).lower() != "none":
        cname = outdir + "/" + reg + str(obj.certificate_name) + "-ca-certificate.cert"
        ca_cert = open(cname, "w")
        ca_cert.write(ca_certificate)
        ca_cert.close()

    if str(public_certificate).lower() != "none":
        pname = outdir + "/" + reg + str(obj.certificate_name) + "-public_certificate.cert"
        public_cert = open(pname, "w")
        public_cert.write(public_certificate)
        public_cert.close()

    cert_name = obj.certificate_name
    ca_cert = str(cname).replace("\\", "\\\\")
    public_cert = str(pname).replace("\\", "\\\\")

    return cert_name, ca_cert, public_cert


def insert_values(values_for_column, oci_objs, sheet_dict, region, comp_name, display_name,subnets, nsgs, hostnames, cert_name, ca_cert,
                  passphrase, privatekey, public_cert, cipher_name, cipher_suites):

    for col_header in values_for_column.keys():
            if col_header == 'Region':
                values_for_column[col_header].append(str(region))
            elif col_header == 'Compartment Name':
                values_for_column[col_header].append(comp_name)
            elif col_header == 'LBR Name':
                values_for_column[col_header].append(display_name)
            elif col_header == "LBR Subnets":
                values_for_column[col_header].append(subnets)
            elif (col_header == "NSGs"):
                values_for_column[col_header].append(nsgs)
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
            elif col_header.lower() in commonTools.tagColumns:
                values_for_column = commonTools.export_tags(oci_objs[0], col_header, values_for_column)
            else:
                values_for_column = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict, values_for_column)


def print_lbr_hostname_certs(region, values_for_column_lhc, lbr, VCNs, LBRs, ntk_compartment_name, SUBNETs, NSGs):

    for eachlbr in LBRs.data:

        #Fetch LBR Name
        display_name = eachlbr.display_name

        #Fetch hostname
        hostname_name_list = ''
        if(eachlbr.hostnames):
            for hostname in eachlbr.hostnames:
                hostname_info = lbr.get_hostname(eachlbr.id, hostname).data
                value = hostname_info.name + ":" + hostname_info.hostname
                hostname_name_list = value + "," + hostname_name_list
            if (hostname_name_list != "" and hostname_name_list[-1] == ','):
                hostname_name_list = hostname_name_list[:-1]

        # Fetch NSGs
        nsg_name = ""
        if eachlbr.network_security_group_ids:
            for nsg_ids in eachlbr.network_security_group_ids:
                nsg_name = ''
                for nsgs in NSGs.data:
                    id = nsgs.id
                    if nsg_ids == id:
                        nsg_name = nsgs.display_name
        else:
            nsg_name = ""

        # Fetch Subnets
        subnet_name_list = ""
        if eachlbr.subnet_ids:
            for subnet_ids in eachlbr.subnet_ids:
                subnet_name_list = ''
                for subnets in SUBNETs.data:
                    id = subnets.__getattribute__('id')
                    if subnet_ids == id:
                        subnet_name = subnets.display_name
                        for eachvcn in VCNs.data:
                            if eachvcn.id == subnets.vcn_id:
                                vcn_name = eachvcn.display_name
                                value = vcn_name + "_" + subnet_name
                                subnet_name_list = value + subnet_name_list
        else:
            subnet_name_list = ""

        #Loops for fetching Certificates and Cipher Suites
        ciphers = eachlbr.ssl_cipher_suites
        certs = eachlbr.certificates
        cert_ct = 0
        cipher_ct = 0
        no_of_certs = ''
        no_of_ciphers = ''
        cipher_list =[]
        certificate_list = []

        if (not certs and not ciphers):
            oci_objs = [eachlbr]
            insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, ntk_compartment_name,display_name,subnet_name_list, nsg_name, hostname_name_list, '', '', '', '', '','','')

        elif (not certs and ciphers):
            oci_objs = [eachlbr, ciphers]

            # Only Ciphers
            for ciphers, details in (eachlbr.ssl_cipher_suites).items():
                cipher_suites = ''
                suites_list = details.ciphers
                for suites in suites_list:
                    cipher_suites = suites + "," + cipher_suites
                    if (cipher_suites != "" and cipher_suites[-1] == ','):
                        cipher_suites = cipher_suites[:-1]
                cipher_name = ciphers

                cipher_ct = cipher_ct + 1

                if (cipher_ct == 1):
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, ntk_compartment_name, display_name,subnet_name_list, nsg_name,hostname_name_list, '','','','','',cipher_name,cipher_suites)
                else:
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc,'','','','','','','','','','','', cipher_name,cipher_suites)

        elif (certs and not ciphers):
            oci_objs = [eachlbr, certs]

            for certificates, details in certs.items():
                # Get cert info
                cert_name,ca_cert,public_cert = print_certs(details,region,outdir)

                cert_ct = cert_ct + 1
                if (cert_ct == 1):
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, ntk_compartment_name,display_name, subnet_name_list, nsg_name,hostname_name_list, cert_name,ca_cert,'','',public_cert, '','')
                else:
                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc,'','','','','','', cert_name,ca_cert,'','',public_cert, '','')

        elif (certs and ciphers):
            oci_objs = [eachlbr, certs, ciphers]

            #Check the number of certs and ciphers; consider largest count for loop
            for certificates,cert_details in certs.items():
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
                            cipher_suites = suites + "," + cipher_suites
                            if (cipher_suites != "" and cipher_suites[-1] == ','):
                                cipher_suites = cipher_suites[:-1]
                        cipher_name = cipher_details.name
                        j = 0
                        for cert, cert_details in certs.items():
                            if i == j:
                                #Insert values of certs and cipher till they are equal
                                cert_name, ca_cert, public_cert = print_certs(cert_details, region, outdir)

                                if i != 0:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '',
                                                  '', '', '', '',
                                                  '', cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                                else:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, ntk_compartment_name, display_name, subnet_name_list, nsg_name, hostname_name_list, cert_name, ca_cert, '', '', public_cert, cipher_name, cipher_suites)
                            elif i >= no_of_certs and j == no_of_certs - 1:
                                #Insert additional values of cipher; as count of cipher is more
                                insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '','','', '', '', '','', '', '', '', '', cipher_name, cipher_suites)
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
                        cert_name, ca_cert, public_cert = print_certs(cert_details, region, outdir)
                        j = 0
                        for cipher, cipher_details in ciphers.items():
                            cipher_suites = ''
                            if i == j:
                                suites_list = cipher_details.ciphers
                                for suites in suites_list:
                                    cipher_suites = suites + "," + cipher_suites
                                    if (cipher_suites != "" and cipher_suites[-1] == ','):
                                        cipher_suites = cipher_suites[:-1]
                                cipher_name = cipher_details.name
                                if i != 0:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '',
                                                  '', '', '', '',
                                                  '', cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                                else:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, ntk_compartment_name, display_name,subnet_name_list, nsg_name, hostname_name_list, cert_name, ca_cert, '', '', public_cert, cipher_name, cipher_suites)
                            elif i >= no_of_ciphers and j == no_of_ciphers - 1:
                                #Insert additional values of certs; as count of certs is more
                                insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '','', '','', '', '',cert_name, ca_cert, '', '', public_cert, '', '')
                            else:
                                pass
                            j = j + 1
                        i = i + 1

            # if both are equal, loop through one of them as main; other as secondary
            elif no_of_certs == no_of_ciphers:
                i=0
                if i == no_of_ciphers:
                    break
                else:
                    for cipher, cipher_details in ciphers.items():
                        cipher_suites = ''
                        suites_list = cipher_details.ciphers
                        for suites in suites_list:
                            cipher_suites = suites + "," + cipher_suites
                            if (cipher_suites != "" and cipher_suites[-1] == ','):
                                cipher_suites = cipher_suites[:-1]
                        cipher_name = cipher_details.name
                        j = 0
                        for cert, cert_details in certs.items():
                            if i == j:
                                cert_name, ca_cert, public_cert = print_certs(cert_details, region, outdir)
                                if i != 0:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, '',
                                                  '', '', '', '',
                                                  '', cert_name, ca_cert, '', '', public_cert,
                                                  cipher_name, cipher_suites)
                                else:
                                    insert_values(values_for_column_lhc, oci_objs, sheet_dict_lhc, region, ntk_compartment_name, display_name,subnet_name_list, nsg_name, hostname_name_list, cert_name, ca_cert, '','', public_cert, cipher_name, cipher_suites)
                            j = j + 1
                        i = i + 1
    return values_for_column_lhc

def print_backendset_backendserver(region, values_for_column_bss, lbr, LBRs, ntk_compartment_name):

    for eachlbr in LBRs.data:
        # Loop through Backend Sets
        for backendsets in eachlbr.__getattribute__('backend_sets'):
            backend_list = ""
            backup_list = ""
            backendset_details = lbr.get_backend_set(eachlbr.__getattribute__('id'), backendsets).data
            certificate_list = ''
            # Process the Backend Server and Backup server details
            for backends in backendset_details.__getattribute__('backends'):
                if str(backends.__getattribute__('name')).lower() != "none":
                    backend_value = str(backends.__getattribute__('name'))
                    backend_list=backend_value+','+backend_list
                if (backend_list != "" and backend_list[-1] == ','):
                    backend_list = backend_list[:-1]

                if str(backends.__getattribute__('backup')).lower() == 'true':
                    backup_value = backends.ip_address
                    backup_list = backup_value + ',' + backup_list
                if (backup_list != "" and backup_list[-1] == ','):
                    backup_list = backup_list[:-1]

            # Process columns related to Session Cookies
            lb_cookie_session_persistence_configuration = backendset_details.__getattribute__('lb_cookie_session_persistence_configuration')
            session_persistence_configuration = backendset_details.__getattribute__('session_persistence_configuration')

            if str(lb_cookie_session_persistence_configuration).lower() != 'none':
                lb_session = 'LB'
                values_for_column_bss['Cookie Session(n|LB|Backend Server)'].append(lb_session)
                values_for_column_bss = cookie_headers(values_for_column_bss, lb_cookie_session_persistence_configuration, sheet_dict_bss)

            elif str(session_persistence_configuration).lower() != 'none':
                lb_session = 'Backend Server'
                values_for_column_bss['Cookie Session(n|LB|Backend Server)'].append(lb_session)
                values_for_column_bss = cookie_headers(values_for_column_bss, session_persistence_configuration, sheet_dict_bss)

            else:
                lb_session = 'n'
                values_for_column_bss['Cookie Session(n|LB|Backend Server)'].append(lb_session)
                values_for_column_bss['Cookie Name'].append("")
                values_for_column_bss['Cookie Path'].append("")
                values_for_column_bss['Disable Fallback(TRUE|FALSE)'].append("")

            for col_headers in values_for_column_bss:
                headers_lower = commonTools.check_column_headers(col_headers)

                # Process Columns that are common across LBR sheets - Region, Compartment Name and LBR Name
                if col_headers in sheet_dict_common.keys():
                    values_for_column_bss = common_headers(region, col_headers, values_for_column_bss, eachlbr, sheet_dict_common,ntk_compartment_name)

                # Process the Tag  Columns
                elif headers_lower in commonTools.tagColumns:
                    values_for_column_bss = commonTools.export_tags(eachlbr, col_headers, values_for_column_bss)

                # Process the Backend Set and Backend Server  Columns
                elif col_headers in sheet_dict_bss.keys():
                    hc = lbr.get_health_checker(eachlbr.__getattribute__('id'), backendsets).data

                    if col_headers == "Backend Policy(LEAST_CONNECTIONS|ROUND_ROBIN|IP_HASH)":
                        policy = backendset_details.__getattribute__(sheet_dict_bss[col_headers])
                        values_for_column_bss['Backend Policy(LEAST_CONNECTIONS|ROUND_ROBIN|IP_HASH)'].append(str(policy))

                    elif 'Backend HealthCheck' in col_headers:
                        values_for_column_bss[col_headers].append(hc.__getattribute__(sheet_dict_bss[col_headers]))

                    elif col_headers == "Backend ServerName:Port":
                        values_for_column_bss[col_headers].append(backend_list)

                    elif col_headers == "Backend Set Name":
                        values_for_column_bss[col_headers].append(backendsets)

                    elif col_headers == "Certificate Name":
                        if str(backendset_details.ssl_configuration).lower() != "none":
                            certificate_list = backendset_details.ssl_configuration
                            values_for_column_bss[col_headers].append(certificate_list.certificate_name)
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
                        oci_objs = [backendset_details,eachlbr,hc,certificate_list]
                        values_for_column_bss = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_bss,values_for_column_bss)
                else:

                    if "Cookie" not in col_headers:
                        # Process the remaining  Columns
                        oci_objs = [backendset_details,eachlbr,hc,certificate_list]
                        values_for_column_bss = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_bss,values_for_column_bss)

    return values_for_column_bss


def print_listener(region, values_for_column_lis, LBRs, ntk_compartment_name):
    for eachlbr in LBRs.data:
        sslcerts = ''
        # Loop through listeners
        for listeners, values in eachlbr.__getattribute__('listeners').items():
            for col_headers in values_for_column_lis.keys():
                headers_lower = commonTools.check_column_headers(col_headers)

                # If value of Certificate Name is needed, check in ssl_configuration attribute
                if col_headers == 'Certificate Name':
                    sslcerts = values.__getattribute__(sheet_dict_lis['UseSSL (y|n)'])
                    if str(sslcerts).lower() == 'none':
                        values_for_column_lis[col_headers].append("")
                    else:
                        values_for_column_lis[col_headers].append(sslcerts.__getattribute__('certificate_name'))

                elif col_headers == 'SSL Protocols':
                    protocols_list = ''
                    if str(sslcerts).lower() == 'none':
                        values_for_column_lis[col_headers].append("")
                    else:

                        for protocols in sslcerts.protocols:
                            protocols_list = protocols+","+protocols_list

                        if (protocols_list != "" and protocols_list[-1] == ','):
                            protocols_list = protocols_list[:-1]

                        values_for_column_lis[col_headers].append(protocols_list)

                # Process Columns that are common across LBR sheets - Region, Compartment Name and LBR Name
                elif col_headers in sheet_dict_common.keys():
                    values_for_column_lis = common_headers(region, col_headers, values_for_column_lis, eachlbr, sheet_dict_common, ntk_compartment_name)

                # Process the Tag Columns
                elif headers_lower in commonTools.tagColumns:
                    values_for_column_lis = commonTools.export_tags(eachlbr, col_headers, values_for_column_lis)

                # Process the Listerner Columns
                elif col_headers in sheet_dict_lis.keys():
                    if col_headers == 'Rule Set Names':
                        rule = ""
                        if values.__getattribute__(sheet_dict_lis[col_headers]) != []:
                            for rule in values.__getattribute__(sheet_dict_lis[col_headers]):
                                value = rule
                                rule = value+","+rule

                            if (rule != "" and rule[-1] == ','):
                                rule = rule[:-1]

                        values_for_column_lis[col_headers].append(rule)

                    elif col_headers == 'UseSSL (y|n)':
                        if str(values.__getattribute__(sheet_dict_lis[col_headers])).lower() != "none":
                            values_for_column_lis[col_headers].append("y")
                        else:
                            values_for_column_lis[col_headers].append("n")

                    elif col_headers == "LBR Hostnames (Name)":
                        hostnames=""
                        if values.__getattribute__(sheet_dict_lis[col_headers]):
                            for eachhostname in values.__getattribute__(sheet_dict_lis[col_headers]):
                                hostnames = eachhostname+","+hostnames
                            if (hostnames != "" and hostnames[-1] == ','):
                                hostnames = hostnames[:-1]
                        values_for_column_lis[col_headers].append(hostnames)

                    elif col_headers == 'Idle Time Out (in Seconds)':
                        connection_config = values.__getattribute__('connection_configuration')
                        values_for_column_lis[col_headers].append(connection_config.__getattribute__(sheet_dict_lis[col_headers]))

                    else:
                        oci_objs = [values,eachlbr,sslcerts]
                        values_for_column_lis = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_lis, values_for_column_lis)

                else:
                    oci_objs = [eachlbr,values,sslcerts]
                    values_for_column_lis = commonTools.export_extra_columns(oci_objs, col_headers, sheet_dict_lis, values_for_column_lis)

    return values_for_column_lis

def print_rule(region, values_for_column_rule, LBRs, ntk_compartment_name):
    for eachlbr in LBRs.data:
        for rulesets, values in eachlbr.__getattribute__('rule_sets').items():
            for eachitem in values.items:
                for col_headers in values_for_column_rule.keys():
                    headers_lower = commonTools.check_column_headers(col_headers)

                    if col_headers in sheet_dict_common.keys():
                        values_for_column_rule = common_headers(region, col_headers, values_for_column_rule, eachlbr,sheet_dict_common, ntk_compartment_name)

                    elif col_headers == 'Rule Set Name':
                        for rulesets, values in eachlbr.__getattribute__('rule_sets').items():
                            values_for_column_rule[col_headers].append(rulesets)

                    elif col_headers in sheet_dict_rule.keys():
                        try:
                            if 'Redirect' in col_headers:
                                uri_details = eachitem.redirect_uri
                                port = uri_details.port
                                host = uri_details.host
                                path = uri_details.path
                                protocol = uri_details.protocol
                                query = uri_details.protocol

                                if 'Host:Port' in col_headers:
                                    value = host+":"+str(port)
                                    values_for_column_rule[col_headers].append(value)

                                if 'Protocol:Path' in col_headers:
                                    value = protocol+":"+path
                                    values_for_column_rule[col_headers].append(value)

                            else:
                                value = str(eachitem.__getattribute__(sheet_dict_rule[col_headers]))
                                if value.lower() == 'none':
                                    value=""
                                values_for_column_rule[col_headers].append(value)

                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")
                            pass

                    elif col_headers == 'Allowed Methods':
                        allowed_method = ''
                        if eachitem.action == "CONTROL_ACCESS_USING_HTTP_METHODS":
                            for method in eachitem.__getattribute__(headers_lower):
                                allowed_method = "\""+ method +"\"," + allowed_method

                            if (allowed_method != "" and allowed_method[-1] == ','):
                                allowed_method = allowed_method[:-1]

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
                        try:
                            suffix_val = eachitem.suffix
                            combined_suffix = "suffix:" + suffix_val
                            prefix_val = eachitem.prefix
                            combined_prefix = "prefix:" + prefix_val
                            combination = combined_suffix + "," + combined_prefix
                            values_for_column_rule[col_headers].append(combination)
                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")
                            pass
                    else:
                        try:
                            value = str(eachitem.__getattribute__(headers_lower))
                            if value.lower() == "none":
                                value = ""
                            values_for_column_rule[col_headers].append(value)
                        except AttributeError as e:
                            values_for_column_rule[col_headers].append("")
                            pass

    return values_for_column_rule

def print_prs(region, values_for_column_prs, LBRs, ntk_compartment_name):
    for eachlbr in LBRs.data:
        for prs,values in eachlbr.__getattribute__('path_route_sets').items():
            for path_routes in values.__getattribute__('path_routes'):
                for col_headers in values_for_column_prs.keys():
                    headers_lower = commonTools.check_column_headers(col_headers)

                    if col_headers in sheet_dict_common.keys():
                        values_for_column_prs = common_headers(region, col_headers, values_for_column_prs, eachlbr,sheet_dict_common, ntk_compartment_name)
                    elif col_headers == 'Match Type':
                        try:
                            key =  path_routes.__getattribute__('path_match_type')
                            match_type = key.match_type
                            values_for_column_prs[col_headers].append(match_type)
                        except AttributeError as e:
                            values_for_column_prs[col_headers].append("")

                    elif col_headers in sheet_dict_prs.keys():
                        values_for_column_prs[col_headers].append(values.__getattribute__(sheet_dict_prs[col_headers]))

                    else:
                        # Process the remaining  Columns
                        attribute = path_routes.__getattribute__(headers_lower)
                        values_for_column_prs[col_headers].append(attribute)

    return values_for_column_prs

def main():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Export LBR on OCI to CD3")
    parser.add_argument("cd3file", help="path of CD3 excel file to export network objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--networkCompartment", help="comma seperated Compartments for which to export LBR Objects", required=False)
    parser.add_argument("--configFileName", help="Config file name" , required=False)

    global tf_import_cmd
    global sheet_dict
    global importCommands
    global config
    global values_for_vcninfo
    global cd3file
    global reg
    global outdir
    global values_for_column_lhc
    global values_for_column_bss
    global values_for_column_lis
    global values_for_column_rule
    global values_for_column_prs
    global sheet_dict_common
    global sheet_dict_lhc
    global sheet_dict_bss
    global sheet_dict_lis
    global sheet_dict_rule
    global sheet_dict_prs
    global listener_to_cd3
    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    cd3file = args.cd3file
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    input_config_file = args.configFileName
    input_compartment_list = args.networkCompartment
    if (input_compartment_list is not None):
        input_compartment_names = input_compartment_list.split(",")
        input_compartment_names = [x.strip() for x in input_compartment_names]
    else:
        input_compartment_names = None

    outdir = args.outdir

    if args.configFileName is not None:
        configFileName = args.configFileName
        config = oci.config.from_file(file_location=configFileName)
    else:
        configFileName=""
        config = oci.config.from_file()

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    # Read CD3
    df, values_for_column_lhc= commonTools.read_cd3(cd3file,"LB-Hostname-Certs")
    df, values_for_column_bss = commonTools.read_cd3(cd3file, "BackendSet-BackendServer")
    df, values_for_column_lis = commonTools.read_cd3(cd3file, "LB-Listener")
    df, values_for_column_rule = commonTools.read_cd3(cd3file, "RuleSet")
    df, values_for_column_prs = commonTools.read_cd3(cd3file, "PathRouteSet")

    # Get dict for columns from Excel_Columns
    sheet_dict_common=ct.sheet_dict["Common-LBR-Headers"]
    sheet_dict_lhc =ct.sheet_dict["LB-Hostname-Certs"]
    sheet_dict_bss = ct.sheet_dict["BackendSet-BackendServer"]
    sheet_dict_lis = ct.sheet_dict["LB-Listener"]
    sheet_dict_rule = ct.sheet_dict["RuleSet"]
    sheet_dict_prs = ct.sheet_dict["PathRouteSet"]


    # Check Compartments
    remove_comps = []
    if (input_compartment_names is not None):
        for x in range(0, len(input_compartment_names)):
            if (input_compartment_names[x] not in ct.ntk_compartment_ids.keys()):
                print("Input compartment: " + input_compartment_names[x] + " doesn't exist in OCI")
                remove_comps.append(input_compartment_names[x])

        input_compartment_names = [x for x in input_compartment_names if x not in remove_comps]
        if (len(input_compartment_names) == 0):
            print("None of the input compartments specified exist in OCI..Exiting!!!")
            exit(1)
        else:
            print("Fetching for Compartments... " + str(input_compartment_names))
    else:
        print("Fetching for all Compartments...")
    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- LB-Hostname-Certs, BackendSet-BackendServer, LB-Listener, RuleSet, PathRouteSet will be overwritten during export process!!!\n")

    # Create backups
    for reg in ct.all_regions:
        resource='tf_import_lbr'
        if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_lbr_nonGF.sh")):
            commonTools.backup_file(outdir + "/" + reg, resource, "tf_import_commands_lbr_nonGF.sh")
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_lbr_nonGF.sh", "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch LBR Details
    print("\nFetching details of Load Balancer...")

    for reg in ct.all_regions:
        importCommands[reg].write("\n\n######### Writing import for Load Balancer Objects #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        lbr = LoadBalancerClient(config)
        vcn = VirtualNetworkClient(config)
        region = reg.capitalize()
        comp_ocid_done = []

        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
                LBRs = oci.pagination.list_call_get_all_results(lbr.list_load_balancers,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="ACTIVE")
                VCNs = oci.pagination.list_call_get_all_results(vcn.list_vcns,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                SUBNETs = oci.pagination.list_call_get_all_results(vcn.list_subnets,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")
                NSGs = oci.pagination.list_call_get_all_results(vcn.list_network_security_groups,compartment_id=ct.ntk_compartment_ids[ntk_compartment_name],
                                                                lifecycle_state="AVAILABLE")

                values_for_column_lhc = print_lbr_hostname_certs(region, values_for_column_lhc, lbr, VCNs, LBRs,ntk_compartment_name, SUBNETs, NSGs)
                values_for_column_lis = print_listener(region,values_for_column_lis,LBRs,ntk_compartment_name)
                values_for_column_bss = print_backendset_backendserver(region, values_for_column_bss, lbr,LBRs,ntk_compartment_name)
                values_for_column_rule = print_rule(region, values_for_column_rule, LBRs, ntk_compartment_name)
                values_for_column_prs = print_prs(region, values_for_column_prs, LBRs, ntk_compartment_name)

                for eachlbr in LBRs.data:
                    importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_lbr_nonGF.sh", "a")
                    lbr_info = eachlbr
                    lbr_display_name = lbr_info.display_name
                    tf_name = commonTools.check_tf_variable(lbr_display_name)
                    importCommands[reg].write("\nterraform import oci_load_balancer_load_balancer." + tf_name + " " + lbr_info.id)

                    for certificates in eachlbr.certificates:
                        cert_tf_name = commonTools.check_tf_variable(certificates)
                        importCommands[reg].write("\nterraform import oci_load_balancer_certificate." + cert_tf_name + "_cert" + " loadBalancers/" + lbr_info.id + "/certificates/" + certificates)

                    for hostnames in eachlbr.hostnames:
                        hostname_tf_name = commonTools.check_tf_variable(hostnames)
                        importCommands[reg].write("\nterraform import oci_load_balancer_hostname." + tf_name + "_" + hostname_tf_name + "_hostname" + " loadBalancers/" + lbr_info.id + "/hostnames/" + hostnames)

                    for listeners in eachlbr.listeners:
                        listener_tf_name = commonTools.check_tf_variable(listeners)
                        importCommands[reg].write("\nterraform import oci_load_balancer_listener." + listener_tf_name + " loadBalancers/" + lbr_info.id + "/listeners/" + listeners)

                    for backendsets, values in eachlbr.backend_sets.items():
                        backendsets_tf_name = commonTools.check_tf_variable(backendsets)
                        importCommands[reg].write("\nterraform import oci_load_balancer_backend_set." + backendsets_tf_name + " loadBalancers/" + lbr_info.id + "/backendSets/" + backendsets)

                        for keys in values.backends:
                            backendservers_name = keys.name
                            backendservers_tf_name = commonTools.check_tf_variable(keys.ip_address)
                            importCommands[reg].write("\nterraform import oci_load_balancer_backend." + backendsets_tf_name + "-" + backendservers_tf_name + " loadBalancers/" + lbr_info.id + "/backendSets/" + backendsets + "/backends/" + backendservers_name)

                    for pathroutes in eachlbr.path_route_sets:
                        pathroutes_tf_name = commonTools.check_tf_variable(pathroutes)
                        importCommands[reg].write("\nterraform import oci_load_balancer_path_route_set." + pathroutes_tf_name + " loadBalancers/" + lbr_info.id + "/pathRouteSets/" + pathroutes)

                    for routerules in eachlbr.rule_sets:
                        routerules_tf_name = commonTools.check_tf_variable(routerules)
                        importCommands[reg].write("\nterraform import oci_load_balancer_rule_set." + tf_name + "-" + routerules_tf_name + " loadBalancers/" + lbr_info.id + "/ruleSets/" + routerules)

                    for ciphers in eachlbr.ssl_cipher_suites:
                        ciphers_tf_name = commonTools.check_tf_variable(ciphers)
                        importCommands[reg].write("\nterraform import oci_load_balancer_ssl_cipher_suite." + ciphers_tf_name + " loadBalancers/" + lbr_info.id + "/sslCipherSuites/" + ciphers)

        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_lbr_nonGF.sh", "a")
        importCommands[reg].write("\n\nterraform plan")
        importCommands[reg].write("\n")
        importCommands[reg].close()
        if ("linux" in sys.platform):
            dir = os.getcwd()
            os.chdir(outdir + "/" + reg)
            os.system("chmod +x tf_import_commands_lbr_nonGF.sh")
            os.chdir(dir)

    commonTools.write_to_cd3(values_for_column_lhc, cd3file, "LB-Hostname-Certs")
    commonTools.write_to_cd3(values_for_column_bss, cd3file, "BackendSet-BackendServer")
    commonTools.write_to_cd3(values_for_column_lis, cd3file, "LB-Listener")
    commonTools.write_to_cd3(values_for_column_rule,cd3file, "RuleSet")
    commonTools.write_to_cd3(values_for_column_prs, cd3file, "PathRouteSet")

    print("LBRs exported to CD3\n")

if __name__ == '__main__':

    # Execution of the code begins here
    main()
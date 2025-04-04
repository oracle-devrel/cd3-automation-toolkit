#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export NLB Components
#
# Author: Suruchi Singla
# Oracle Consulting
#
import sys
import oci
import os
import datetime
from oci.network_firewall import NetworkFirewallClient
from oci.vault import VaultsClient
from oci.key_management import KmsVaultClient
from oci.identity import IdentityClient
import time
import subprocess as sp
from oci.network_load_balancer import NetworkLoadBalancerClient

sys.path.append(os.getcwd() + "/..")
from commonTools import *

importCommands,importCommands_nfp,importCommands_nfao,importCommands_ulo,importCommands_slo,importCommands_alo,importCommands_sro,importCommands_mso,importCommands_dpo,importCommands_dro,importCommands_fpo,importCommands_tio = {},{},{},{},{},{},{},{},{},{},{},{}
oci_obj_names = {}


def print_firewall_policy(region, ct, values_for_column_fwpolicy, fwpolicies, fwpolicy_compartment_name,export_tags,state):
    if not clone:
        print("Exporting Policy details for " + region)
    for eachfwpolicy in fwpolicies:
            # Tags filter
            defined_tags = eachfwpolicy.defined_tags
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

            fwpolicy_display_name = eachfwpolicy.display_name
            if clone :
                fwpolicy_display_name = target_pol[src_pol.index(fwpolicy_display_name)]
            else:
                tf_name = commonTools.check_tf_variable(fwpolicy_display_name)
                tf_resource = f'module.policies[\\"{str(tf_name)}\\"].oci_network_firewall_network_firewall_policy.network_firewall_policy'
                if tf_resource not in state["resources"]:
                    importCommands_nfp[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {eachfwpolicy.id}'

            for col_header in values_for_column_fwpolicy:
                if col_header == 'Region':
                    values_for_column_fwpolicy[col_header].append(region)
                elif col_header == 'Compartment Name':
                    values_for_column_fwpolicy[col_header].append(fwpolicy_compartment_name)

                elif col_header == 'Policy Name':
                    values_for_column_fwpolicy[col_header].append(fwpolicy_display_name)

                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_fwpolicy = commonTools.export_tags(eachfwpolicy, col_header, values_for_column_fwpolicy)

    return values_for_column_fwpolicy

def print_firewall_address(region, ct, values_for_column_fwaddress, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Address-list details " + region)
    for policy in fwpolicies:
            # Tags filter
            defined_tags = policy.defined_tags
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

            policy_id = policy.id
            addpolicy_display_name = policy.display_name
            if clone:
                addpolicy_display_name = target_pol[src_pol.index(addpolicy_display_name)]

            addpolicy_tf_name = commonTools.check_tf_variable(addpolicy_display_name)
            fwaddresslist = oci.pagination.list_call_get_all_results(fwclient.list_address_lists, policy_id)
            addresslist_info = fwaddresslist.data
            #importCommands[reg].write("\nterraform import \"module.address_list[\\\"" + str(addpolicy_tf_name) + "_" + str(address_tf_name) + "\\\"].oci_network_firewall_network_firewall_policy_address_list.network_firewall_policy_address_list\" networkFirewallPolicies/" + policy_id + "/addressLists/" + address_display_name)
            for add in addresslist_info:
               address_info = fwclient.get_address_list(add.parent_resource_id, add.name).data.addresses
               address_display_name = add.name
               address_tf_name = commonTools.check_tf_variable(address_display_name)
               tf_resource = f'module.address_lists[\\"{str(addpolicy_tf_name)}_{str(address_tf_name)}\\"].oci_network_firewall_network_firewall_policy_address_list.network_firewall_policy_address_list'
               if not clone and tf_resource not in state["resources"]:
                   importCommands_nfao[reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{policy_id}/addressLists/{address_display_name}'

               address_detail = ""
               for address in address_info:
                   address_detail = address_detail + "," + address
               if (address_detail != ""):
                   address_detail = address_detail[1:]


               for col_header in values_for_column_fwaddress:
                    if col_header == 'Region':
                        values_for_column_fwaddress[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwaddress[col_header].append(addpolicy_display_name)
                    elif col_header == 'List Name':
                        values_for_column_fwaddress[col_header].append(address_display_name)
                    elif col_header == 'Address Type':
                        values_for_column_fwaddress[col_header].append(add.type)
                    elif col_header == 'Address List':
                        values_for_column_fwaddress[col_header].append(address_detail)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwaddress = commonTools.export_tags(policy, col_header, values_for_column_fwaddress)

    return values_for_column_fwaddress

def print_firewall_urllist(region, ct, values_for_column_fwurllist, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Url-list details " + region)
    for urlpolicy in fwpolicies:
            # Tags filter
            defined_tags = urlpolicy.defined_tags
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
            urlpolicy_id = urlpolicy.id
            urlpolicy_display_name = urlpolicy.display_name
            if clone:
                urlpolicy_display_name = target_pol[src_pol.index(urlpolicy_display_name)]
            urlpolicy_tf_name = commonTools.check_tf_variable(urlpolicy_display_name)
            fwurllists = oci.pagination.list_call_get_all_results(fwclient.list_url_lists, urlpolicy_id)
            urllist_info = fwurllists.data
            for url in urllist_info:
                url_info = fwclient.get_url_list(url.parent_resource_id, url.name).data.urls
                url_display_name = url.name
                url_tf_name = commonTools.check_tf_variable(url_display_name)
                tf_resource = f'module.url_lists[\\"{str(urlpolicy_tf_name)}_{str(url_tf_name)}\\"].oci_network_firewall_network_firewall_policy_url_list.network_firewall_policy_url_list'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_ulo[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{urlpolicy_id}/urlLists/{url_display_name}'
                a = url_info
                url_detail = ""
                for b in a:
                    url1 = (b.pattern)
                    url_detail = url_detail + "\n" + url1
                if (url_detail != ""):
                    url_detail = url_detail[1:]
                for col_header in values_for_column_fwurllist:
                    if col_header == 'Region':
                        values_for_column_fwurllist[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwurllist[col_header].append(urlpolicy_display_name)
                    elif col_header == 'List Name':
                        values_for_column_fwurllist[col_header].append(url_display_name)
                    elif col_header == 'URL List':
                        values_for_column_fwurllist[col_header].append(url_detail)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwurllist = commonTools.export_tags(urlpolicy, col_header,values_for_column_fwurllist)

    return values_for_column_fwurllist

def print_firewall_servicelist(region, ct, values_for_column_fwservicelist, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Service and Service-list details " + region)
    for servicelistpolicy in fwpolicies:

            # Tags filter
            defined_tags = servicelistpolicy.defined_tags
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

            servicelistpolicy_id = servicelistpolicy.id
            servicelistpolicy_display_name = servicelistpolicy.display_name
            if clone:
                servicelistpolicy_display_name = target_pol[src_pol.index(servicelistpolicy_display_name)]
            servicelistpolicy_tf_name = commonTools.check_tf_variable(servicelistpolicy_display_name)
            fwservicelists = oci.pagination.list_call_get_all_results(fwclient.list_service_lists, servicelistpolicy_id)
            servicelist_info = fwservicelists.data
            service_seen_so_far = set()
            for service in servicelist_info:
                service_info = fwclient.get_service_list(service.parent_resource_id, service.name).data.services

                service_display_name = service.name
                service_tf_name = commonTools.check_tf_variable(service_display_name)
                tf_resource = f'module.service_lists[\\"{str(servicelistpolicy_tf_name)}_{str(service_display_name)}\\"].oci_network_firewall_network_firewall_policy_service_list.network_firewall_policy_service_list'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_slo[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{servicelistpolicy_id}/serviceLists/{service_display_name}'
                service_detail = ""

                for eachservice in service_info:

                    service_seen_so_far.add(eachservice)
                    servicelist = fwclient.get_service(service.parent_resource_id, eachservice).data
                    servicetype = servicelist.type
                    port_detail = ""
                    servicename = servicelist.name
                    servicename_tf =commonTools.check_tf_variable(servicename)
                    tf_resource = f'module.services[\\"{str(servicelistpolicy_tf_name)}_{str(servicename_tf)}\\"].oci_network_firewall_network_firewall_policy_service.network_firewall_policy_service'
                    if not clone and tf_resource not in state["resources"]:
                        importCommands_slo[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{servicelistpolicy_id}/services/{servicename}'
                    for svc in servicelist.port_ranges:
                        port_detail = port_detail + "," + str(svc.minimum_port) + "-" + str(svc.maximum_port)
                    if (port_detail != ""):
                        port_detail = port_detail[1:]


                    service_detail = service_detail + "\n" + servicename + "::" + servicetype + "::" + port_detail

                if (service_detail != ""):
                    service_detail = service_detail[1:]
                for col_header in values_for_column_fwservicelist:
                    if col_header == 'Region':
                        values_for_column_fwservicelist[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwservicelist[col_header].append(servicelistpolicy_display_name)
                    elif col_header == 'Service List':
                        values_for_column_fwservicelist[col_header].append(service_display_name)
                    elif col_header == 'Services':
                        values_for_column_fwservicelist[col_header].append(service_detail)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwservicelist = commonTools.export_tags(servicelistpolicy, col_header,values_for_column_fwservicelist)

            ## Fetch services without Lists
            fwservices = oci.pagination.list_call_get_all_results(fwclient.list_services,servicelistpolicy_id)
            services = fwservices.data
            service_detail = ""
            for service in services:

                service_display_name = service.name
                if service.name in service_seen_so_far:
                    continue

                service_data  = fwclient.get_service(service.parent_resource_id, service.name).data
                service_tf_name = commonTools.check_tf_variable(service_display_name)
                tf_resource = f'module.services[\\"{str(servicelistpolicy_tf_name)}_{str(service_tf_name)}\\"].oci_network_firewall_network_firewall_policy_service.network_firewall_policy_service'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_slo[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{servicelistpolicy_id}/services/{service_display_name}'

                port_detail = ""
                for svc_port_range in service_data.port_ranges:
                    port_detail = port_detail + "," + str(svc_port_range.minimum_port) + "-" + str(svc_port_range.maximum_port)
                    if (port_detail != ""):
                        port_detail = port_detail[1:]

                service_detail = service_detail + "\n" + service.name + "::" + service.type + "::" + port_detail

            if (service_detail != ""):
                service_detail = service_detail[1:]

            for col_header in values_for_column_fwservicelist:
                if col_header == 'Region':
                    values_for_column_fwservicelist[col_header].append(region)
                elif col_header == 'Firewall Policy':
                    values_for_column_fwservicelist[col_header].append(servicelistpolicy_display_name)
                elif col_header == 'Service List':
                    values_for_column_fwservicelist[col_header].append("")
                elif col_header == 'Services':
                    values_for_column_fwservicelist[col_header].append(service_detail)
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_fwservicelist = commonTools.export_tags(servicelistpolicy, col_header,values_for_column_fwservicelist)

    return values_for_column_fwservicelist

def print_firewall_applist(region, ct, values_for_column_fwapplist, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Application and Application-list details " + region)
    for applistpolicy in fwpolicies:

            # Tags filter
            defined_tags = applistpolicy.defined_tags
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

            applistpolicy_id = applistpolicy.id
            applistpolicy_display_name = applistpolicy.display_name
            if clone:
                applistpolicy_display_name = target_pol[src_pol.index(applistpolicy_display_name)]
            applistpolicy_tf_name = commonTools.check_tf_variable(applistpolicy_display_name)
            fwapplists = oci.pagination.list_call_get_all_results(fwclient.list_application_groups, applistpolicy_id)
            applist_info = fwapplists.data

            app_seen_so_far = set()
            for application in applist_info:

                application_info = fwclient.get_application_group(application.parent_resource_id, application.name).data.apps

                application_display_name = application.name
                application_tf_name = commonTools.check_tf_variable(application_display_name)
                tf_resource = f'module.application_groups[\\"{str(applistpolicy_tf_name)}_{str(application_tf_name)}\\"].oci_network_firewall_network_firewall_policy_application_group.network_firewall_policy_application_group'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_alo[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{applistpolicy_id}/applicationGroups/{application_display_name}'
                application_detail = ""
                for eachapplication in application_info:
                    applist = fwclient.get_application(application.parent_resource_id, eachapplication).data
                    applicationname = applist.name
                    app_seen_so_far.add(eachapplication)
                    applicationname_tf = commonTools.check_tf_variable(applicationname)
                    tf_resource = f'module.applications[\\"{str(applistpolicy_tf_name)}_{str(applicationname_tf)}\\"].oci_network_firewall_network_firewall_policy_application.network_firewall_policy_application'
                    if not clone and tf_resource not in state["resources"]:
                        importCommands_alo[
                            reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{applistpolicy_id}/applications/{applicationname}'

                    if applist.icmp_code != None:
                        application_detail = application_detail + "\n" + applist.name + "::" + applist.type + "::" + str(applist.icmp_type) + "::" + str(applist.icmp_code)
                    else:
                        application_detail = application_detail + "\n" + applist.name + "::" + applist.type + "::" + str(applist.icmp_type)

                if (application_detail != ""):
                    application_detail = application_detail[1:]


                for col_header in values_for_column_fwapplist:
                    if col_header == 'Region':
                        values_for_column_fwapplist[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwapplist[col_header].append(applistpolicy_display_name)
                    elif col_header == 'Application List':
                        values_for_column_fwapplist[col_header].append(application_display_name)
                    elif col_header == 'Applications':
                        values_for_column_fwapplist[col_header].append(application_detail)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwapplist = commonTools.export_tags(applistpolicy, col_header,values_for_column_fwapplist)

            ## Fetch apps without Lists
            fwapps = oci.pagination.list_call_get_all_results(fwclient.list_applications, applistpolicy_id)
            apps = fwapps.data
            application_detail = ""
            for app in apps:
                app_display_name = app.name
                if app.name in app_seen_so_far:
                    continue
                app_data = fwclient.get_application(app.parent_resource_id, app.name).data
                app_tf_name = commonTools.check_tf_variable(app_display_name)
                tf_resource = f'module.applications[\\"{str(applistpolicy_tf_name)}_{str(app_tf_name)}\\"].oci_network_firewall_network_firewall_policy_application.network_firewall_policy_application'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_alo[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{applistpolicy_id}/applications/{app_display_name}'

                if app_data.icmp_code != None:
                    application_detail = application_detail + "\n" + app.name + "::" + app.type + "::" + str(
                            app_data.icmp_type) + "::" + str(app_data.icmp_code)
                else:
                    application_detail = application_detail + "\n" + app.name + "::" + app.type + "::" + str(
                            app_data.icmp_type)

            if (application_detail != ""):
                application_detail = application_detail[1:]

            for col_header in values_for_column_fwapplist:
                if col_header == 'Region':
                    values_for_column_fwapplist[col_header].append(region)
                elif col_header == 'Firewall Policy':
                    values_for_column_fwapplist[col_header].append(applistpolicy_display_name)
                elif col_header == 'Application List':
                    values_for_column_fwapplist[col_header].append("")
                elif col_header == 'Applications':
                    values_for_column_fwapplist[col_header].append(application_detail)
                elif col_header.lower() in commonTools.tagColumns:
                    values_for_column_fwapplist = commonTools.export_tags(applistpolicy, col_header,
                                                                          values_for_column_fwapplist)

    return values_for_column_fwapplist

def print_firewall_secrules(region, ct, values_for_column_fwsecrules, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Security rules details " + region)
    for secrulespolicy in fwpolicies:
            # Tags filter
            defined_tags = secrulespolicy.defined_tags
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

            secrulespolicy_id = secrulespolicy.id
            secrulespolicy_display_name = secrulespolicy.display_name
            if clone:
                secrulespolicy_display_name = target_pol[src_pol.index(secrulespolicy_display_name)]
            secrulespolicy_tf_name = commonTools.check_tf_variable(secrulespolicy_display_name)
            fwsecrules = oci.pagination.list_call_get_all_results(fwclient.list_security_rules,secrulespolicy_id)
            secrules_info = fwsecrules.data
            #print(secrules_info)
            for rules in secrules_info:
                rule_info = fwclient.get_security_rule(rules.parent_resource_id, rules.name).data
                rules_display_name = rules.name
                rules_tf_name = commonTools.check_tf_variable(rules_display_name)
                tf_resource = f'module.security_rules[\\"{str(secrulespolicy_tf_name)}_{str(rules_tf_name)}\\"].oci_network_firewall_network_firewall_policy_security_rule.network_firewall_policy_security_rule'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_sro[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{secrulespolicy_id}/securityRules/{rules_display_name}'

                rsrc_detail = ""
                rdst_detail = ""
                rapp_detail = ""
                rsvc_detail = ""
                rurl_detail = ""
                raction = ""
                rposition = ""
                if rule_info.condition.source_address != None:
                    for rsrc in rule_info.condition.source_address:
                        rsrc_detail = rsrc_detail + "," + rsrc
                    if (rsrc_detail != ""):
                        rsrc_detail = rsrc_detail[1:]
                if rule_info.condition.destination_address != None:
                    for rdst in rule_info.condition.destination_address:
                        rdst_detail = rdst_detail + "," + rdst
                    if (rdst_detail != ""):
                        rdst_detail = rdst_detail[1:]
                if rule_info.condition.application != None:
                    for rapp in rule_info.condition.application:
                        rapp_detail = rapp_detail + "," + rapp
                    if (rapp_detail != ""):
                        rapp_detail = rapp_detail[1:]
                if rule_info.condition.service != None:
                    for rsvc in rule_info.condition.service:
                        rsvc_detail = rsvc_detail + "," + rsvc
                    if (rsvc_detail != ""):
                        rsvc_detail = rsvc_detail[1:]
                if rule_info.condition.url != None:
                    for rurl in rule_info.condition.url:
                        rurl_detail = rurl_detail + "," + rurl
                    if (rurl_detail != ""):
                        rurl_detail = rurl_detail[1:]
                if rule_info.action == "INSPECT":
                    raction = rule_info.action + "::" + rule_info.inspection
                else:
                    raction = rule_info.action
                if rule_info.position.after_rule == None and rule_info.position.before_rule == None:
                    rposition = None
                elif rule_info.position.after_rule == None:
                    rposition = None
                elif rule_info.position.before_rule == None:
                    rposition = "after_rule::" + rule_info.position.after_rule
                else:
                    rposition = "after_rule::" + rule_info.position.after_rule


                for col_header in values_for_column_fwsecrules:
                    if col_header == 'Region':
                        values_for_column_fwsecrules[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwsecrules[col_header].append(secrulespolicy_display_name)
                    elif col_header == 'Rule Name':
                        values_for_column_fwsecrules[col_header].append(rules_display_name)
                    elif col_header == 'Source Address':
                        values_for_column_fwsecrules[col_header].append(rsrc_detail)
                    elif col_header == 'Destination Address':
                        values_for_column_fwsecrules[col_header].append(rdst_detail)
                    elif col_header == 'Service List':
                        values_for_column_fwsecrules[col_header].append(rsvc_detail)
                    elif col_header == 'Application List':
                        values_for_column_fwsecrules[col_header].append(rapp_detail)
                    elif col_header == 'Url List':
                        values_for_column_fwsecrules[col_header].append(rurl_detail)
                    elif col_header == 'Action':
                        values_for_column_fwsecrules[col_header].append(raction)
                    elif col_header == 'Position':
                        values_for_column_fwsecrules[col_header].append(rposition)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwsecrules = commonTools.export_tags(secrulespolicy, col_header,values_for_column_fwsecrules)

    return values_for_column_fwsecrules
def print_firewall_secret(region, ct, values_for_column_fwsecret, fwpolicies, fwclient, vault, compartment, export_tags,kmsvault,state):
    if not clone:
        print("Exporting Mapped secret details " + region)
    for secretpolicy in fwpolicies:
            # Tags filter
            defined_tags = secretpolicy.defined_tags
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

            secretpolicy_id = secretpolicy.id
            secretpolicy_display_name = secretpolicy.display_name
            if clone:
                secretpolicy_display_name = target_pol[src_pol.index(secretpolicy_display_name)]
            secretpolicy_tf_name = commonTools.check_tf_variable(secretpolicy_display_name)
            fwsecrets = oci.pagination.list_call_get_all_results(fwclient.list_mapped_secrets, secretpolicy_id)
            secret_info = fwsecrets.data
            for key in secret_info:
                key_info = fwclient.get_mapped_secret(key.parent_resource_id, key.name).data
                secretdisplay_name = key.name
                secretdisplay_tf_name = commonTools.check_tf_variable(secretdisplay_name)
                vault_secret = vault.get_secret(key_info.vault_secret_id).data
                kmsvault_name = kmsvault.get_vault(vault_secret.vault_id).data
                vault_secret_name = kmsvault_name.display_name + '::' + vault_secret.secret_name
                vault_secret_compartment_detail = compartment.get_compartment(vault_secret.compartment_id).data.name
                tf_resource = f'module.secrets[\\"{str(secretpolicy_tf_name)}_{str(secretdisplay_tf_name)}\\"].oci_network_firewall_network_firewall_policy_mapped_secret.network_firewall_policy_mapped_secret'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_mso[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{secretpolicy_id}/mappedSecrets/{secretdisplay_name}'

                for col_header in values_for_column_fwsecret:
                    if col_header == 'Region':
                        values_for_column_fwsecret[col_header].append(region)
                    elif col_header == 'Vault Compartment Name':
                        values_for_column_fwsecret[col_header].append(vault_secret_compartment_detail)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwsecret[col_header].append(secretpolicy_display_name)
                    elif col_header == 'Secret Name':
                        values_for_column_fwsecret[col_header].append(secretdisplay_name)
                    elif col_header == 'Secret Source':
                        values_for_column_fwsecret[col_header].append(key_info.source)
                    elif col_header == 'Secret Type':
                        values_for_column_fwsecret[col_header].append(key_info.type)
                    elif col_header == 'Vault Secret Id':
                        values_for_column_fwsecret[col_header].append(vault_secret_name)
                    elif col_header == 'Version Number':
                        values_for_column_fwsecret[col_header].append(key_info.version_number)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwsecret = commonTools.export_tags(secretpolicy, col_header,values_for_column_fwsecret)

    return values_for_column_fwsecret

def print_firewall_decryptprofile(region, ct, values_for_column_fwdecryptprofile, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Decryption Profile details " + region)
    for decryptionprofile in fwpolicies:
            # Tags filter
            defined_tags = decryptionprofile.defined_tags
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

            decryptionprofile_id = decryptionprofile.id
            decryptionprofile_display_name = decryptionprofile.display_name
            if clone:
                decryptionprofile_display_name = target_pol[src_pol.index(decryptionprofile_display_name)]
            decryptionprofile_tf_name = commonTools.check_tf_variable(decryptionprofile_display_name)
            fwdcyrptionprofiles = oci.pagination.list_call_get_all_results(fwclient.list_decryption_profiles, decryptionprofile_id)
            decryptionprofile_info = fwdcyrptionprofiles.data
            for decryption in decryptionprofile_info:
                key_info = fwclient.get_decryption_profile(decryption.parent_resource_id, decryption.name).data
                key_info_name = key_info.name
                key_info_tf_name = commonTools.check_tf_variable(key_info.name)
                tf_resource = f'module.decryption_profiles[\\"{str(decryptionprofile_tf_name)}_{str(key_info_tf_name)}\\"].oci_network_firewall_network_firewall_policy_decryption_profile.network_firewall_policy_decryption_profile'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_dpo[
                        reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{decryptionprofile_id}/decryptionProfiles/{key_info_name}'

                if key_info.type == "SSL_INBOUND_INSPECTION":
                    key_info1_are_certificate_extensions_restricted = ""
                    key_info1_is_auto_include_alt_name = ""
                    key_info1_is_expired_certificate_blocked = ""
                    key_info1_is_revocation_status_timeout_blocked = ""
                    key_info1_is_unknown_revocation_status_blocked = ""
                    key_info1_is_untrusted_issuer_blocked = ""
                elif key_info.type == "SSL_FORWARD_PROXY":
                    key_info1_are_certificate_extensions_restricted = key_info.are_certificate_extensions_restricted
                    key_info1_is_auto_include_alt_name = key_info.is_auto_include_alt_name
                    key_info1_is_expired_certificate_blocked = key_info.is_expired_certificate_blocked
                    key_info1_is_revocation_status_timeout_blocked = key_info.is_revocation_status_timeout_blocked
                    key_info1_is_unknown_revocation_status_blocked = key_info.is_unknown_revocation_status_blocked
                    key_info1_is_untrusted_issuer_blocked = key_info.is_untrusted_issuer_blocked
                for col_header in values_for_column_fwdecryptprofile:
                    if col_header == 'Region':
                        values_for_column_fwdecryptprofile[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwdecryptprofile[col_header].append(decryptionprofile_display_name)
                    elif col_header == 'Decryption Profile Name':
                        values_for_column_fwdecryptprofile[col_header].append(key_info_name)
                    elif col_header == 'Decryption Profile Type':
                        values_for_column_fwdecryptprofile[col_header].append(key_info.type)
                    elif col_header == 'are certificate extensions restricted':
                        values_for_column_fwdecryptprofile[col_header].append(key_info1_are_certificate_extensions_restricted)
                    elif col_header == 'is auto include alt name':
                        values_for_column_fwdecryptprofile[col_header].append(key_info1_is_auto_include_alt_name)
                    elif col_header == 'is expired certificate blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info1_is_expired_certificate_blocked)
                    elif col_header == 'is out of capacity blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info.is_out_of_capacity_blocked)
                    elif col_header == 'is revocation status timeout blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info1_is_revocation_status_timeout_blocked)
                    elif col_header == 'is unknown revocation status blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info1_is_unknown_revocation_status_blocked)
                    elif col_header == 'is unsupported cipher blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info.is_unsupported_cipher_blocked)
                    elif col_header == 'is unsupported version blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info.is_unsupported_version_blocked)
                    elif col_header == 'is untrusted issuer blocked':
                        values_for_column_fwdecryptprofile[col_header].append(key_info1_is_untrusted_issuer_blocked)

                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwdecryptprofile = commonTools.export_tags(decryptionprofile, col_header,values_for_column_fwdecryptprofile)

    return values_for_column_fwdecryptprofile
def print_firewall_decryptrule(region, ct, values_for_column_fwdecryptrule, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Decryption rules details " + region)
    for decryptrulepolicy in fwpolicies:
            # Tags filter
            defined_tags = decryptrulepolicy.defined_tags
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


            decryptrulepolicy_id = decryptrulepolicy.id
            decryptrulepolicy_display_name = decryptrulepolicy.display_name
            if clone:
                decryptrulepolicy_display_name = target_pol[src_pol.index(decryptrulepolicy_display_name)]
            decryptrulepolicy_tf_name = commonTools.check_tf_variable(decryptrulepolicy_display_name)
            fwdecrypteules = oci.pagination.list_call_get_all_results(fwclient.list_decryption_rules, decryptrulepolicy_id)
            decrypteules_info = fwdecrypteules.data
            for drules in decrypteules_info:
                drule_info = fwclient.get_decryption_rule(drules.parent_resource_id, drules.name).data
                drules_display_name = drules.name
                drules_tf_name = commonTools.check_tf_variable(drules_display_name)
                tf_resource = f'module.decryption_rules[\\"{str(decryptrulepolicy_tf_name)}_{str(drules_tf_name)}\\"].oci_network_firewall_network_firewall_policy_decryption_rule.network_firewall_policy_decryption_rule'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_dro[reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{decryptrulepolicy_id}/decryptionRules/{drules_display_name}'

                rsrc_detail = ""
                rdst_detail = ""
                if drule_info.condition.source_address != None:
                    for rsrc in drule_info.condition.source_address:
                        rsrc_detail = rsrc_detail + "," + rsrc
                    if (rsrc_detail != ""):
                        rsrc_detail = rsrc_detail[1:]
                if drule_info.condition.destination_address != None:
                    for rdst in drule_info.condition.destination_address:
                        rdst_detail = rdst_detail + "," + rdst
                    if (rdst_detail != ""):
                        rdst_detail = rdst_detail[1:]
                if drule_info.position.after_rule == None and drule_info.position.before_rule == None:
                    dposition = None
                elif drule_info.position.after_rule == None:
                    dposition = None
                elif drule_info.position.before_rule == None:
                    dposition = "after_rule::" + drule_info.position.after_rule
                else:
                    dposition = "after_rule::" + drule_info.position.after_rule

                for col_header in values_for_column_fwdecryptrule:
                    if col_header == 'Region':
                        values_for_column_fwdecryptrule[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwdecryptrule[col_header].append(decryptrulepolicy_display_name)
                    elif col_header == 'Rule Name':
                        values_for_column_fwdecryptrule[col_header].append(drules_display_name)
                    elif col_header == 'Source Address':
                        values_for_column_fwdecryptrule[col_header].append(rsrc_detail)
                    elif col_header == 'Destination Address':
                        values_for_column_fwdecryptrule[col_header].append(rdst_detail)
                    elif col_header == 'Secret Name':
                        values_for_column_fwdecryptrule[col_header].append(drule_info.secret)
                    elif col_header == 'Decryption Profile':
                        values_for_column_fwdecryptrule[col_header].append(drule_info.decryption_profile)
                    elif col_header == 'Action':
                        values_for_column_fwdecryptrule[col_header].append(drule_info.action)
                    elif col_header == 'Position':
                        values_for_column_fwdecryptrule[col_header].append(dposition)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwdecryptrule = commonTools.export_tags(decryptrulepolicy, col_header,values_for_column_fwdecryptrule)
    return values_for_column_fwdecryptrule

def  print_firewall_tunnelinspect(region, ct, values_for_column_fwtunnelinspect, fwpolicies, fwclient,export_tags,state):
    if not clone:
        print("Exporting Tunnel inspections rules details " + region)
    for tunnelinspectrulepolicy in fwpolicies:

            # Tags filter
            defined_tags = tunnelinspectrulepolicy.defined_tags
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


            tunnelinspectrulepolicy_id = tunnelinspectrulepolicy.id
            tunnelinspectrulepolicy_display_name = tunnelinspectrulepolicy.display_name
            if clone:
                tunnelinspectrulepolicy_display_name = target_pol[src_pol.index(tunnelinspectrulepolicy_display_name)]
            tunnelinspectrulepolicy_tf_name = commonTools.check_tf_variable(tunnelinspectrulepolicy_display_name)
            fwtunnelinspectrules = oci.pagination.list_call_get_all_results(fwclient.list_tunnel_inspection_rules, tunnelinspectrulepolicy_id)
            tunnelinspectrule_info = fwtunnelinspectrules.data
            for tirules in tunnelinspectrule_info:
                tirule_info = fwclient.get_tunnel_inspection_rule(tirules.parent_resource_id, tirules.name).data
                tirules_display_name = tirules.name
                tirules_tf_name = commonTools.check_tf_variable(tirules_display_name)
                tf_resource = f'module.tunnelinspect_rules[\\"{str(tunnelinspectrulepolicy_tf_name)}_{str(tirules_tf_name)}\\"].oci_network_firewall_network_firewall_policy_tunnel_inspection_rule.network_firewall_policy_tunnel_inspection_rule'
                if not clone and tf_resource not in state["resources"]:
                    importCommands_tio[reg] += f'\n{tf_or_tofu} import "{tf_resource}" networkFirewallPolicies/{tunnelinspectrulepolicy_id}/tunnelInspectionRules/{tirules_display_name}'

                rsrc_detail = ""
                rdst_detail = ""
                if tirule_info.condition.source_address != None:
                    for rsrc in tirule_info.condition.source_address:
                        rsrc_detail = rsrc_detail + "," + rsrc
                    if (rsrc_detail != ""):
                        rsrc_detail = rsrc_detail[1:]
                if tirule_info.condition.destination_address != None:
                    for rdst in tirule_info.condition.destination_address:
                        rdst_detail = rdst_detail + "," + rdst
                    if (rdst_detail != ""):
                        rdst_detail = rdst_detail[1:]
                if tirule_info.position.after_rule == None and tirule_info.position.before_rule == None:
                    dposition = None
                elif tirule_info.position.after_rule == None:
                    dposition = None
                elif tirule_info.position.before_rule == None:
                    dposition = "after_rule::" + tirule_info.position.after_rule
                else:
                    dposition = "after_rule::" + tirule_info.position.after_rule

                for col_header in values_for_column_fwtunnelinspect:
                    if col_header == 'Region':
                        values_for_column_fwtunnelinspect[col_header].append(region)
                    elif col_header == 'Firewall Policy':
                        values_for_column_fwtunnelinspect[col_header].append(tunnelinspectrulepolicy_display_name)
                    elif col_header == 'Rule Name':
                        values_for_column_fwtunnelinspect[col_header].append(tirules_display_name)
                    elif col_header == 'Source Address':
                        values_for_column_fwtunnelinspect[col_header].append(rsrc_detail)
                    elif col_header == 'Destination Address':
                        values_for_column_fwtunnelinspect[col_header].append(rdst_detail)
                    elif col_header == 'Action':
                        values_for_column_fwtunnelinspect[col_header].append(tirule_info.action)
                    elif col_header == 'Position':
                        values_for_column_fwtunnelinspect[col_header].append(dposition)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_fwtunnelinspect = commonTools.export_tags(tunnelinspectrulepolicy, col_header,values_for_column_fwtunnelinspect)
    return values_for_column_fwtunnelinspect



# Execution of the code begins here
def export_firewallpolicy(inputfile, _outdir, service_dir, config, signer, ct, export_compartments, export_regions, export_tags, export_policies,target_policies=[],attached_policy_only="",clone_policy=False):
    global tf_import_cmd
    global sheet_dict
    global importCommands,importCommands_nfp,importCommands_nfao,importCommands_ulo,importCommands_slo,importCommands_alo,importCommands_sro,importCommands_mso,importCommands_dpo,importCommands_dro,importCommands_fpo,importCommands_tio
    global values_for_vcninfo
    global cd3file
    global reg
    global outdir
    global values_for_column_fwpolicy
    global values_for_column_fwaddress
    global values_for_column_fwurllist
    global values_for_column_fwservicelist
    global values_for_column_fwapplist
    global values_for_column_fwsecrules
    global values_for_column_fwsecret
    global values_for_column_fwdecryptprofile
    global values_for_column_fwdecryptrule
    global values_for_column_fwtunnelinspect
    global sheet_dict_fwpolicy
    global sheet_dict_fwaddress
    global sheet_dict_fwurllist
    global listener_to_cd3
    global clone
    global src_pol
    global target_pol,tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    src_pol = export_policies.copy() if export_policies else []
    target_pol = []
    if not target_policies :
        for src in src_pol:
            target_pol.append("network_firewall_policy_"+datetime.datetime.now().strftime("%d-%m-%y-%H%M%S").replace('/', '-'))
            time.sleep(2)
    else:
        target_pol = target_policies.copy()
    clone = clone_policy

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()
    sheetname = "Firewall-Policy"
    outdir = _outdir


    # Read CD3
    df, values_for_column_fwpolicy = commonTools.read_cd3(cd3file, sheetname)
    df, values_for_column_fwaddress = commonTools.read_cd3(cd3file, "Firewall-Policy-AddressList")
    df, values_for_column_fwurllist = commonTools.read_cd3(cd3file, "Firewall-Policy-UrlList")
    df, values_for_column_fwservicelist = commonTools.read_cd3(cd3file, "Firewall-Policy-ServiceList")
    df, values_for_column_fwapplist = commonTools.read_cd3(cd3file, "Firewall-Policy-ApplicationList")
    df, values_for_column_fwsecrules = commonTools.read_cd3(cd3file, "Firewall-Policy-SecRule")
    df, values_for_column_fwsecret = commonTools.read_cd3(cd3file, "Firewall-Policy-Secret")
    df, values_for_column_fwdecryptprofile = commonTools.read_cd3(cd3file, "Firewall-Policy-DecryptProfile")
    df, values_for_column_fwdecryptrule = commonTools.read_cd3(cd3file, "Firewall-Policy-DecryptRule")
    df, values_for_column_fwtunnelinspect = commonTools.read_cd3(cd3file, "Firewall-Policy-TunnelInspect")
    # Get dict for columns from Excel_Columns
    #sheet_dict_fwpolicy = ct.sheet_dict[sheetname]
    #sheet_dict_fwaddress = ct.sheet_dict["Firewall-Policy-Address"]


    # Create backups
    if not clone:
        print("\nCD3 excel file should not be opened during export process!!!")
        print("Tabs related to firewall and firewall policies will be overwritten during export process!!!\n")

        for reg in export_regions:
            resource = 'import_fwpolicy'
            if (os.path.exists(outdir + "/" + reg + "/" + service_dir + "/import_commands_firewallpolicy.sh")):
                commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, "import_commands_firewallpolicy.sh")
            importCommands[reg], importCommands_nfp[reg], importCommands_nfao[reg], importCommands_ulo[reg], \
            importCommands_slo[reg], importCommands_alo[reg], importCommands_sro[reg], importCommands_mso[reg], \
            importCommands_dpo[reg], importCommands_dro[reg], importCommands_fpo[
                reg], importCommands_tio[reg]= "", "", "", "", "", "", "", "", "", "", "", ""


    # Fetch Network firewall Policy Details
    print("\nFetching details of Network firewall policy...")

    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        fwclient = NetworkFirewallClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        vault = VaultsClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        kmsvault = KmsVaultClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        compartment = IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        region = reg.capitalize()

        for compartment_name in export_compartments:
            fwpolicies = []
            fw_data = oci.pagination.list_call_get_all_results(fwclient.list_network_firewall_policies,compartment_id=ct.ntk_compartment_ids[compartment_name], lifecycle_state="ACTIVE").data
            for eachfwpolicy in fw_data:
                if export_policies is not None:
                    eachfwpolicy1 = fwclient.get_network_firewall_policy(network_firewall_policy_id=eachfwpolicy.id).data

                    # Tags filter
                    defined_tags = eachfwpolicy1.defined_tags
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

                    fwpolicy_display_name1 = eachfwpolicy1.display_name
                    if (fwpolicy_display_name1 in export_policies):
                        if clone:
                            if attached_policy_only == "y":
                                if eachfwpolicy1.attached_network_firewall_count == 0:
                                    print("Skipping "+str(fwpolicy_display_name1) + " as it is not attached.")
                                    continue
                            print("Cloning " + str(fwpolicy_display_name1) +" to "+str(target_pol[src_pol.index(fwpolicy_display_name1)]) )
                            fwpolicies.append(eachfwpolicy)
                            continue
                        print("Processing "+str(fwpolicy_display_name1))
                        fwpolicies.append(eachfwpolicy)
                else:
                    fwpolicies.append(eachfwpolicy)

            #fwpolicies.append(data)
            values_for_column_fwpolicy = print_firewall_policy(region, ct, values_for_column_fwpolicy, fwpolicies,compartment_name,export_tags,state)
            values_for_column_fwaddress = print_firewall_address(region, ct, values_for_column_fwaddress, fwpolicies, fwclient,export_tags,state)
            values_for_column_fwurllist = print_firewall_urllist(region, ct, values_for_column_fwurllist, fwpolicies, fwclient,export_tags,state)
            values_for_column_fwservicelist = print_firewall_servicelist(region, ct, values_for_column_fwservicelist, fwpolicies, fwclient,export_tags,state)
            values_for_column_fwapplist = print_firewall_applist(region, ct, values_for_column_fwapplist, fwpolicies, fwclient,export_tags,state)
            values_for_column_fwsecrules = print_firewall_secrules(region, ct, values_for_column_fwsecrules,fwpolicies, fwclient,export_tags,state)
            values_for_column_fwsecret = print_firewall_secret(region, ct, values_for_column_fwsecret, fwpolicies,fwclient, vault, compartment, export_tags,kmsvault,state)
            values_for_column_fwdecryptprofile = print_firewall_decryptprofile(region, ct,values_for_column_fwdecryptprofile,fwpolicies, fwclient,export_tags,state)
            values_for_column_fwdecryptrule = print_firewall_decryptrule(region, ct, values_for_column_fwdecryptrule,fwpolicies, fwclient,export_tags,state)
            values_for_column_fwtunnelinspect = print_firewall_tunnelinspect(region, ct, values_for_column_fwtunnelinspect,fwpolicies,fwclient,export_tags,state)
    if clone:
        commonTools.write_to_cd3(values_for_column_fwpolicy, cd3file, "Firewall-Policy",append=True)
        commonTools.write_to_cd3(values_for_column_fwaddress, cd3file, "Firewall-Policy-AddressList",append=True)
        commonTools.write_to_cd3(values_for_column_fwurllist, cd3file, "Firewall-Policy-UrlList",append=True)
        commonTools.write_to_cd3(values_for_column_fwservicelist, cd3file, "Firewall-Policy-ServiceList",append=True)
        commonTools.write_to_cd3(values_for_column_fwapplist, cd3file, "Firewall-Policy-ApplicationList",append=True)
        commonTools.write_to_cd3(values_for_column_fwsecrules, cd3file, "Firewall-Policy-SecRule",append=True)
        commonTools.write_to_cd3(values_for_column_fwsecret, cd3file, "Firewall-Policy-Secret",append=True)
        commonTools.write_to_cd3(values_for_column_fwdecryptprofile, cd3file, "Firewall-Policy-DecryptProfile",append=True)
        commonTools.write_to_cd3(values_for_column_fwdecryptrule, cd3file, "Firewall-Policy-DecryptRule",append=True)
        commonTools.write_to_cd3(values_for_column_fwtunnelinspect, cd3file, "Firewall-Policy-TunnelInspect", append=True)
    else:
        commonTools.write_to_cd3(values_for_column_fwpolicy, cd3file, "Firewall-Policy")
        commonTools.write_to_cd3(values_for_column_fwaddress, cd3file, "Firewall-Policy-AddressList")
        commonTools.write_to_cd3(values_for_column_fwurllist, cd3file, "Firewall-Policy-UrlList")
        commonTools.write_to_cd3(values_for_column_fwservicelist, cd3file, "Firewall-Policy-ServiceList")
        commonTools.write_to_cd3(values_for_column_fwapplist, cd3file, "Firewall-Policy-ApplicationList")
        commonTools.write_to_cd3(values_for_column_fwsecrules, cd3file, "Firewall-Policy-SecRule")
        commonTools.write_to_cd3(values_for_column_fwsecret, cd3file, "Firewall-Policy-Secret")
        commonTools.write_to_cd3(values_for_column_fwdecryptprofile, cd3file, "Firewall-Policy-DecryptProfile")
        commonTools.write_to_cd3(values_for_column_fwdecryptrule, cd3file, "Firewall-Policy-DecryptRule")
        commonTools.write_to_cd3(values_for_column_fwtunnelinspect, cd3file, "Firewall-Policy-TunnelInspect")
        print("Firewall Policies exported to CD3\n")

        # writing data
        init_commands = f'\n######### Writing import for Network firewall policy Objects #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        importCommands_message = ["Policy","Address Objects","url list Objects","service list Objects","application list Objects","Security Rules Objects","Mapped Secret Objects","Decrypt profile Objects","decryption Rules Objects","policy Objects","Tunnel Inspect Objects"]
        for reg in export_regions:
            count = 0
            all_importCommands = [importCommands_nfp[reg], importCommands_nfao[reg], importCommands_ulo[reg], importCommands_slo[reg],
                                  importCommands_alo[reg], importCommands_sro[reg], importCommands_mso[reg], importCommands_dpo[reg],
                                  importCommands_dro[reg], importCommands_fpo[reg], importCommands_tio[reg]]
            for item in all_importCommands:
                if item != "":
                    importCommands[reg] += f'\n\n######### Writing import for Network firewall {importCommands_message[count]} #########\n\n'
                    importCommands[reg] += item
                count += 1
            script_file = f'{outdir}/{reg}/{service_dir}/import_commands_firewallpolicy.sh'

            if importCommands[reg] != "":
                importCommands[reg] += f'\n{tf_or_tofu} plan\n'
                with open(script_file, 'a') as importCommandsfile:
                    importCommandsfile.write(init_commands + importCommands[reg])



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
import Security
import numpy as np
from oci.network_firewall import NetworkFirewallClient
from oci.vault import VaultsClient
from oci.identity import IdentityClient
from oci.network_load_balancer import NetworkLoadBalancerClient

sys.path.append(os.getcwd() + "/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}




def clone_firewallpolicy(inputfile, _outdir, service_dir, config, signer, ct, export_compartments, export_regions, export_firewall, export_policy):

    global tf_import_cmd
    global sheet_dict
    global importCommands
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

    global sheet_dict_fwpolicy
    global sheet_dict_fwaddress
    global sheet_dict_fwurllist
    global listener_to_cd3


    outdir = _outdir


    # Clone Network firewall Policy Details
    print("\nCloning details of Network firewall policy...")
    for reg in export_regions:
        if export_regions == "":
            print("\nRegion can not be left empty to clone a policy ")
        else:
            config.__setitem__("region", ct.region_dict[reg])
            fwpolicy = NetworkFirewallClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
            region = reg.capitalize()
            if export_compartments == "":
               print("\nCompartment can not be left empty to clone a policy ")

            else:
                for compartment_name in export_compartments:
                    if export_policy != None:
                        if len(export_firewall) != len(export_policy):
                            print("Declare cloned policy name for all the firewalls or leave the policy name empty for auto generation of Policy name..")
                            exit()
                        else:
                            arr_export_policy = np.array(export_policy)
                            i = 0
                            policy_detail = ""
                            for eachfirewall in export_firewall:
                                if eachfirewall != "":
                                    fw = oci.pagination.list_call_get_all_results(fwpolicy.list_network_firewalls,compartment_id=ct.ntk_compartment_ids[compartment_name], display_name=export_firewall, lifecycle_state="ACTIVE")
                                    policy_id = fw.data
                                    for eachfw in policy_id:
                                        policy_ocid = eachfw.network_firewall_policy_id
                                        new_policy = fwpolicy.clone_network_firewall_policy(network_firewall_policy_id=policy_ocid, clone_network_firewall_policy_details=oci.network_firewall.models.CloneNetworkFirewallPolicyDetails(display_name=arr_export_policy[i], compartment_id=ct.ntk_compartment_ids[compartment_name]))
                                        print("Wait for the policy " + arr_export_policy[i] + " to become Active")
                                        policy_detail = policy_detail + "," + new_policy.data.display_name
                                        get_clone_status = fwpolicy.get_network_firewall_policy(new_policy.data.id)
                                        wait_until_policy_cloned = oci.wait_until(fwpolicy, get_clone_status, 'lifecycle_state', "ACTIVE", max_interval_seconds=30, max_wait_seconds=300)
                                    i += 1
                                else:
                                    print("\nFirewall name can not be left empty to clone a policy ")
                                    exit()
                        if (policy_detail != ""):
                            policy_detail = policy_detail[1:]
                    else:
                        policy_detail = ""
                        for eachfirewall in export_firewall:
                            if eachfirewall != "":
                                fw = oci.pagination.list_call_get_all_results(fwpolicy.list_network_firewalls,compartment_id=ct.ntk_compartment_ids[compartment_name], display_name=eachfirewall, lifecycle_state="ACTIVE")
                                policy_id = fw.data
                                for eachfw in policy_id:
                                    arr_export_policy = eachfirewall + "_Policy_" + datetime.datetime.now().strftime("%d-%m-%y-%H%M%S").replace('/', '-')
                                    policy_ocid = eachfw.network_firewall_policy_id
                                    new_policy = fwpolicy.clone_network_firewall_policy(network_firewall_policy_id=policy_ocid, clone_network_firewall_policy_details=oci.network_firewall.models.CloneNetworkFirewallPolicyDetails(display_name=arr_export_policy, compartment_id=ct.ntk_compartment_ids[compartment_name]))
                                    print("Wait for the policy " + arr_export_policy + " to become Active ")
                                    policy_detail = policy_detail + "," + new_policy.data.display_name
                                    get_clone_status = fwpolicy.get_network_firewall_policy(new_policy.data.id)
                                    wait_until_policy_cloned = oci.wait_until(fwpolicy, get_clone_status, 'lifecycle_state', "ACTIVE", max_interval_seconds=30, max_wait_seconds=300)
                                    print("Firewall Policy cloned for " + region)
                            else:
                                print("\nFirewall name can not be left empty to clone a policy ")
                                exit()
                        if (policy_detail != ""):
                            policy_detail = policy_detail[1:]

        Security.cloneexport_firewallpolicy(inputfile, outdir, service_dir, config, signer, ct, export_compartments, export_regions,policy_detail)



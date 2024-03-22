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
import Security
from oci.network_firewall import NetworkFirewallClient
sys.path.append(os.getcwd() + "/..")
from commonTools import *

importCommands = {}
oci_obj_names = {}


def delete_firewallpolicy(inputfile, _outdir, service_dir, config, signer, ct, delete_compartments, delete_regions, delete_policy):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global outdir


    outdir = _outdir


     # Delete Network firewall Policy Details
    print("\nDeleting details of Network firewall policy...")
    for reg in delete_regions:
        if delete_regions == "":
            print("\nRegion can not be left empty to clone a policy ")
        else:
            config.__setitem__("region", ct.region_dict[reg])
            fwpolicy = NetworkFirewallClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer= signer)

            region = reg.capitalize()
            if delete_compartments == "":
                print("\nCompartment can not be left empty to delete a policy ")

            else:
                for compartment_name in delete_compartments:
                    if delete_policy != None:
                        policy_detail = ""
                        for eachpolicy in delete_policy:
                            if eachpolicy != "":
                                fwpolicy1 = oci.pagination.list_call_get_all_results(fwpolicy.list_network_firewall_policies, compartment_id=ct.ntk_compartment_ids[compartment_name], display_name=eachpolicy, lifecycle_state="ACTIVE")
                                policy_id = fwpolicy1.data

                                for eachfw in policy_id:
                                    policy_ocid = eachfw.id
                                    policystatus = fwpolicy.get_network_firewall_policy(network_firewall_policy_id=policy_ocid)
                                    if (policystatus.data.attached_network_firewall_count == 0):
                                        delete_policy = fwpolicy.delete_network_firewall_policy(network_firewall_policy_id=policy_ocid)
                                        print("Wait for the policy " + eachpolicy + " to be deleted")
                                        get_delete_status = fwpolicy.get_network_firewall_policy(policy_ocid)
                                        wait_until_policy_cloned = oci.wait_until(fwpolicy, get_delete_status, 'lifecycle_state', "DELETED", max_interval_seconds=30, max_wait_seconds=300)
                                        print(eachpolicy + " has been deleted")
                                    else:
                                        print("Policy " + eachpolicy + " Attached to the firewall can not be deleted")

    Security.cloneexport_firewallpolicy(inputfile, outdir, service_dir, config,signer, ct,delete_compartments, delete_regions, policy_detail)


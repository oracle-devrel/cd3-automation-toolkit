# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

resource "oci_network_firewall_network_firewall_policy_application" "network_firewall_policy_application" {
    #Required
    icmp_type                  = var.icmp_type
    name                       = var.app_list_name
    network_firewall_policy_id = var.network_firewall_policy_id
    type                       = var.app_type

    #Optional
    icmp_code = var.icmp_code
}
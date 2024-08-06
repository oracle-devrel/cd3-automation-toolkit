# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall_policy_application_group" "network_firewall_policy_application_group" {
    #Required
    apps = var.apps
    name = var.app_group_name
    network_firewall_policy_id = var.network_firewall_policy_id
}
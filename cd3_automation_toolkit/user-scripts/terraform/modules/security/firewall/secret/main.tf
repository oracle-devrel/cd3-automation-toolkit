# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall_policy_mapped_secret" "network_firewall_policy_mapped_secret" {
    #Required
    name = var.secret_name
    network_firewall_policy_id = var.network_firewall_policy_id
    source = var.secret_source
    type = var.secret_type
    vault_secret_id = local.secret_ocid
    version_number = var.version_number
}
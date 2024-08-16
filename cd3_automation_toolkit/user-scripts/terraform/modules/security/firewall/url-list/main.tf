# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall_policy_url_list" "network_firewall_policy_url_list" {
  name = var.urllist_name
  network_firewall_policy_id = var.network_firewall_policy_id
  dynamic "urls" {
    for_each = var.urls_details != null ? var.urls_details : []
    content {
      pattern = urls.value.pattern
      type    = urls.value.type
    }
  }
}

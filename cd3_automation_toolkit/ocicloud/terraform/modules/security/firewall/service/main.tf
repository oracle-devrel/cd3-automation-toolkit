# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall_policy_service" "network_firewall_policy_service" {
  name = var.service_name
  network_firewall_policy_id = var.network_firewall_policy_id
  dynamic "port_ranges" {
    for_each = var.port_ranges != null ? var.port_ranges : []
    #for_each = var.service_port_ranges[var.key_name].port_ranges != null ? var.service_port_ranges[var.key_name].port_ranges : []
    /*content {
      minimum_port = port_ranges.value.minimum_port
      maximum_port = port_ranges.value.maximum_port
    }*/
    content {
      minimum_port = port_ranges.value.minimum_port
      maximum_port = port_ranges.value.maximum_port
    }
  }

  type = var.service_type
}

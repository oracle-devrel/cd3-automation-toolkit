# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
/*
locals {
  services = var.services != null ? flatten(tolist([for  sid in var.services : (length(regexall("ocid1.networkfirewallpolicy.oc*", sid)) > 0 ? [sid] : data.oci_network_firewall_network_firewall_policy_services.fw-services[sid].*.name)])) : null

}
data "oci_network_firewall_network_firewall_policy_services" "fw-services" {
  for_each = var.services != null ? { for sid in var.services : sid => sid } : {}
  network_firewall_policy_id = var.network_firewall_policy_id
  display_name = each.value
}
*/
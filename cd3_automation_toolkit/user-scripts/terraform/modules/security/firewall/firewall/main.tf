# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_network_firewall_network_firewall" "network_firewall" {
  compartment_id = var.compartment_id
  network_firewall_policy_id = var.network_firewall_policy_id
  subnet_id = var.subnet_id
  display_name = var.display_name
  ipv4address = var.ipv4address
  ipv6address = var.ipv6address
  availability_domain = var.availability_domain
  network_security_group_ids = var.nsg_id != null ? (local.nsg_id == [] ? ["INVALID NSG Name"] : local.nsg_id) : null
  defined_tags          = var.defined_tags
  freeform_tags         = var.freeform_tags
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], defined_tags["SE_Details.SE_Name"]]
  }
}

# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Load Balancer
# Create Load Balancer
############################

resource "oci_load_balancer_load_balancer" "load_balancer" {
  #Required
  compartment_id = var.compartment_id
  display_name   = var.display_name
  shape          = var.shape
  #subnet_ids     = var.subnet_ids
  subnet_ids = flatten(tolist([for subnet in var.subnet_ids : (length(regexall("ocid1.subnet.oc*", subnet)) > 0 ? [subnet] : data.oci_core_subnets.oci_subnets_lbs[subnet].subnets[*].id)]))


  #Optional
  defined_tags               = var.defined_tags
  freeform_tags              = var.freeform_tags
  ip_mode                    = var.ip_mode
  is_private                 = var.is_private
  network_security_group_ids = var.network_security_group_ids != null ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : null

  dynamic "reserved_ips" {
    for_each = var.reserved_ips_id != [] ? var.reserved_ips_id : []
    content {
      #Optional
      id = reserved_ips.value
    }
  }

  dynamic "shape_details" {
    for_each = var.load_balancers[var.key_name].shape_details != null ? var.load_balancers[var.key_name].shape_details : []
    content {
      #Required
      maximum_bandwidth_in_mbps = shape_details.value.maximum_bandwidth_in_mbps
      minimum_bandwidth_in_mbps = shape_details.value.minimum_bandwidth_in_mbps
    }
  }

  lifecycle {
    ignore_changes = [reserved_ips]
  }

}
# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Storage
# Create MTs
############################

resource "oci_file_storage_mount_target" "mount_target" {
  #Required
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  subnet_id           = var.subnet_id
  #Optional
  defined_tags   = var.defined_tags
  display_name   = var.display_name
  freeform_tags  = var.freeform_tags
  hostname_label = var.hostname_label
  ip_address     = var.ip_address
  nsg_ids        = var.network_security_group_ids != null ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : null
}
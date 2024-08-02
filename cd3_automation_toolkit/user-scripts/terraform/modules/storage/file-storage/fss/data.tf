# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
data "oci_file_storage_filesystem_snapshot_policies" "filesystem_snapshot_policies" {
  #Required
  count               = var.filesystem_snapshot_policy_id != null ? 1 : 0
  availability_domain = var.availability_domain
  compartment_id      = var.policy_compartment_id
  state        = "Active"
   filter {
    name   = "display_name"
    values = [var.filesystem_snapshot_policy_id]
  }
}

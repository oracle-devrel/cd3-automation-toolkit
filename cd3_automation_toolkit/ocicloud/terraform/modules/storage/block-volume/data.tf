# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Data Block - Block Volume
## Create Block Volume and Block Volume Backup Policy
################################

locals {
  compartment_id      = var.compartment_id
  availability_domain = var.availability_domain
}

data "oci_core_volumes" "all_volumes" {
  depends_on = [oci_core_volume.block_volume]
  count      = var.block_tf_policy != null ? 1 : 0
  #Required
  compartment_id = var.compartment_id
  state          = "AVAILABLE"
  filter {
    name   = "display_name"
    values = [var.display_name]
  }
  filter {
    name   = "state"
    values = ["AVAILABLE"]
  }
}

data "oci_core_volume_backup_policies" "block_vol_backup_policy" {
  count = var.block_tf_policy != null ? 1 : 0
  filter {
    name   = "display_name"
    values = [lower(var.block_tf_policy)]
  }
}

data "oci_core_volume_backup_policies" "block_vol_custom_policy" {
  count          = var.block_tf_policy != null ? 1 : 0
  compartment_id = local.policy_tf_compartment_id
  filter {
    name   = "display_name"
    values = [var.block_tf_policy]
  }
}
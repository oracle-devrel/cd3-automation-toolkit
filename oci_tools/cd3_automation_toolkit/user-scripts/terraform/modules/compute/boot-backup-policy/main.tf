// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

####################################
## Resource Block - Backup Policy
## Create Block Volume Backup Policy
####################################

data "oci_core_boot_volumes" "all_boot_volumes" {
  count     = var.boot_tf_policy != "" ? 1 : 0
  #Required
  compartment_id = var.compartment_id
  availability_domain =  var.availability_domain
  filter {
    name   = "display_name"
    values = [var.display_name]
  }
}

data "oci_core_volume_backup_policies" "boot_vol_backup_policy" {
  count     = var.boot_tf_policy != "" ? 1 : 0
  filter {
    name   = "display_name"
    values = [var.boot_tf_policy]
  }
}

data "oci_core_volume_backup_policies" "block_vol_custom_policy" {
  count     = var.boot_tf_policy != "" ? 1 : 0
  compartment_id = local.policy_tf_compartment_id
  filter {
    name   = "display_name"
    values = [var.boot_tf_policy]
  }
}

locals {
  policy_tf_compartment_id = var.policy_tf_compartment_id != "" ? var.policy_tf_compartment_id : ""
  current_policy_id        = var.boot_tf_policy != "" ? (var.boot_tf_policy == "gold" || var.boot_tf_policy == "silver" || var.boot_tf_policy == "bronze" ? data.oci_core_volume_backup_policies.boot_vol_backup_policy[0].volume_backup_policies.0.id : "") : ""
}

resource "oci_core_volume_backup_policy_assignment" "volume_backup_policy_assignment" {
  count     = var.boot_tf_policy != "" ? 1 : 0
  asset_id  = data.oci_core_boot_volumes.all_boot_volumes[0].boot_volumes.0.id
  policy_id = local.current_policy_id
}


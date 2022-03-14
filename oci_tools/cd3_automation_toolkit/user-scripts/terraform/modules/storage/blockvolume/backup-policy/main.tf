#// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
#
####################################
## Resource Block - Backup Policy
## Create Block Volume Backup Policy
####################################

data "oci_core_volumes" "all_volumes" {
  #Required
  compartment_id = var.compartment_id
  state          = "AVAILABLE"
  filter {
    name   = "display_name"
    values = [var.display_name]
  }
}

data "oci_core_volume_backup_policies" "block_vol_backup_policy" {
  filter {
    name   = "display_name"
    values = [var.block_tf_policy]
  }
}

data "oci_core_volume_backup_policies" "block_vol_custom_policy" {
  compartment_id = local.policy_tf_compartment_id
  filter {
    name   = "display_name"
    values = [var.block_tf_policy]
  }
}

locals {
  existing_volume_id       = length(data.oci_core_volumes.all_volumes.volumes) > 0 ? length(regexall("ocid1.volume.oc1*", data.oci_core_volumes.all_volumes.volumes[0].id)) > 0 ? data.oci_core_volumes.all_volumes.volumes[0].id : "" : ""
  policy_tf_compartment_id = var.policy_tf_compartment_id != "" ? var.policy_tf_compartment_id : ""
  current_policy_id        = var.block_tf_policy == "gold" || var.block_tf_policy == "silver" || var.block_tf_policy == "bronze" ? data.oci_core_volume_backup_policies.block_vol_backup_policy.volume_backup_policies.0.id : data.oci_core_volume_backup_policies.block_vol_custom_policy.volume_backup_policies.0.id
}

resource "oci_core_volume_backup_policy_assignment" "volume_backup_policy_assignment" {
  count     = var.block_tf_policy != "" ? 1 : 0
  asset_id  = data.oci_core_volumes.all_volumes.volumes[0].id
  policy_id = local.current_policy_id
}


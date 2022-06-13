// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Resource Block - Block Volume
## Create Block Volume
################################

resource "oci_core_volume" "block_volume" {
  availability_domain  = local.availability_domain
  compartment_id       = local.compartment_id
  freeform_tags        = var.freeform_tags
  defined_tags         = var.defined_tags
  display_name         = var.display_name
  is_auto_tune_enabled = var.is_auto_tune_enabled
  vpus_per_gb          = var.vpus_per_gb
  kms_key_id           = var.kms_key_id
  size_in_gbs          = var.size_in_gbs

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], freeform_tags]
  }
}

resource "oci_core_volume_attachment" "block_vol_instance_attachment" {
  count           = var.attachment_type != "" && var.attachment_type != null ? 1 : 0
  attachment_type = var.attachment_type
  instance_id     = var.attach_to_instance
  volume_id       = oci_core_volume.block_volume.id

  #optional
  device                              = var.device
  display_name                        = var.attachment_display_name
  encryption_in_transit_type          = var.encryption_in_transit_type          # Applicable when attachment_type=iscsi
  is_pv_encryption_in_transit_enabled = var.is_pv_encryption_in_transit_enabled # Applicable when attachment_type=paravirtualized
  is_read_only                        = var.is_read_only
  is_shareable                        = var.is_shareable
  use_chap                            = var.use_chap # Applicable when attachment_type=iscsi

}

// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

####################################
## Resource Block - Backup Policy
## Create Block Volume Backup Policy
####################################

locals {
  #existing_volume_id       = length(data.oci_core_volumes.all_volumes[0].volumes) > 0 ? length(regexall("ocid1.volume.oc1*", data.oci_core_volumes.all_volumes[0].volumes[0].id)) > 0 ? data.oci_core_volumes.all_volumes[0].volumes[0].id : "" : ""
  policy_tf_compartment_id = var.policy_tf_compartment_id != "" ? var.policy_tf_compartment_id : ""
  current_policy_id        = var.block_tf_policy != "" ? (lower(var.block_tf_policy) == "gold" || lower(var.block_tf_policy) == "silver" || lower(var.block_tf_policy) == "bronze" ? data.oci_core_volume_backup_policies.block_vol_backup_policy[0].volume_backup_policies.0.id : data.oci_core_volume_backup_policies.block_vol_custom_policy[0].volume_backup_policies.0.id) : ""
}

resource "oci_core_volume_backup_policy_assignment" "volume_backup_policy_assignment" {
  depends_on = [oci_core_volume.block_volume]
  count      = var.block_tf_policy != "" ? 1 : 0
  asset_id   = data.oci_core_volumes.all_volumes[0].volumes[0].id
  policy_id  = local.current_policy_id
}
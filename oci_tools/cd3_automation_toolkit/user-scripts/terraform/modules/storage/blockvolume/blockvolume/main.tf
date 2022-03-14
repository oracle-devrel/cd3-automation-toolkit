#// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
#
################################
## Resource Block - Block Volume
## Create Block Volume
################################

resource "oci_core_volume" "block_volume" {
  availability_domain  = local.availability_domain
  compartment_id       = var.compartment_id
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
  count           = var.attach_to_instance == "" ? 0 : 1
  attachment_type = var.attachment_type
  instance_id     = data.oci_core_instances.instance.instances[0].id
  volume_id       = oci_core_volume.block_volume.id
}

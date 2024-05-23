// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Storage
# Create FSS Replication
############################

resource "oci_file_storage_replication" "file_system_replication" {
  #Required
  compartment_id      = var.compartment_id
  source_id           = var.source_id
  target_id           = var.target_id
  #Optional
  defined_tags       = var.defined_tags
  display_name       = var.display_name
  freeform_tags      = var.freeform_tags
  replication_interval = var.replication_interval

}

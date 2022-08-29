// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Storage
# Create FSS
############################

resource "oci_file_storage_file_system" "file_system" {
    #Required
    availability_domain = var.availability_domain
    compartment_id = var.compartment_id

    #Optional
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags
    kms_key_id = var.kms_key_id
    source_snapshot_id = var.source_snapshot_id
    lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}

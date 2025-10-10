# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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

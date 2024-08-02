# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Storage
# Create FSS
############################

resource "oci_file_storage_file_system" "file_system" {
  #Required
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id

  #Optional
  defined_tags       = var.defined_tags
  display_name       = var.display_name
  freeform_tags      = var.freeform_tags
  kms_key_id         = var.kms_key_id
  source_snapshot_id = var.source_snapshot_id
  filesystem_snapshot_policy_id = var.filesystem_snapshot_policy_id != null ? (length(regexall("ocid1.filesystemsnapshotpolicy.oc*", var.filesystem_snapshot_policy_id)) > 0 ? var.filesystem_snapshot_policy_id : data.oci_file_storage_filesystem_snapshot_policies.filesystem_snapshot_policies[0].filesystem_snapshot_policies[0].id) : null

}

# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Storage
# Create Export Options
############################

resource "oci_file_storage_export" "export" {
  #Required
  export_set_id  = var.export_set_id
  file_system_id = var.file_system_id
  path           = var.export_path

  #Optional
  dynamic "export_options" {
    for_each = var.nfs_export_options[var.key_name].export_options != null ? var.nfs_export_options[var.key_name].export_options : []

    content {
      #Required
      source = export_options.value.source

      #Optional
      access                         = export_options.value.access
      allowed_auth                   = export_options.value.allowed_auth
      anonymous_gid                  = export_options.value.anonymous_gid
      anonymous_uid                  = export_options.value.anonymous_uid
      identity_squash                = export_options.value.identity_squash
      is_anonymous_access_allowed    = export_options.value.is_anonymous_access_allowed
      require_privileged_source_port = export_options.value.require_privileged_source_port
    }
  }
  is_idmap_groups_for_sys_auth  = var.is_idmap_groups_for_sys_auth
}
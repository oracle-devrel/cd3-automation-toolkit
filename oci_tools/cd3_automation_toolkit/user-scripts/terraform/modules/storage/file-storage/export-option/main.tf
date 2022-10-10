// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
    for_each = var.nfs_export_options[var.key_name].export_options != [] ? var.nfs_export_options[var.key_name].export_options : []

    content {
      #Required
      source = export_options.value.source

      #Optional
      access                         = export_options.value.access != "" ? export_options.value.access : null
      anonymous_gid                  = export_options.value.anonymous_gid != "" ? export_options.value.anonymous_gid : null
      anonymous_uid                  = export_options.value.anonymous_uid != "" ? export_options.value.anonymous_uid : null
      identity_squash                = export_options.value.identity_squash != "" ? export_options.value.identity_squash : null
      require_privileged_source_port = export_options.value.require_privileged_source_port != "" ? export_options.value.require_privileged_source_port : null
    }
  }
}
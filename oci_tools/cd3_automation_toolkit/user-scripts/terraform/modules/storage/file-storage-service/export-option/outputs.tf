// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Storage
# Create Export Options
############################

output "export_options_tf_id" {
  value = oci_file_storage_export.export.id
}
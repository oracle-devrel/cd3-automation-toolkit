// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Storage
# Create FSS
############################

output "fss_tf_id" {
  value = oci_file_storage_file_system.file_system.id
}

// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Storage
# Create FSS Replication
############################

output "fss_replication_tf_id" {
  value = oci_file_storage_replication.file_system_replication.id
}

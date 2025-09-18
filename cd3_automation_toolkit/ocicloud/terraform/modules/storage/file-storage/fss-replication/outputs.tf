# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Storage
# Create FSS Replication
############################

output "fss_replication_tf_id" {
  value = oci_file_storage_replication.file_system_replication.id
}

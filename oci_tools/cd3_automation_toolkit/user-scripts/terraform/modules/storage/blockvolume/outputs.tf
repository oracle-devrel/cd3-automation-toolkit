// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Block Volume
## Create Block Volume and Block Volume Backup Policy
################################

output "block_volume_tf_id" {
  value = oci_core_volume.block_volume.id
}
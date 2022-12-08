// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Security
## Create Cloud Guard Target
################################

output "cg_target_tf_id" {
  value = oci_cloud_guard_target.target.id
}

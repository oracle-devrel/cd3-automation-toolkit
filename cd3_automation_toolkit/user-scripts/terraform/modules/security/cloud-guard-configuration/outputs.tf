// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Security
## Create Cloud Guard Config
################################

output "cg_config_tf_id" {
  depends_on = [time_sleep.wait_60_seconds]
  value      = oci_cloud_guard_cloud_guard_configuration.cloud_guard_configuration.id
}
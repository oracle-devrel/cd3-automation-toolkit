# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Outputs Block - Security
## Create Cloud Guard Config
################################

output "cg_config_tf_id" {
  depends_on = [time_sleep.wait_60_seconds]
  value      = oci_cloud_guard_cloud_guard_configuration.cloud_guard_configuration.id
}
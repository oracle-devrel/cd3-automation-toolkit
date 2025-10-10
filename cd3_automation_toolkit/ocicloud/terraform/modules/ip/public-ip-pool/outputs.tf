# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Outputs Block - Public IP Pool
## Create Public IP Pool
################################

output "public_ip_pool_tf_id" {
  value = oci_core_public_ip_pool.public_ip_pool.id
}
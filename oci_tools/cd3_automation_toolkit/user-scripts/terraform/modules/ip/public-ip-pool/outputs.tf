// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Public IP Pool
## Create Public IP Pool
################################

output "public_ip_pool_tf_id" {
  value = oci_core_public_ip_pool.public_ip_pool.id
}
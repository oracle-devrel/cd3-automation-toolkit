// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Secondary Private IP
## Create Secondary Private IP
################################

output "private_ip_tf_id" {
  value = oci_core_private_ip.private_ip.id
}
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Reserved IP
## Create Reserved IP
################################

output "reserved_ip_tf_id" {
  value = oci_core_public_ip.public_ip.id
}
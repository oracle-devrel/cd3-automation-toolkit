// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Default Security List
############################

output "default_seclist_tf_id" {
  value = oci_core_default_security_list.default_security_list.id
}
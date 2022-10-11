// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Security List
############################

output "seclist_tf_id" {
  value = oci_core_security_list.security_list.id
}
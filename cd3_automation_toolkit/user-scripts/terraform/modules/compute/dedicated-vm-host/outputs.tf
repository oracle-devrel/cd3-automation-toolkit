// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

###################################
# Outputs Block - Dedicated VM Host
# Create Dedicated VM Hosts
###################################

output "dedicated_host_tf_id" {
  value = oci_core_dedicated_vm_host.dedicated_vm_host.id
}
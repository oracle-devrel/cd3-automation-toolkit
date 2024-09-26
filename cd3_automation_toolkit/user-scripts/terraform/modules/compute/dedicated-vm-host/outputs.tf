# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
###################################
# Outputs Block - Dedicated VM Host
# Create Dedicated VM Hosts
###################################

output "dedicated_host_tf_id" {
  value = oci_core_dedicated_vm_host.dedicated_vm_host.id
}
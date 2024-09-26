# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Resource Block - Dedicated VM Host
## Create Dedicated VM Hosts
#####################################

resource "oci_core_dedicated_vm_host" "dedicated_vm_host" {
  availability_domain     = var.availability_domain
  compartment_id          = var.compartment_id
  dedicated_vm_host_shape = var.vm_host_shape

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  display_name  = var.display_name
  fault_domain  = var.fault_domain
}

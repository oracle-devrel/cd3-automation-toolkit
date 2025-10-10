# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
###################################
## Module Block - Dedicated VM Host
## Create Dedicated VM Hosts
###################################

module "dedicated-hosts" {
  source   = "./modules/compute/dedicated-vm-host"
  for_each = var.dedicated_hosts != null ? var.dedicated_hosts : {}

  availability_domain = each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : null
  compartment_id      = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  defined_tags        = each.value.defined_tags
  freeform_tags       = each.value.freeform_tags
  vm_host_shape       = each.value.vm_host_shape
  display_name        = each.value.display_name
  fault_domain        = each.value.fault_domain

}
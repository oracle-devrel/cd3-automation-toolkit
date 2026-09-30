# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Data Block - Reserved Private IP
## Create Reserved Private IP
#############################

data "oci_core_vcns" "oci_vcn" {
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : null
  display_name   = var.vcn_name
}

data "oci_core_subnets" "oci_subnet" {
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : null
  display_name   = var.subnet_id
  vcn_id         = one(data.oci_core_vcns.oci_vcn.virtual_networks[*].id)
}

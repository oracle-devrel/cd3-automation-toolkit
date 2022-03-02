// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Identity
# Fetch Compartments
############################

#Fetch Compartment Details
data "oci_identity_compartments" "compartments" {
  #Required
  compartment_id = var.tenancy_ocid

  #Optional
  #name = var.compartment_name
  access_level              = "ANY"
  compartment_id_in_subtree = true
  state                     = "ACTIVE"
}


############################
# Data Block - Network
# Fetch ADs
############################

data "oci_identity_availability_domains" "availability_domains" {
  #Required
  compartment_id = var.tenancy_ocid
}


/*
output "compartment_id_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  value = zipmap(data.oci_identity_compartments.compartments.compartments.*.name,data.oci_identity_compartments.compartments.compartments.*.id)
}

output "ads" {
  value = data.oci_identity_availability_domains.availability_domains.availability_domains.*.name
}
*/

################################
# Data Block - Network
# DRG Route Rules and DRG Route Distributions
################################

data "oci_core_drg_route_tables" "drg_route_tables" {
  for_each = (var.data_drg_route_tables != null || var.data_drg_route_tables != {}) ? var.data_drg_route_tables : {}

  #Required
  drg_id = merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"]
  filter {
    name   = "display_name"
    values = [each.value.values]
  }

}


data "oci_core_drg_route_distributions" "drg_route_distributions" {
  for_each = (var.data_drg_route_table_distributions != null || var.data_drg_route_table_distributions != {}) ? var.data_drg_route_table_distributions : {}

  #Required
  drg_id = merge(module.drgs.*...)[each.value.drg_id]["drg_tf_id"]
  filter {
    name   = "display_name"
    values = [each.value.values]
  }

}
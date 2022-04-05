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
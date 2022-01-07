// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Compartments
############################

output "compartment_id" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = zipmap(oci_identity_compartment.compartment.*.name,oci_identity_compartment.compartment.*.id)
}

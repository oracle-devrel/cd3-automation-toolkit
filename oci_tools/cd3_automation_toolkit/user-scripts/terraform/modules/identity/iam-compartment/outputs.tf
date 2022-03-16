// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Compartments
############################

output "compartment_tf_id" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  value = oci_identity_compartment.compartment.id
}

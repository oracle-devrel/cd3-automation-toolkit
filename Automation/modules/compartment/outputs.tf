// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Compartments
############################

output "compartment_tf_id" {
  description = "Compartment ocid"
  value = oci_identity_compartment.compartment.id
}

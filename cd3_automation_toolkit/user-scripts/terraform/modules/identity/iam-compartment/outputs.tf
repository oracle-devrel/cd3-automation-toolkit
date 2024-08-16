# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Identity
# Create Compartments
############################

output "compartment_tf_id" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  value = oci_identity_compartment.compartment.id
}

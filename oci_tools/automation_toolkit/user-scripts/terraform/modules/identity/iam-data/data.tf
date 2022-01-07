// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Identity
# Fetch Compartments
############################

#Fetch Compartment Details
data "oci_identity_compartments" "compartments" {
    #Required
    compartment_id = var.compartment_id

    #Optional
    #name = var.compartment_name
    access_level = "ANY"
    compartment_id_in_subtree = true
    state = "ACTIVE"
}


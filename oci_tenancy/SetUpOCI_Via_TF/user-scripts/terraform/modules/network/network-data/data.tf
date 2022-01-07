// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Data Block - Networking
# Fetch VCNs
############################

data "oci_core_vcns" "vcns" {
    #Required
    compartment_id = var.compartment_id

    #Optional
    #display_name = var.display_name
    state = "AVAILABLE"
}

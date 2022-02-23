// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Data Block - Network
# Fetch ADs
############################

data "oci_identity_availability_domains" "availability_domains" {
  #Required
  compartment_id = var.tenancy_ocid
}

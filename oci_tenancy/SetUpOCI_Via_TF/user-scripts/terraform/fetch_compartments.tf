// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - Identity
# Fetch Compartments
############################

module "fetch-compartments" {
  source         = "./modules/identity/iam-data"
  compartment_id = var.tenancy_ocid
}

/*
output "compartment_id_map" {
  value = module.fetch-compartments.compartment_id_map
}
*/
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - Network
# Fetch VCNs
############################

module "fetch-vcns" {
  source         = "./modules/network/network-data/vcns"
  for_each = var.vcns != null ? var.vcns : {}
  compartment_id = try(zipmap(data.oci_identity_compartments.compartments.compartments.*.name,data.oci_identity_compartments.compartments.compartments.*.id)[each.value.compartment_name],var.compartment_ocids[0][each.value.compartment_name])

}

/*
output "vcn_id_map" {
  depends_on = [module.vcns, module.fetch-vcns, module.fetch-compartments]
  value      = [ for k,v in merge(module.fetch-vcns.*...) : v.vcns ]
}
*/

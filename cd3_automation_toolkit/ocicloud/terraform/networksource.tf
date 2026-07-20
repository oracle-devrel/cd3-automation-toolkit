# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#


############################
# Module - Network Source
# Create Network Source
############################

#locals {
#
#vcns = flatten ([
#for key, val in var.networkSources : [
# for k,virtual_source in val.virtual_source_list  != null ? val.virtual_source_list : [] :{
#	 vcn_name = virtual_source.vcn_name.0
#	 network_compartment = virtual_source.network_compartment_id.0
#	 }
#	]
#])
#}

#data "oci_core_vcns" "oci_vcns_networksource" {
#
#	for_each        = { for vcn in local.vcns : vcn.vcn_name => vcn... }
#	display_name    = each.key
#	compartment_id  = var.compartment_ocids[each.value[0].network_compartment]
#}

module "iam-network-sources" {
  source       = "./modules/identity/iam-network-sources"
  for_each     = var.networkSources
  name         = each.value.name
  description  = each.value.description
  tenancy_ocid = var.tenancy_ocid

  #Optional
  public_source_list = each.value.public_source_list != null ? each.value.public_source_list : null
  #virtual_source_list  = each.value.virtual_source_list != null ? each.value.virtual_source_list : null
  virtual_source_list = { for k, v in each.value.virtual_source_list != null ? each.value.virtual_source_list : [] : k =>
    {
      #vcn_id = data.oci_core_vcns.oci_vcns_networksource[v.vcn_name.0].virtual_networks.*.id[0]
      ip_ranges = v.ip_ranges
  } }
  #vcn_comp_map = each.value.vcn_comp_map != null ? each.value.vcn_comp_map : null
  defined_tags  = try(each.value.defined_tags, null)
  freeform_tags = try(each.value.freeform_tags, null)
}

# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Identity
# Create Compartments
############################

module "iam-compartments" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.root != null ? var.compartments.root : {}

  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = each.value.parent_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])) : var.tenancy_ocid
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level1" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level1 != null ? var.compartments.compartment_level1 : {}

  depends_on = [module.iam-compartments]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id], merge(module.iam-compartments.*...)[each.value.parent_compartment_id]["compartment_tf_id"])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level2" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level2 != null ? var.compartments.compartment_level2 : {}

  depends_on = [module.sub-compartments-level1]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id], merge(module.sub-compartments-level1.*...)[each.value.parent_compartment_id]["compartment_tf_id"])
  compartment_name        = each.value.name
  compartment_description = each.value.description

  enable_delete = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level3" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level3 != null ? var.compartments.compartment_level3 : {}

  depends_on = [module.sub-compartments-level2]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id], merge(module.sub-compartments-level2.*...)[each.value.parent_compartment_id]["compartment_tf_id"])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level4" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level4 != null ? var.compartments.compartment_level4 : {}

  depends_on = [module.sub-compartments-level3]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id], merge(module.sub-compartments-level3.*...)[each.value.parent_compartment_id]["compartment_tf_id"])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level5" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level5 != null ? var.compartments.compartment_level5 : {}

  depends_on = [module.sub-compartments-level4]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id], merge(module.sub-compartments-level4.*...)[each.value.parent_compartment_id]["compartment_tf_id"])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "root_compartments_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.iam-compartments.*...) : v.compartment_tf_id]
}

output "sub_compartments_level1_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level1.*...) : v.compartment_tf_id]
}

output "sub_compartments_level2_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level2.*...) : v.compartment_tf_id]
}

output "sub_compartments_level3_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level3.*...) : v.compartment_tf_id]
}

output "sub_compartments_level4_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level4.*...) : v.compartment_tf_id]
}

output "sub_compartments_level5_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level5.*...) : v.compartment_tf_id]
}
*/


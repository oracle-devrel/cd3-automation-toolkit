# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Storage
# Create Tag Namespaces, Tag Keys and Default Tags
############################

module "tag-namespaces" {
  source   = "./modules/governance/tagging/tag-namespace"
  for_each = (var.tag_namespaces != null || var.tag_namespaces != {}) ? var.tag_namespaces : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  description    = each.value.description != "" ? each.value.description : each.value.name
  name           = each.value.name

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  is_retired    = each.value.is_retired

}

module "tag-keys" {
  source   = "./modules/governance/tagging/tag-key"
  for_each = (var.tag_keys != null || var.tag_keys != {}) ? var.tag_keys : {}

  #Required
  tag_namespace_id = length(regexall("ocid1.tagnamespace.oc*", each.value.tag_namespace_id)) > 0 ? each.value.tag_namespace_id : merge(module.tag-namespaces.*...)[each.value.tag_namespace_id]["namespace_tf_id"]
  description      = each.value.description != "" ? each.value.description : each.value.name
  name             = each.value.name

  #Optional
  defined_tags     = each.value.defined_tags
  freeform_tags    = each.value.freeform_tags
  is_cost_tracking = each.value.is_cost_tracking
  key_name         = each.key
  is_retired       = each.value.is_retired
  tag_keys         = var.tag_keys
}

module "tag-defaults" {
  source   = "./modules/governance/tagging/tag-default"
  for_each = (var.tag_defaults != null || var.tag_defaults != {}) ? var.tag_defaults : {}

  #Required
  compartment_id    = length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : try(zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.compartment_id], var.compartment_ocids[each.value.compartment_id])
  tag_definition_id = length(regexall("ocid1.tagdefinition.oc*", each.value.tag_definition_id)) > 0 ? each.value.tag_definition_id : merge(module.tag-keys.*...)[each.value.tag_definition_id]["tag_key_tf_id"]
  value             = each.value.value

  #Optional
  is_required = each.value.is_required
}
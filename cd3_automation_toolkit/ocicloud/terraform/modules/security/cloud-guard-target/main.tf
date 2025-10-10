# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Security
## Create Cloud Guard Target
################################

resource "oci_cloud_guard_detector_recipe" "cloned_detector_recipes" {
  for_each                  = local.detector_recipes
  compartment_id            = var.compartment_id
  display_name              = format("%s%s", var.prefix, trimprefix(each.key, "OCI"))
  source_detector_recipe_id = each.value
}


resource "oci_cloud_guard_responder_recipe" "cloned_responder_recipes" {
  for_each                   = local.responder_recipes
  compartment_id             = var.compartment_id
  display_name               = format("%s%s", var.prefix, trimprefix(each.key, "OCI"))
  source_responder_recipe_id = each.value
}

resource "oci_cloud_guard_target" "target" {
  #Required
  compartment_id       = var.compartment_id
  display_name         = var.display_name
  target_resource_id   = var.target_resource_id
  target_resource_type = var.target_resource_type

  #Optional
  defined_tags  = var.defined_tags
  description   = var.description
  freeform_tags = var.freeform_tags
  state         = var.state

  dynamic "target_detector_recipes" {
    for_each = oci_cloud_guard_detector_recipe.cloned_detector_recipes
    content {
      #Required
      detector_recipe_id = target_detector_recipes.value.id

      #Optional
      dynamic "detector_rules" {
        for_each = try(target_detector_recipes.value.id.value.detector_rules, [])
        content {
          #Required
          details {
            #Optional
            condition_groups {
              #Required
              compartment_id = detector_rules.value.compartment_id
              condition      = detector_rules.value.condition
            }
          }
          detector_rule_id = detector_rules.value.detector_rule_id
        }
      }
    }
  }
  dynamic "target_responder_recipes" {
    for_each = oci_cloud_guard_responder_recipe.cloned_responder_recipes
    content {
      #Required
      responder_recipe_id = target_responder_recipes.value.id
      #Optional
      dynamic "responder_rules" {
        for_each = try(target_responder_recipes.value.responder_rules, [])
        content {
          #Required
          details {

            #Optional
            condition = responder_rules.value.condition
            configurations {
              #Required
              config_key = responder_rules.value.config_key
              name       = responder_rules.value.name
              value      = responder_rules.value.value
            }
            mode = responder_rules.value.mode
          }
          responder_rule_id = responder_rules.value.responder_rule_id
        }
      }
    }
  }
}
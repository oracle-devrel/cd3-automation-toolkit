// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Resource Block - Security
## Create Cloud Guard Target
################################

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
    for_each = var.target_detector_recipes != [] ? var.target_detector_recipes : []
    content {
      #Required
      detector_recipe_id = local.recipes[target_detector_recipes.value.detector_recipe_id]

      #Optional
      dynamic "detector_rules" {
        for_each = target_detector_recipes.value.detector_rules != [] ? target_detector_recipes.value.detector_rules : []
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
    for_each = var.target_responder_recipes != [] ? var.target_responder_recipes : []
    content {
      #Required
      responder_recipe_id = local.recipes[target_responder_recipes.value.responder_recipe_id]

      #Optional
      dynamic "responder_rules" {
        for_each = target_responder_recipes.value.responder_rules != [] ? target_responder_recipes.value.responder_rules : []
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
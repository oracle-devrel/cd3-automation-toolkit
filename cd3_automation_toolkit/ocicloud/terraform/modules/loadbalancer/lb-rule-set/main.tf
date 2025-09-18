# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Load Balancer
# Create Load Balancer Rule Set
############################

resource "oci_load_balancer_rule_set" "rule_set" {

  # Access Control Rules
  dynamic "items" {
    for_each = var.rule_sets[var.key_name].access_control_rules != null ? var.rule_sets[var.key_name].access_control_rules : []
    content {
      #Required
      action = items.value.action
      conditions {
        #Required
        attribute_name  = items.value.attribute_name
        attribute_value = items.value.attribute_value
      }
      description = items.value.description
    }
  }

  # Access Control Method Rules
  dynamic "items" {
    for_each = var.rule_sets[var.key_name].access_control_method_rules != null ? var.rule_sets[var.key_name].access_control_method_rules : []
    content {
      #Required
      action = items.value.action

      #Optional
      allowed_methods = items.value.allowed_methods
      status_code     = items.value.status_code
    }
  }

  # HTTP Header Rules
  dynamic "items" {
    for_each = var.rule_sets[var.key_name].http_header_rules != null ? var.rule_sets[var.key_name].http_header_rules : []
    content {
      #Required
      action                         = items.value.action
      are_invalid_characters_allowed = items.value.are_invalid_characters_allowed
      http_large_header_size_in_kb   = items.value.http_large_header_size_in_kb
    }
  }

  # URI Redirect Rules
  dynamic "items" {
    for_each = var.rule_sets[var.key_name].uri_redirect_rules != null ? var.rule_sets[var.key_name].uri_redirect_rules : []
    content {
      #Required
      action = items.value.action
      conditions {
        #Required
        attribute_name  = items.value.attribute_name
        attribute_value = items.value.attribute_value

        #Optional
        operator = items.value.operator
      }
      redirect_uri {
        #Optional
        host     = items.value.host
        path     = items.value.path
        port     = items.value.port
        protocol = items.value.protocol
        query    = items.value.query
      }
      response_code = items.value.response_code
    }
  }

  # Request Response Header Rules
  dynamic "items" {
    for_each = var.rule_sets[var.key_name].request_response_header_rules != null ? var.rule_sets[var.key_name].request_response_header_rules : []
    content {
      #Required
      action = items.value.action
      header = items.value.header
      prefix = items.value.prefix
      suffix = items.value.suffix
      value  = items.value.value
    }
  }

  load_balancer_id = var.load_balancer_id
  name             = var.name
}
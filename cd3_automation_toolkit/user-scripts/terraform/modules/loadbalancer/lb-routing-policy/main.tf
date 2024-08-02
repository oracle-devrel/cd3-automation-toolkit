// Copyright (c) 2024, 2025, Oracle and/or its affiliates.

#####################################
# Resource Block - Load Balancer
# Create Load Balancer Routing Policy
#####################################

resource "oci_load_balancer_load_balancer_routing_policy" "load_balancer_routing_policy" {
  #Required
  condition_language_version = var.condition_language_version
  load_balancer_id           = var.load_balancer_id
  name                       = var.name

  dynamic rules {
    for_each = var.rules != null ? var.rules : []
    content {
      condition = rules.value.condition
      name      = rules.value.name
      actions {
        name =  "FORWARD_TO_BACKENDSET"
        backend_set_name = rules.value.backend_set_name
      }
    }
  }


}

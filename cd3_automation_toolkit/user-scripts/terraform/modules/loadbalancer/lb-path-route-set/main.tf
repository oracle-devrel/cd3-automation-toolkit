# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Load Balancer
# Create Load Balancer Path Route Set
############################

resource "oci_load_balancer_path_route_set" "path_route_set" {
  #Required
  load_balancer_id = var.load_balancer_id
  name             = var.name
  dynamic "path_routes" {
    for_each = var.path_route_sets[var.key_name].path_routes != null ? var.path_route_sets[var.key_name].path_routes : []
    content {
      #Required
      backend_set_name = path_routes.value.backend_set_name
      path             = path_routes.value.path
      path_match_type {
        #Required
        match_type = path_routes.value.match_type
      }
    }
  }
}
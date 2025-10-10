# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Listener
#######################################

resource "oci_network_load_balancer_listener" "listener" {
  #Required
  default_backend_set_name = var.default_backend_set_name
  name                     = var.name
  network_load_balancer_id = var.network_load_balancer_id
  port                     = var.port
  protocol                 = var.protocol

  #Optional
  ip_version = var.ip_version
}

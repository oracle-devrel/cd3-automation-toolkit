// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Backend
#######################################

resource "oci_network_load_balancer_backend" "backend" {
  #Required
  backend_set_name         = var.backend_set_name
  network_load_balancer_id = var.network_load_balancer_id
  port                     = var.port

  #Optional
  ip_address = var.ip_address
  is_drain   = var.is_drain
  is_offline = var.is_offline
  name       = var.name
  target_id  = var.target_id
  weight     = var.weight
}

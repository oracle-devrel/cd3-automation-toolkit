// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Load Balancer
# Create Load Balancer Backend
############################

resource "oci_load_balancer_backend" "backend" {
  #Required
  backendset_name  = var.backendset_name
  ip_address       = var.ip_address
  load_balancer_id = var.load_balancer_id
  port             = var.port

  #Optional
  backup  = var.backup
  drain   = var.drain
  offline = var.offline
  weight  = var.weight
}
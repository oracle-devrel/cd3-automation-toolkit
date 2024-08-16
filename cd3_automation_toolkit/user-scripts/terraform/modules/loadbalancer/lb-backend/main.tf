# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
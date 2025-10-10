# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Load Balancer
# Create Load Balancer Hostname
############################

resource "oci_load_balancer_hostname" "hostname" {
  #Required
  hostname         = var.hostname
  load_balancer_id = var.load_balancer_id
  name             = var.name

  #Optional
  lifecycle {
    create_before_destroy = true # As per hashicorp terraform
  }
}
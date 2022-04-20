// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
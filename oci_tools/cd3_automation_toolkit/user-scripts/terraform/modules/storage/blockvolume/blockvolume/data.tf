#// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
#
################################
## Data Block - Block Volume
## Create Block Volume
################################
locals {
  compartment_id           = var.compartment_id
  availability_domain      = var.availability_domain
}

data "oci_core_instances" "instance" {
  compartment_id      = local.compartment_id
  display_name        = var.attach_to_instance
  #availability_domain= local.availability_domain
  state               = "RUNNING"
}

data "oci_core_volumes" "all_volumes" {
  #Required
  compartment_id = local.compartment_id
  state          = "AVAILABLE"
  filter {
    name   = "display_name"
    values = [var.display_name]
  }
}
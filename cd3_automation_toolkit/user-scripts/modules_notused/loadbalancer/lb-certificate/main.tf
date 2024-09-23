# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Load Balancer
# Create Load Balancer Certificate
############################

resource "oci_load_balancer_certificate" "certificate" {
  #Required
  certificate_name = var.certificate_name
  load_balancer_id = var.load_balancer_id

  #Optional
  ca_certificate     = var.ca_certificate
  passphrase         = var.passphrase
  private_key        = var.private_key
  public_certificate = var.public_certificate

  lifecycle {
    create_before_destroy = true # As per hashicorp terraform
    ignore_changes        = [ca_certificate, public_certificate, private_key]
  }
}
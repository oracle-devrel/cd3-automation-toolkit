// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Load Balancer
# Create Load Balancer Cipher Suite
############################

resource "oci_load_balancer_ssl_cipher_suite" "ssl_cipher_suite" {
  #Required
  ciphers = var.ciphers
  name    = var.name

  #Optional
  load_balancer_id = var.load_balancer_id

  lifecycle {
    ignore_changes = [ciphers]
  }
}
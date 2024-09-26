# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
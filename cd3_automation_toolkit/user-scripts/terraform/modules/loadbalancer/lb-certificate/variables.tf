# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Load Balancer
# Create Load Balancer Certificate
############################

variable "certificate_name" {
  type        = string
  description = "Name of the certificate"
  default     = null
}

variable "load_balancer_id" {
  type        = string
  description = "The OCID of load balancer"
  default     = null
}

variable "ca_certificate" {
  type        = string
  description = "The Certificate Authority certificate, or any interim certificate"
  default     = null
}

variable "passphrase" {
  type        = string
  description = "A passphrase for encrypted private keys."
  default     = null
}

variable "private_key" {
  type        = string
  description = "The SSL private key for your certificate, in PEM format."
  default     = null
}

variable "public_certificate" {
  type        = string
  description = "The public certificate, in PEM format, that you received from your SSL certificate provider."
  default     = null
}

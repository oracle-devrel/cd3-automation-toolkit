# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Load Balancer
# Create Load Balancer Cipher Suite
############################

variable "ciphers" {
  type        = list(any)
  description = "A list of SSL ciphers the load balancer must support for HTTPS or SSL connections."
  default     = []
}

variable "name" {
  type        = string
  description = "A friendly name for the SSL cipher suite."
  default     = null
}

variable "load_balancer_id" {
  type        = string
  description = "The Load Balancer OCID"
  default     = null
}

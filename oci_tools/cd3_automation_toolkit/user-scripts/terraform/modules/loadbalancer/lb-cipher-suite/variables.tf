// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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

# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Variable Block - Network Load Balancer
# Create Network Load Balancer Listener
#######################################

variable "default_backend_set_name" {
  type        = string
  description = "The name of the associated backend set"
  default     = null
}

variable "network_load_balancer_id" {
  type        = string
  description = "The OCID of load balancer"
  default     = null
}

variable "name" {
  type        = string
  description = "The name of the Listener."
  default     = null
}

variable "port" {
  type        = number
  description = "The communication port for the listener."
  default     = 80 # Default as per example in hashicorp terraform
}

variable "protocol" {
  type        = string
  description = "The protocol on which the listener accepts connection requests."
  default     = null
}

variable "ip_version" {
  type    = string
  default = null
}


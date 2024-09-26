# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Load Balancer
# Create Load Balancer Listener
############################

variable "default_backend_set_name" {
  type        = string
  description = "The name of the associated backend set"
  default     = null
}

variable "load_balancer_id" {
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

variable "hostname_names" {
  type        = list(any)
  description = "An array of hostname resource names."
  default     = []
}

variable "path_route_set_name" {
  type        = string
  description = "Deprecated !! The name of the set of path-based routing rules, PathRouteSet, applied to this listener's traffic."
  default     = null
}

variable "routing_policy_name" {
  type        = string
  description = "The name of the routing policy applied to this listener's traffic."
  default     = null
}

variable "rule_set_names" {
  type        = list(any)
  description = "The names of the rule sets to apply to the listener."
  default     = []
}

variable "key_name" {
  type    = string
  default = null
}

variable "listeners" {}

variable "certificate_name" {
  type    = string
  default = null
}

variable "cipher_suite_name" {
  type    = string
  default = null
}
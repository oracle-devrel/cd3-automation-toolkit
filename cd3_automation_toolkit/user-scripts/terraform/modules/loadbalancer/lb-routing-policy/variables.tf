// Copyright (c) 2024, 2025, Oracle and/or its affiliates.

#####################################
# Variables Block - Load Balancer
# Create Load Balancer Routing Policy
#####################################

variable "condition_language_version" {
  description = "The version of the condition language."
  type        = string
}

variable "load_balancer_id" {
  description = "The OCID of the load balancer."
  type        = string
}

variable "name" {
  description = "The name of the load balancer routing policy."
  type        = string
}

variable "rules" {
  type = list(any)
  default = null
}
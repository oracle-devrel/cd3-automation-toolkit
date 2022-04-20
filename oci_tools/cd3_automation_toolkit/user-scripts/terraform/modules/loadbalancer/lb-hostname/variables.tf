// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Load Balancer
# Create Load Balancer Hostname
############################

variable "hostname" {
  type        = string
  description = "A virtual hostname for load balancer"
  default     = null
}

variable "load_balancer_id" {
  type        = string
  description = "The OCID of load balancer"
  default     = null
}

variable "name" {
  type        = string
  description = "Load Balancer Name"
  default     = null
}

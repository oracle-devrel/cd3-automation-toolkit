# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Load Balancer
# Create Load Balancer Backend
############################

variable "backendset_name" {
  type        = string
  description = "The name of the backend set to add the backend server to."
  default     = null
}

variable "ip_address" {
  type        = string
  description = " The IP address of the backend server."
  default     = null
}

variable "load_balancer_id" {
  type        = string
  description = "The OCID of load balancer"
  default     = null
}

variable "port" {
  type        = number
  description = "The communication port for the backend server."
  default     = 80 # Default value at random
}

variable "backup" {
  type        = bool
  description = "Whether the load balancer should treat this server as a backup unit. If true, the load balancer forwards no ingress traffic to this backend server unless all other backend servers not marked as backup fail the health check policy."
  default     = false # Default value at random
}

variable "drain" {
  type        = bool
  description = "Whether the load balancer should drain this server. Servers marked drain receive no new incoming traffic."
  default     = false # Default value as per hashicorp terraform
}

variable "offline" {
  type        = bool
  description = "Whether the load balancer should treat this server as offline. Offline servers receive no incoming traffic."
  default     = false # Default value as per hashicorp terraform
}

variable "weight" {
  type        = number
  description = "The load balancing policy weight assigned to the server. Backend servers with a higher weight receive a larger proportion of incoming traffic. Weight values must be from 1 to 100."
  default     = 1 # Default value as per hashicorp terraform
}

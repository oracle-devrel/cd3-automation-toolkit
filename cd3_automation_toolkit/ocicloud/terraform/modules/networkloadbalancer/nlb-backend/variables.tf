# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Variable Block - Network Load Balancer
# Create Network Load Balancer Backend
#######################################


variable "instance_compartment" {
  type        = string
  description = "The compartment of the instance"
  default     = null
}

variable "backend_set_name" {
  type        = string
  description = "The name of the backend set to add the backend server to."
  default     = null
}

variable "network_load_balancer_id" {
  type        = string
  description = "The OCID of network load balancer"
  default     = null
}

variable "port" {
  type        = string
  description = " The port of the backend server."
  default     = null
}

variable "vnic_vlan" {
  type        = string
  description = " The VNIC the backend server."
  default     = null
}

variable "ip_address" {
  type        = string
  description = " The IP address of the backend server."
  default     = null
}


variable "is_drain" {
  type        = bool
  description = "Whether the load balancer should drain this server. Servers marked drain receive no new incoming traffic."
  default     = false # Default value as per hashicorp terraform
}

variable "is_backup" {
  type        = bool
  description = "Whether the load balancer should treat this server as a backup unit."
  default     = false # Default value as per hashicorp terraform
}

variable "is_offline" {
  type        = bool
  description = "Whether the load balancer should treat this server as offline. Offline servers receive no incoming traffic."
  default     = false # Default value as per hashicorp terraform
}

variable "name" {
  type    = string
  default = null
}

variable "target_id" {
  type    = string
  default = null
}


variable "weight" {
  type        = number
  description = "The load balancing policy weight assigned to the server. Backend servers with a higher weight receive a larger proportion of incoming traffic. Weight values must be from 1 to 100."
  default     = 1 # Default value as per hashicorp terraform
}

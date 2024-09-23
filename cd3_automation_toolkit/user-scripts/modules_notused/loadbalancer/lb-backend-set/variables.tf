# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Load Balancer
# Create Load Balancer Backend Set
############################

variable "protocol" {
  type        = string
  description = "The protocol the health check must use; either HTTP or TCP."
  default     = "HTTP" # Default as per hashicorp terraform
}

variable "interval_ms" {
  type        = number
  description = "The interval between health checks, in milliseconds"
  default     = 10000 # Default as per hashicorp terraform
}

variable "is_force_plain_text" {
  type        = string
  description = "Specifies if health checks should always be done using plain text instead of depending on whether or not the associated backend set is using SSL."
}

variable "port" {
  type        = number
  description = "The backend server port against which to run the health check."
  default     = 80 # Default value at random
}

variable "response_body_regex" {
  type        = string
  description = "A regular expression for parsing the response body from the backend server"
  default     = null
}

variable "retries" {
  type        = number
  description = " The number of retries to attempt before a backend server is considered unhealthy"
  default     = 3 # Default value as per hashicorp terraform
}

variable "return_code" {
  type        = number
  description = "The status code a healthy backend server should return."
  default     = 200 # Default value as per hashicorp terraform
}

variable "timeout_in_millis" {
  type        = number
  description = "The maximum time, in milliseconds, to wait for a reply to a health check."
  default     = 3000 # Default value as per hashicorp terraform
}

variable "url_path" {
  type        = string
  description = "The path against which to run the health check."
  default     = "/" # Default value as per hashicorp terraform
}

variable "load_balancer_id" {
  type        = string
  description = "The OCID of load balancer"
  default     = null
}

variable "name" {
  type        = string
  description = "The display name of the load balancer backend set"
  default     = null
}

variable "policy" {
  type        = string
  description = "The load balancer policy for the backend set. Allowed Values: ROUND_ROBIN|LEAST_CONNECTIONS|IP_HASH"
  default     = "ROUND_ROBIN" #Default value as per hashicorp terraform
}

variable "key_name" {
  type    = string
  default = null
}

variable "backend_sets" {}

variable "subnet_ids" {
  type        = list(any)
  description = "Subnets to place the load balancer in"
  default     = []
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "ip_mode" {
  type        = string
  description = "Whether the load balancer has an IPv4 or IPv6 IP address"
  default     = "IPV4" #Default value as per hashicorp terraform
}

variable "is_private" {
  type        = bool
  description = "Whether the load balancer has a VCN-local (private) IP address. If True , Load Balancer is private, else it's public"
  default     = "false" #Default value as per hashicorp terraform; Creates a Public Load Balancer
}

variable "network_security_group_ids" {
  type        = list(any)
  description = "NSGs to place the load balancer in"
  default     = []
}

variable "certificate_name" {
  type    = string
  default = null
}

variable "cipher_suite_name" {
  type    = string
  default = null
}
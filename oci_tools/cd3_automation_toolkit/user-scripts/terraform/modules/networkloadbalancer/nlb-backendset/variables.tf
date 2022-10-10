// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Variable Block - Network Load Balancer
# Create Network Load Balancer Backend Set
#######################################

variable "protocol" {
  type        = string
  description = "The protocol the health check must use; either HTTP or TCP."
  default     = null
}

variable "interval_in_millis" {
  type        = number
  description = "The interval between health checks, in milliseconds"
  default     = 10000 # Default as per hashicorp terraform
}

variable "port" {
  type        = number
  description = "The backend server port against which to run the health check."
  default     = null
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
  default     = null
}

variable "timeout_in_millis" {
  type        = number
  description = "The maximum time, in milliseconds, to wait for a reply to a health check."
  default     = 3000 # Default value as per hashicorp terraform
}

variable "url_path" {
  type        = string
  description = "The path against which to run the health check."
  default     = null
}

variable "network_load_balancer_id" {
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
  default     = null
}

variable "ip_version" {
  type    = string
  default = ""
}

variable "is_preserve_source" {
  type    = bool
  default = null
}

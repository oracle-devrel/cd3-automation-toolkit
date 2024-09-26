# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
variable "compartment_id" {
  type        = string
  description = "The OCID of the compartment"
  default     = null
}

variable "network_compartment_id" {
  type        = string
  description = "The OCID of the compartment that has Network components"
  default     = null
}

variable "display_name" {
  type        = string
  description = "The display name of the cluster"
  default     = null
}

variable "vcn_names" {
  type        = list(string)
  description = "The vcn name of the cluster"
  default     = []
}


variable "kubernetes_version" {
  type        = string
  description = "The version of the kubernetes"
  default     = null
}

variable "type" {
  type        = string
  description = "The type of the cluster"
  default     = null
}

variable "cni_type" {
  type        = string
  description = "The configuration for pod networking for the cluster"
  default     = null
}

variable "is_public_ip_enabled" {
  type        = bool
  description = "Whether public IP is enabled for endpoint"
}

variable "nsg_ids" {
  type        = list(any)
  description = "The NSG IDs for endpoint"
  default     = []
}

variable "endpoint_subnet_id" {
  type        = string
  description = "The subnet for the endpoint"
  default     = null
}

variable "is_policy_enabled" {
  type        = bool
  description = "Whether the image verification policy is enabled"
  default     = false
}

variable "policy_kms_key_id" {
  type    = string
  description = "The OCIDs of the KMS key that will be used to verify whether the images are signed by an approved source"
  default = null
}

variable "is_kubernetes_dashboard_enabled" {
  type        = bool
  description = "Whether kubernetes dashboard is enabled"
}

variable "is_tiller_enabled" {
  type        = bool
  description = "Whether tiller is ebabled"
}

variable "is_pod_security_policy_enabled" {
  type        = bool
  description = "Whether a pod security needs to be enabled for the nodepool"
}

variable "pods_cidr" {
  type        = string
  description = "The pod CIDR value"
  default     = null
}

variable "services_cidr" {
  type        = string
  description = "The service CIDR value"
  default     = null
}

variable "service_lb_subnet_ids" {
  type        = list(any)
  description = "The loadbalancer subnet IDs"
  default     = []
}

variable "kms_key_id" {
  type    = string
  default = null
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

variable "volume_defined_tags" {
  type = map(any)
  default = {}
}

variable "volume_freeform_tags" {
  type    = map(any)
  default = {}
}

variable "lb_defined_tags" {
  type = map(any)
  default = {}
}

variable "lb_freeform_tags" {
  type    = map(any)
  default = {}
}


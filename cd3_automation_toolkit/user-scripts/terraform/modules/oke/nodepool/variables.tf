# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy"
  default     = null
}
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

variable "availability_domain" {
  type        = number
  description = "The availability domain for the nodepool"
  default     = null
}

variable "vcn_names" {
  type        = list(any)
  description = "The vcn name of the nodepool"
  default     = null
}

variable "display_name" {
  type        = string
  description = "The display name of the nodepool"
  default     = null
}

variable "cluster_name" {
  type        = string
  description = "The display name of the cluster"
  default     = null
}

variable "kubernetes_version" {
  type        = string
  description = "The version of the kubernetes"
  default     = null
}

variable "ssh_public_key" {
  type        = string
  description = "The SSh key for the nodes"
  default     = null
}

variable "node_shape" {
  type        = string
  description = "The shape of the nodes in nodepool"
  default     = null
}

variable "initial_node_labels" {
  type        = map(any)
  description = "The labels for nodepool"
  default     = {}
}

variable "subnet_id" {
  type        = string
  description = "The subnet of the worker nodepool"
  default     = null
}

variable "size" {
  type        = number
  description = "The size of the nodepool"
  default     = null
}

variable "cni_type" {
  type        = string
  description = "The network configuration for the nodes"
  default     = null
}

variable "fault_domains" {
  type        = list(any)
  description = "fault domain"
  default     = null
}

variable "max_pods_per_node" {
  type        = number
  description = "The maximum nuber of pods in a node"
  default     = null
}

variable "pod_nsg_ids" {
  type        = list(any)
  description = "The nsg ids for pods"
  default     = []
}

variable "pod_subnet_ids" {
  type        = string
  description = "The nsubnets for the pods"
  default     = null
}

variable "worker_nsg_ids" {
  type        = list(any)
  description = "The NSG IDs for nodepool"
  default     = []
}

variable "memory_in_gbs" {
  type        = number
  description = "The node memory in GB"
  default     = null
}

variable "ocpus" {
  type        = number
  description = "The ocpu for the node"
  default     = null
}

variable "image_id" {
  type        = string
  description = "The image ID for node"
  default     = null
}

variable "source_type" {
  type        = string
  description = "The type of the image ID"
  default     = null
}

variable "boot_volume_size_in_gbs" {
  type        = number
  description = "The boot volume size for nodes in nodepool"
  default     = null
}

variable "is_pv_encryption_in_transit_enabled" {
  type        = bool
  description = "Whether in-transit encryptions is enabled for data in persistent volume"
}

variable "kms_key_id" {
  type    = string
  default = null
}

variable "node_defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "node_freeform_tags" {
  type    = map(any)
  default = {}
}
variable "nodepool_defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "nodepool_freeform_tags" {
  type    = map(any)
  default = {}
}


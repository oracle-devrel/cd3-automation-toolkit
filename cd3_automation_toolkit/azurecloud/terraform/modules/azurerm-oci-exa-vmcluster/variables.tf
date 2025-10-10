# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Variables Block - Oracle ExaVM Cluster @Azure
## Create Oracle ExaVM Cluster @Azure
#####################################

# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/oracle_cloud_vm_cluster

variable "resource_group_name" {
  description = "The name of the Resource Group where the Cloud VM Cluster should exist"
  type        = string
}
variable "location" {
  description = "The Azure Region where the Cloud VM Cluster should exist."
  type        = string
}
variable "exadata_infrastructure_id" {
  description = "The OCID of the Cloud Exadata infrastructure."
  type        = string
}
variable "exadata_infrastructure_name" {
  description = "The name of the Cloud Exadata infrastructure."
  type        = string
}
variable "cluster_name" {
  description = "The cluster name for cloud VM cluster. The cluster name must begin with an alphabetic character, and may contain hyphens (-). Underscores (_) are not permitted. The cluster name can be no longer than 11 characters and is not case sensitive."
  type        = string
  default = null
}
variable "display_name" {
  description = "The display name for cloud VM cluster."
  type        = string
  default = null
}
variable "hostname" {
  description = "The prefix forms the first portion of the Exadata VM Cluster host name. Recommended maximum: 12 characters."
  type        = string
  default = null
}

variable "time_zone" {
  description = "The time zone of the Cloud VM Cluster. For details, see Exadata Infrastructure Time Zones."
  type        = string
  default = null
}
variable "license_model" {
  description = "The Oracle license model that applies to the Cloud VM Cluster, either BringYourOwnLicense or LicenseIncluded."
  type        = string
  default = "LicenseIncluded"
}
variable "gi_version" {
  description = "A valid Oracle Grid Infrastructure (GI) software version."
  type        = string
}
variable "system_version" {
  description = "Operating system version of the Exadata image."
  type        = string
  default     = null
}
variable "db_servers" {
  description = "DB Serverset."
  type        = list(string)
  default = null
}
variable "ssh_public_keys" {
  description = "The public key portion of one or more key pairs used for SSH access to the Cloud VM Cluster."
  type        = list(string)
}
variable "tags" {
  description = "A mapping of tags which should be assigned to the Cloud VM Cluster."
  type        = map(string)
  default     = null
}

variable "vnet_id" {
  description = "The ID of the Virtual Network associated with the Cloud VM Cluster."
  type        = string
}

variable "subnet_id" {
  description = "The ID of the subnet associated with the Cloud VM Cluster."
  type        = string
}

variable "backup_subnet_cidr" {
  description = "The backup subnet CIDR of the Virtual Network associated with the Cloud VM Cluster."
  type        = string
  default = null
}

variable "cpu_core_count" {
  description = "The number of CPU cores enabled on the Cloud VM Cluster."
  type        = string
}

variable "memory_size_in_gbs" {
  description = "The memory to be allocated in GBs."
  type        = number
  default = null
}

variable "dbnode_storage_size_in_gbs" {
  description = "The local node storage to be allocated in GBs."
  type        = number
  default = null
}

variable "data_storage_size_in_tbs" {
  description = "The data disk group size to be allocated in TBs."
  type        = number
  default = null
}
variable "data_storage_percentage" {
  description = "The percentage assigned to DATA storage (user data and database files). The remaining percentage is assigned to RECO storage (database redo logs, archive logs, and recovery manager backups). Accepted values are 35, 40, 60 and 80."
  type        = number
  default = null
}
variable "is_local_backup_enabled" {
  description = "If true, database backup on local Exadata storage is configured for the Cloud VM Cluster. If false, database backup on local Exadata storage is not available in the Cloud VM Cluster."
  type        = bool
  default = null
}
variable "is_sparse_diskgroup_enabled" {
  description = "If true, the sparse disk group is configured for the Cloud VM Cluster. If false, the sparse disk group is not created."
  type        = bool
  default = null
}
variable "is_diagnostic_events_enabled" {
  description = "Indicates whether diagnostic collection is enabled for the Cloud VM Cluster. Enabling diagnostic collection allows you to receive Events service notifications for guest VM issues. Diagnostic collection also allows Oracle to provide enhanced service and proactive support for your Exadata system. You can enable diagnostic collection during VM Cluster/Cloud VM Cluster provisioning."
  type = bool
  default = false
}
variable "is_health_monitoring_enabled" {
  description = "Indicates whether health monitoring is enabled for the Cloud VM Cluster. Enabling health monitoring allows Oracle to collect diagnostic data and share it with its operations and support personnel. You may also receive notifications for some events. Collecting health diagnostics enables Oracle to provide proactive support and enhanced service for your system. Optionally enable health monitoring while provisioning a system. "
  type = bool
  default = false
}
variable "is_incident_logs_enabled" {
  description = "Indicates whether incident logs and trace collection are enabled for the Cloud VM Cluster. Enabling incident logs collection allows Oracle to receive Events service notifications for guest VM issues, collect incident logs and traces, and use them to diagnose issues and resolve them. Optionally enable incident logs collection while provisioning a system. "
  type = bool
  default = false
}
variable "domain" {
  description = "The name of the existing OCI Private DNS Zone to be associated with the Cloud VM Cluster. This allow you to specify your own private domain name instead of the default OCI DNS zone (oraclevcn.com)"
  type = string
  default = ""
}
variable "zone_id" {
  description = "The OCID of the existing OCI Private DNS Zone to be associated with the Cloud VM Cluster. This allow you to specify your own private domain name instead of the default OCI DNS zone (oraclevcn.com)"
  type = string
  default = ""
}

variable "mount_point" {
  description = "file mount path"
  type = string
  default = ""
}

variable "size_in_gb" {
  description = "file mount path size in gb"
  type = string
  default = ""
}

variable "scan_listener_port_tcp" {
  description = "listener port"
  type = number
  default = 1521
}

variable "scan_listener_port_tcp_ssl" {
  description = "listener port ssl"
  type = number
  default = 2484
}
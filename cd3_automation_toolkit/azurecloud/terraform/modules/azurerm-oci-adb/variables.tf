# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Variables Block - Oracle ADB @Azure
## Create Oracle ADB @Azure
#####################################

variable "name" {
  description = "Azure resource name which should be used for this Autonomous Database."
  type        = string
}

variable "resource_group_name" {
  description = "The name of Resource Group in Azure"
  type        = string
}

variable "location" {
  description = "The Azure Region where the Autonomous Database should exist. Changing this forces a new Autonomous Database to be created"
  type        = string
}

variable "subnet_id" {
  description = "The ID of the subnet the resource is associated with."
  type        = string
}

variable "display_name" {
  description = "The user-friendly name for the Autonomous Database in OCI. The name does not have to be unique."
  type        = string
}

variable "db_workload" {
  description = "The Autonomous Database workload type. The following values are valid: OLTP, DW, AJD, APEX"
  type        = string
  default     = "OLTP"
}

variable "mtls_connection_required" {
  description = "Specifies if the Autonomous Database requires mTLS connections."
  type        = bool
  default     = false
}
variable "backup_retention_period_in_days" {
  description = "Retention period, in days, for backups."
  type        = number
  default     = 60
}

variable "compute_model" {
  description = "The compute model of the Autonomous Database. This is required if using the computeCount parameter. If using cpuCoreCount then it is an error to specify computeModel to a non-null value. ECPU compute model is the recommended model and OCPU compute model is legacy."
  type        = string
  default     = "ECPU"
}

variable "data_storage_size_in_tbs" {
  description = "The maximum storage that can be allocated for the database, in terabytes."
  type        = number
  default     = 1
}

variable "auto_scaling_for_storage_enabled" {
  description = "Indicates if auto scaling is enabled for the Autonomous Database storage. The default value is false."
  type        = bool
  default     = false
}

variable "virtual_network_id" {
  description = "The ID of the vnet associated with the Autonomous Database."
  type        = string
}

variable "admin_password" {
  description = "The password must be between 12 and 30characters long, and must contain at least 1 uppercase, 1 lowercase, and 1 numeric character. It cannot contain the double quote symbol or the username 'admin', regardless of casing."
  type        = string
  sensitive   = true
}

variable "auto_scaling_enabled" {
  description = " Indicates if auto scaling is enabled for the Autonomous Database CPU core count. The default value is true."
  type        = bool
  default     = true
}

variable "character_set" {
  description = "The character set for the autonomous database. The default is AL32UTF8"
  type        = string
  default     = "AL32UTF8"
}

variable "compute_count" {
  description = "The compute amount (CPUs) available to the database. Minimum and maximum values depend on the compute model and whether the database is an Autonomous Database Serverless instance or an Autonomous Database on Dedicated Exadata Infrastructure. For an Autonomous Database Serverless instance, the ECPU compute model requires a minimum value of one, for databases in the elastic resource pool and minimum value of two, otherwise. Required when using the computeModel parameter. When using cpuCoreCount parameter, it is an error to specify computeCount to a non-null value. Providing computeModel and computeCount is the preferred method for both OCPU and ECPU."
  type        = number
  default     = 2
}

variable "ncharacter_set" {
  description = "The national character set for the autonomous database. The default is AL16UTF16. Allowed values are: AL16UTF16 or UTF8."
  type        = string
  default     = "AL16UTF16"
}

variable "license_model" {
  description = "The Oracle license model that applies to the Oracle Autonomous Database. Bring your own license (BYOL) allows you to apply your current on-premises Oracle software licenses to equivalent, highly automated Oracle services in the cloud. License Included allows you to subscribe to new Oracle Database software licenses and the Oracle Database service. Note that when provisioning an Autonomous Database on dedicated Exadata infrastructure, this attribute must be null. It is already set at the Autonomous Exadata Infrastructure level. When provisioning an Autonomous Database Serverless database, if a value is not specified, the system defaults the value to BRING_YOUR_OWN_LICENSE. Bring your own license (BYOL) also allows you to select the DB edition using the optional parameter."
  type        = string
  default     = "LicenseIncluded"
}

variable "db_version" {
  description = "A valid Oracle Database version for Autonomous Database."
  type        = string
  default     = "19c"
}

variable "customer_contacts" {
  description = "The email address used by Oracle to send notifications regarding databases and infrastructure. Provide up to 10 unique maintenance contact email addresses."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Resource tags for the Cloud Exadata Infrastructure"
  type        = map(string)
  default     = null
}
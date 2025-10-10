# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Object Storage
## Create Object Storage
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "name" {
  description = "Object Storage Bucket name"
  type        = string
}

variable "namespace" {
  description = "Object Storage Bucket namespace"
  type        = string
}

variable "access_type" {
  description = "The type of public access enabled on this bucket."
  type        = string
  default     = null
}

variable "auto_tiering" {
  description = "Set the auto tiering status on the bucket. By default, a bucket is created with auto tiering Disabled"
  type        = string
  default     = false
}

variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the volume"
  type        = map(string)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "kms_key_id" {
description = "The OCID of a master encryption key used to call the Key Management service to generate a data encryption key or to encrypt or decrypt a data #encryption key."
type        = string
}

#variable "metadata" {
#description = "Arbitrary string, up to 4KB, of keys and values for user-defined metadata."
#type        = map(any)
#}



variable "object_events_enabled" {
  description = "Whether or not events are emitted for object state changes in this bucket. By default, objectEventsEnabled is set to false."
  type        = bool
}

variable "storage_tier" {
  description = "The type of storage tier of this bucket. A bucket is set to 'Standard' tier by default, which means the bucket will be put in the standard storage tier. When 'Archive' tier type is set explicitly, the bucket is put in the Archive Storage tier. The 'storageTier' property is immutable after bucket is created."
  type        = string
}

variable "versioning" {
  description = "Set the versioning status on the bucket. By default, a bucket is created with versioning Disabled.Allowed Create values: Enabled, Disabled. Allowed Update values: Enabled, Suspended."
  type        = string
}

variable "retention_rules" {}

variable "bucket" {
  description = "The name of the bucket."
  type        = string
}

variable "replpol_name" {
  description = "Replication policy name."
  type        = string
  default     = ""
}
variable "replication_policy" {
  description = "Replication policy detail."
  type        = map(any)
  default     = {}
}

variable "destination_bucket_name" {
  description = "Destination Bucket name to replicate to."
  type        = string
  default     = ""
}

variable "destination_region_name" {
  description = "Destination region to replicate to."
  type        = string
  default     = ""
}

variable "lifecycle_policy" {}

variable "rules" {}
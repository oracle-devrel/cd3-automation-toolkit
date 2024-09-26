# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Block Volume
## Create Block Volume and Block Volume Backup Policy
#################################

variable "availability_domain" {
  description = "Availability domain of the volume"
  type        = string
}

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "vpus_per_gb" {
  description = "The number of volume performance units (VPUs) that will be applied to this volume per GB"
  type        = number
  default     = null
}

#variable "existing_block_volume" {
#  type    = bool
#  default = false
#}

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

variable "display_name" {
  description = "User-friendly name to the volume"
  type        = string
}

variable "is_auto_tune_enabled" {
  description = "the auto-tune performance for the volume"
  type        = bool
}

variable "kms_key_id" {
  description = "The OCID of the Key Management master key"
  type        = string
}

variable "size_in_gbs" {
  description = "The size of the block volume in GBs"
  type        = number
}

variable "autotune_policies" {
  description = "List of Autotune Policies for Block volume"
  type = list(map(any))
  default = []
}
variable "source_details" {
  description = "OCID for existing Block volume, Block volume backup or Replica"
  type = list(map(any))
  default = []
}
variable "block_volume_replicas" {
  description = "Details for Block volume replication"
  type = list(map(any))
  default = []
}
variable "block_volume_replicas_deletion" {
  type = bool
  default = false
}

variable "attach_to_instance" {
  description = "The instance display name to attach the volume"
  type        = string
  default     = ""
}

variable "block_tf_policy" {
  description = "One of oracle defined backup policy bronze, silver and gold or custom policy name"
  type        = string
  default     = ""
}

variable "policy_tf_compartment_id" {
  description = "Provide compartment OCID if custome policy name used"
  type        = string
  default     = ""
}

variable "attachment_type" {
  description = "The attachment type iscsi or para-virtualized"
  type        = string
  default     = ""
}


#Volume Attachment Optional Params
variable "device" {
  type    = string
  default = null
}
variable "attachment_display_name" {
  type    = string
  default = null
}
variable "encryption_in_transit_type" {
  type    = string
  default = null
}
variable "is_pv_encryption_in_transit_enabled" {
  type    = bool
  default = null
}
variable "is_read_only" {
  type    = bool
  default = null
}
variable "is_shareable" {
  type    = bool
  default = null
}
variable "use_chap" {
  type    = bool
  default = null
}
variable "is_agent_auto_iscsi_login_enabled" {
  type    = bool
  default = null
}
variable "blockvolume_source_ocids" {
  type = map(any)
  default = {}
}
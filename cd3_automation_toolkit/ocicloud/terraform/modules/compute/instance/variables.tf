# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Instance
# Create Instance and Boot Volume Backup Policy
############################

variable "availability_domain" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "shape" {
  type        = string
  description = "The shape of an instance."
  default     = null
}

variable "ocpu_count" {
  type    = number
  default = null
}

variable "dedicated_vm_host_name" {
  type    = string
  default = null
}

variable "defined_tags" {
  type    = map(string)
  default = {}
}

variable "display_name" {
  type    = string
  default = null
}

variable "fault_domain" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(string)
  default = {}
}

variable "ssh_public_keys" {
  type    = string
  default = null
}

variable "assign_public_ip" {
  type    = bool
  default = null
}

variable "hostname_label" {
  type    = string
  default = null
}

variable "nsg_ids" {
  type    = list(string)
  default = []
}

variable "private_ip" {
  type    = string
  default = null
}

variable "subnet_id" {
  type    = string
  default = null
}

variable "source_type" {
  type    = string
  default = null
}

variable "source_image_id" {
  type    = string
  default = null
}

variable "boot_volume_size_in_gbs" {
  type    = number
  default = null
}

variable "network_compartment_id" {
  description = "Network compartmenet OCID to fetch NSG/Subnet details"
  type        = string
  default     = null
}

#Optional
variable "capacity_reservation_id" {
  type        = string
  description = "The OCID of the compute capacity reservation this instance is launched under"
  default     = null
}

variable "kms_key_id" {
  type    = string
  default = null
}

variable "extended_metadata" {
  type    = map(any)
  default = {}
}

variable "ipxe_script" {
  type    = string
  default = null
}

variable "create_is_pv_encryption_in_transit_enabled" {
  type    = bool
  default = null
}

#variable "update_is_pv_encryption_in_transit_enabled" {
#  type    = bool
#  default = null
#}

variable "preserve_boot_volume" {
  type    = bool
  default = null
}

variable "assign_private_dns_record" {
  type    = string
  default = null
}

variable "vlan_id" {
  type    = string
  default = null
}

variable "skip_source_dest_check" {
  type        = bool
  description = "Whether the source/destination check is disabled on the VNIC"
  default     = null
}

variable "baseline_ocpu_utilization" {
  type        = string
  description = "The baseline OCPU utilization for a subcore burstable VM instance"
  default     = ""
}

variable "memory_in_gbs" {
  type        = number
  description = "The total amount of memory available to the instance, in gigabytes"
  default     = null
}

variable "preemptible_instance_config" {
  type        = map(any)
  description = "The configuration for preemption action instance"
  default     = {}
}

variable "all_plugins_disabled" {
  type        = bool
  description = "To run all the available plugins"
  default     = null
}

variable "is_management_disabled" {
  type        = bool
  description = "To run all the available management plugins"
  default     = null
}

variable "is_monitoring_disabled" {
  type        = bool
  description = "To gather performance metrics and monitor the instance"
  default     = null
}

variable "plugins_details" {
  type        = map(any)
  default     = null
  description = "The configuration of plugins associated with this instance"
}

variable "is_live_migration_preferred" {
  type        = bool
  description = "Whether live migration is preferred for infrastructure maintenance"
  default     = null
}

variable "recovery_action" {
  type        = string
  description = "The lifecycle state for an instance when it is recovered after infrastructure maintenance"
  default     = null
}

variable "are_legacy_imds_endpoints_disabled" {
  type        = bool
  description = "Whether to disable the legacy (/v1) instance metadata service endpoints"
  default     = null
}

variable "boot_volume_type" {
  type        = string
  description = "Emulation type for the boot volume like ISCSI, SCSI etc"
  default     = null
}

variable "firmware" {
  type        = string
  description = "Firmware used to boot VM like BIOS, UEFI_64 etc"
  default     = null
}

variable "is_consistent_volume_naming_enabled" {
  type        = string
  description = "Whether to enable consistent volume naming feature"
  default     = null
}

variable "network_type" {
  type        = string
  description = "Emulation type for the physical network interface card (NIC)"
  default     = null
}

variable "remote_data_volume_type" {
  type        = string
  description = "Emulation type for volume"
  default     = null
}

variable "platform_config" {
  type        = list(map(any))
  description = "Platform config list of map"
  default     = []
}

variable "launch_options" {
  type = list(map(any))
  description = "Launch config list of map"
  default = []
}

variable "config_type" {
  type        = string
  description = "The type of platform being configured"
  default     = null
}

variable "is_measured_boot_enabled" {
  type        = bool
  description = "Whether the Measured Boot feature is enabled on the instance"
  default     = null
}

variable "is_secure_boot_enabled" {
  type        = bool
  description = "Whether Secure Boot is enabled on the instance"
  default     = null
}

variable "is_trusted_platform_module_enabled" {
  type        = bool
  description = "Whether the Trusted Platform Module (TPM) is enabled on the instance"
  default     = null
}

variable "numa_nodes_per_socket" {
  type        = string
  description = "The number of NUMA nodes per socket (NPS)"
  default     = null
}

variable "vcn_names" {
  type    = list(any)
  default = []
}

variable "boot_tf_policy" {
  type    = string
  default = ""
}

variable "policy_tf_compartment_id" {
  default = ""
}

variable "vnic_defined_tags" {
  type    = map(string)
  default = {}
}

variable "vnic_display_name" {
  type    = string
  default = ""
}

variable "vnic_freeform_tags" {
  type    = map(string)
  default = {}
}

variable "ssh_private_key_file_path" {
  type    = string
  default = null
}

variable "remote_execute" {
  type        = string
  description = "To execute a script remotely post provisioning instance(shell/ansible)"
  default     = null
}

variable "bastion_ip" {
  type        = string
  description = "Bastion IP to connect the host privately"
  default     = null
}

variable "cloud_init_script" {
  type    = string
  default = null
}
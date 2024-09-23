# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - SDDC
# Create SDDC
############################

variable "compartment_id" {
  description = "(Required) (Updatable) The OCID of the compartment to contain the SDDC."
  type        = string
  default     = null
}

variable "compute_availability_domain" {
  description = "(Required) The Availability Domain to create the SDDC cluster. Default is set to AD1 in main.tf"
  type        = string
  default     = null
}



variable "instance_display_name_prefix" {
  description = "A string that will be prepended to all ESXI "
  type        = string
}

##################
# SDDC Parameters#
##################

variable "initial_cluster_display_name" {
  description = "initial cluster display name."
  type        = string
  default     = null
}

variable "sddc_enabled" {
  description = "Whether to deploy SDDC Cluster. If set to true, creates a SDDC Cluster."
  type        = bool
  default     = true
}

variable "display_name" {
  description = "(Optional) (Updatable) A descriptive name for the SDDC. SDDC name requirements are 1-16 character length limit, Must start with a letter, Must be English letters, numbers, - only, No repeating hyphens, Must be unique within the region. Avoid entering confidential information."
  type        = string
  default     = null
}

variable "esxi_hosts_count" {
  description = "(Required) The number of ESXi hosts to create in the SDDC. Changing this value post-deployment will delete the entire cluster. You can add more hosts in the OCI GUI following the initial deployment"
  type        = number
}

variable "vmware_software_version" {
  description = "(Required) The VMware software bundle to install on the ESXi hosts in the SDDC. To get a list of the available versions. Documentation states updateable but that's incorrect. DO NOT UPDATE POST-DEPLOYMENT"
  type        = string
}

variable "initial_commitment" {
  description = "commitment Hourly/Monthly"
  type        = string
  default     = null
}

variable "workload_network_cidr" {
  description = "(Optional) The CIDR block for the IP addresses that VMware VMs in the SDDC use to run application workloads."
  type        = string
  default     = null
}

variable "ssh_authorized_keys" {
  description = "(Required) (Updatable) One or more public SSH keys to be included in the ~/.ssh/authorized_keys file for the default user on each ESXi host. Use a newline character to separate multiple keys. The SSH keys must be in the format required for the authorized_keys file"
  type        = string
}

variable "is_hcx_enabled" {
  description = "Whether to deploy HCX during provisioning. If set to true, HCX is included in the workflow."
  type        = bool
  default     = null
}



##########################
# Subnets/VLANs for SDDC #
##########################
variable "provisioning_subnet_id" {
  description = " The OCID of the management subnet to use for provisioning the SDDC"
  type        = string
  default     = null

}

variable "nsx_edge_uplink1vlan_id" {
  description = "The OCID of the VLAN to use for the NSX Edge Uplink 1 component of the VMware environment"
  type        = string
  default     = null

}

variable "nsx_edge_uplink2vlan_id" {
  description = " The OCID of the VLAN to use for the NSX Edge Uplink 2 component of the VMware environment"
  type        = string
  default     = null
}

variable "nsx_vtep_vlan_id" {
  description = " The OCID of the VLAN to use for the NSX VTEP component of the VMware environment"
  type        = string
  default     = null
}


variable "nsx_edge_vtep_vlan_id" {
  description = " The OCID of the VLAN to use for the NSX Edge VTEP component of the VMware environment"
  type        = string
  default     = null
}

variable "vsan_vlan_id" {
  description = "The OCID of the VLAN to use for the vSAN component of the VMware environment"
  type        = string
  default     = null
}

variable "vmotion_vlan_id" {
  description = "(Required)(Updatable) The OCID of the VLAN to use for the vMotion component of the VMware environment"
  type        = string
  default     = null
}

variable "vsphere_vlan_id" {
  description = " The OCID of the VLAN to use for the vMotion component of the VMware environment"
  type        = string
  default     = null
}

variable "hcx_vlan_id" {
  description = " The OCID of the VLAN to use for the HCX component of the VMware environment. This value is required only when isHcxEnabled is true"
  type        = string
  default     = null
}

variable "hcx_action" {
  description = "The action to be performed upon HCX license"
  type        = string
  default     = null
}

variable "provisioning_vlan_id" {
  description = "The OCID of the VLAN used by the SDDC for the Provisioning component of the VMware environment."
  type        = string
  default     = null
}

variable "replication_vlan_id" {
  description = "The OCID of the VLAN used by the SDDC for the vSphere Replication component of the VMware environment."
  type        = string
  default     = null
}
variable "esxi_hardware_type" {
  description = "The hardware type for esxi."
  type        = string
  default     = null
}

variable "capacity_reservation_id" {
  description = "Reservation id of ocvs allocated capacity."
  type        = string
  default     = null
}

variable "initial_host_ocpu_count" {
  description = "initial_host_ocpu_count."
  type        = string
  default     = null
}

variable "initial_host_shape_name" {
  description = "initial_host_shape_name."
  type        = string
  default     = null
}

variable "is_shielded_instance_enabled" {
  description = "is_shielded_instance_enabled"
  type        = string
  default     = null
}

variable "is_single_host_sddc" {
  description = "is_single_host_sddc"
  type        = string
  default     = null
}

variable "defined_tags" {
  description = "Reservation id of ocvs allocated capacity."
  type        = map(any)
  default = {
    "Oracle-Tags.CreatedOn" = "$$(oci.datetime)",
    "Oracle-Tags-CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  description = "Free-form tags for SDDC cluster"
  type        = map(string)
}



variable "reserving_hcx_on_premise_license_keys" {
  description = "Network compartmenet OCID to fetch NSG/Subnet details"
  type        = string
  default     = null
}

variable "refresh_hcx_license_status" {
  description = "Network compartmenet OCID to fetch NSG/Subnet details"
  type        = string
  default     = null
}

variable "network_compartment_id" {
  description = "Network compartmenet OCID to fetch NSG/Subnet details"
  type        = string
  default     = null
}

variable "management_datastore" {
 type = list(string)
 default = []
}

variable "workload_datastore" {
 type = list(string)
 default = []
}


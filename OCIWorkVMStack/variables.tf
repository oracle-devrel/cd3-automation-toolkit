/*
 * Copyright (c) 2023 Oracle and/or its affiliates. All rights reserved.
 */

variable "tenancy_ocid" {
  type = string
}

variable "current_user_ocid" {
  type = string
}

variable "region" {
  type = string
}


###############################################################################
#  Marketplace Image Listing - information available in the Partner portal    #
###############################################################################
variable "mp_subscription_enabled" {
  description = "Subscribe to Marketplace listing?"
  type        = bool
  default     = false
}

variable "mp_listing_id" {
  // default = "ocid1.appcataloglisting.oc1.."
  default     = ""
  description = "Marketplace Listing OCID"
}

variable "mp_listing_resource_id" {
  // default = "ocid1.image.oc1.."
  default     = ""
  description = "Marketplace Listing Image OCID"
}

variable "mp_listing_resource_version" {
  // default = "1.0"
  default     = ""
  description = "Marketplace Listing Package/Resource Version"
}

###################################################################


# CD3 Automation Toolkit WorkVM details

variable "instance_os_version" {
  description = "Instance OS version"
  type        = string
  default     = "Oracle-Linux-7"
}

variable "instance_compartment_strategy" {
  description = "Instance Compartment strategy - use existing or create new"
  type        = string
  default     = "Use Existing Compartment"
}

variable "parent_compartment_ocid" {
  description = "Parent Compartment OCID"
  type        = string
  default     = null
}
variable "new_compartment_name" {
  description = "New Compartment name"
  type        = string
  default     = "workvm-cmp"
}
variable "instance_compartment_ocid" {
  description = "Instance Compartment"
  type        = string
  default     = null
}

variable "instance_name" {
  description = "Hostname"
  type        = string
  default     = "workvm"
}

variable "instance_shape" {
  description = "The shape for compute instance."
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "instance_ram" {
  description = "The total amount of memory in GBs available to a compute instance."
  type        = number
  default     = 1
}

variable "instance_ocpus" {
  description = "The total number of OCPUS available to a compute instance."
  type        = number
  default     = 1
}

variable "boot_volume_size" {
  description = "Boot volume size"
  type        = number
  default     = 50
}

variable "instance_ad" {
  description = "The Availability domain in which instance will be provisioned."
  type        = string
}

variable "instance_fd" {
  description = "The Fault domain in which instance will be provisioned."
  type        = string
  default     = ""
}

variable "ssh_public_key" {
  description = "SSH public key for instance. Use the corresponding private key to access the compute instances."
  type        = string
}

variable "subnet_id" {
  description = "Subnet OCID to use for CD3 Automation Toolkit WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "nsg_id" {
  description = "NSG OCID to use for CD3 Automation Toolkit WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "assign_public_ip" {
  description = "assign Public IP to VM"
  type        = bool
  default     = false
}

variable "assign_publicip_existing_subnet" {
  description = "assign Public IP to VM"
  type        = bool
  default     = false
}

#Networking Details

variable "vcn_compartment_ocid" {
  description = "VCN Compartment"
  type        = string
  default     = null
}

variable "vcn_strategy" {
  description = "Create or use existing VCN"
  type        = string
}

variable "existing_vcn_id" {
  description = "VCN OCID to use for CD3 Automation Toolkit WorkVM."
  type        = string
  default     = ""
}

variable "existing_subnet_id" {
  description = "Subnet OCID to use for CD3 Automation Toolkit WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "existing_nsg_id" {
  description = "NSG OCID to use for CD3 Automation Toolkit WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "assign_existing_nsg" {
  description = "NSG OCID to use for CD3 Automation Toolkit WorkVM. Private subnets are recommended."
  type        = bool
  default     = false
}

variable "vcn_name" {
  description = "The name of the new Virtual Cloud Network (VCN) to create for this service. Make sure that there is no conflict with the existing VCN name."
  type        = string
  default     = "workvm-vcn"
}

variable "vcn_cidr" {
  description = "The CIDR to assign to the new virtual cloud network (VCN) to create for this service. Make sure that there is no conflict with the existing VCN CIDR."
  type        = string
  default     = ""
}

variable "vcn_dns_label" {
  description = "The dns label for the VCN. Only letters and numbers, starting with a letter and can be 15 characters max"
  type        = string
  default     = "workvmvcn"
}


variable "subnet_name" {
  description = "The name of the new regional subnet to create for Enterprise Manager compute instances."
  type        = string
  default     = "workvm-sub"
}

variable "subnet_type" {
  description = "Choose between private and public regional subnets. Private regional subnet is recommended."
  type        = string
  default     = "Private"
}

variable "subnet_cidr" {
  description = "The CIDR of the new subnet."
  type        = string
  default     = null
}

variable "subnet_dns_label" {
  description = "The dns label for the subnet. Only letters and numbers, starting with a letter and can be 15 characters max"
  type        = string
  default     = "workvmsub"
}

variable "drg_attachment" {
  description = "Attach DRG"
  type        = bool
  default     = false
}

variable "existing_drg_id" {
  description = "DRG OCID."
  type        = string
  default     = ""
}

variable "source_cidr" {
  description = "Source CIDRs"
  type        = list(string)
  default     = []
}
variable "cloud_init_script" {
  description = "cloud_init_script file name"
  type        = string
  default     = "installToolkit.sh"
}

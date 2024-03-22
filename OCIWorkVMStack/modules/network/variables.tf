variable "vcn_compartment_ocid" {
  type = string
}



/*
Networking parameters
*/
variable "vcn_strategy" {
  description = "Create or use existing VCN"
  type        = string
}
# Required for Create New VCN flow
variable "vcn_name" {
  description = "The name of the new Virtual Cloud Network (VCN) to create for this service. Make sure that there is no conflict with the existing VCN name."
  type        = string
}

variable "vcn_cidr" {
  description = "The CIDR to assign to the new virtual cloud network (VCN) to create for this service. Make sure that there is no conflict with the existing VCN CIDR."
  type        = string
}

variable "vcn_dns_label" {
  description = "The dns label for the VCN. Only letters and numbers, starting with a letter and can be 15 characters max"
  type        = string
}

variable "subnet_name" {
  description = "The name of the new regional subnet to create for Enterprise Manager compute instances."
  type        = string
}

variable "subnet_type" {
  description = "Choose between private and public regional subnets. Private regional subnet is recommended."
  type        = string
}

variable "subnet_cidr" {
  description = "The CIDR of the new regional subnet to create for Enterprise Manager compute instances."
  type        = string
}

variable "subnet_dns_label" {
  description = "The dns label for the subnet. Only letters and numbers, starting with a letter and can be 15 characters max"
  type        = string
}


# Required for Existing VCN flow
variable "existing_vcn_id" {
  description = "VCN OCID to use for OCI Automation WorkVM."
  type        = string
  default     = ""
}

variable "existing_subnet_id" {
  description = "Subnet OCID to use for OCI Automation WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "existing_nsg_id" {
  description = "NSG OCID to use for OCI Automation WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "drg_attachment" {
  description = "Attach DRG"
  type        = bool
  default     = false
}

variable "existing_drg_id" {
  description = "DRG OCID"
  type        = string
  default     = ""
}

variable "source_cidr" {
  description = "The CIDR of the new subnet."
  type        = list(string)
  default     = []
}
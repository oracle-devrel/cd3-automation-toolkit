variable "instance_image_ocid" {
  description = "image ocid"
  type        = string
  default     = "ocid1.image.oc1.iad.aaaaaaaaesxggkbcxdt3fw7nfstan5eq52ityh4vgeyh3bodkoqrvpj44o3a"
}

variable "vcn_strategy" {
  description = "Create or use existing VCN"
  type        = string
}

variable "subnet_id" {
  description = "Subnet OCID to use for OCI Automation WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
}

variable "assign_public_ip" {
  description = "assign Public IP to VM"
  type        = bool
  default     = false
}

variable "nsg_id" {
  description = "NSG OCID to use for OCI Automation WorkVM. Private subnets are recommended."
  type        = string
  default     = ""
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

variable "cloud_init_script" {
  description = "cloud_init_script file name"
  type        = string
  default     = "installToolkit.sh"
}

variable "tenancy_ocid" {
  type = string
}

variable "current_user_ocid" {
  type = string
}

variable "tenancy_name" {
  type = string
}

variable "config_region" {
  type = string
}

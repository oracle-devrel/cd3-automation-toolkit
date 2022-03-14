// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
#
# Variables Block
# OCI
#
############################

variable "tenancy_ocid" {
        type = string
        default = "<TENANCY OCID HERE>"
}

variable "user_ocid" {
        type = string
        default = "<USER OCID HERE>"
}

variable "fingerprint" {
        type = string
        default = "<SSH KEY FINGERPRINT HERE>"
}

variable "private_key_path" {
        type = string
        default = "<SSH PRIVATE KEY FULL PATH HERE>"
}

variable "region" {
        type = string
        default = "<OCI TENANCY REGION HERE eg: us-phoenix-1 or us-ashburn-1>"
}

#################################
# SSH Keys
#################################

variable "ssh_public_key" {
	type = string
	default = "<SSH PUB KEY STRING HERE>"
}

variable instance_ssh_keys {
    type = map(any)
    default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    #START_instance_ssh_keys#
    # exported instance ssh keys
    #instance_ssh_keys_END#
    }
}

variable exacs_ssh_keys {
    type = map(any)
    default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    #START_exacs_ssh_keys#
    # exported exacs ssh keys
    #exacs_ssh_keys_END#
    }
}

variable dbsystem_ssh_keys {
    type = map(any)
    default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    #START_dbsystem_ssh_keys#
    # exported dbsystem ssh keys
    #dbsystem_ssh_keys_END#
    }
}

#################################
# Platform Image OCIDs and
# Market Place Images
#################################
variable instance_source_ocids {
    type = map(any)
    default = {
    Linux = "<Latest Linux OCID>"
    Windows = "<Latest Windows OCID>"
    PaloAlto = "Palo Alto Networks VM-Series Next Generation Firewall"
    #START_instance_source_ocids#
    # exported instance image ocids
    #instance_source_ocids_END#
    }
}

#########################
## Instances ##
#########################

#Example for OS value 'Windows' in Instances sheet
variable "Windows" {
        type = string
        default = "<LATEST WINDOWS OCID HERE>"
        description = "<WINDOWS DESCRIPTION HERE>"
}

#Example for OS value 'Linux' in Instances sheet
variable "Linux"{
        type = string
        default = "<LATEST LINUX OCID HERE>"
        description = "<LINUX DESCRIPTION HERE>"
}

#################################
#
# Variables according to Services
# PLEASE DO NOT MODIFY
#
#################################

############################
### Fetch Compartments #####
############################

#START_compartment_ocids#
variable "compartment_ocids" {
    type = list(any)
    default = [{}]
}
#compartment_ocids_END#

#########################
##### Identity ##########
#########################

variable "compartments" {
  type    = map(any)
  default = {
      root = {},
      compartment_level1= {},
      compartment_level2 = {},
      compartment_level3 = {},
      compartment_level4 = {},
      compartment_level5  = {},
  }
}

variable "policies" {
  type    = map(any)
  default = {}
}

variable "groups" {
  type    = map(any)
  default = {}
}

#########################
##### Network ########
#########################

variable "default_dhcps" {
  type = map(any)
  default = {}
}

variable "custom_dhcps" {
  type = map(any)
  default = {}
}

variable "vcns" {
  type    = map(any)
  default = {}
}

variable "igws" {
  type    = map(any)
  default = {}
}

variable "sgws" {
  type    = map(any)
  default = {}
}

variable "ngws" {
  type    = map(any)
  default = {}
}

variable "lpgs" {
        type    = map(any)
        default = {
            hub-lpgs = {},
            spoke-lpgs = {},
            peer-lpgs = {},
            none-lpgs  = {},
            exported-lpgs = {},
        }
}

variable "drgs" {
  type    = map(any)
  default = {}
}

variable "seclists" {
  type = map(any)
  default = {}
}

variable "default_seclists" {
  type = map(any)
  default = {}
}

variable "route_tables" {
  type = map(any)
  default = {}
}

variable "default_route_tables" {
  type    = map(any)
  default = {}
}

variable "nsgs" {
  type = map(any)
  default = {}
}

variable "nsg_rules" {
  type = map(any)
  default = {}
}

variable "subnets" {
  type    = map(any)
  default = {}
}

variable "drg_attachments" {
  type    = map(any)
  default = {}
}

variable "drg_route_tables" {
  type    = map(any)
  default = {}
}

variable "drg_route_rules" {
  type    = map(any)
  default = {}
}

variable "drg_route_distributions" {
  type    = map(any)
  default = {}
}

variable "drg_route_distribution_statements" {
  type    = map(any)
  default = {}
}

variable "data_drg_route_tables" {
  type    = map(any)
  default = {}
}

variable "data_drg_route_table_distributions" {
  type    = map(any)
  default = {}
}

#########################
##### Logging ###########
#########################

variable "log_groups" {
  type    = map(any)
  default = {}
}

variable "logs" {
  type    = map(any)
  default = {}
}

#########################
## Management Services ##
#########################

variable "alarms" {
  type    = map(any)
  default = {}
}

variable "events" {
  type    = map(any)
  default = {}
}

variable "notifications_topics" {
  type    = map(any)
  default = {}
}

variable "notifications_subscriptions" {
  type    = map(any)
  default = {}
}

#########################
## Database ##
#########################

variable "exa_infra" {
  description = "To provision exadata infrastructure"
  type        = map(any)
  default     = {}
}

variable "exa_vmclusters" {
  description = "To provision exadata cloud VM cluster"
  type        = map(any)
  default     = {}
}

variable "dbsystems_vm_bm" {
  description = "To provision DB System"
  type        = map(any)
  default     = {}
}

##########################
# Add new variables here #
##########################

######################### END #########################
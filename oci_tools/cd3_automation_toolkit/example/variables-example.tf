// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
#
# Variables Block
# OCI
#
############################

variable "ssh_public_key" {
	type = string
	default = "<YOUR SSH PUB KEY STRING HERE>"
}

variable "tenancy_ocid" {
        type = string
        default = "<YOUR TENANCY OCID HERE>"
}

variable "user_ocid" {
        type = string
        default = "<USER OCID HERE>"
}

variable "fingerprint" {
        type = string
        default = "<SSH KEY FINGERPRINT> - Use the create_keys.sh for easily creating keys and its fingerprint> "
}

variable "private_key_path" {
        type = string
        default = "<The Private key file path> - If you've used the createPEMKeys.py then the full path of where the .pem file is>"
}

variable "region" {
        type = string
        default = "<OCI Tenancy Region where these objects will be created - us-phoenix-1 or us-ashburn-1>"
}

#################################
#
# Variables according to Services
# Please do not modify
#
#################################

############################
### Fetch Compartments #####
############################

## Do Not Modify #START_Compartment_OCIDs#
variable "compartment_ocids" {
    type = list(any)
    default = [{}]
}
#Compartment_OCIDs_END#  ## Do Not Modify

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
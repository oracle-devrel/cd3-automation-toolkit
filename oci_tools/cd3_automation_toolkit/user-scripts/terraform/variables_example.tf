// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
#
# Variables Block
# OCI
#
############################

variable "tenancy_ocid" {
  type    = string
  default = "<TENANCY OCID HERE>"
}

variable "user_ocid" {
  type    = string
  default = "<USER OCID HERE>"
}

variable "fingerprint" {
  type    = string
  default = "<SSH KEY FINGERPRINT HERE>"
}

variable "private_key_path" {
  type    = string
  default = "<SSH PRIVATE KEY FULL PATH HERE>"
}

variable "region" {
  type    = string
  default = "<OCI TENANCY REGION HERE eg: us-phoenix-1 or us-ashburn-1>"
}

#################################
# SSH Keys
#################################

variable "instance_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    #START_instance_ssh_keys#
    # exported instance ssh keys
    #instance_ssh_keys_END#
  }
}

variable "exacs_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = ["<SSH PUB KEY STRING HERE>"]
    #START_exacs_ssh_keys#
    # exported exacs ssh keys
    #exacs_ssh_keys_END#
  }
}

variable "dbsystem_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = ["<SSH PUB KEY STRING HERE>"]
    #START_dbsystem_ssh_keys#
    # exported dbsystem ssh keys
    #dbsystem_ssh_keys_END#
  }
}

#################################
# Platform Image OCIDs and
# Market Place Images
#################################

variable "instance_source_ocids" {
  type = map(any)
  default = {
    Linux    = "<LATEST LINUX OCID HERE>"
    Windows  = "<LATEST WINDOWS OCID HERE>"
    PaloAlto = "Palo Alto Networks VM-Series Next Generation Firewall"
    #START_instance_source_ocids#
    # exported instance image ocids
    #instance_source_ocids_END#
  }
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
  type    = map(any)
  default = {}
}
#compartment_ocids_END#

#########################
##### Identity ##########
#########################

variable "compartments" {
  type = map(any)
  default = {
    root               = {},
    compartment_level1 = {},
    compartment_level2 = {},
    compartment_level3 = {},
    compartment_level4 = {},
    compartment_level5 = {},
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
## Tagging ##
#########################

variable "tag_namespaces" {
  description = "To provision Namespaces"
  type        = map(any)
  default     = {}
}

variable "tag_keys" {
  description = "To provision Tag Keys"
  type        = map(any)
  default     = {}
}

variable "tag_defaults" {
  description = "To make the Tag keys as default to compartments"
  type        = map(any)
  default     = {}
}

#########################
##### Network ########
#########################

variable "default_dhcps" {
  type    = map(any)
  default = {}
}

variable "custom_dhcps" {
  type    = map(any)
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
  type = map(any)
  default = {
    hub-lpgs      = {},
    spoke-lpgs    = {},
    peer-lpgs     = {},
    none-lpgs     = {},
    exported-lpgs = {},
  }
}

variable "drgs" {
  type    = map(any)
  default = {}
}

variable "seclists" {
  type    = map(any)
  default = {}
}

variable "default_seclists" {
  type    = map(any)
  default = {}
}

variable "route_tables" {
  type    = map(any)
  default = {}
}

variable "default_route_tables" {
  type    = map(any)
  default = {}
}

variable "nsgs" {
  type    = map(any)
  default = {}
}

variable "nsg_rules" {
  type    = map(any)
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
## Instances/Block Volumes ##
#########################

variable "blockvolumes" {
  type    = map(any)
  description = "To provision block volumes"
  default = {}
}

variable "block_backup_policies" {
  type = map(any)
  description = "To create block volume back policy"
  default = {}
}

variable "instances" {
  type = map(any)
  description = "Map of instances to be provisioned"
  default = {}
}

variable "boot_backup_policies" {
  type = map(any)
  description = "Map of boot volume backup policies to be provisioned"
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

variable "db_home" {
  type = map(any)
  description = "Map of database db home to be provisioned"
  default = {}
}

variable "databases" {
    description = "Map of databases to be provisioned in an existing db_home"
    type = map(any)
    default = {}
}

#########################
## FSS ##
#########################

variable "mount_targets" {
  description = "To provision Mount Targets"
  type        = map(any)
  default     = {}
}

variable "fss" {
  description = "To provision File System Services"
  type        = map(any)
  default     = {}
}

variable "export_options" {
  description = "To provision Export Sets"
  type        = map(any)
  default     = {}
}

#########################
## Load Balancers ##
#########################

variable "load_balancers" {
  description = "To provision Load Balancers"
  type        = map(any)
  default     = {}
}

variable "hostnames" {
  description = "To provision Load Balancer Hostnames"
  type        = map(any)
  default     = {}
}

variable "certificates" {
  description = "To provision Load Balancer Certificates"
  type        = map(any)
  default     = {}
}

variable "cipher_suites" {
  description = "To provision Load Balancer Cipher Suites"
  type        = map(any)
  default     = {}
}

variable "backend_sets" {
  description = "To provision Load Balancer Backend Sets"
  type        = map(any)
  default     = {}
}

variable "backends" {
  description = "To provision Load Balancer Backends"
  type        = map(any)
  default     = {}
}

variable "listeners" {
  description = "To provision Load Balancer Listeners"
  type        = map(any)
  default     = {}
}

variable "path_route_sets" {
  description = "To provision Load Balancer Path Route Sets"
  type        = map(any)
  default     = {}
}

variable "rule_sets" {
  description = "To provision Load Balancer Rule Sets"
  type        = map(any)
  default     = {}
}

#########################
##### IP Management #####
#########################

variable "public_ip_pools" {
  type    = map(any)
  default = {}
}

variable "private_ips" {
  type    = map(any)
  default = {}
}

variable "reserved_ips" {
  type    = map(any)
  default = {}
}

variable "vnic_attachments"{
  type    = map(any)
  default = {}
}

#########################
##### VCN Logs ##########
#########################

variable "vcn_log_groups" {
  type    = map(any)
  default = {}
}

variable "vcn_logs" {
  type    = map(any)
  default = {}
}
#########################
## OSS Buckets ##
#########################

variable "oss" {
  description = "To provision Buckets - OSS"
  type        = map(any)
  default     = {}
}

#########################
## OSS Logs ##
#########################

variable "oss_log_groups" {
  description = "To provision Log Groups for OSS"
  type        = map(any)
  default     = {}
}

variable "oss_logs" {
  description = "To provision Logs for OSS"
  type        = map(any)
  default     = {}
}

#########################
## OSS IAM Policies ##
#########################

variable "oss_policies" {
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

############################
## Key Management Service ##
############################

variable "vaults" {
  type    = map(any)
  default = {}
}

variable "keys" {
  type    = map(any)
  default = {}
}

##########################
# Add new variables here #
##########################
variable "capacity_reservation_ocids" {
  type = map(any)
  default = {
    "AD1" : "ocid1.capacityreservation.oc1.iad.anuwcljrmbgqraachdisdnhc5z7swiwyzhi6radkn7xxtw6uosysheiadlja",
    "AD2" : "ocid1.capacityreservation.oc1.iad.anuwcljsmbgqraacm4edb4dbsrqsgtskzjicudhmasmpqe7aopxmjvnukugq",
    "AD3" : "ocid1.capacityreservation.oc1.iad.anuwcljtmbgqraactoi5gwv6ahzutllmjmfgtrabarhcq7wvkx6mz2b7dwga"
  }
}

######################### END #########################
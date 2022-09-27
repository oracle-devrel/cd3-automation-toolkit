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

##########################
## Fetch Compartments ####
##########################

variable "compartment_ocids" {
  type = map(any)
  default = {
    #START_compartment_ocids#
    # compartment ocids
    #compartment_ocids_END#
  }
}

#########################
##### Identity ##########
#########################

variable "compartments" {
  type = object({
    root = optional(map(object({
      tenancy_ocid          = optional(string)
      parent_compartment_id = string
      name                  = string
      description           = optional(string)
      enable_delete         = optional(bool)
      defined_tags          = optional(map(any))
      freeform_tags         = optional(map(any))
    })))
    compartment_level1 = optional(map(object({
      tenancy_ocid          = optional(string)
      parent_compartment_id = string
      name                  = string
      description           = optional(string)
      enable_delete         = optional(bool)
      defined_tags          = optional(map(any))
      freeform_tags         = optional(map(any))
    })))
    compartment_level2 = optional(map(object({
      tenancy_ocid          = optional(string)
      parent_compartment_id = string
      name                  = string
      description           = optional(string)
      enable_delete         = optional(bool)
      defined_tags          = optional(map(any))
      freeform_tags         = optional(map(any))
    })))
    compartment_level3 = optional(map(object({
      tenancy_ocid          = optional(string)
      parent_compartment_id = string
      name                  = string
      description           = optional(string)
      enable_delete         = optional(bool)
      defined_tags          = optional(map(any))
      freeform_tags         = optional(map(any))
    })))
    compartment_level4 = optional(map(object({
      tenancy_ocid          = optional(string)
      parent_compartment_id = string
      name                  = string
      description           = optional(string)
      enable_delete         = optional(bool)
      defined_tags          = optional(map(any))
      freeform_tags         = optional(map(any))
    })))
    compartment_level5 = optional(map(object({
      tenancy_ocid          = optional(string)
      parent_compartment_id = string
      name                  = string
      description           = optional(string)
      enable_delete         = optional(bool)
      defined_tags          = optional(map(any))
      freeform_tags         = optional(map(any))
    })))
  })
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
  type = map(object({
    name                = string
    compartment_id      = string
    policy_description  = string
    policy_statements   = list(string)
    policy_version_date = optional(string)
    defined_tags        = optional(map(any))
    freeform_tags       = optional(map(any))
  }))
  default = {}
}

variable "groups" {
  type = map(object({
    group_name        = string
    group_description = string
    matching_rule     = optional(string)
    defined_tags      = optional(map(any))
    freeform_tags     = optional(map(any))
  }))
  default = {}
}

#########################
####### Tagging #########
#########################

variable "tag_namespaces" {
  description = "To provision Namespaces"
  type = map(object({
    compartment_id = string
    description    = string
    name           = string
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
    is_retired     = optional(bool)
  }))
  default = {}
}

variable "tag_keys" {
  description = "To provision Tag Keys"
  type = map(object({
    tag_namespace_id = string
    description      = string
    name             = string
    defined_tags     = optional(map(any))
    freeform_tags    = optional(map(any))
    is_cost_tracking = optional(bool)
    is_retired       = optional(bool)
    validator = optional(list(object({
      validator_type   = optional(string)
      validator_values = optional(list(any))
    })))
  }))
  default = {}
}

variable "tag_defaults" {
  description = "To make the Tag keys as default to compartments"
  type = map(object({
    compartment_id    = string
    tag_definition_id = string
    value             = string
    is_required       = optional(bool)
  }))
  default = {}
}

#########################
###### Network ##########
#########################

variable "default_dhcps" {
  type = map(object({
    server_type                = string
    manage_default_resource_id = optional(string)
    custom_dns_servers         = optional(list(any))
    search_domain              = optional(map(list(any)))
    defined_tags               = optional(map(any))
    freeform_tags              = optional(map(any))
  }))
  default = {}
}

variable "custom_dhcps" {
  type = map(object({
    compartment_id     = string
    server_type        = string
    vcn_id             = string
    custom_dns_servers = optional(list(any))
    domain_name_type   = optional(string)
    display_name       = optional(string)
    search_domain      = optional(map(list(any)))
    defined_tags       = optional(map(any))
    freeform_tags      = optional(map(any))
  }))
  default = {}
}

variable "vcns" {
  type = map(object({
    compartment_id                   = string
    cidr_blocks                      = optional(list(string))
    byoipv6cidr_details              = optional(list(map(any)))
    display_name                     = optional(string)
    dns_label                        = optional(string)
    is_ipv6enabled                   = optional(bool)
    defined_tags                     = optional(map(any))
    freeform_tags                    = optional(map(any))
    ipv6private_cidr_blocks          = optional(list(string))
    is_oracle_gua_allocation_enabled = optional(bool)
  }))
  default = {}
}

variable "igws" {
  type = map(object({
    compartment_id = string
    vcn_id         = string
    enable_igw     = optional(bool)
    igw_name       = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
    route_table_id = optional(string)
  }))
  default = {}
}

variable "sgws" {
  type = map(object({
    compartment_id = string
    vcn_id         = string
    service        = optional(string)
    sgw_name       = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "ngws" {
  type = map(object({
    compartment_id = string
    vcn_id         = string
    block_traffic  = optional(bool)
    public_ip_id   = optional(string)
    ngw_name       = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
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
  type = map(object({
    compartment_id = string
    display_name   = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "seclists" {
  type = map(object({
    compartment_id = string
    vcn_id         = string
    display_name   = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
    ingress_sec_rules = optional(list(object({
      protocol    = optional(string)
      stateless   = optional(string)
      description = optional(string)
      source      = optional(string)
      source_type = optional(string)
      options     = optional(map(any))
    })))
    egress_sec_rules = optional(list(object({
      protocol         = optional(string)
      stateless        = optional(string)
      description      = optional(string)
      destination      = optional(string)
      destination_type = optional(string)
      options          = optional(map(any))
    })))
  }))
  default = {}
}

variable "default_seclists" {
  type = map(object({
    compartment_id = string
    vcn_id         = string
    display_name   = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
    ingress_sec_rules = optional(list(object({
      protocol    = optional(string)
      stateless   = optional(string)
      description = optional(string)
      source      = optional(string)
      source_type = optional(string)
      options     = optional(map(any))
    })))
    egress_sec_rules = optional(list(object({
      protocol         = optional(string)
      stateless        = optional(string)
      description      = optional(string)
      destination      = optional(string)
      destination_type = optional(string)
      options          = optional(map(any))
    })))
  }))
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
  type = map(object({
    compartment_id = string
    vcn_id         = string
    display_name   = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "nsg_rules" {
  type = map(object({
    nsg_id           = string
    direction        = string
    protocol         = string
    description      = optional(string)
    stateless        = optional(string)
    source_type      = optional(string)
    destination_type = optional(string)
    destination      = optional(string)
    source           = optional(string)
    options          = optional(map(any))
  }))
  default = {}
}

variable "subnets" {
  type = map(object({
    compartment_id             = string
    vcn_id                     = string
    cidr_block                 = string
    display_name               = optional(string)
    dns_label                  = optional(string)
    ipv6cidr_block             = optional(string)
    defined_tags               = optional(map(any))
    freeform_tags              = optional(map(any))
    prohibit_internet_ingress  = optional(string)
    prohibit_public_ip_on_vnic = optional(string)
    availability_domain        = optional(string)
    dhcp_options_id            = optional(string)
    route_table_id             = optional(string)
    security_list_ids          = optional(list(string))
  }))
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
  type = map(object({
    distribution_type = string
    drg_id            = string
    defined_tags      = optional(map(any))
    freeform_tags     = optional(map(any))
    display_name      = optional(string)
  }))
  default = {}
}

variable "drg_route_distribution_statements" {
  type = map(object({
    drg_route_distribution_id = string
    action                    = string
    match_criteria = optional(list(object({
      match_type        = string
      attachment_type   = optional(string)
      drg_attachment_id = optional(string)
    })))
    priority = optional(string)
  }))
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
## Dedicated VM Hosts ##
#########################

variable "dedicated_hosts" {
  type        = map(any)
  description = "To provision new dedicated VM hosts"
  default     = {}
}

#########################
## Instances/Block Volumes ##
#########################

variable "blockvolumes" {
  type        = map(any)
  description = "To provision block volumes"
  default     = {}
}

variable "block_backup_policies" {
  type        = map(any)
  description = "To create block volume back policy"
  default     = {}
}

variable "instances" {
  type        = map(any)
  description = "Map of instances to be provisioned"
  default     = {}
}

variable "boot_backup_policies" {
  type        = map(any)
  description = "Map of boot volume backup policies to be provisioned"
  default     = {}
}

#########################
####### Database ########
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
  type        = map(any)
  description = "Map of database db home to be provisioned"
  default     = {}
}

variable "databases" {
  description = "Map of databases to be provisioned in an existing db_home"
  type        = map(any)
  default     = {}
}

####################################
####### Autonomous Database ########
####################################

variable "adb" {
  type = map(object({
    admin_password = optional(string)
    character_set  = optional(string)
    compartment_id = string
    cpu_core_count = optional(number)
    database_edition = optional(string)
    data_storage_size_in_tbs   = optional(number)
    db_name        = string
    db_version     = optional(string)
    db_workload    = optional(string)
    display_name   = optional(string)
    license_model  = optional(string)
    ncharacter_set = optional(string)
    network_compartment_id = optional(string)
    nsg_ids        = optional(list(string))
    subnet_id      = optional(string)
    vcn_name       = optional(string)
    whitelisted_ips = optional(list(string))
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

#########################
######### FSS ###########
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

variable "nfs_export_options" {
  description = "To provision Export Sets"
  type        = map(any)
  default     = {}
}

#########################
#### Load Balancers #####
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

variable "lbr_reserved_ips" {
  description = "To provision Load Balancer Reserved IPs"
  type        = map(any)
  default     = {}
}

###################################
####### Load Balancer Logs ########
###################################

variable "loadbalancer_log_groups" {
  description = "To provision Log Groups for Load Balancers"
  type        = map(any)
  default     = {}
}

variable "loadbalancer_logs" {
  description = "To provision Logs for Load Balancers"
  type        = map(any)
  default     = {}
}

#########################
## Network Load Balancers ##
#########################

variable "network_load_balancers" {
  type    = map(any)
  default = {}
}
variable "nlb_listeners" {
  type    = map(any)
  default = {}
}

variable "nlb_backend_sets" {
  type    = map(any)
  default = {}
}
variable "nlb_backends" {
  type    = map(any)
  default = {}
}
variable "nlb_reserved_ips" {
  description = "To provision Network Load Balancer Reserved IPs"
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

variable "vnic_attachments" {
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
###### OSS Buckets ######
#########################

variable "oss" {
  description = "To provision Buckets - OSS"
  type        = map(any)
  default     = {}
}

#########################
####### OSS Logs ########
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
### OSS IAM Policies ####
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

###########################
######### Budgets #########
###########################

variable "budgets" {
  type    = map(any)
  default = {}
}

variable "budget_alert_rules" {
  type    = map(any)
  default = {}
}

###########################
####### Cloud Guard #######
###########################

variable "cloud_guard_configs" {
  type    = map(any)
  default = {}
}

variable "cloud_guard_targets" {
  type    = map(any)
  default = {}
}

####################################
####### Custom Backup Policy #######
####################################

variable "custom_backup_policies" {
  type    = map(any)
  default = {}
}

##########################
# Add new variables here #
##########################

variable "capacity_reservation_ocids" {
  type = map(any)
  default = {
    "AD1" : "<AD1 Capacity Reservation OCID>",
    "AD2" : "<AD2 Capacity Reservation OCID>",
    "AD3" : "<AD3 Capacity Reservation OCID>"
  }
}

######################### END #########################
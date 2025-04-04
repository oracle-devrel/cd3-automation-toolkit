# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
    # Use '\n' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
    #START_instance_ssh_keys#
    # exported instance ssh keys
    #instance_ssh_keys_END#
  }
}

variable "oke_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    # Use '\n' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
    #START_oke_ssh_keys#
    #oke_ssh_keys_END#
  }
}
variable "sddc_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    # Use '\n' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
    #START_sddc_ssh_keys#
    #sddc_ssh_keys_END#
  }
}

variable "exacs_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = ["<SSH PUB KEY STRING HERE>"]
    # Use ',' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = ["ssh-rsa AAXXX......yhdlo","ssh-rsa AAxxskj...edfwf"]
    #START_exacs_ssh_keys#
    # exported exacs ssh keys
    #exacs_ssh_keys_END#
  }
}

variable "dbsystem_ssh_keys" {
  type = map(any)
  default = {
    ssh_public_key = ["<SSH PUB KEY STRING HERE>"]
    # Use ',' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = ["ssh-rsa AAXXX......yhdlo","ssh-rsa AAxxskj...edfwf"]
    #START_dbsystem_ssh_keys#
    # exported dbsystem ssh keys
    #dbsystem_ssh_keys_END#
  }
}

###################################
# Platform Image OCIDs, Source OCIDS
# and Market Place Images
###################################
# Reference url to get the OCIDS : https://docs.oracle.com/en-us/iaas/images/
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

variable "blockvolume_source_ocids" {
  type = map(any)
  default = {
    block1 = "<Source OCID here>"
    #blockvolume_source_ocid    = "<VOLUME SOURCE OCID HERE>"
    #START_blockvolume_source_ocids#
    # exported block volume source ocids
    #blockvolume_source_ocids_END#
  }
}

variable "fss_source_ocids" {
  type = map(any)
  default = {
    snapshot1 = "<Source Snapshot OCID here>"
    #fss_source_snapshot_ocid    = "<SOURCE SNAPSHOT OCID HERE>"
    #START_fss_source_snapshot_ocids#
    # exported fss source snapshot ocids
    #fss_source_snapshot_ocids_END#
  }
}

variable "oke_source_ocids" {
  type = map(any)
  default = {
    Linux = "<OKE LINUX OCID HERE>"
    #START_oke_source_ocids#
    # exported oke image ocids
    #oke_source_ocids_END#
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
	members           = optional(list(string), [])
    matching_rule     = optional(string)
    defined_tags      = optional(map(any))
    freeform_tags     = optional(map(any))
  }))
  default = {}
}

variable "identity_domain_groups" {
  type = map(object({
    group_name        = string
    group_description = optional(string)
    idcs_endpoint     = string
    domain_compartment_id    = string
    matching_rule     = optional(string)
    defined_tags      = optional(list(map(any)))
    freeform_tags     = optional(list(map(any)))
    members           = optional(list(string))
    user_can_request_access = optional(bool)
  }))
  default = {}
}


variable "users" {
  type = map(object({
    name                 = string
    description          = string
    email                = string
    enabled_capabilities = optional(list(string))
    group_membership     = optional(list(string))
    defined_tags         = optional(map(any))
    freeform_tags        = optional(map(any))
  }))
  default = {}
}

variable "identity_domain_users" {
  type = map(object({
    name = object({
      family_name = string
      given_name  = optional(string)
      middle_name = optional(string)
      honorific_prefix      = optional(string)
    })
    display_name         = optional(string)
    idcs_endpoint        = string
    user_name            = string
    domain_compartment_id    = string
    description          = optional(string)
    groups               = optional(list(string))
    email                = string
    recovery_email       = optional(string)
    home_phone_number    = optional(string)
    mobile_phone_number  = optional(string)
    enabled_capabilities = list(string)
    defined_tags      = optional(list(map(any)))
    freeform_tags     = optional(list(map(any)))
  }))
  default = {}
}



variable "networkSources" {
  type = map(object({
    name                = string
    description         = string
    public_source_list  = optional(list(string))
    defined_tags        = optional(map(any))
    freeform_tags       = optional(map(any))
    virtual_source_list = optional(list(map(list(string))))

  }))
  default = {}
}

#########################
####### Governance #########
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

variable "quota_policies" {
  type = map(object({
	quota_name               = string
	quota_description        = string
	quota_statements         = list(string)
    defined_tags               = optional(map(any))
    freeform_tags              = optional(map(any))
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
    route_table_id = optional(string)
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
    route_table_id = optional(string)
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
  type = map(object({
    compartment_id      = string
    vcn_id              = string
    display_name        = optional(string)
    defined_tags        = optional(map(any))
    freeform_tags       = optional(map(any))
    route_rules_igw     = list(map(any))
    route_rules_ngw     = list(map(any))
    route_rules_sgw     = list(map(any))
    route_rules_drg     = list(map(any))
    route_rules_lpg     = list(map(any))
    route_rules_ip      = list(map(any))
    gateway_route_table = optional(bool)
    default_route_table = optional(bool)

  }))
  default = {}
}

variable "default_route_tables" {
  type = map(object({
    compartment_id      = string
    vcn_id              = string
    display_name        = optional(string)
    defined_tags        = optional(map(any))
    freeform_tags       = optional(map(any))
    route_rules_igw     = list(map(any))
    route_rules_ngw     = list(map(any))
    route_rules_sgw     = list(map(any))
    route_rules_drg     = list(map(any))
    route_rules_lpg     = list(map(any))
    route_rules_ip      = list(map(any))
    gateway_route_table = optional(bool)
    default_route_table = optional(bool)
  }))
  default = {}
}

variable "nsgs" {
  type = map(object({
    compartment_id         = string
    network_compartment_id = string
    vcn_name               = string
    display_name           = optional(string)
    defined_tags           = optional(map(any))
    freeform_tags          = optional(map(any))
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

variable "vlans" {
  type = map(object({
    cidr_block             = string
    compartment_id         = string
    network_compartment_id = string
    vcn_name               = string
    display_name           = optional(string)
    nsg_ids                = optional(list(string))
    route_table_name       = optional(string)
    vlan_tag               = optional(string)
    availability_domain    = optional(string)
    freeform_tags          = optional(map(any))
    defined_tags           = optional(map(any))
  }))
  default = {}
}

variable "drg_attachments" {
  type    = map(any)
  default = {}
}

variable "drg_other_attachments" {
  type    = map(any)
  default = {}
}

variable "drg_route_tables" {
  type = map(object({
    drg_id                           = string
    display_name                     = optional(string)
    defined_tags                     = optional(map(any))
    freeform_tags                    = optional(map(any))
    is_ecmp_enabled                  = optional(bool)
    import_drg_route_distribution_id = optional(string)
  }))
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

####################
####### DNS  #######
####################

variable "zones" {
  type = map(object({
    compartment_id      = string
    display_name        = string
    view_compartment_id = optional(string)
    view_id             = optional(string)
    zone_type           = optional(string)
    scope               = optional(string)
    freeform_tags       = optional(map(any))
    defined_tags        = optional(map(any))
  }))
  default = {}
}

variable "views" {
  type = map(object({
    compartment_id = string
    display_name   = string
    scope          = optional(string)
    freeform_tags  = optional(map(any))
    defined_tags   = optional(map(any))
  }))
  default = {}
}

variable "rrsets" {
  type = map(object({
    compartment_id      = optional(string)
    view_compartment_id = optional(string)
    view_id             = optional(string)
    zone_id             = string
    domain              = string
    rtype               = string
    ttl                 = number
    rdata               = optional(list(string))
    scope               = optional(string)
  }))
  default = {}
}

variable "resolvers" {
  type = map(object({
    network_compartment_id = string
    vcn_name               = string
    display_name           = optional(string)
    views = optional(map(object({
      view_id             = optional(string)
      view_compartment_id = optional(string)
    })))
    resolver_rules = optional(map(object({
      client_address_conditions = optional(list(any))
      destination_addresses     = optional(list(any))
      qname_cover_conditions    = optional(list(any))
      source_endpoint_name      = optional(string)
    })))
    endpoint_names = optional(map(object({
      is_forwarding      = optional(bool)
      is_listening       = optional(bool)
      name               = optional(string)
      subnet_name        = optional(string)
      forwarding_address = optional(string)
      listening_address  = optional(string)
      nsg_ids            = optional(list(string))
    })))
    freeform_tags = optional(map(any))
    defined_tags  = optional(map(any))
  }))
  default = {}
}


#########################
## Dedicated VM Hosts ##
#########################

variable "dedicated_hosts" {
  type = map(object({
    availability_domain = string
    compartment_id      = string
    vm_host_shape       = string
    defined_tags        = optional(map(any))
    display_name        = optional(string)
    fault_domain        = optional(string)
    freeform_tags       = optional(map(any))
  }))
  description = "To provision new dedicated VM hosts"
  default     = {}
}

#########################
## Instances/Block Volumes ##
#########################

variable "blockvolumes" {
  description = "To provision block volumes"
  type = map(object({
    availability_domain                 = string
    compartment_id                      = string
    display_name                        = string
    size_in_gbs                         = optional(string)
    is_auto_tune_enabled                = optional(string)
    vpus_per_gb                         = optional(string)
    kms_key_id                          = optional(string)
    attach_to_instance                  = optional(string)
    attachment_type                     = optional(string)
    backup_policy                       = optional(string)
    policy_compartment_id               = optional(string)
    device                              = optional(string)
    encryption_in_transit_type          = optional(string)
    attachment_display_name             = optional(string)
    is_read_only                        = optional(bool)
    is_pv_encryption_in_transit_enabled = optional(bool)
    is_shareable                        = optional(bool)
    use_chap                            = optional(bool)
    is_agent_auto_iscsi_login_enabled   = optional(bool)
    defined_tags                        = optional(map(any))
    freeform_tags                       = optional(map(any))
    source_details                      = optional(list(map(any)))
    block_volume_replicas               = optional(list(map(any)))
    block_volume_replicas_deletion      = optional(bool)
    autotune_policies                   = optional(list(map(any)))
  }))
  default = {}
}

variable "block_backup_policies" {
  type        = map(any)
  description = "To create block volume back policy"
  default     = {}
}

variable "instances" {
  description = "Map of instances to be provisioned"
  type = map(object({
    availability_domain                        = string
    compartment_id                             = string
    shape                                      = string
    source_id                                  = string
    source_type                                = string
    vcn_name                                   = string
    subnet_id                                  = string
    network_compartment_id                     = string
    display_name                               = optional(string)
    assign_public_ip                           = optional(bool)
    boot_volume_size_in_gbs                    = optional(string)
    fault_domain                               = optional(string)
    dedicated_vm_host_id                       = optional(string)
    private_ip                                 = optional(string)
    hostname_label                             = optional(string)
    nsg_ids                                    = optional(list(string))
    ocpus                                      = optional(string)
    memory_in_gbs                              = optional(number)
    capacity_reservation_id                    = optional(string)
    create_is_pv_encryption_in_transit_enabled = optional(bool)
    remote_execute                             = optional(string)
    bastion_ip                                 = optional(string)
    cloud_init_script                          = optional(string)
    ssh_authorized_keys                        = optional(string)
    backup_policy                              = optional(string)
    policy_compartment_id                      = optional(string)
    network_type                               = optional(string)
    #extended_metadata                          = optional(string)
    skip_source_dest_check    = optional(bool)
    baseline_ocpu_utilization = optional(string)
    #preemptible_instance_config                = optional(string)
    all_plugins_disabled                = optional(bool)
    is_management_disabled              = optional(bool)
    is_monitoring_disabled              = optional(bool)
    assign_private_dns_record           = optional(string)
    plugins_details                     = optional(map(any))
    is_live_migration_preferred         = optional(bool)
    recovery_action                     = optional(string)
    are_legacy_imds_endpoints_disabled  = optional(bool)
    boot_volume_type                    = optional(string)
    firmware                            = optional(string)
    is_consistent_volume_naming_enabled = optional(bool)
    remote_data_volume_type             = optional(string)
    platform_config                     = optional(list(map(any)))
    launch_options                      = optional(list(map(any)))
    ipxe_script                         = optional(string)
    preserve_boot_volume                = optional(bool)
    vlan_id                             = optional(string)
    kms_key_id                          = optional(string)
    vnic_display_name                   = optional(string)
    vnic_defined_tags                   = optional(map(any))
    vnic_freeform_tags                  = optional(map(any))
    defined_tags                        = optional(map(any))
    freeform_tags                       = optional(map(any))
  }))
  default = {}
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
    admin_password           = optional(string)
    character_set            = optional(string)
    compartment_id           = string
    cpu_core_count           = optional(number)
    database_edition         = optional(string)
    data_storage_size_in_tbs = optional(number)
    customer_contacts        = optional(list(string))
    db_name                  = string
    db_version               = optional(string)
    db_workload              = optional(string)
    display_name             = optional(string)
    license_model            = optional(string)
    ncharacter_set           = optional(string)
    network_compartment_id   = optional(string)
    nsg_ids                  = optional(list(string))
    subnet_id                = optional(string)
    vcn_name                 = optional(string)
    whitelisted_ips          = optional(list(string))
    defined_tags             = optional(map(any))
    freeform_tags            = optional(map(any))
  }))
  default = {}
}

####################################
####### MySql Database ########
####################################
variable "mysql_db_system" {
  type = map(object({
    compartment_id                                             = string
    network_compartment_id                                     = string
    configuration_compartment_id                               = string
    mysql_db_system_display_name                               = string
    configuration_id                                           = string
    mysql_shape_name                                           = string
    mysql_db_system_admin_username                             = optional(string)
    mysql_db_system_admin_password                             = optional(string)
    mysql_db_system_availability_domain                        = optional(string)
    subnet_id                                                  = string
    mysql_db_system_data_storage_size_in_gb                    = number
    mysql_db_system_hostname_label                             = string
    vcn_names                                                  = string
    mysql_db_system_backup_policy_is_enabled                   = bool
    mysql_db_system_backup_policy_pitr_policy_is_enabled       = bool
    mysql_db_system_backup_policy_retention_in_days            = number
    mysql_db_system_backup_policy_window_start_time            = string
    mysql_db_system_crash_recovery                             = string
    mysql_db_system_database_management                        = string
    mysql_db_system_deletion_policy_automatic_backup_retention = string
    mysql_db_system_deletion_policy_final_backup               = string
    mysql_db_system_deletion_policy_is_delete_protected        = bool
    mysql_db_system_description                                = string
    mysql_db_system_fault_domain                               = string
    mysql_db_system_ip_address                                 = optional(string)
    mysql_db_system_is_highly_available                        = bool
    mysql_db_system_maintenance_window_start_time              = string
    mysql_db_system_port                                       = number
    mysql_db_system_port_x                                     = number
    mysql_db_system_source_source_type                         = optional(string)
    backup_id                                                  = optional(string)
    defined_tags                                               = optional(map(any))
    freeform_tags                                              = optional(map(any))


  }))
  default = {}
}


variable "mysql_configuration" {
  type = map(object({
    compartment_id                                                            = string
    mysql_configuration_shape_name                                            = optional(string)
    defined_tags                                                              = optional(map(any))
    freeform_tags                                                             = optional(map(any))
    mysql_configuration_description                                           = optional(string)
    mysql_configuration_display_name                                          = optional(string)
    mysql_configuration_init_variables_lower_case_table_names                 = optional(string)
    mysql_configuration_variables_autocommit                                  = optional(string)
    mysql_configuration_variables_big_tables                                  = optional(string)
    mysql_configuration_variables_binlog_expire_logs_seconds                  = optional(string)
    mysql_configuration_variables_binlog_row_metadata                         = optional(string)
    mysql_configuration_variables_binlog_row_value_options                    = optional(string)
    mysql_configuration_variables_binlog_transaction_compression              = optional(string)
    mysql_configuration_variables_connection_memory_chunk_size                = optional(string)
    mysql_configuration_variables_connect_timeout                             = optional(string)
    mysql_configuration_variables_completion_type                             = optional(string)
    mysql_configuration_variables_connection_memory_limit                     = optional(string)
    mysql_configuration_variables_cte_max_recursion_depth                     = optional(string)
    mysql_configuration_variables_default_authentication_plugin               = optional(string)
    mysql_configuration_variables_foreign_key_checks                          = optional(string)
    mysql_configuration_variables_global_connection_memory_limit              = optional(string)
    mysql_configuration_variables_global_connection_memory_tracking           = optional(string)
    mysql_configuration_variables_group_replication_consistency               = optional(string)
    mysql_configuration_variables_information_schema_stats_expiry             = optional(string)
    mysql_configuration_variables_innodb_buffer_pool_dump_pct                 = optional(string)
    mysql_configuration_variables_innodb_buffer_pool_instances                = optional(string)
    mysql_configuration_variables_innodb_buffer_pool_size                     = optional(string)
    mysql_configuration_variables_innodb_ddl_buffer_size                      = optional(string)
    mysql_configuration_variables_innodb_ddl_threads                          = optional(string)
    mysql_configuration_variables_innodb_ft_enable_stopword                   = optional(string)
    mysql_configuration_variables_innodb_ft_max_token_size                    = optional(string)
    mysql_configuration_variables_innodb_ft_min_token_size                    = optional(string)
    mysql_configuration_variables_innodb_ft_num_word_optimize                 = optional(string)
    mysql_configuration_variables_innodb_ft_result_cache_limit                = optional(string)
    mysql_configuration_variables_innodb_ft_server_stopword_table             = optional(string)
    mysql_configuration_variables_innodb_lock_wait_timeout                    = optional(string)
    mysql_configuration_variables_innodb_log_writer_threads                   = optional(string)
    mysql_configuration_variables_innodb_max_purge_lag                        = optional(string)
    mysql_configuration_variables_innodb_max_purge_lag_delay                  = optional(string)
    mysql_configuration_variables_innodb_stats_persistent_sample_pages        = optional(string)
    mysql_configuration_variables_innodb_stats_transient_sample_pages         = optional(string)
    mysql_configuration_variables_interactive_timeout                         = optional(string)
    mysql_configuration_variables_local_infile                                = optional(string)
    mysql_configuration_variables_mandatory_roles                             = optional(string)
    mysql_configuration_variables_max_allowed_packet                          = optional(string)
    mysql_configuration_variables_max_binlog_cache_size                       = optional(string)
    mysql_configuration_variables_max_connect_errors                          = optional(string)
    mysql_configuration_variables_max_connections                             = optional(string)
    mysql_configuration_variables_max_execution_time                          = optional(string)
    mysql_configuration_variables_max_heap_table_size                         = optional(string)
    mysql_configuration_variables_max_prepared_stmt_count                     = optional(string)
    mysql_configuration_variables_mysql_firewall_mode                         = optional(string)
    mysql_configuration_variables_mysqlx_connect_timeout                      = optional(string)
    mysql_configuration_variables_mysqlx_deflate_default_compression_level    = optional(string)
    mysql_configuration_variables_mysqlx_deflate_max_client_compression_level = optional(string)
    mysql_configuration_variables_mysqlx_enable_hello_notice                  = optional(string)
    mysql_configuration_variables_mysqlx_interactive_timeout                  = optional(string)
    mysql_configuration_variables_mysqlx_lz4default_compression_level         = optional(string)
    mysql_configuration_variables_mysqlx_lz4max_client_compression_level      = optional(string)
    mysql_configuration_variables_mysqlx_max_allowed_packet                   = optional(string)
    mysql_configuration_variables_mysqlx_read_timeout                         = optional(string)
    mysql_configuration_variables_mysqlx_wait_timeout                         = optional(string)
    mysql_configuration_variables_mysqlx_write_timeout                        = optional(string)
    mysql_configuration_variables_mysqlx_zstd_default_compression_level       = optional(string)
    mysql_configuration_variables_mysqlx_zstd_max_client_compression_level    = optional(string)
    mysql_configuration_variables_net_read_timeout                            = optional(string)
    mysql_configuration_variables_net_write_timeout                           = optional(string)
    mysql_configuration_variables_parser_max_mem_size                         = optional(string)
    mysql_configuration_variables_regexp_time_limit                           = optional(string)
    mysql_configuration_variables_sort_buffer_size                            = optional(string)
    mysql_configuration_variables_sql_mode                                    = optional(string)
    mysql_configuration_variables_sql_require_primary_key                     = optional(string)
    mysql_configuration_variables_sql_warnings                                = optional(string)
    mysql_configuration_variables_thread_pool_dedicated_listeners             = optional(string)
    mysql_configuration_variables_thread_pool_max_transactions_limit          = optional(string)
    mysql_configuration_variables_time_zone                                   = optional(string)
    mysql_configuration_variables_tmp_table_size                              = optional(string)
    mysql_configuration_variables_transaction_isolation                       = optional(string)
    mysql_configuration_variables_wait_timeout                                = optional(string)

  }))
  default = {}
}
#########################
######### FSS ###########
#########################

variable "mount_targets" {
  description = "To provision Mount Targets"
  type = map(object({
    availability_domain    = string
    compartment_id         = string
    network_compartment_id = string
    vcn_name               = string
    subnet_id              = string
    display_name           = optional(string)
    ip_address             = optional(string)
    hostname_label         = optional(string)
    nsg_ids                = optional(list(any))
    defined_tags           = optional(map(any))
    freeform_tags          = optional(map(any))
  }))
  default = {}
}

variable "fss" {
  description = "To provision File System Services"
  type = map(object({
    availability_domain   = string
    compartment_id        = string
    display_name          = optional(string)
    source_snapshot       = optional(string)
    snapshot_policy       = optional(string)
    policy_compartment_id = optional(string)
    kms_key_id            = optional(string)
    defined_tags          = optional(map(any))
    freeform_tags         = optional(map(any))
  }))
  default = {}
}

variable "nfs_export_options" {
  description = "To provision Export Sets"
  type = map(object({
    export_set_id                = string
    file_system_id               = string
    path                         = string
    export_options               = optional(list(any))
    defined_tags                 = optional(map(any))
    freeform_tags                = optional(map(any))
    is_idmap_groups_for_sys_auth = optional(bool)
  }))
  default = {}
}

variable "fss_replication" {
  description = "To provision File System Replication"
  type = map(object({
    compartment_id       = string
    source_id            = string
    target_id            = string
    display_name         = optional(string)
    replication_interval = optional(number)
    defined_tags         = optional(map(any))
    freeform_tags        = optional(map(any))
  }))
  default = {}
}

#########################
####### FSS Logs ########
#########################

variable "nfs_log_groups" {
  description = "To provision Log Groups for Mount Target"
  type = map(object({
    compartment_id = string
    display_name   = string
    description    = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "nfs_logs" {
  description = "To provision Logs for Mount Target"
  type = map(object({
    display_name       = string
    log_group_id       = string
    log_type           = string
    compartment_id     = optional(string)
    category           = optional(string)
    resource           = optional(string)
    service            = optional(string)
    source_type        = optional(string)
    is_enabled         = optional(bool)
    retention_duration = optional(number)
    defined_tags       = optional(map(any))
    freeform_tags      = optional(map(any))
  }))
  default = {}
}


#########################
#### Load Balancers #####
#########################

variable "load_balancers" {
  description = "To provision Load Balancers"
  type = map(object({
    compartment_id         = string
    vcn_name               = string
    shape                  = string
    subnet_ids             = list(any)
    network_compartment_id = string
    display_name           = string
    shape_details          = optional(list(map(any)))
    nsg_ids                = optional(list(any))
    is_private             = optional(bool)
    ip_mode                = optional(string)
    defined_tags           = optional(map(any))
    freeform_tags          = optional(map(any))
    reserved_ips_id        = optional(string)
  }))
  default = {}
}

variable "hostnames" {
  description = "To provision Load Balancer Hostnames"
  type = map(object({
    load_balancer_id = string
    hostname         = string
    name             = string
  }))
  default = {}
}

variable "certificates" {
  description = "To provision Load Balancer Certificates"
  type = map(object({
    certificate_name   = string
    load_balancer_id   = string
    ca_certificate     = optional(string)
    passphrase         = optional(string)
    private_key        = optional(string)
    public_certificate = optional(string)
  }))
  default = {}
}

variable "cipher_suites" {
  description = "To provision Load Balancer Cipher Suites"
  type = map(object({
    ciphers          = list(string)
    name             = string
    load_balancer_id = optional(string)
  }))
  default = {}
}

variable "backend_sets" {
  description = "To provision Load Balancer Backend Sets"
  type = map(object({
    name                = string
    load_balancer_id    = string
    policy              = string
    protocol            = optional(string)
    interval_ms         = optional(string)
    is_force_plain_text = optional(string)
    port                = optional(string)
    response_body_regex = optional(string)
    retries             = optional(string)
    return_code         = optional(string)
    timeout_in_millis   = optional(string)
    url_path            = optional(string)
    lb_cookie_session = optional(list(object({
      cookie_name        = optional(string)
      disable_fallback   = optional(string)
      path               = optional(string)
      domain             = optional(string)
      is_http_only       = optional(string)
      is_secure          = optional(string)
      max_age_in_seconds = optional(string)
    })))
    session_persistence_configuration = optional(list(object({
      cookie_name      = optional(string)
      disable_fallback = optional(string)
    })))
    certificate_name  = optional(string)
    cipher_suite_name = optional(string)
    ssl_configuration = optional(list(object({
      certificate_ids                   = optional(list(any))
      server_order_preference           = optional(string)
      trusted_certificate_authority_ids = optional(list(any))
      verify_peer_certificate           = optional(string)
      verify_depth                      = optional(string)
      protocols                         = optional(list(any))
    })))
  }))
  default = {}
}

variable "backends" {
  description = "To provision Load Balancer Backends"
  type = map(object({
    backendset_name      = string
    ip_address           = string
    load_balancer_id     = string
    port                 = string
    instance_compartment = optional(string)
    backup               = optional(string)
    drain                = optional(string)
    offline              = optional(string)
    weight               = optional(string)
  }))
  default = {}
}

variable "listeners" {
  description = "To provision Load Balancer Listeners"
  type = map(object({
    name                     = string
    load_balancer_id         = string
    port                     = string
    protocol                 = string
    default_backend_set_name = string
    connection_configuration = optional(list(map(any)))
    hostname_names           = optional(list(any))
    path_route_set_name      = optional(string)
    rule_set_names           = optional(list(any))
    routing_policy_name      = optional(string)
    certificate_name         = optional(string)
    cipher_suite_name        = optional(string)
    ssl_configuration = optional(list(object({
      certificate_ids                   = optional(list(any))
      server_order_preference           = optional(string)
      trusted_certificate_authority_ids = optional(list(any))
      verify_peer_certificate           = optional(string)
      verify_depth                      = optional(string)
      protocols                         = optional(list(any))
    })))
  }))
  default = {}
}

variable "path_route_sets" {
  description = "To provision Load Balancer Path Route Sets"
  type = map(object({
    name             = string
    load_balancer_id = string
    path_routes      = optional(list(map(any)))
  }))
  default = {}
}

variable "rule_sets" {
  description = "To provision Load Balancer Rule Sets"
  type = map(object({
    name             = string
    load_balancer_id = string
    access_control_rules = optional(list(object({
      action          = string
      attribute_name  = optional(string)
      attribute_value = optional(string)
      description     = optional(string)
    })))
    access_control_method_rules = optional(list(object({
      action          = string
      allowed_methods = optional(list(any))
      status_code     = optional(string)
    })))
    http_header_rules = optional(list(object({
      action                         = string
      are_invalid_characters_allowed = optional(bool)
      http_large_header_size_in_kb   = optional(string)
    })))
    uri_redirect_rules = optional(list(object({
      action          = string
      attribute_name  = optional(string)
      attribute_value = optional(string)
      operator        = optional(string)
      host            = optional(string)
      path            = optional(string)
      port            = optional(string)
      protocol        = optional(string)
      query           = optional(string)
      response_code   = optional(string)
    })))
    request_response_header_rules = optional(list(object({
      action = string
      header = optional(string)
      prefix = optional(string)
      suffix = optional(string)
      value  = optional(string)
    })))
  }))
  default = {}
}

variable "lbr_reserved_ips" {
  description = "To provision Load Balancer Reserved IPs"
  type = map(object({
    compartment_id    = string
    display_name      = string
    lifetime          = string
    private_ip_id     = optional(string)
    public_ip_pool_id = optional(string)
    defined_tags      = optional(map(any))
    freeform_tags     = optional(map(any))
  }))
  default = {}
}

variable "lb_routing_policies" {
  description = "To provision Load Balancer Routing Policies"
  type = map(object({
    name                       = string
    load_balancer_id           = string
    condition_language_version = optional(string)
    rules                      = optional(list(map(any)))
  }))
  default = {}
}

###################################
####### Load Balancer Logs ########
###################################

variable "loadbalancer_log_groups" {
  description = "To provision Log Groups for Load Balancers"
  type = map(object({
    compartment_id = string
    display_name   = string
    description    = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "loadbalancer_logs" {
  description = "To provision Logs for Load Balancers"
  type = map(object({
    display_name       = string
    log_group_id       = string
    log_type           = string
    compartment_id     = optional(string)
    category           = optional(string)
    resource           = optional(string)
    service            = optional(string)
    source_type        = optional(string)
    is_enabled         = optional(bool)
    retention_duration = optional(number)
    defined_tags       = optional(map(any))
    freeform_tags      = optional(map(any))
  }))
  default = {}
}

#########################
## Network Load Balancers ##
#########################

variable "network_load_balancers" {
  type = map(object({
    display_name                   = string
    compartment_id                 = string
    network_compartment_id         = string
    vcn_name                       = string
    subnet_id                      = string
    is_private                     = optional(bool)
    reserved_ips_id                = string
    is_preserve_source_destination = optional(bool)
    is_symmetric_hash_enabled      = optional(bool)
    nlb_ip_version                 = optional(string)
    assigned_private_ipv4          = optional(string)
    nsg_ids                        = optional(list(string))
    defined_tags                   = optional(map(any))
    freeform_tags                  = optional(map(any))
  }))
  default = {}
}
variable "nlb_listeners" {
  type = map(object({
    name                     = string
    network_load_balancer_id = string
    default_backend_set_name = string
    port                     = number
    protocol                 = string
    ip_version               = optional(string)
  }))
  default = {}
}

variable "nlb_backend_sets" {
  type = map(object({
    name                     = string
    network_load_balancer_id = string
    policy                   = string
    protocol                 = string
    domain_name              = optional(string)
    query_class              = optional(string)
    query_type               = optional(string)
    rcodes                   = optional(list(string))
    transport_protocol       = optional(string)
    return_code              = optional(number)
    interval_in_millis       = optional(number)
    port                     = optional(number)
    request_data             = optional(string)
    response_body_regex      = optional(string)
    response_data            = optional(string)
    retries                  = optional(number)
    timeout_in_millis        = optional(number)
    url_path                 = optional(string)
    is_preserve_source       = optional(bool)
    ip_version               = optional(string)
  }))
  default = {}
}
variable "nlb_backends" {
  type = map(object({
    name                     = optional(string)
    backend_set_name         = string
    network_load_balancer_id = string
    port                     = number
    #vnic_vlan                = optional(string)
    #vnic_ip                  = optional(string)
    ip_address               = string
    instance_compartment     = string
    is_drain                 = optional(bool)
    is_backup                = optional(bool)
    is_offline               = optional(bool)
    weight                   = optional(number)
    target_id                = optional(string)
  }))
  default = {}
}
variable "nlb_reserved_ips" {
  description = "To provision Network Load Balancer Reserved IPs"
  type = map(object({
    compartment_id    = string
    lifetime          = string
    defined_tags      = optional(map(any))
    freeform_tags     = optional(map(any))
    display_name      = optional(string)
    private_ip_id     = optional(string)
    public_ip_pool_id = optional(string)
  }))
  default = {}
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
  type = map(object({
    compartment_id = string
    display_name   = string
    description    = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "vcn_logs" {
  type = map(object({
    display_name       = string
    log_group_id       = string
    log_type           = string
    compartment_id     = optional(string)
    category           = optional(string)
    resource           = optional(string)
    service            = optional(string)
    source_type        = optional(string)
    is_enabled         = optional(bool)
    retention_duration = optional(number)
    defined_tags       = optional(map(any))
    freeform_tags      = optional(map(any))
  }))
  default = {}
}

#########################
###### OSS Buckets ######
#########################

variable "buckets" {
  type    = map(any)
  default = {}
}

#########################
####### OSS Logs ########
#########################

variable "oss_log_groups" {
  description = "To provision Log Groups for OSS"
  type = map(object({
    compartment_id = string
    display_name   = string
    description    = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "oss_logs" {
  description = "To provision Logs for OSS"
  type = map(object({
    display_name       = string
    log_group_id       = string
    log_type           = string
    compartment_id     = optional(string)
    category           = optional(string)
    resource           = optional(string)
    service            = optional(string)
    source_type        = optional(string)
    is_enabled         = optional(bool)
    retention_duration = optional(number)
    defined_tags       = optional(map(any))
    freeform_tags      = optional(map(any))
  }))
  default = {}
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
  type = map(object({
    compartment_id                                = string
    destinations                                  = list(string)
    alarm_name                                    = string
    is_enabled                                    = bool
    metric_compartment_id                         = string
    namespace                                     = string
    query                                         = string
    severity                                      = string
    body                                          = optional(string)
    message_format                                = optional(string)
    defined_tags                                  = optional(map(any))
    freeform_tags                                 = optional(map(any))
    is_notifications_per_metric_dimension_enabled = optional(bool)
    metric_compartment_id_in_subtree              = optional(string)
    trigger_delay_minutes                         = optional(string)
    repeat_notification_duration                  = optional(string)
    resolution                                    = optional(string)
    resource_group                                = optional(string)
    suppression                                   = optional(map(any))
  }))
  default = {}
}

variable "events" {
  type = map(object({
    event_name     = string
    compartment_id = string
    description    = string
    is_enabled     = bool
    condition      = string
    actions = optional(list(object({
      action_type = string
      is_enabled  = string
      description = optional(string)
      function_id = optional(string)
      stream_id   = optional(string)
      topic_id    = optional(string)
    })))
    message_format = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "notifications_topics" {
  type = map(object({
    compartment_id = string
    topic_name     = string
    description    = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "notifications_subscriptions" {
  type = map(object({
    compartment_id = string
    endpoint       = string
    protocol       = string
    topic_id       = string
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "service_connectors" {
  type        = any
  default     = {}
  description = "To provision service connector hub resources"
}

#########################
## Developer Services ##
#########################

## OKE

variable "clusters" {
  type = map(object({
    display_name                    = string
    compartment_id                  = string
    network_compartment_id          = string
    vcn_name                        = string
    kubernetes_version              = string
    cni_type                        = string
    cluster_type                    = string
    is_policy_enabled               = optional(bool)
    policy_kms_key_id               = optional(string)
    is_kubernetes_dashboard_enabled = optional(bool)
    is_tiller_enabled               = optional(bool)
    is_public_ip_enabled            = optional(bool)
    nsg_ids                         = optional(list(string))
    endpoint_subnet_id              = string
    is_pod_security_policy_enabled  = optional(bool)
    pods_cidr                       = optional(string)
    services_cidr                   = optional(string)
    service_lb_subnet_ids           = optional(list(string))
    cluster_kms_key_id              = optional(string)
    defined_tags                    = optional(map(any))
    freeform_tags                   = optional(map(any))
    lb_defined_tags                 = optional(map(any))
    lb_freeform_tags                = optional(map(any))
    volume_defined_tags             = optional(map(any))
    volume_freeform_tags            = optional(map(any))
  }))
  default = {}
}

variable "nodepools" {
  type = map(object({
    display_name                        = string
    cluster_name                        = string
    compartment_id                      = string
    network_compartment_id              = string
    vcn_name                            = string
    node_shape                          = string
    initial_node_labels                 = optional(map(any))
    kubernetes_version                  = string
    is_pv_encryption_in_transit_enabled = optional(bool)
    availability_domain                 = number
    fault_domains                       = optional(list(string))
    subnet_id                           = string
    size                                = number
    cni_type                            = string
    max_pods_per_node                   = optional(number)
    pod_nsg_ids                         = optional(list(string))
    pod_subnet_ids                      = optional(string)
    worker_nsg_ids                      = optional(list(string))
    memory_in_gbs                       = optional(number)
    ocpus                               = optional(number)
    image_id                            = string
    source_type                         = string
    boot_volume_size_in_gbs             = optional(number)
    ssh_public_key                      = optional(string)
    nodepool_kms_key_id                 = optional(string)
    node_defined_tags                   = optional(map(any))
    node_freeform_tags                  = optional(map(any))
    nodepool_defined_tags               = optional(map(any))
    nodepool_freeform_tags              = optional(map(any))
  }))
  default = {}
}

variable "virtual-nodepools" {
  type = map(object({
    display_name                = string
    cluster_name                = string
    compartment_id              = string
    network_compartment_id      = string
    vcn_name                    = string
    node_shape                  = string
    initial_virtual_node_labels = optional(map(any))
    availability_domain         = number
    fault_domains               = list(string)
    subnet_id                   = string
    size                        = number
    pod_nsg_ids                 = optional(list(string))
    pod_subnet_id               = string
    worker_nsg_ids              = optional(list(string))
    taints                      = optional(list(any))
    node_defined_tags           = optional(map(any))
    node_freeform_tags          = optional(map(any))
    nodepool_defined_tags       = optional(map(any))
    nodepool_freeform_tags      = optional(map(any))
  }))
  default = {}
}


##################################
############## SDDCs #############
##################################
variable "sddcs" {
  type = map(object({
    compartment_id                        = string
    availability_domain                   = string
    network_compartment_id                = string
    vcn_name                              = string
    esxi_hosts_count                      = number
    nsx_edge_uplink1vlan_id               = string
    nsx_edge_uplink2vlan_id               = string
    nsx_edge_vtep_vlan_id                 = string
    nsx_vtep_vlan_id                      = string
    provisioning_subnet_id                = string
    ssh_authorized_keys                   = string
    vmotion_vlan_id                       = string
    vmware_software_version               = string
    vsan_vlan_id                          = string
    vsphere_vlan_id                       = string
    capacity_reservation_id               = optional(string)
    defined_tags                          = optional(map(any))
    display_name                          = optional(string)
    initial_cluster_display_name          = optional(string)
    freeform_tags                         = optional(map(any))
    hcx_action                            = optional(string)
    hcx_vlan_id                           = optional(string)
    initial_host_ocpu_count               = optional(number)
    initial_host_shape_name               = optional(string)
    initial_commitment                    = optional(string)
    instance_display_name_prefix          = optional(string)
    is_hcx_enabled                        = optional(bool)
    is_shielded_instance_enabled          = optional(bool)
    is_single_host_sddc                   = optional(bool)
    provisioning_vlan_id                  = optional(string)
    refresh_hcx_license_status            = optional(bool)
    replication_vlan_id                   = optional(string)
    reserving_hcx_on_premise_license_keys = optional(string)
    workload_network_cidr                 = optional(string)
    management_datastore                  = optional(list(string))
    workload_datastore                    = optional(list(string))

  }))
  default = {}

}

variable "sddc-clusters" {
  type = map(object({
    compartment_id                        = string
    availability_domain                   = string
    network_compartment_id                = string
    vcn_name                              = string
    esxi_hosts_count                      = number
    nsx_edge_uplink1vlan_id               = string
    nsx_edge_uplink2vlan_id               = optional(string)
    nsx_edge_vtep_vlan_id                 = string
    nsx_vtep_vlan_id                      = string
    provisioning_subnet_id                = string
    ssh_authorized_keys                   = optional(string)
    vmotion_vlan_id                       = string
    vmware_software_version               = string
    vsan_vlan_id                          = string
    vsphere_vlan_id                       = string
    capacity_reservation_id               = optional(string)
    defined_tags                          = optional(map(any))
    display_name                          = optional(string)
    freeform_tags                         = optional(map(any))
    hcx_action                            = optional(string)
    hcx_vlan_id                           = optional(string)
    initial_host_ocpu_count               = optional(number)
    initial_host_shape_name               = optional(string)
    initial_commitment                    = optional(string)
    instance_display_name_prefix          = optional(string)
    is_hcx_enabled                        = optional(bool)
    is_shielded_instance_enabled          = optional(bool)
    is_single_host_sddc                   = optional(bool)
    provisioning_vlan_id                  = optional(string)
    refresh_hcx_license_status            = optional(bool)
    replication_vlan_id                   = optional(string)
    reserving_hcx_on_premise_license_keys = optional(string)
    workload_network_cidr                 = optional(string)
    workload_datastore                    = optional(list(string))
    sddc_id                               = optional(string)
    esxi_software_version                 = optional(string)

  }))
  default = {}

}


############################
## KMS (Keys/Vauts) ##
############################

variable "vaults" {
  type = map(object({
    compartment_id = string
    display_name   = string
    vault_type     = string
    freeform_tags  = optional(map(any))
    defined_tags   = optional(map(any))
    replica_region = optional(string)
  }))
  default = {}
}

variable "keys" {
  type = map(object({
    compartment_id            = string
    display_name              = string
    vault_name                = string
    algorithm                 = optional(string)
    length                    = optional(string)
    curve_id                  = optional(string)
    protection_mode           = optional(string)
    freeform_tags             = optional(map(any))
    defined_tags              = optional(map(any))
    is_auto_rotation_enabled  = optional(bool)
    rotation_interval_in_days = optional(string)

  }))
  default = {}
}

###########################
######### Budgets #########
###########################

variable "budgets" {
  type = map(object({
    amount                                = string
    compartment_id                        = string
    reset_period                          = string
    budget_processing_period_start_offset = optional(string)
    defined_tags                          = optional(map(any))
    description                           = optional(string)
    display_name                          = optional(string)
    freeform_tags                         = optional(map(any))
    processing_period_type                = optional(string)
    budget_end_date                       = optional(string)
    budget_start_date                     = optional(string)
    target_type                           = optional(string)
    targets                               = optional(list(any))
  }))
  default = {}
}

variable "budget_alert_rules" {
  type = map(object({
    budget_id      = string
    threshold      = string
    threshold_type = string
    type           = string
    defined_tags   = optional(map(any))
    description    = optional(string)
    display_name   = optional(string)
    freeform_tags  = optional(map(any))
    message        = optional(string)
    recipients     = optional(string)
  }))
  default = {}
}

###########################
####### Cloud Guard #######
###########################

variable "cloud_guard_configs" {
  type = map(object({
    compartment_id        = string
    reporting_region      = string
    status                = string
    self_manage_resources = optional(string)

  }))
  default = {}
}

variable "cloud_guard_targets" {
  type = map(object({
    compartment_id           = string
    display_name             = string
    target_resource_id       = string
    target_resource_type     = string
    prefix                   = string
    description              = optional(string)
    state                    = optional(string)
    target_detector_recipes  = optional(list(any))
    target_responder_recipes = optional(list(any))
    freeform_tags            = optional(map(any))
    defined_tags             = optional(map(any))
  }))
  default = {}
}

####################################
####### Custom Backup Policy #######
####################################

variable "custom_backup_policies" {
  type    = map(any)
  default = {}
}

variable "capacity_reservation_ocids" {
  type = map(any)
  default = {
    "AD1" : "<AD1 Capacity Reservation OCID>",
    "AD2" : "<AD2 Capacity Reservation OCID>",
    "AD3" : "<AD3 Capacity Reservation OCID>"
  }
}

#####################################
####### Firewall as a Service #######
#####################################
variable "firewalls" {
  type = map(object({
    compartment_id             = string
    network_compartment_id     = string
    network_firewall_policy_id = string
    subnet_id                  = string
    vcn_name                   = string
    display_name               = string
    ipv4address                = optional(string)
    nsg_id                     = optional(list(string))
    ipv6address                = optional(string)
    availability_domain        = optional(string)
    defined_tags               = optional(map(any))
    freeform_tags              = optional(map(any))
  }))
  default = {}
}

variable "fw-policies" {
  type = map(object({
    compartment_id = optional(string)
    display_name   = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}
variable "services" {
  type = map(object({
    service_name               = string
    service_type               = string
    network_firewall_policy_id = string
    port_ranges = list(object({
      minimum_port = string
      maximum_port = optional(string)
    }))
  }))
  default = {}
}
variable "url_lists" {
  type = map(object({
    urllist_name               = string
    network_firewall_policy_id = string
    urls = list(object({
      pattern = string
      type    = string
    }))
  }))
  default = {}
}
variable "service_lists" {
  type = map(object({
    service_list_name          = string
    network_firewall_policy_id = string
    services                   = list(string)
  }))
  default = {}
}

variable "address_lists" {
  type = map(object({
    address_list_name          = string
    network_firewall_policy_id = string
    address_type               = string
    addresses                  = list(string)
  }))
  default = {}
}

variable "applications" {
  type = map(object({
    app_list_name              = string
    network_firewall_policy_id = string
    app_type                   = string
    icmp_type                  = number
    icmp_code                  = optional(number)
  }))
  default = {}
}

variable "application_groups" {
  type = map(object({
    app_group_name             = string
    network_firewall_policy_id = string
    apps                       = list(string)

  }))
  default = {}
}

variable "security_rules" {
  type = map(object({
    action                     = string
    rule_name                  = string
    network_firewall_policy_id = string
    condition = optional(list(object({
      application         = optional(list(string))
      destination_address = optional(list(string))
      service             = optional(list(string))
      source_address      = optional(list(string))
      url                 = optional(list(string))
    })))
    inspection  = optional(string)
    after_rule  = optional(string)
    before_rule = optional(string)

  }))
  default = {}
}

variable "secrets" {
  type = map(object({
    secret_name                = string
    network_firewall_policy_id = string
    secret_source              = string
    secret_type                = string
    vault_secret_id            = string
    version_number             = number
    vault_name                 = string
    vault_compartment_id       = string
  }))
  default = {}
}

variable "decryption_profiles" {
  type = map(object({
    profile_name                          = string
    profile_type                          = string
    network_firewall_policy_id            = string
    are_certificate_extensions_restricted = optional(bool)
    is_auto_include_alt_name              = optional(bool)
    is_expired_certificate_blocked        = optional(bool)
    is_out_of_capacity_blocked            = optional(bool)
    is_revocation_status_timeout_blocked  = optional(bool)
    is_unknown_revocation_status_blocked  = optional(bool)
    is_unsupported_cipher_blocked         = optional(bool)
    is_unsupported_version_blocked        = optional(bool)
    is_untrusted_issuer_blocked           = optional(bool)
  }))
  default = {}
}

variable "decryption_rules" {
  type = map(object({
    action                     = string
    rule_name                  = string
    network_firewall_policy_id = string
    condition = optional(list(object({

      destination_address = optional(list(string))

      source_address = optional(list(string))

    })))
    decryption_profile = optional(string)
    secret             = optional(string)
    after_rule         = optional(string)
    before_rule        = optional(string)

  }))
  default = {}
}

variable "tunnelinspect_rules" {
  type = map(object({
    action                     = string
    rule_name                  = string
    network_firewall_policy_id = string
    condition = optional(list(object({
      destination_address = optional(list(string))
      source_address = optional(list(string))
    })))
    protocol = optional(string)
    after_rule         = optional(string)
    before_rule        = optional(string)
  }))
  default = {}
}
#########################
####### Firewall Logs ########
#########################

variable "fw_log_groups" {
  description = "To provision Log Groups for Network Firewall"
  type = map(object({
    compartment_id = string
    display_name   = string
    description    = optional(string)
    defined_tags   = optional(map(any))
    freeform_tags  = optional(map(any))
  }))
  default = {}
}

variable "fw_logs" {
  description = "To provision Logs for Network Firewall"
  type = map(object({
    display_name       = string
    log_group_id       = string
    log_type           = string
    compartment_id     = optional(string)
    category           = optional(string)
    resource           = optional(string)
    service            = optional(string)
    source_type        = optional(string)
    is_enabled         = optional(bool)
    retention_duration = optional(number)
    defined_tags       = optional(map(any))
    freeform_tags      = optional(map(any))
  }))
  default = {}
}

##########################
# Add new variables here #
##########################
######################### END #########################


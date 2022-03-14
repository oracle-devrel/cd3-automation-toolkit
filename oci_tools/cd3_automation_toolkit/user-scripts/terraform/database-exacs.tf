// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################################
# Module Block - Database
# Create ExaInfra
############################################

module "exa-infra" {
  source              = "./modules/database/exa-infra"
  for_each            = var.exa_infra != null ? var.exa_infra : {}
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id      = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name        = each.value.display_name
  shape               = each.value.shape
  compute_count       = each.value.compute_count
  #     customer_contacts_email = each.value.customer_contacts_email
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  storage_count = each.value.storage_count

  #Optional
  #   maintenance_window_preference = each.value.maintenance_window_preference
  #   maintenance_window_days_of_week_name = each.value.maintenance_window_days_of_week_name
  #   maintenance_window_hours_of_day = each.value.maintenance_window_hours_of_day
  #   maintenance_window_lead_time_in_weeks = each.value.maintenance_window_lead_time_in_weeks
  #   maintenance_window_months_name = each.value.maintenance_window_months_name
  #   maintenance_window_weeks_of_month = each.value.maintenance_window_weeks_of_month
}


############################################
# Module Block - Database
# Create ExaVMClusters
############################################

module "exa-vmclusters" {
  depends_on = [module.exa-infra]
  source     = "./modules/database/exa-vmcluster"

  for_each = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  backup_subnet_id = length(regexall("ocid1.subnet.oc1*", each.value.backup_subnet_id)) > 0 ? each.value.backup_subnet_id : merge(module.subnets.*...)[each.value.backup_subnet_id]["subnet_tf_id"]
  exadata_infrastructure_id = length(regexall("ocid1.cloudexadatainfrastructure.oc1*", each.value.exadata_infrastructure_id)) > 0 ? each.value.exadata_infrastructure_id : merge(module.exa-infra.*...)[each.value.exadata_infrastructure_id].exainfra_tf_id
  cpu_core_count            = each.value.cpu_core_count
  display_name              = each.value.display_name
  compartment_id            = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  gi_version                = each.value.gi_version
  hostname                  = each.value.hostname
  #ssh_public_keys          = length(regexall("ssh-rsa*",each.value.ssh_public_key)) > 0 ? each.value.ssh_public_key : var.ssh_public_key
  ssh_public_keys           = lookup(var.exacs_ssh_keys, each.value.ssh_public_keys, var.exacs_ssh_keys["ssh_public_key"] )
  cluster_subnet_id         = length(regexall("ocid1.subnet.oc1*", each.value.cluster_subnet_id)) > 0 ? each.value.cluster_subnet_id : merge(module.subnets.*...)[each.value.cluster_subnet_id]["subnet_tf_id"]
  backup_network_nsg_ids      = [for nsg in each.value.backup_network_nsg_ids : ( length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : try(merge(module.nsgs.*...)[nsg]["nsg_tf_id"][nsg],merge(module.nsgs.*...)[nsg]["nsg_tf_id"],merge(module.nsgs.*...)[nsg]["nsg_tf_id"]))]
  cluster_name                = each.value.cluster_name
  data_storage_percentage     = each.value.data_storage_percentage
  defined_tags                = each.value.defined_tags
  domain                      = each.value.domain
  freeform_tags               = each.value.freeform_tags
  is_local_backup_enabled     = each.value.is_local_backup_enabled
  is_sparse_diskgroup_enabled = each.value.is_sparse_diskgroup_enabled
  license_model               = each.value.license_model
  nsg_ids                     = [for nsg in each.value.nsg_ids : ( length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : try(merge(module.nsgs.*...)[nsg]["nsg_tf_id"][nsg],merge(module.nsgs.*...)[nsg]["nsg_tf_id"],merge(module.nsgs.*...)[nsg]["nsg_tf_id"]))]
  #nsg_ids                     = length(regexall("ocid1.networksecuritygroup.oc1*", each.value.nsg_ids)) > 0 ? each.value.nsg_id : merge(module.nsgs.*...)[each.value.nsg_ids]["nsg_tf_id"][0]
  ocpu_count                  = each.value.ocpu_count
  scan_listener_port_tcp      = each.value.scan_listener_port_tcp
  scan_listener_port_tcp_ssl  = each.value.scan_listener_port_tcp_ssl
  time_zone                   = each.value.time_zone
}
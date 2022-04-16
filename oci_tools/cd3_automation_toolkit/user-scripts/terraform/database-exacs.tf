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
  #   customer_contacts_email = each.value.customer_contacts_email
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

data "oci_core_subnets" "oci_cluster_subnets" {
  for_each = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.cluster_subnet_id
  vcn_id         = data.oci_core_vcns.oci_exa_vcns[each.value.display_name].virtual_networks.*.id[0]
}

data "oci_core_subnets" "oci_backup_subnets" {
  for_each = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.backup_subnet_id
  vcn_id         = data.oci_core_vcns.oci_exa_vcns[each.value.display_name].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_exa_vcns" {
  for_each = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "exa-vmclusters" {
  depends_on = [module.exa-infra]
  source     = "./modules/database/exa-vmcluster"

  for_each = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  exadata_infrastructure_id = length(regexall("ocid1.cloudexadatainfrastructure.oc1*", each.value.exadata_infrastructure_id)) > 0 ? each.value.exadata_infrastructure_id : merge(module.exa-infra.*...)[each.value.exadata_infrastructure_id].exainfra_tf_id
  cpu_core_count            = each.value.cpu_core_count
  display_name              = each.value.display_name
  compartment_id            = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id    = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null

  gi_version                = each.value.gi_version
  hostname                  = each.value.hostname
  #ssh_public_keys          = length(regexall("ssh-rsa*",each.value.ssh_public_key)) > 0 ? each.value.ssh_public_key : var.ssh_public_key
  ssh_public_keys           = lookup(var.exacs_ssh_keys, each.value.ssh_public_keys, var.exacs_ssh_keys["ssh_public_key"] )
  #cluster_subnet_id        = length(regexall("ocid1.subnet.oc1*", each.value.cluster_subnet_id)) > 0 ? each.value.cluster_subnet_id : merge(module.subnets.*...)[each.value.cluster_subnet_id]["subnet_tf_id"]
  #backup_subnet_id         = length(regexall("ocid1.subnet.oc1*", each.value.backup_subnet_id)) > 0 ? each.value.backup_subnet_id : merge(module.subnets.*...)[each.value.backup_subnet_id]["subnet_tf_id"]
  cluster_subnet_id         = each.value.cluster_subnet_id != "" ? length(regexall("ocid1.subnet.oc1*", each.value.cluster_subnet_id)) > 0 ? each.value.cluster_subnet_id : data.oci_core_subnets.oci_cluster_subnets[each.value.display_name].subnets.*.id[0] : null
  backup_subnet_id          = each.value.backup_subnet_id != "" ? length(regexall("ocid1.subnet.oc1*", each.value.backup_subnet_id)) > 0 ? each.value.backup_subnet_id : data.oci_core_subnets.oci_backup_subnets[each.value.display_name].subnets.*.id[0] : null
 # backup_network_nsg_ids      = each.value.backup_network_nsg_ids != null ? [for nsg in each.value.backup_network_nsg_ids : (length(regexall("ocid1.networksecuritygroup.o#c1*",nsg)) > 0 ? nsg : merge(module.nsgs.*...)[nsg]["nsg_tf_id"])] : null
  cluster_name                = each.value.cluster_name
  data_storage_percentage     = each.value.data_storage_percentage
  defined_tags                = each.value.defined_tags
  domain                      = each.value.domain
  freeform_tags               = each.value.freeform_tags
  is_local_backup_enabled     = each.value.is_local_backup_enabled
  is_sparse_diskgroup_enabled = each.value.is_sparse_diskgroup_enabled
  license_model               = each.value.license_model
#  nsg_ids                     = each.value.nsg_ids != null ? [for nsg in each.value.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : merge(m#odule.nsgs.*...)[nsg]["nsg_tf_id"])] : null
  nsg_ids               = each.value.nsg_ids != [] ? each.value.nsg_ids : []
  backup_network_nsg_ids        = each.value.backup_network_nsg_ids != [] ? each.value.backup_network_nsg_ids : []
  ocpu_count                  = each.value.ocpu_count
  scan_listener_port_tcp      = each.value.scan_listener_port_tcp
  scan_listener_port_tcp_ssl  = each.value.scan_listener_port_tcp_ssl
  time_zone                   = each.value.time_zone
}

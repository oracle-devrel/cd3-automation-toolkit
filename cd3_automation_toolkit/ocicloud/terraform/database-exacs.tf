# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Block - Database
# Create ExaInfra
############################################

data "oci_core_subnets" "oci_exacs_subnets" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.cluster_subnet_id
  vcn_id         = data.oci_core_vcns.oci_exacs_vcns[each.key].virtual_networks.*.id[0]
}

data "oci_core_subnets" "oci_exacs_backup_subnets" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.backup_subnet_id
  vcn_id         = data.oci_core_vcns.oci_exacs_vcns[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_exacs_vcns" {
  # depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each       = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "exa-infra" {
  source              = "./modules/database/exa-infra"
  for_each            = var.exa_infra != null ? var.exa_infra : {}
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id      = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
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

module "exa-vmclusters" {
  depends_on = [module.exa-infra]
  source     = "./modules/database/exa-vmcluster"

  for_each                  = var.exa_vmclusters != null ? var.exa_vmclusters : {}
  backup_subnet_id          = each.value.backup_subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.backup_subnet_id)) > 0 ? each.value.backup_subnet_id : data.oci_core_subnets.oci_exacs_backup_subnets[each.key].subnets.*.id[0]) : null
  exadata_infrastructure_id = length(regexall("ocid1.cloudexadatainfrastructure.oc*", each.value.exadata_infrastructure_id)) > 0 ? each.value.exadata_infrastructure_id : merge(module.exa-infra.*...)[each.value.exadata_infrastructure_id].exainfra_tf_id
  cpu_core_count            = each.value.cpu_core_count
  display_name              = each.value.display_name
  compartment_id            = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  gi_version                = each.value.gi_version
  hostname                  = each.value.hostname
  #ssh_public_keys          = length(regexall("ssh-rsa*",each.value.ssh_public_key)) > 0 ? each.value.ssh_public_key : var.ssh_public_key
  ssh_public_keys = lookup(var.exacs_ssh_keys, each.value.ssh_public_keys, var.exacs_ssh_keys["ssh_public_key"])
  //  cluster_subnet_id           = length(regexall("ocid1.subnet.oc*", each.value.cluster_subnet_id)) > 0 ? each.value.cluster_subnet_id : merge(module.subnets.*...)[each.value.cluster_subnet_id]["subnet_tf_id"]
  network_compartment_id      = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  vcn_names                   = [each.value.vcn_name]
  cluster_subnet_id           = each.value.cluster_subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.cluster_subnet_id)) > 0 ? each.value.cluster_subnet_id : data.oci_core_subnets.oci_exacs_subnets[each.key].subnets.*.id[0]) : null
  backup_network_nsg_ids      = each.value.backup_network_nsg_ids != null ? each.value.backup_network_nsg_ids : []
  cluster_name                = each.value.cluster_name
  data_storage_percentage     = each.value.data_storage_percentage
  db_node_storage_size_in_gbs = each.value.db_node_storage_size_in_gbs != null ? each.value.db_node_storage_size_in_gbs : null
  memory_size_in_gbs          = each.value.memory_size_in_gbs != null ? each.value.memory_size_in_gbs : null
  data_storage_size_in_tbs    = each.value.data_storage_size_in_tbs != null ? each.value.data_storage_size_in_tbs : null
  db_servers                  = each.value.db_servers != [] ? each.value.db_servers : []
  defined_tags                = each.value.defined_tags
  domain                      = each.value.domain
  freeform_tags               = each.value.freeform_tags
  is_local_backup_enabled     = each.value.is_local_backup_enabled
  is_sparse_diskgroup_enabled = each.value.is_sparse_diskgroup_enabled
  license_model               = each.value.license_model
  //  nsg_ids                     = each.value.nsg_ids != null ? [for nsg in each.value.nsg_ids : length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? nsg : merge(module.nsgs.*...)[nsg]["nsg_tf_id"]] : null
  nsg_ids                    = each.value.nsg_ids != null ? each.value.nsg_ids : []
  ocpu_count                 = each.value.ocpu_count
  scan_listener_port_tcp     = each.value.scan_listener_port_tcp
  scan_listener_port_tcp_ssl = each.value.scan_listener_port_tcp_ssl
  time_zone                  = each.value.time_zone
}
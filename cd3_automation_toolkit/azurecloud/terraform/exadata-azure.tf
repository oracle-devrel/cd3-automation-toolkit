#data "azurerm_resource_group" "resource_group" {
# for_each       = var.azurerm_oci_adb != null ? var.azurerm_oci_adb : {}
#  name = each.value.resource_group_name
#}

data "azurerm_virtual_network" "exa_vmc_virtual_networks" {
  #depends_on = [module.avm_network]
  for_each            = var.az_oci_exa_vmclusters != null ? var.az_oci_exa_vmclusters : {}
  name                = each.value.virtual_network_id
  resource_group_name = each.value.network_resource_group_name
}

data "azurerm_subnet" "exa_vmc_subnets" {
  #depends_on = [module.avm_network]
  for_each             = var.az_oci_exa_vmclusters != null ? var.az_oci_exa_vmclusters : {}
  name                 = each.value.subnet_id
  virtual_network_name = each.value.virtual_network_id
  resource_group_name  = each.value.network_resource_group_name
}

data "azurerm_oracle_exadata_infrastructure" "exa_infras" {
depends_on = [ module.exa-infra-azure ]
  #depends_on = [module.avm_network]
  for_each             = var.az_oci_exa_vmclusters != null ? var.az_oci_exa_vmclusters : {}
  name                 = each.value.exadata_infrastructure_name
  resource_group_name  = each.value.resource_group_name
}

data "azurerm_oracle_db_servers" "this" {
  depends_on = [ module.exa-infra-azure]
  for_each             = var.az_oci_exa_vmclusters != null ? var.az_oci_exa_vmclusters : {}
  resource_group_name               = each.value.resource_group_name
  cloud_exadata_infrastructure_name = each.value.exadata_infrastructure_name
}

# AzureRM - Exadata Infrastructure
module "exa-infra-azure" {
  for_each = var.az_oci_exa_infra != null ? var.az_oci_exa_infra : {}
  source   = "./modules/azurerm-oci-exa-infra"
  # depends_on = [ module.azure-resource-grp ]

  # Mandatory
  location            = each.value.az_region
  zone                = each.value.az_zone
  resource_group_name = each.value.resource_group_name
  name                = each.value.display_name
  compute_count       = each.value.compute_count
  storage_count       = each.value.storage_count

  # Optional
  shape              = each.value.shape
  tags               = each.value.common_tags
  customer_contacts  = each.value.customer_contacts
  maintenance_window = each.value.maintenance_window

}



# Known Issue - https://docs.oracle.com/en-us/iaas/odexa/odexa-troubleshooting-and-known-issues-exadata-services.html
#resource "time_sleep" "wait_after_deletion" {
#  destroy_duration = var.destroy_duration
#  depends_on = [module.azurerm_exadata_infra]
#}

# AzureRM - Exadata VM Cluster
module "exa-vmcluster-azure" {

  for_each = var.az_oci_exa_vmclusters != null ? var.az_oci_exa_vmclusters : {}
  source   = "./modules/azurerm-oci-exa-vmcluster"

  # VM Cluster details
  resource_group_name               = each.value.resource_group_name
    display_name                      = each.value.display_name

  exadata_infrastructure_id         = data.azurerm_oracle_exadata_infrastructure.exa_infras[each.key].id
  exadata_infrastructure_name       = each.value.exadata_infrastructure_name
  db_servers = [for obj in data.azurerm_oracle_db_servers.this[each.key].db_servers : obj.ocid]

  location                          = each.value.az_region
  cluster_name                      = each.value.cluster_name
  hostname                          = each.value.hostname
  time_zone                         = each.value.time_zone
  license_model                     = each.value.license_model
  gi_version                        = each.value.gi_version
  system_version                    = each.value.system_version
  ssh_public_keys                   = each.value.ssh_public_keys

  # Networking
  vnet_id            = data.azurerm_virtual_network.exa_vmc_virtual_networks[each.key].id
  subnet_id          = data.azurerm_subnet.exa_vmc_subnets[each.key].id
  backup_subnet_cidr = each.value.backup_subnet_cidr
  domain             = each.value.domain
  zone_id            = each.value.oci_zone_id

  # VM Cluster allocation
  cpu_core_count             = each.value.cpu_core_count
  memory_size_in_gbs         = each.value.memory_size_in_gbs
  dbnode_storage_size_in_gbs = each.value.db_node_storage_size_in_gbs

  # Exadata storage
  data_storage_size_in_tbs    = each.value.data_storage_size_in_tbs
  data_storage_percentage     = each.value.data_storage_percentage
  is_local_backup_enabled     = each.value.local_backup_enabled
  is_sparse_diskgroup_enabled = each.value.sparse_diskgroup_enabled

  # Diagnostics Collection
  is_diagnostic_events_enabled = each.value.diagnostics_events_enabled
  is_health_monitoring_enabled = each.value.health_monitoring_enabled
  is_incident_logs_enabled     = each.value.incident_logs_enabled

  # Ports
  scan_listener_port_tcp       = each.value.scan_listener_port_tcp
  scan_listener_port_tcp_ssl   = each.value.scan_listener_port_tcp_ssl

  # File System Config
  mount_point                  = each.value.mount_point
  size_in_gb                   = each.value.size_in_gb


  tags = each.value.common_tags
  #depends_on = [time_sleep.wait_after_deletion]
  # depends_on = [module.azurerm_exadata_infra]

}

locals {
  oracle_dbs_azure = merge(var.az_oci_exa_vmclusters, var.az_oci_adb)
}

data "azurerm_resource_group" "this" {
  for_each = { for k, v in local.oracle_dbs_azure : k => v if v.create_odb_network }
  name     = each.value.network_resource_group_name
}

# Azure VNet with delegated subnet
module "avm_network" {

  for_each = { for k, v in local.oracle_dbs_azure : k => v if v.create_odb_network }
  source   = "Azure/avm-res-network-virtualnetwork/azurerm"
  version  = "0.17.1"

  # depends_on = [ module.azure-resource-grp ]

  tags          = each.value.common_tags
  parent_id     = data.azurerm_resource_group.this[each.key].id
  location      = each.value.network_az_region
  name          = each.value.virtual_network_name
  address_space = [each.value.virtual_network_address_space]

  subnets = {
    delegated = {
      name             = each.value.delegated_subnet_name
      address_prefixes = [each.value.delegated_subnet_address_prefix]

      delegations = [{
        name = "Oracle.Database/networkAttachments"
        service_delegation = {
          name    = "Oracle.Database/networkAttachments"
          actions = ["Microsoft.Network/networkinterfaces/*", "Microsoft.Network/virtualNetworks/subnets/join/action"]

        }
      }]
    }
  }
}

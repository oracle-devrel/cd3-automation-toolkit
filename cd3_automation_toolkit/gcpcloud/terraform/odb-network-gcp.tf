locals {
  oracle_dbs_gcp = merge(var.gcp_oci_exa_vmclusters, var.gcp_oci_adb)
}

# GCP Network
module "gcp_network" {

  for_each = { for k, v in local.oracle_dbs_gcp : k => v if v.create_odb_network || v.create_odb_network_subnets }

  source = "./modules/gcp-oci-odb-network"

  labels                      = each.value.labels
  odb_network_project         = each.value.odb_network_project
  location                    = each.value.location
  vpc_network_name            = each.value.vpc_network_name
  odb_network_id              = each.value.odb_network_id
  odb_network_gcp_oracle_zone = each.value.odb_network_gcp_oracle_zone
  odb_client_subnet_id        = each.value.odb_client_subnet_id
  odb_backup_subnet_id        = each.value.odb_backup_subnet_id
  create_odb_network          = each.value.create_odb_network
  create_odb_network_subnets  = each.value.create_odb_network_subnets
  client_subnet_cidr          = each.value.client_subnet_cidr
  backup_subnet_cidr          = each.value.backup_subnet_cidr

}
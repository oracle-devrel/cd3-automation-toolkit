# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

##################################
# Module Block - ADB @GCP
# Create ADB
##################################

/*
data "google_oracle_database_odb_network" "gcp_odb_network" {

  location = "us-east4"
  project  = "oradb-489018"
  odb_network_id = "nework1"
}

output "odb_network1" {
  description = "Exadata Infrastructure ID"
  value       = data.google_oracle_database_odb_network.gcp_odb_network.id
}
*/
module "adb-gcp" {

  depends_on = [module.gcp_network]
  source   = "./modules/gcp-oci-adb"
  for_each = var.gcp_oci_adb != null ? var.gcp_oci_adb : {}

  adb_config = each.value
  odb_network_id            = each.value.odb_network_id!=null ? "projects/${each.value.odb_network_project}/locations/${each.value.location}/odbNetworks/${each.value.odb_network_id}" : null
  odb_client_subnet_id      = each.value.odb_network_id!=null && each.value.odb_client_subnet_id!=null ? "projects/${each.value.odb_network_project}/locations/${each.value.location}/odbNetworks/${each.value.odb_network_id}/odbSubnets/${each.value.odb_client_subnet_id}" : null

  labels       = each.value.labels
}

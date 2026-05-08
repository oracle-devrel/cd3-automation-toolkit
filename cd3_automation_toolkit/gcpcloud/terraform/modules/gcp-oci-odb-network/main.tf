resource "google_compute_network" "vpc_network" {

  count                   = var.create_odb_network ? 1 : 0
  name                    = var.vpc_network_name
  project                 = var.odb_network_project
  auto_create_subnetworks = false # Sets the VPC to "Custom" mode
  mtu                     = 1460
}


# Create ODB Network
resource "google_oracle_database_odb_network" "odb_network" {
  count           = var.create_odb_network ? 1 : 0
  odb_network_id  = var.odb_network_id
  location        = var.location
  project         = var.odb_network_project
  network         = google_compute_network.vpc_network[0].id
  gcp_oracle_zone = var.odb_network_gcp_oracle_zone
  labels          = var.labels
  #deletion_protection = "false"
}

# Create ODB Network Subnets
resource "google_oracle_database_odb_subnet" "odb_client_subnet" {
  count         = var.create_odb_network_subnets ? 1 : 0
  odb_subnet_id = var.odb_client_subnet_id
  location      = var.location
  project       = var.odb_network_project
  odbnetwork    = var.create_odb_network == true ? google_oracle_database_odb_network.odb_network[0].odb_network_id : "${var.odb_network_id}"
  cidr_range    = var.client_subnet_cidr
  purpose       = "CLIENT_SUBNET"
  labels        = var.labels
  #deletion_protection = "false"
}
resource "google_oracle_database_odb_subnet" "odb_backup_subnet" {

  count         = var.create_odb_network_subnets && var.backup_subnet_cidr != "" && var.backup_subnet_cidr != null ? 1 : 0
  odb_subnet_id = var.odb_backup_subnet_id
  location      = var.location
  project       = var.odb_network_project
  odbnetwork    = var.create_odb_network == true ? google_oracle_database_odb_network.odb_network[0].odb_network_id : "${var.odb_network_id}"
  cidr_range    = var.backup_subnet_cidr
  purpose       = "BACKUP_SUBNET"
  labels        = var.labels
  #deletion_protection = "false"
}
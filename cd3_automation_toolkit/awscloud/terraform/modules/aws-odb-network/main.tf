# ========================================
# Module: aws-odb-network / main.tf
# ========================================

resource "aws_odb_network" "odb_network" {
  # Required
  display_name         = var.network_config.display_name
  availability_zone_id = var.network_config.availability_zone_id
  client_subnet_cidr   = var.network_config.client_subnet_cidr
  s3_access            = var.network_config.s3_access
  zero_etl_access      = var.network_config.zero_etl_access

  # Optional
  backup_subnet_cidr = var.network_config.backup_subnet_cidr
  availability_zone  = var.network_config.availability_zone

  # Mutually exclusive — set only one or neither
  custom_domain_name = var.network_config.custom_domain_name
  default_dns_prefix = var.network_config.default_dns_prefix

  tags = var.network_config.tags
}

# ──────────────────────────────────────────────────────────────────────────────
# Peering — conditionally created within this module.
# create_odb_peering = true  → creates the peering connection for this network.
# create_odb_peering = false → no peering resource is created (count = 0).
# ──────────────────────────────────────────────────────────────────────────────
resource "aws_odb_network_peering_connection" "odb_peering" {
  count = var.network_config.create_odb_peering ? 1 : 0

  display_name    = var.network_config.peering_display_name
  odb_network_id  = aws_odb_network.odb_network.id
  peer_network_id = var.network_config.peer_vpc_id
  region          = var.network_config.peering_region

  tags = var.network_config.peering_tags

  depends_on = [aws_odb_network.odb_network]
}

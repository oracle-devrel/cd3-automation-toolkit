# ========================================
# Module: aws-odb-network / outputs.tf
# ========================================

output "odb_network_id" {
  description = "ID of the created ODB network"
  value       = aws_odb_network.odb_network.id
}

output "odb_network_arn" {
  description = "ARN of the created ODB network"
  value       = aws_odb_network.odb_network.arn
}

output "odb_network_status" {
  description = "Lifecycle state of the ODB network"
  value       = aws_odb_network.odb_network.status
}

output "odb_network_display_name" {
  description = "Display name of the created ODB network"
  value       = aws_odb_network.odb_network.display_name
}

output "odb_peering_id" {
  description = "ID of the peering connection (null when create_odb_peering = false)"
  value       = var.network_config.create_odb_peering ? aws_odb_network_peering_connection.odb_peering[0].id : null
}

output "odb_peering_status" {
  description = "Status of the peering connection (null when create_odb_peering = false)"
  value       = var.network_config.create_odb_peering ? aws_odb_network_peering_connection.odb_peering[0].status : null
}

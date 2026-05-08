# ========================================
# Child Module - modules/aws-oci-exa-vmcluster/outputs.tf
# ========================================

output "vm_cluster_id" {
  value = aws_odb_cloud_vm_cluster.vm_cluster.id
}

output "vm_cluster_status" {
  value = aws_odb_cloud_vm_cluster.vm_cluster.status
}

output "scan_dns_name" {
  value = aws_odb_cloud_vm_cluster.vm_cluster.scan_dns_name
}


output "subnet_id" {
  value = local.create_vcn == 1 ? oci_core_subnet.subnet[0].id : null
}

output "nsg_id" {
  value = local.create_vcn == 1 ? oci_core_network_security_group.nsg[0].id : null
}
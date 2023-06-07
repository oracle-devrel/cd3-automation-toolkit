############################
# Outputs Block - DNS Zone #
############################

output "dns_zone_id" {
  value = oci_dns_zone.zone.id
}
output "dns_zone_name" {
  value = oci_dns_zone.zone.name
}
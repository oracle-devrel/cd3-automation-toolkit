##########################
# Resource Block - rrset #
##########################
resource "oci_dns_rrset" "rrset" {
  #Required
  domain          = var.rrset_domain
  rtype           = var.rrset_rtype
  zone_name_or_id = var.rrset_zone

  #Optional
  #compartment_id = var.rrset_compartment_id != null ? var.rrset_compartment_id : null
  dynamic "items" {
    for_each = { for rdata in var.rrset_rdata : rdata => rdata }
    content {
      #Required
      domain = var.rrset_domain
      rdata  = items.key
      rtype  = var.rrset_rtype
      ttl    = var.rrset_ttl
    }
  }
  scope   = var.rrset_scope != null ? (var.rrset_scope != "PRIVATE" ? null : var.rrset_scope) : null
  view_id = var.rrset_view_id != null ? var.rrset_view_id : null
}
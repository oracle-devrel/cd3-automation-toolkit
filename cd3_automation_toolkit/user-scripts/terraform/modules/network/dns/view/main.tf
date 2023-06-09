#########################
# Resource Block - View #
#########################

resource "oci_dns_view" "view" {
  #Required
  compartment_id = var.view_compartment_id

  #Optional
  scope         = var.view_scope != null ? var.view_scope : null
  display_name  = var.view_display_name != null ? var.view_display_name : null
  defined_tags  = var.view_defined_tags
  freeform_tags = var.view_freeform_tags
}

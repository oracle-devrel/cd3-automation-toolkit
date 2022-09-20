// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Resource Block - Network
# Create Dynamic Routing Gateway Attachment
############################
resource "oci_core_drg_attachment" "drg_attachment" {
  #Required
  drg_id = var.drg_id
  #Optional
  defined_tags       = var.defined_tags
  display_name       = var.drg_display_name == "" ? null : var.drg_display_name #join("_",[var.drg_display_name,"attachment"])
  drg_route_table_id = var.drg_route_table_id
  freeform_tags      = var.freeform_tags

  dynamic "network_details" {
    for_each = var.drg_attachments[var.key_name].network_details != [] ? var.drg_attachments[var.key_name].network_details : []

    content {
      #Required
      id   = length(regexall("ocid1.*", network_details.value.id)) > 0 ? network_details.value.id : var.vcns_tf_id[network_details.value.id]["vcn_tf_id"]
      type = network_details.value.type
      #Optional
      route_table_id = (network_details.value.vcn_route_table_id != "" && network_details.value.vcn_route_table_id != null) ? (length(regexall("ocid1*", network_details.value.vcn_route_table_id)) > 0 ? network_details.value.vcn_route_table_id : (length(regexall(".Default-Route-Table-for*", network_details.value.vcn_route_table_id))) > 0 ? var.default_route_table_tf_id[network_details.value.vcn_route_table_id]["vcn_default_route_table_id"] : var.route_table_tf_id[network_details.value.vcn_route_table_id]["route_table_ids"]) : null
    }
  }

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}
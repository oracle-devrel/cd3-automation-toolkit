// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Dynamic Routing Gateway Attachment
############################

resource "oci_core_drg_attachment" "drg_attachment" {
    count = (var.drg_display_name != "" && var.drg_display_name != null) ? 1 : 0
    
    #Required
    drg_id = var.drg_id

    #Optional
    defined_tags = var.defined_tags
    display_name = var.display_name == "" ? null : var.display_name #join("_",[var.drg_display_name,"attachment"])
    drg_route_table_id = var.drg_route_table_id
    freeform_tags = var.freeform_tags
    network_details {
        #Required
        id = var.network_details_id
        type = var.network_details_type

        #Optional
        route_table_id = var.vcn_route_table_id
    }
    lifecycle {
      ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
  }

}
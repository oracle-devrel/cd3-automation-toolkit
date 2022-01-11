// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Networking
# Create Dynamic Routing Gateway
############################

resource "oci_core_drg" "drg" {
    count = (var.drg_display_name != null  && var.drg_display_name != "") ? 1 : 0
    #Required
    compartment_id = var.compartment_id

    #Optional
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags
    
    lifecycle {
      ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
  }

}
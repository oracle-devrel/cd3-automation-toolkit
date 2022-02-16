// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create DRG Route Table
############################


resource "oci_core_drg_route_table" "drg_route_table" {

    count = (var.display_name != null  && var.display_name != "") ? 1 : 0

    #Required
    drg_id = var.drg_id

    #Optional
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags
    import_drg_route_distribution_id = var.import_drg_route_distribution_id
    is_ecmp_enabled = var.is_ecmp_enabled
}
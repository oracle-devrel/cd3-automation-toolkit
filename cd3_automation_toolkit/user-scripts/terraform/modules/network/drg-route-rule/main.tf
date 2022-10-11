// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create DRG Route Rule
############################

resource "oci_core_drg_route_table_route_rule" "drg_route_rule" {

  #Required
  drg_route_table_id         = var.drg_route_table_id
  destination                = var.destination
  destination_type           = var.destination_type
  next_hop_drg_attachment_id = var.next_hop_drg_attachment_id

}
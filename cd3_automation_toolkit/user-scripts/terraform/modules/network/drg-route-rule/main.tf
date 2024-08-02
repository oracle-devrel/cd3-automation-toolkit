# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
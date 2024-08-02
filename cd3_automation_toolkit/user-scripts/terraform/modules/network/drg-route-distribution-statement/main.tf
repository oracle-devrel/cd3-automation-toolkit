# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##########################################
# Resource Block - Network
# Create DRG Route Distributions Statement
##########################################

resource "oci_core_drg_route_distribution_statement" "drg_route_distribution_statement" {

  #Required
  drg_route_distribution_id = var.drg_route_distribution_id
  action                    = var.action
  priority                  = var.priority

  #Optional
  dynamic "match_criteria" {
    for_each = var.drg_route_distribution_statements[var.key_name]["match_criteria"] != [] ? var.drg_route_distribution_statements[var.key_name]["match_criteria"] : []
    content {
      #Required
      match_type = match_criteria.value.match_type

      #Optional
      attachment_type   = match_criteria.value.attachment_type
      drg_attachment_id = match_criteria.value.drg_attachment_id != "" && match_criteria.value.drg_attachment_id != null ? (length(regexall("ocid1.drgattachment.oc*", match_criteria.value.drg_attachment_id)) > 0 ? match_criteria.value.drg_attachment_id : var.drg_attachment_ids[match_criteria.value.drg_attachment_id]["drg_attachment_tf_id"]) : ""
    }
  }
}
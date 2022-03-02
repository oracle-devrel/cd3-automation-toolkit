// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Module Block - Logging
# Create Log Groups
#############################

resource "oci_logging_log_group" "log_group" {

  #Required
  compartment_id = var.compartment_id
  display_name   = var.display_name

  #Optional
  defined_tags  = var.defined_tags
  description   = join(" ", ["Log group for", var.description])
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}


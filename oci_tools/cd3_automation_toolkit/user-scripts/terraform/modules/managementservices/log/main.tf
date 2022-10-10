// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Module Block - Logging
# Create Logs
#############################

resource "oci_logging_log" "log" {

  #Required
  display_name = var.display_name
  log_group_id = var.log_group_id
  log_type     = var.log_type

  #Optional
  configuration {
    #Required
    source {
      #Required
      category    = var.source_category
      resource    = var.source_resource
      service     = var.source_service
      source_type = var.source_type
    }

    #Optional
    compartment_id = var.compartment_id
  }
  defined_tags       = var.defined_tags
  freeform_tags      = var.freeform_tags
  is_enabled         = var.log_is_enabled
  retention_duration = var.log_retention_duration

}
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
####################################
# Resource Block - Service Connector
# Create Service Connector Hub
#####################################

resource "oci_sch_service_connector" "service_connector" {
  compartment_id = var.compartment_id
  display_name   = var.display_name
  description    = var.description

  source {
    kind = local.source_kind

    dynamic "monitoring_sources" {
      for_each = var.source_monitoring_details
      content {
        #Optional
        compartment_id = data.oci_identity_compartments.compartments[monitoring_sources.key].compartments[0].id
        namespace_details {
          #Required
          kind = "selected"
          dynamic "namespaces" {
            for_each = toset(monitoring_sources.value)
            content {
              namespace = namespaces.value
              #Required
              metrics {
                #Required
                kind = "all"
              }
            }
          }
        }
      }
    }

    dynamic "log_sources" {
      for_each = toset(var.log_group_names)
      content {
        compartment_id = split("&", log_sources.key)[0]
        log_group_id   = length(regexall("Audit", split("&", log_sources.key)[1])) > 0 ? (length(regexall("Audit_In_Subcompartment", split("&", log_sources.key)[1])) > 0 ? "_Audit_Include_Subcompartment" : "_Audit" ) : data.oci_logging_log_groups.source_log_groups[log_sources.key].log_groups[0].id
      }
    }
    stream_id = var.source_kind == "streaming" ? data.oci_streaming_streams.source_streams[one(keys(var.source_stream_id))].streams[0].id : null
  }

  target {
    kind                  = var.target_kind
    stream_id             = var.target_kind == "streaming" ? data.oci_streaming_streams.target_streams[one(keys(var.stream_id))].streams[0].id : null
    log_group_id          = var.target_kind == "loggingAnalytics" ? data.oci_log_analytics_log_analytics_log_groups.target_log_analytics_log_groups[one(keys(var.destination_log_group_id))].log_analytics_log_group_summary_collection[0].items[0].id : null
    log_source_identifier = var.target_kind == "loggingAnalytics" ? var.target_log_source_identifier : null


    #For object storage
    bucket = var.bucket_name
    #namespace = data.oci_objectstorage_namespace.os_namespace.namespace
    object_name_prefix = var.object_name_prefix

    #For notifications
    topic_id                   = var.target_kind == "notifications" ? data.oci_ons_notification_topics.target_topics[one(keys(var.topic_id))].notification_topics[0].topic_id : null
    enable_formatted_messaging = var.enable_formatted_messaging
  }

  #  dynamic tasks {
  #    for_each = local.source_kind == "logging" ? var.log_rules : {}
  #    content {
  #      kind = "logging"
  #      condition = "data.compartmentName = Ulag"
  #    }
  #  }

  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],
    defined_tags["Oracle-Tags.CreatedBy"]]
  }
}
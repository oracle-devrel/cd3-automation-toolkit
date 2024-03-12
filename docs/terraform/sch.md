# auto.tfvars file for Service Connectors Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.Comments proceed with <b>##</b>.


**1. service_connectors**

- <b>Syntax</b>

```
  service_connectors = {
      ## key - Is a unique value to reference the resources respectively
      key = {
        compartment_id      = string
        display_name        = string
        description         = string
        source_details = {
                source_kind                  = string
                source_log_group_names       = list(string)  # Required when source is logging
                source_stream_name           = map(string)   # Required when source is streaming 
        }
        target_details = {
                target_kind                  = string
                target_stream_name           = map(string)   # Required when target is streaming
                target_log_source_identifier = string        # Required when source is streaming and target is loggingAnalytics
                target_topic_name            = map(string)   # Required when target is notifications
                enable_formatted_messaging   = bool          # Optional when target is notifications.Default is `true`
                target_bucket_name           = string        # Required when target is objectStorage
                target_object_name_prefix    = string        # Optional when target is objectStorage 
                target_log_group_name        = map(string)   # Required when target is loggingAnalytics

        }
        defined_tags                         = optional(map(any))
        freeform_tags                        = optional(map(any))
      }
  }
  
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    #############################
    # Management Services
    # Service Connectors - tfvars
    #############################
  
  service_connectors= {
    # Service Connector Hub map #
    SCH-01 = {
          compartment_id      = "Network"
          display_name        = "SCH-01"
          description         = "logging to stream"
          source_details = {
                  source_kind               = "logging"
                  source_log_group_names    = ["Security&network-vcn-logs"]
          }
          target_details = {
                  target_kind                = "streaming"
                  target_stream_name         = {"Security": "sch-tracing-logs"}
          }
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-01-12T08:30:51.301Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/xyz@oracle.com"
          }
          freeform_tags = {}
        },
        
    SCH-02 = {
          compartment_id      = "Security"
          display_name        = "SCH-02"
          description         = "stream to loganalytics"
          source_details = {
                  source_kind               = "streaming"
                  source_stream_name        = {"Network": "demo-sch-testing"}
          }
          target_details = {
                  target_kind                = "loggingAnalytics"
                  target_log_group_name      = {"Security": "LogGroup_Demo"}
                  target_log_source_identifier = "AVDF Alert in Oracle Database"
          }
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-01-12T08:30:51.345Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/xyz@oracle.com"
          }
          freeform_tags = {}
        },
    
    SCH-03 = {
          compartment_id      = "Dev"
          display_name        = "SCH-03"
          description         = "logging to notification"
          source_details = {
                  source_kind               = "logging"
                  source_log_group_names    = ["Security&VCNFlowLogGroup"]
          }
          target_details = {
                  target_kind                = "notifications"
                  target_topic_name          = {"Network": "topic-testing"}
                    enable_formatted_messaging = true
          }
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-01-12T08:30:51.303Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/xyz@oracle.com"
          }
          freeform_tags = {}
        },
  
    SCH-04 = {
          compartment_id      = "Demo"
          display_name        = "SCH-04"
          description         = "logging to bucket"
          source_details = {
                  source_kind               = "logging"
                  source_log_group_names    = ["Security--comp_one&Audit", "Demo--new_comp_one--new_comp_two&Audit", "Demo&test-gs-01"]
          }
          target_details = {
                  target_kind                = "objectStorage"
                  target_bucket_name         =  "bucket-logging"
                  target_object_name_prefix  = "complaince"
          }
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-01-12T08:30:51.328Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/xyz@oracle.com"
          }
          freeform_tags = {}
        }
  ##Add New SCH for phoenix here##
  }  
```
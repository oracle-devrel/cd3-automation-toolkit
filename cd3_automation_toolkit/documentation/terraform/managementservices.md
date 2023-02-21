## auto.tfvars syntax for Management Services Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## Management Services
1. Alarms
- <b>Syntax</b>

  ````
  alarms = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          compartment_id             = string 
          destinations               = list
          is_enabled                 = bool
          metric_compartment_id      = string
          namespace                  = string
          query                      = string
          severity                   = string
        
          # Optional
          body                       = string
          message_format             = string
          defined_tags               = map
          freeform_tags              = map
          is_notifications_per_metric_dimension_enabled = bool
          metric_compartment_id_in_subtree = string
          trigger_delay_minutes      = string
          repeat_notification_duration = string
          resolution             = string
          resource_group         = string
          suppression            = map
      },
  }
     ````
- <b>Example</b>
  ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # Alarms - tfvars
    # Allowed Values:
    # compartment_id and metric_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
    ############################
    alarms = {
     Network_vpn-status-alarm = {
       #Required
           compartment_id = "Security"
           destinations = ["NetworkTopic"]
           alarm_name = "vpn-status-alarm"
           is_enabled = true
           metric_compartment_id = "Network"
           namespace = "oci_vpn"
           query = "TunnelState[1m].mean() == 0"
           severity = "CRITICAL"
           message_format = "PRETTY_JSON"
           trigger_delay_minutes = "PT5M"
       },
       Network_fast-connect-status-alarm = {
       #Required
           compartment_id = "Security"
           destinations = ["NetworkTopic"]
           alarm_name = "fast-connect-status-alarm"
           is_enabled = true
           metric_compartment_id = "Network"
           namespace = "oci_fastconnect"
           query = "ConnectionState[1m].mean() == 0"
           severity = "CRITICAL"
           message_format = "PRETTY_JSON"
           trigger_delay_minutes = "PT5M"
       },
       Network_bare-metal-unhealthy-alarm = {
       #Required
           compartment_id = "Security"
           destinations = ["ComputeTopic"]
           alarm_name = "bare-metal-unhealthy-alarm"
           is_enabled = true
           metric_compartment_id = "Network"
           namespace = "oci_compute_infrastructure_health"
           query = "health_status[1m].count() == 1"
           severity = "CRITICAL"
           message_format = "PRETTY_JSON"
           trigger_delay_minutes = "PT5M"
           defined_tags = {
             "Operations.os"= "Linux" ,
             "Organization.department"= "Administrators" ,
           }
       },
    }
    ````
  
2. Notification Topics
- <b>Syntax</b>
  ````
   notifications_topics = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          compartment_id             = string 
          topic_name                 = string
             
          # Optional
          description                = string
          defined_tags               = map
          freeform_tags              = map
      },      
   }
  ````
- <b>Example</b>
  ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # Notifications_Topics - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
    ############################
    notifications_topics = {
       NetworkTopic = {
         compartment_id = "Security"
         description = "Topic for network related notifications."
         topic_name = "NetworkTopic"
       },
       SecurityTopic = {
         compartment_id = "Security"
         description = "Topic for security related notifications."
         topic_name = "SecurityTopic" 
         defined_tags = {
          "Operations.os"= "Linux" ,
          "Organization.department"= "Administrators" ,
         }
       },
    }
  ````

3. Notification Subscriptions
- <b>Syntax</b>
  ````
   notifications_subscriptions = {
      ## key - Is a unique value to reference the resources respectively
     key = {
          # Required
          compartment_id           = string
          endpoint                 = string
          protocol                 = string
          topic_id                 = string
         
          # Optional
          defined_tags             = map
          freeform_tags            = map
      }
   }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # Notifications_Subscriptions - tfvars
  # Allowed Values:
  # topic_id can be ocid or the key of notifications_topics (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  notifications_subscriptions = {
   NetworkTopic_sub1 = {
     subscription_name = "NetworkTopic_sub1"
     compartment_id = "Security"
     endpoint = "abc@xyz.com"
     protocol = "EMAIL"
     topic_id = "NetworkTopic"
     defined_tags = {
         "Operations.os"= "Linux" ,
         "Organization.department"= "Administrators" ,
     }
   },
   SecurityTopic_sub1 = {
       subscription_name = "SecurityTopic_sub1"
       compartment_id = "Security"
       endpoint = "abc@xyz.com"
       protocol = "EMAIL"
       topic_id = "SecurityTopic"
   },
  }
    ````
4. Events
- <b>Syntax</b>
  ````
  events = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          compartment_id           = string
          event_name               = string
          description              = string
          is_enabled               = bool
          condition                = string
              
          # Optional
          actions                  = [{ 
                 # Required
                 action_type = string
                 is_enabled  = string
     
                 # Optional
                 description = string
                 function_id = string
                 stream_id   = string
                 topic_id    = string
          }]
          message_format           = string
          defined_tags             = map
          freeform_tags            = map
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # Events - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  events = {
      ## key - Is a unique value to reference the resources respectively
     notify-on-budget-changes-rule = {
         compartment_id = "Security"
         event_name = "notify-on-budget-changes-rule"
         is_enabled = true
         description    = "events rule to detect when cost resources such as budgets and financial tracking constructs are created, updated or deleted."
         condition      = "{\"eventType\":[\"com.oraclecloud.budgets.updatealertrule\",\"com.oraclecloud.budgets.deletealertrule\",\"com.oraclecloud.budgets.updatebudget\",\"com.oraclecloud.budgets.deletebudget\"],\"data\":{}}"
         actions        = [
                        {
                 action_type = "ONS"
                 is_enabled = true
                 topic_id = "BudgetTopic"
                 description = "Sends notification via ONS"
                },
         ]
         defined_tags = {
             "Operations.os"= "Linux" ,
             "Organization.department"= "Administrators" ,
         }
     },
     notify-on-compute-changes-rule = {
         compartment_id = "Security"
         event_name = "notify-on-compute-changes-rule"
         is_enabled = true
         description    = "events rule to detect when compute related resources are created, updated or deleted."
         condition      = "{\"eventType\":[\"com.oraclecloud.computeapi.terminateinstance.begin\"],\"data\":{}}"
         actions        = [
                        {
                 action_type = "ONS"
                 is_enabled = true
                 topic_id = "ComputeTopic"
                 description = "Sends notification via ONS"
                },
         ]
     },
  }
  ````

## Logging for OSS, VCN and Load Balancers
5. Object Storage Log Groups
- <b>Syntax</b>
  
    ````
    oss_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
    }
    ````
- <b>Example</b>
    ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # OSS Log Groups - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  oss_log_groups = {
    # Log Group map #
    CD3-london-oss-log-group = {
        compartment_id = "Storage"
        display_name   = "CD3-london-oss-log-group"
        description    = "Log Group for OSS bucket"
      },
  ##Add New Log Groups for london here##
  }
    ````

6. Object Storage Logs
- <b>Syntax</b>
  
    ````
    oss_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
    }
    ````
- <b>Example</b>
    ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # OSS Logs - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  oss_logs = {
    # Log map #
    CD3-london-oss-log  = {
          display_name = "CD3-london-oss-log"
          log_group_id = "CD3-london-oss-log-group"
          log_type     = "SERVICE"
          category    = "write"
          resource    = "CD3-london-oss-bucket"
          service     = "objectstorage"
          source_type = "OCISERVICE"
          compartment_id = "Storage"
          is_enabled         = true
          retention_duration = 30
        },
  ##Add New Logs for london here##
  }
            
    ````
7. VCN Log Groups
- <b>Syntax</b>
  
    ````
    vcn_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
    }
    ````
- <b>Example</b>
    ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # VCN Log Groups - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  vcn_log_groups = {
    # Log Group map #
      fwl-vcn-flow-log-group = {
          # Required
          compartment_id = "Network"
          display_name   = "fwl-vcn-flow-log-group"
  
          # Optional
          description    = "Log Group for VCN"
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-01-10T08:18:18.100Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                  "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                  "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                  "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
          }
          freeform_tags = {}
        },
  ##Add New Log Groups for london here##
  }
    ````

8. VCN Flow Logs
- <b>Syntax</b>
  
    ````
    vcn_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
    }
    ````
- <b>Example</b>
    ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # VCN Logs - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    vcn_logs = {
      # Log map #
      fwl-vcn_fwl-priv-flow-log  = {
        # Required
        display_name = "fwl-priv-flow-log"
        log_group_id = "fwl-vcn-flow-log-group"
        log_type     = "SERVICE"
  
        # Optional
        category    = "all"
        resource    = "fwl-vcn_fwl-priv"
        service     = "flowlogs"
        source_type = "OCISERVICE"
        compartment_id = "Network"
        is_enabled         = true
        retention_duration = 30
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-10T08:18:18.100Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
        }
      },
      fwl-vcn_fwl-mgmt-flow-log  = {
        # Required
        display_name = "fwl-mgmt-flow-log"
        log_group_id = "fwl-vcn-flow-log-group"
        log_type     = "SERVICE"
  
        # Optional
        category    = "all"
        resource    = "fwl-vcn_fwl-mgmt"
        service     = "flowlogs"
        source_type = "OCISERVICE"
        compartment_id = "Network"
        is_enabled         = true
        retention_duration = 30
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-10T08:18:19.064Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
        }
      },
    ##Add New Logs for london here##
    }
    ````
9. Load Balancer Log Groups
- <b>Syntax</b>
  
    ````
    loadbalancer_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
    }
    ````
- <b>Example</b>
    ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # LOADBALANCER Log Groups - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  loadbalancer_log_groups = {
    # Log Group map #
    lbr2-log-group = {
        compartment_id = "Network"
        display_name   = "lbr2-log-group"
        description    = "Log Group for lbr2"
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.567Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
        }
        freeform_tags = {}
      },
    lbr1-log-group = {
        compartment_id = "Network"
        display_name   = "lbr1-log-group"
        description    = "Log Group for lbr1"
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.566Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
        }
        freeform_tags = {}
      },
  ##Add New Log Groups for london here##
  }
    ````

10. Load Balancer Logs
- <b>Syntax</b>
  
    ````
    loadbalancer_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
    }
    ````
- <b>Example</b>
    ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # LOADBALANCER Logs - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    loadbalancer_logs = {
      # Log map #
        lbr2-log-access  = {
            display_name = "lbr2_access-log"
            log_group_id = "lbr2-log-group"
            log_type     = "SERVICE"
            category    = "access"
            resource    = "lbr2"
            service     = "loadbalancer"
            source_type = "OCISERVICE"
            compartment_id = "OMCDev--OMCDev-VM"
            is_enabled         = true
            retention_duration = 30
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.567Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                    "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                    "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                    "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
            }
          },
        lbr2-log-error  = {
            display_name = "lbr2_error-log"
            log_group_id = "lbr2-log-group"
            log_type     = "SERVICE"
            category    = "error"
            resource    = "lbr2"
            service     = "loadbalancer"
            source_type = "OCISERVICE"
            compartment_id = "OMCDev--OMCDev-VM"
            is_enabled         = true
            retention_duration = 30
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.567Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                    "Schedule.Weekend"= "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0" ,
                    "Schedule.WeekDay"= "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" ,
                    "ArchitectureCenter\devops_oke-d802.ArchitectureCenter\testrelease"= "test"
            }
          },
      ##Add New Logs for london here##
      }
    ````

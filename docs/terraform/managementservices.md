# auto.tfvars syntax for Management Services Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

**1. Alarms**

- <b>Syntax</b>

```
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
```

- <b>Example</b>
```
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
```
  
**2. Notification Topics**

- <b>Syntax</b>
```
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
```

- <b>Example</b>
```
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
```

**3. Notification Subscriptions**

- <b>Syntax</b>
```
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
```

- <b>Example</b>
```
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
```

**4. Events**

- <b>Syntax</b>
```
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
```

- <b>Example</b>
```
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
```
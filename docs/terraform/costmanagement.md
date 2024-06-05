# auto.tfvars syntax for Cost management module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.

<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.


## Budgets

- <b>Syntax</b>

```
    budgets = {
    ## key - Is a unique value to reference the resources respectively
        key =  {
            amount                                = string
            compartment_id                        = string
            reset_period                          = string
            budget_processing_period_start_offset = string
            defined_tags                          = map(any)
            description                           = string
            display_name                          = string
            freeform_tags                         = map(any)
            processing_period_type                = string
            budget_end_date                       = string
            budget_start_date                     = string
            target_type                           = string
            targets                               = list(any)
        },
    }

```

- <b>Example</b>

```
    budgets = {
        Budget1 = {
                amount = 100
                compartment_id = "root"
                reset_period = "MONTHLY"
                description = "demo budget1"
                display_name = "Budget1"
                processing_period_type = "SINGLE_USE"
                budget_start_date = "2024-06-01"
                budget_end_date = "2024-06-11"
                target_type = "COMPARTMENT"
                targets = ["root--Network"]
                defined_tags = {
                        "ssc_resource_tag.APP_CODE"= "test1" ,
                        "ssc_resource_tag.LEGAL_HOLD"= "N"
                }
        },
        Budget2 = {
                compartment_id = <valid_compartment_ocid>
                amount = 100
                reset_period = "MONTHLY"
                description = "demo budget 2"
                budget_processing_period_start_offset = "5"
                display_name = "Budget2"
                processing_period_type = "MONTH"
                target_type = "TAG"
                targets = ["Global.AppID.Test"]
                defined_tags = {
                        "ssc_resource_tag.PLATFORM_ID"= "OCI" ,
                        "ssc_resource_tag.REGION_ID"= "ASH"
                }
        },
    } 
    
```

-----------------------------------------------------------------


## Budget Alert Rules

- <b>Syntax</b>

```
    budget_alert_rules =
    ## key - Is a unique value to reference the resources respectively
        key =  {
            budget_id      = string
            threshold      = string
            threshold_type = string
            type           = string
            defined_tags   = map(any)
            description    = string
            display_name   = string
            freeform_tags  = map(any)
            message        = string
            recipients     = string
    }
```

- <b>Example</b>

```
    budget_alert_rules = {
        "Budget2_ACTUAL_PERCENTAGE_100-0" = {
                budget_id = "Budget2"
                type = "ACTUAL"
                threshold = "100.0"
                threshold_type = "PERCENTAGE"
                message = "test message"
                recipients = "abc@oracle.com , def@oracle.com"
                },
        "Budget2_FORECAST_ABSOLUTE_20-0" = {
                budget_id = "Budget2"
                type = "FORECAST"
                threshold = "20.0"
                threshold_type = "ABSOLUTE"
                recipients = "hello@oracle.com"
                },
    }
```


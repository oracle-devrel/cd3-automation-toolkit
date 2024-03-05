## auto.tfvars syntax for Governance Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## TAGS
1. Tag Namespaces
- <b>Syntax</b>
  
    ````
  tag_namespaces = {
      ## key - Is a unique value to reference the resources respectively
      key = {
            # Required
            compartment_id = string
            description    = string
            name           = string
            
            # Optional
            defined_tags   = map
            freeform_tags  = map
            is_retired     = boolean
        },
  }
    ````
- <b>Example</b>
    ````
    ############################
    # Governance
    # Create Tag Namespaces
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    tag_namespaces = {
        ArchitectureCenter--cis-oci-landing-zone-quickstart-managed = {
                # Required
                compartment_id = "root"
                description = "CIS Landing Zone tag namespace for OCI Architecture Center."
                name = "ArchitectureCenter\\cis-oci-landing-zone-quickstart-managed"
                },
        Oracle-Tags = {
                # Required
                compartment_id = "root"
                description = "The namespace for the automatic tags."
                name = "Oracle-Tags"
                },
        OracleInternalReserved = {
                # Required
                compartment_id = "root"
                description = "Oracle Internal Reserved Tags for workload classification"
                name = "OracleInternalReserved"
                },
    }
    ````
  

2. Tag Keys
- <b>Syntax</b>
  
    ````
    tag_keys = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            tag_namespace_id   = string
            description        = string
            name               = string
  
            # Optional
            defined_tags       = map
            freeform_tags      = map
            is_cost_tracking   = boolean
            is_retired         = boolean
            validator          = {
                  validator_type   = string
                  validator_values = list
            }
        },
    }
    ````
- <b>Example</b>
    ````
    ############################
    # Governance
    # Create Tag Keys
    # Allowed Values:
    # tag_namespace_id can be the ocid or the key of tag_namespaces (map)
    ############################
    tag_keys = {
        ArchitectureCenter--cis-oci-landing-zone-quickstart-managed_release = {
                tag_namespace_id = "ArchitectureCenter--cis-oci-landing-zone-quickstart-managed"
                description = "CIS Landing Zone tag for OCI Architecture Center."
                name = "release"
                is_cost_tracking = false
                },
        Oracle-Tags_CreatedBy = {
                tag_namespace_id = "Oracle-Tags"
                description = "The name of the principal that created the resource."
                name = "CreatedBy"
                is_cost_tracking = true
                },
        Oracle-Tags_CreatedOn = {
                tag_namespace_id = "Oracle-Tags"
                description = "The date and time that the resource was created."
                name = "CreatedOn"
                is_cost_tracking = false
                },
        Oracle-Tags_TestTag = {
                tag_namespace_id = "Oracle-Tags"
                description = "test"
                name = "TestTag"
                is_cost_tracking = false
                validator = [{
                validator_type = "ENUM"
                validator_values = ["hey hi","my tag","value 1"]
                }]
                },
    }
    ````
  

3. Tag Defaults
 - <b>Syntax</b>
  
    ````
    tag_defaults = {
        ## key - Is a unique value to reference the resources respectively
         key = {
                # Required
                compartment_id    = string
                tag_definition_id = string
                value             = string
    
                # Optional
                is_required       = bool
         }
    }
  
    ````
- <b>Example</b>
    ````
    ############################
    # Governance
    # Create Default Tags
    # Allowed Values:
    # tag_definition_id can be the ocid or the key of tag_definitions (map)
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ########################################################
    tag_defaults = {
        Oracle-Tags_CreatedBy_root-default = {
                # Required
                tag_definition_id = "Oracle-Tags_CreatedBy"
                compartment_id = "root"
                value = "$${iam.principal.name}"
                 },
        Oracle-Tags_CreatedOn_root-default = {
                # Required
                tag_definition_id = "Oracle-Tags_CreatedOn"
                compartment_id = "root"
                value = "$${oci.datetime}"
                 },
    }
    ````

## Billing
4. Budgets
- <b>Syntax</b>

  ````
  budgets = {
  ## key - Is a unique value to reference the resources respectively
      key = {
         #Required
         amount         = string
         compartment_id = string
         reset_period   = string

         #Optional
         budget_processing_period_start_offset  = number
         defined_tags                           = map
         description                            = string
         display_name                           = string
         freeform_tags                          = map
         processing_period_type                 = string
         target_type                            = string
         targets                                = list
      },
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Governance
    # Create Budgets
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # processing_period_type : Valid values are INVOICE and MONTH.
    # target_type : Valid values are COMPARTMENT and TAG
    # targets :  list of compartment OCIDs or list of cost tracking tag identifiers in the form of "{tagNamespace}.{tagKey}.{tagValue}"
    ############################
    budgets = {
        CD3-main-budget = {
                compartment_id = "root"
                amount = 10
                reset_period = "MONTHLY"
                description = "Tracks spending from the root compartment and down"
                budget_processing_period_start_offset = "1"
                display_name = "CD3-main-budget"
                target_type = "COMPARTMENT"
                targets = ["root"]
                },
    }

  ````
5. Alert Rule
- <b>Syntax</b>
   ````
    budget_alert_rules = {
    ## key - Is a unique value to reference the resources respectively
        key = {
          #Required
          budget_id      = string
          threshold      = string
          threshold_type = string
          type           = string
      
          #Optional
          defined_tags   = map
          description    = string
          display_name   = string
          freeform_tags  = map
          message        = string
          recipients     = string
        },
    }
    ````
- <b>Example</b>
  ````
   // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Governance
    # Create Budget Alert Rules
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    budget_alert_rules = {
        CD3-main-budget_alert_rule = {
                budget_id = "CD3-main-budget"
                type = "FORECAST"
                threshold = "50"
                threshold_type = "PERCENTAGE"
                description = "Budget Alert Rule"
                display_name = "CD3-main-budget_alert_rule"
                },
    }
  ````

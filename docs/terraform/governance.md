# auto.tfvars syntax for Governance Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## 1. Tag Namespaces

- <b>Syntax</b>
  
```
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
```

- <b>Example</b>
```
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
```
  

## 2. Tag Keys

- <b>Syntax</b>
  
```
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
```

- <b>Example</b>
```
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
```
  

## 3. Tag Defaults
 
- <b>Syntax</b>
  
```
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
  
```

- <b>Example</b>
```
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
```



## 4. Quotas

- <b>Syntax</b>

```
    quota-template
    quota_policies = {
        ## key - Is a unique value to reference the resources respectively
        key =  {
            quota_name               = string
            quota_description        = string
            quota_statements         = list(string)
            defined_tags               = map(any)
            freeform_tags              = map(any)
        }
    }
```

- <b>Example</b>

```
    quota_policies = {
        Compute_1-x_Quota =  {
            quota_name               = "Compute_1.x_Quota"
            quota_description        = "Quota policies for 1.x compute shapes"
            quota_statements         = ["zero compute-core quota standard1-core-count in tenancy", "set compute-core quota standard1-core-count to 100 in compartment root:AppDev where any{request.region = 'us-ashburn-1', request.region = 'us-phoenix-1'}"]
            defined_tags = {
                    "ssc_resource_tag.APP_CODE"= "test1" ,
                    "ssc_resource_tag.LEGAL_HOLD"= "N"
            }
        },
    }
```
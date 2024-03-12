# auto.tfvars syntax for Security Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.


**1. Cloud Guard Configs**

- <b>Syntax</b>

```
  cloud_guard_configs = {
  ## key - Is a unique value to reference the resources respectively
      key = {
         # Required
         compartment_id         = string
         reporting_region       = string
         status                 = string

         # Optional
         self_manage_resources  = string
      },
  }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Security
    # Create Cloud Guard and Alerts
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # status : Valid values are DISABLED, ENABLED
    ############################
    cloud_guard_configs = {
        CD3-cloud_guard = {
                #Required
                compartment_id = "root"
                reporting_region = "us-phoenix-1"
                status = "ENABLED"
                
                #Optional
                self_manage_resources = false
               },
    ##Add New Cloud Guard Configurations for phoenix here##
    }
```

**2. Cloud Guard Targets**

- <b>Syntax</b>
```
    cloud_guard_targets = {
    ## key - Is a unique value to reference the resources respectively
        key = {
          # Required
          compartment_id      = string
          display_name        = string
          target_resource_id  = string
          target_resource_type= string
  
          # Optional
          state               = string
          description         = string
          target_detector_recipes  = [{
              {
                detector_recipe_id = string
              },]
          target_responder_recipes = [{
              {
                responder_recipe_id = string
              },]
          freeform_tags            = map
          defined_tags             = map
        },
    }
```

- <b>Example</b>
```
   // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Security
    # Create Cloud Guard and Alerts
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # target-resource-type : Valid values are COMPARTMENT, ERPCLOUD, HCMCLOUD.
    # state : Valid values are ACTIVE, CREATING, DELETED, DELETING, FAILED, INACTIVE, UPDATING
    ############################
    cloud_guard_targets = {
        CD3-cloudguard-target = {
                #Required
                compartment_id = "root"
                display_name = "CD3-cloudguard-target"
                target_resource_id = "root"
                target_resource_type = "COMPARTMENT"
                
                #Optional
                target_detector_recipes = [
                {
                detector_recipe_id = "OCI_Activity_Detector_Recipe"
                },
                {
                detector_recipe_id = "OCI_Configuration_Detector_Recipe"
                },
                {
                detector_recipe_id = "OCI_Threat_Detector_Recipe"
                }
                ]
                target_responder_recipes = [
                {
                responder_recipe_id = "OCI_Responder_Recipe"
                }
                ]
               },
    ##Add New Cloud Guard Targets for phoenix here##
    }
```

**3. Vault**

- <b>Syntax</b>

```
  vaults = {
  ## key - Is a unique value to reference the resources respectively
      key = {
         # Required
         compartment_id         = string
         display_name           = string
         vault_type             = string

         # Optional
         defined_tags           = map
         freeform_tags          = map
      },
  }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Security
    # Create KMS Vault and Key
    # Allowed Values:
    # compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    vaults = {
        CD3-phoenix-kms-vault = {
                compartment_id = "Security"
                display_name = "CD3-phoenix-kms-vault"
                vault_type = "DEFAULT"
                },
    ##Add New Vaults for phoenix here##
    }
```

**4. Keys**

- <b>Syntax</b>

```
  keys = {
  ## key - Is a unique value to reference the resources respectively
      key = {
         # Required
         compartment_id         = string
         display_name           = string
         management_endpoint    = string

         # Optional
         defined_tags           = map
         freeform_tags          = map
         algorithm              = string
         length                 = number
         protection_mode        = string
      },
  }
```

- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Security
    # Create KMS Vault and Key
    # Allowed Values:
    # compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # length : AES: 16, 24, or 32, RSA: 256, 384, or 512, ECDSA: 32, 48, or 66
    ############################
    keys = {
        CD3-phoenix-kms-key = {
                compartment_id = "Security"
                display_name = "CD3-phoenix-kms-key"
                management_endpoint = "CD3-phoenix-kms-vault"
                algorithm = ""
                },
    ##Add New Keys for phoenix here##
    }
```
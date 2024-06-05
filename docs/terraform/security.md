# auto.tfvars syntax for Security Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.


## KMS - Keys and Vaults

## 1.Vaults

- <b>Syntax</b>

```
    vaults = {
            ## key - Is a unique value to reference the resources respectively
            key = {
                    # Required
                    compartment_id            = string
                    display_name              = string
                    vault_type                = string

  
                    # Optional
                    replica_region            = optional(string)
                    defined_tags              = map
                    freeform_tags             = map
        }
    }
    
```

- <b>Example</b>

```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Security
# Create KMS Vault and Key
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c"
# Sample import command:
# terraform import "module.vaults[\"<<vault name>>\"].oci_kms_vault.vault" <vault id>
############################
vaults = {
    vault1 = {
            compartment_id = "cd3_compartment"
            display_name = "vault1"
            vault_type = "VIRTUAL_PRIVATE"
            replica_region = "us-phoenix-1"
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2021-10-20T15:03:19.457Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
                }
            },
    vault2 = {
            compartment_id = "cd3_compartment"
            display_name = "vault2"
            vault_type = "DEFAULT"
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2021-10-20T15:03:19.457Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
                }
            },
##Add New Vaults for ashburn here##
}

```
        
## 2.Keys

 - <b>Syntax</b>

```
    keys = {
        key = {
                ## key - Is a unique value to reference the resources respectively
                # Required
                compartment_id        = string
                display_name          = string
                vault_name            = string
                algorithm             = string
                length                = int
                protection_mode       = string


                #optional
                curve_id                  = string
                is_auto_rotation_enabled  = string
                rotation_interval_in_days = int
                defined_tags              = map
                freeform_tags             = map               
                
            }
    }
    
```

- <b>Example</b>

```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Security
# Create KMS Vault and Key
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" 
# length : AES: 16, 24, or 32, RSA: 256, 384, or 512, ECDSA: 32, 48, or 66
# Sample import command:
# terraform import "module.keys[\"<< key name>>\"].oci_kms_key.key" managementEndpoint/<management_endpoint>/keys/<key id>
############################
keys = {
    key1 = {
            compartment_id = "cd3_compartment"
            display_name = "key1"
            vault_name = "vault1"
            algorithm = "AES"
            length = 32
            protection_mode = "HSM"
            is_auto_rotation_enabled = "true"
            rotation_interval_in_days = 100
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2021-10-20T15:03:19.457Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
                }
            },
    key2 = {
            compartment_id = "cd3_compartment"
            display_name = "key2"
            vault_name = "vault1"
            algorithm = "AES"
            length = 32
            protection_mode = "HSM"
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2021-10-20T15:03:19.457Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
                }
            },
    key3 = {
            compartment_id = "cd3_compartment"
            display_name = "key3"
            vault_name = "vault2"
            algorithm = "ECDSA"
            length = 32
            curve_id = "NIST_P256"
            protection_mode = "HSM"
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2021-10-20T15:03:19.457Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
                }
            },
    ##Add New Keys for ashburn here##
}

```

## Cloud Guard

**3. Cloud Guard Configs**

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

**4. Cloud Guard Targets**

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


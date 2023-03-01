## auto.tfvars syntax for Compute Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## Storage
1. Block Volumes
- <b>Syntax</b>

    ````
    blockvolumes = {
            ## key - Is a unique value to reference the resources respectively
            key = {
                    # Required
                    availability_domain       = string
                    compartment_id            = string
                    display_name              = string
  
                    # Optional
                    size_in_gbs               = string
                    is_auto_tune_enabled      = string
                    vpus_per_gb               = string
                    kms_key_id                = string
                    attach_to_instance        = string
                    attachment_type           = string
                    backup_policy             = string
                    policy_compartment_id     = string
                    device                    = string
                    encryption_in_transit_type= string
                    attachment_display_name   = string
                    is_read_only              = bool
                    is_pv_encryption_in_transit_enabled = bool
                    is_shareable              = bool
                    use_chap                  = bool
                    defined_tags              = map
                    freeform_tags             = map
        }
    }
    
    ````
  - <b>Example</b>
    ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.

    ############################
    # Block Volumes
    # Block Volumes - tfvars
    # Allowed Values:
    # compartment_id and policy_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # Sample import command for block volume:
    # terraform import "module.block-volumes[\"<<blockvolumes terraform variable name>>\"].oci_core_volume.block_volume" <<block volume ocid>>
    # terraform import "module.block-volumes[\"<<blockvolumes terraform variable name>>\"].oci_core_volume_attachment.block_vol_instance_attachment[0]" <<block volume attachment ocid>>
    # terraform import "module.block-volumes[\"<<blockvolumes terraform variable name>>\"].oci_core_volume_backup_policy_assignment.volume_backup_policy_assignment[0]" <<block volume policy assignment ocid>>
    ############################
    
    blockvolumes = {
        block01 =  {
            # Required
            availability_domain  = 0
            compartment_id       = "AppDev"
            display_name         = "block01"

            # Optional
            size_in_gbs          = 100
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2021-10-20T15:03:19.457Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
            }
        },
       block02 =  {

            # Required
            availability_domain  = 0
            compartment_id       = "AppDev"
            display_name         = "block02"
    
            # Optional
            size_in_gbs          = 500
            attach_to_instance = "server01"
            attachment_type = "iscsi"
            backup_policy          = "gold"
            is_pv_encryption_in_transit_enabled = "false"
            defined_tags = {
                "Operations.os"= "Linux" ,
                "Organization.department"= "Administrators" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                "Oracle-Tags.CreatedOn"= "2021-09-16T19:59:21.745Z" ,
            }
        }
    }
    ````
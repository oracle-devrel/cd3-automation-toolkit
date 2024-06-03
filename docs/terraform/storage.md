# auto.tfvars syntax for Storage Module 
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.


### Block Volumes

- <b>Syntax</b>

```
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
                    is_agent_auto_iscsi_login_enabled = bool
                    use_chap                  = bool
                    source_details            = list(map(any))
                    block_volume_replicas     = list(map(any))
                    block_volume_replicas_deletion = bool
                    autotune_policies         = list(map(any))
                    defined_tags              = map
                    freeform_tags             = map
        }
    }
    
```

- <b>Example</b>
```
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
            attach_to_instance   = "server01"
            attachment_type = "iscsi"
            backup_policy        = "gold"
            is_pv_encryption_in_transit_enabled = "false"
            source_details       = "blockvolume_source"
            block_volume_replicas = [{
                availability_domain = "IiKv:US-ASHBURN-AD-3"
                display_name = "replica-1"
            }]
            autotune_policies    = [
                  {
                    autotune_type = "DETACHED_VOLUME"
                    max_vpus_per_gb = null
                  },
                  {
                    autotune_type = "PERFORMANCE_BASED"
                    max_vpus_per_gb = "50"
                  }
               ]
            defined_tags = {
                "Operations.os"= "Linux" ,
                "Organization.department"= "Administrators" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                "Oracle-Tags.CreatedOn"= "2021-09-16T19:59:21.745Z" ,
            }
        }
    }
```
    
### Buckets

- <b>Syntax</b>

```
  buckets = {
    Bucket Name = {
                  compartment_id        = string
                  name                  = string
                  access_type           = string
                  auto_tiering          = string
                  object_events_enabled = bool
                  storage_tier          = string
                  retention_rules =[
                  {
                      display_name    = string
                      duration = [{
                          time_amount = int,
                          time_unit   = string
                      }]
                      time_rule_locked = string
                  }
                  ]
                  replication_policy = {
                      name                    = string
                      destination_bucket_name = string
                      destination_region_name = string
                  }
                  lifecycle_policy = {
                      rules = [
                              {
                                name        = string
                                action      = string
                                is_enabled  = bool
                                Time_Amount = int
                                Time_Unit   = string
                                target      = string
                                exclusion_patterns = [string]
                                inclusion_patterns = [string]
                                inclusion_prefixes = [string]
                              },
                      ]
                    }
                  versioning          = string
                  defined_tags = {}
                  freeform_tags = {}
            }
    
```

- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # Object Storage Service
  # Object Storage - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  # Sample import commands:
  # importCommands[region.lower()].write(f'\nterraform import "module.oss-buckets[\\"{variable name of the bucket}\\"].oci_objectstorage_bucket.bucket" 'f'n/{namespace name}/b/{bucket name}')
  # importCommands[region.lower()].write(f'\nterraform import "module.oss-buckets[\\"{variable name of the bucket}\\"].oci_objectstorage_replication_policy.replication_policy[0]" 'f'n/{namespace name}/b/{bucket name}/replicationPolicies/{replication policy id}')
  # importCommands[region.lower()].write(f'\nterraform import "module.oss-buckets[\\"{variable name of the bucket}\\"].oci_objectstorage_object_lifecycle_policy.lifecycle_policy" 'f'n/{namespace name}/b/{bucket name}/l')
  ############################
  buckets = {
          Test_Bucket =  {
                  compartment_id        = "Test"
                  name                  = "Test_Bucket"
                  access_type           = "NoPublicAccess"
                  auto_tiering          = "Disabled"
                  object_events_enabled = "true"
                  storage_tier          = "Standard"
                  retention_rules =[
                  {
                      display_name    = "RT_Rule"
                      duration = [{
                          time_amount = 1,
                          time_unit   = "DAYS"
                      }]
                      time_rule_locked = "2023-05-30T15:04:05Z"
                  },
                  {
                      display_name    = "RT_Rule1"
                      duration = [{
                          time_amount = 2,
                          time_unit   = "DAYS"
                      }]
                      time_rule_locked = "2023-05-30T15:04:05Z"
                  },
                  ]
                  replication_policy = {
                      name                    = "Test"
                      destination_bucket_name = "bucket1"
                      destination_region_name = "uk-london-1"
                  }
                  lifecycle_policy = {
                      rules = [
                              {
                                name        = "Policy1"
                                action      = "ARCHIVE"
                                is_enabled  = "true"
                                Time_Amount = 1
                                Time_Unit   = "YEARS"
                                target      = "objects"
                                exclusion_patterns = [".pdf"]
                                inclusion_patterns = []
                                inclusion_prefixes = []
                              },
                      ]
                    }
                  versioning          = "Disabled"
                  defined_tags = {}
                  freeform_tags = {}
            },
  ##Add New OSS Buckets for phoenix here##
  }
```
### FSS

- <b>Syntax</b>

```
   mount_targets = {
     mt_key = {
          availability_domain    = string
          compartment_id         = string
          network_compartment_id = string
          vcn_name               = string
          subnet_id              = string
          # Optional
          display_name           = string
          ip_address             = string
          hostname_label         = string
          nsg_ids                = list
          defined_tags           = map
          freeform_tags          = map
     }
  
   }

   fss = {
      fss_key = {
          availability_domain         = string
          compartment_id              = string
          # optional
          display_name                = string
          source_snapshot             = string
          snapshot_policy             = string
          snapshot_policy_compartment = string
          kms_key_id                  = string
          defined_tags                = map
          freeform_tags               = map
      }
  }

  nfs_export_options =  {
      export_key = {
          export_set_id  = string
          file_system_id = string
          path           = string
          export_options = list
          defined_tags   = map
          freeform_tags  = map
          is_idmap_groups_for_sys_auth = bool
      }
  }

   fss_replication = {
       replication_key = {
            compartment_id       = string
            source_id            = string
            target_id            = string
            # optional
            display_name         = string
            replication_interval = number
            defined_tags         = map
            freeform_tags        = map
       }
  }

```
- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Storage
# Mount Target - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
# Sample import command for Mount Target:
# terraform import "module.mts[\"<<mount_targets terraform variable name>>\"].oci_file_storage_mount_target.mount_target" <<mount target ocid>>
############################
mount_targets = {
    mnt-iad = {
        availability_domain = "0"
        compartment_id = "appdev"
        network_compartment_id = "network"
        vcn_name = "vcn-iad"
        subnet_id = "app-sub-1"
        #Optional
        display_name = "mnt-iad"
        ip_address = "10.255.254.107"
       
        },
}
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Storage
# FSS - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
# Sample import command for FSS:
# terraform import "module.fss[\"<<fss terraform variable name>>\"].oci_file_storage_file_system.file_system" <<file system ocid>>
############################
fss = {
    fss-iad = {
        availability_domain = "0"
        compartment_id = "storage"
        #Optional
        display_name = "fss-iad"
        snapshot_policy = "SnapshotPolicy-1"
        policy_compartment_id = "storage"
    },    
}
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Storage
# Export Options - tfvars
# Allowed Values:
# compartment_id and policy_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
# Sample import command for Export Options:
# terraform import "module.fss-export-options[\"<<nfs_export_options terraform variable name>>\"].oci_file_storage_export.export" <<export option ocid>>
############################
nfs_export_options = {
    fss-iad-export = {
        export_set_id = "mnt-iad"
        file_system_id = "fss-iad"
        is_idmap_groups_for_sys_auth = true
        path = "/fss-iad"
        export_options=[{
            #Required
            source = "0.0.0.0/0"
            #Optional
            access = "READ_WRITE"
            allowed_auth = ["SYS"]
            anonymous_gid = "65534"
            anonymous_uid = "65534"
            identity_squash = "NONE"
            is_anonymous_access_allowed = "false"
            require_privileged_source_port = "false"
        },]
       
        },
}
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Storage
# FSS REPLICATION - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
# Sample import command for FSS:
# terraform import "module.fss-replication[\"<<fss replication terraform variable name>>\"].oci_file_storage_replication.file_system_replication" <<file system ocid>>
############################
fss_replication = {
    Replication-1 = {
        compartment_id = "storage"
        source_id    = "fss-iad"
        target_id    = "ocid1.filesystem.oc1.phx.aaaaaaaaaagd6g6nobuhqllqojxwiotqnb4c2ylefuzaaaaa"
        #Optional
        display_name = "Replication-to-phx"
        replication_interval = 60
        },
    Replication-2 = {
        compartment_id = "sto"
        source_id    = "fss1"
        target_id    = "fss3"
        #Optional
        display_name = "Replication-20240531-1315-22"
        replication_interval = 480
        },
}

```
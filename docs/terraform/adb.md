# auto.tfvars syntax for ADB Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.Comments preceed with <b>##</b>.


**1. ADB**

- <b>Syntax</b>

```
  adb = {
      ## key - Is a unique value to reference the resources respectively
      key = {
            admin_password                    = string
            compartment_id                    = string
            are_primary_whitelisted_ips_used  = bool
            auto_refresh_frequency_in_seconds = number
            auto_refresh_point_lag_in_seconds = number
            adb_source = string
            source_id = string
            #source detail used as source_id
            autonomous_database_source_backup_id = string
            autonomous_database_id         = string
            #storage
            is_auto_scaling_for_storage_enabled  = bool
            data_storage_size_in_gb              = number
            data_storage_size_in_tbs             = number
            autonomous_maintenance_schedule_type = string
            character_set                        = string
            compute_count                        = number
            compute_model                        = string
            ocpu_count                        = number
            customer_contacts                    = list(string)
            data_safe_status                     = string
            database_edition                     = string
            db_name                              = string
            db_version                           = string
            db_workload                          = string
            display_name                         = string
            is_auto_scaling_enabled              = bool
            #Dedicated Exadata Infrastructure
            is_dedicated                     = bool
            autonomous_container_database_id = string
            
            # TDE MEK
            kms_key_id = string
            # ADB customer managed key
            vault_id = string
            # Only to Autonomous Databases on the Exadata Cloud@Customer platform
            in_memory_percentage = number
            
            is_local_data_guard_enabled = bool
            is_mtls_connection_required = bool
            tde_kms_key_id              = string
            license_model               = string
            ncharacter_set              = string
            private_endpoint_ip         = string
            private_endpoint_label      = string
            refreshable_mode            = string
            time_of_auto_refresh_start  = string
            # Network
            network_compartment_id = string
            subnet_compartment_id = string
            subnet_id              = string
            vcn_name               = string
            nsg_ids                = list(string)
            #Backup
            backup_retention_period_in_days = number
            is_backup_retention_locked      = bool
            #DisasterRecoveryConfiguration
            is_replicate_automatic_backups = bool
            remote_disaster_recovery_type  = string
            ##source=BACKUP_FROM_TIMESTAMP
            timestamp           = string
            use_latest_available_backup_time_stamp = bool
            whitelisted_ips                        = list(string)
            defined_tags                           = map(any)
            freeform_tags                          = map(any)
      }
  }
```

- <b>Example</b>
```
    # Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
    #
    ############################
    # ADB
    # ADB - tfvars
    # Allowed Values:
    # compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Database--Prod" where "Database" is the parent of "Prod" compartment
    ############################
    adb = {
      adb1_key = {
        compartment_id           = "db-comp"
        db_name                  = "ebsadbp"
        display_name             = "ebsadbp"
        admin_password           = "ocid1.vaultsecret.oc1.iad.anuwcljrntxkdlyab4r6"
        source_id = "ocid1.autonomousdatabase.oc1.iad.anuwcljrntxkdlyab4r6qwxoghuinss6sx4f6a"
        data_storage_size_in_tbs = 1
        autonomous_maintenance_schedule_type = "REGULAR"
        character_set            = "AL32UTF8"
        compute_count = 2
        compute_model = "ECPU"
        database_edition         = null
        db_version = "23ai"
        db_workload              = "DW"
        is_auto_scaling_enabled = false
        license_model            = "LICENSE_INCLUDED"
        ncharacter_set           = "AL16UTF16"
        network_compartment_id   = "vcn-comp"
        subnet_compartment_id = "snet-comp"
        subnet_id                = "subnet-test"
        vcn_name                 = "VCN-test"
        nsg_ids                  = []
        backup_retention_period_in_days = 60
        whitelisted_ips          = []
      },
     adb2_key = {
        compartment_id           = "db-comp"
        db_name                  = "UY0VMZL2JOGNZB5O"
        display_name             = "Clone-of-ebsadbp"
        admin_password           = ""
        source_id = "ocid1.autonomousdatabase.oc1.iad.anuwclcgnsnex6gz5xvmn2yisq"
        data_storage_size_in_gb = 1045
        character_set            = "AL32UTF8"
        compute_count = 2
        compute_model = "ECPU"
        database_edition         = null
        db_version = "19c"
        db_workload              = "OLTP"
        is_auto_scaling_enabled = true
        license_model            = "LICENSE_INCLUDED"
        ncharacter_set           = "AL16UTF16"
        network_compartment_id   = null
        subnet_compartment_id = null
        subnet_id                = null
        vcn_name                 = null
        nsg_ids                  = []
        whitelisted_ips          = ["160.34.112.0/20","160.34.88.0/21","160.34.92.0/23"]
      }
  ##Add New ADB for phoenix here##
  }
```

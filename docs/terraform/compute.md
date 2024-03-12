# auto.tfvars syntax for Compute Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.


**1. Virtual Machines (VMs)**

- <b>Syntax</b>

```
  instances = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          availability_domain       = string
          compartment_id            = string
          shape                     = string
          source_id                 = string
          source_type               = string
          vcn_name                  = string
          subnet_id                 = string
          network_compartment_id    = string
        
          # Optional
          display_name              = string
          assign_public_ip          = bool
          boot_volume_size_in_gbs   = string
          fault_domain              = string
          dedicated_vm_host_id      = string
          private_ip                = string
          hostname_label            = string
          nsg_ids                   = list
          ocpus                     = string
          memory_in_gbs             = number
          capacity_reservation_id   = string
          create_is_pv_encryption_in_transit_enabled = bool
          update_is_pv_encryption_in_transit_enabled = bool
          ssh_authorized_keys       = string
          backup_policy             = string
          policy_compartment_id     = string
          network_type              = string
          extended_metadata         = string
          skip_source_dest_check    = bool
          baseline_ocpu_utilization = string
          preemptible_instance_config = string
          all_plugins_disabled      = bool
          is_management_disabled    = bool
          is_monitoring_disabled    = bool
          plugins_details           = map
          is_live_migration_preferred = bool
          recovery_action          = string
          are_legacy_imds_endpoints_disabled = bool
          boot_volume_type          = string
          firmware                  = string
          is_consistent_volume_naming_enabled = bool
          remote_data_volume_type   = string
          platform_config           = map
          ipxe_script               = string
          firmware                  = string
          preserve_boot_volume      = bool
          vlan_id                   = string
          kms_key_id                = string
          vnic_display_name         = string
          vnic_defined_tags         = map
          vnic_freeform_tags        = map
          defined_tags              = map
          freeform_tags             = map
      },
  }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Instances
    # Instance - tfvars
    # Allowed Values:
    # vcn_name must be the name of the VCN as in OCI
    # subnet_id can be the ocid of the subnet or the name as in OCI
    # compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # Sample import command for Instance and volume backup policy:
    # terraform import "module.instances[\"<<instances terraform variable name>>\"].oci_core_instance.instance" <<instance ocid>>
    # terraform import "module.instances[\"<<instances terraform variable name>>\"].oci_core_volume_backup_policy_assignment.volume_backup_policy_assignment[0]" <<volume backup policy ocid>>
    ############################
    instances = {
           server01 =  {
                # Required
                availability_domain  = 0
                compartment_id       = "AppDev"
                shape                = "VM.Standard.A1.Flex"
                source_id        =  "Linux"
                source_type      = "image"
                vcn_name         = "dev"
                subnet_id        = "app"
                network_compartment_id = "Dev"
    
                # Optional
                display_name         = "server01"
                boot_volume_size_in_gbs = 50
                fault_domain         = "FAULT-DOMAIN-2"
                assign_public_ip = false
                private_ip       = "172.10.10.10"
                nsg_ids          = ["app-nsg"]
                ocpus            = "4"
                memory_in_gbs = 16
                ssh_authorized_keys  = "instance-ssh-key"
                backup_policy          = "gold"
                ## Section for adding VNIC Defined and Freeform Tags
                vnic_defined_tags = {
                        "Operations.os"= "Linux" ,
                        "Organization.department"= "Administrators" ,
                        "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                        "Oracle-Tags.CreatedOn"= "2021-09-16T19:59:21.745Z" ,
                }
                vnic_freeform_tags = {
                        "Operations.os"= "Linux" ,
                }
                defined_tags = {
                        "Operations.os"= "Linux" ,
                        "Organization.department"= "Administrators" ,
                        "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
                        "Oracle-Tags.CreatedOn"= "2021-09-16T19:59:21.745Z" ,
                }
        },
       server02 =  {
                # Required
                availability_domain  = 0
                compartment_id       = "Sbox--T11-Testing--AppDev--Non-Prod"
                shape                = "VM.Standard.E4.Flex"
                source_id        =  "Linux"
                source_type      = "image"
                network_compartment_id = "Dev"
                vcn_name         = "dev"
                subnet_id        = "app"
  
                # Optional
                display_name         = "server02"
                boot_volume_size_in_gbs = 50
                fault_domain         = "FAULT-DOMAIN-2"
                assign_public_ip = false
                private_ip       = "172.10.10.10"
                nsg_ids          = ["app-nsg"]
                ocpus            = "4"
                memory_in_gbs = 16
                update_is_pv_encryption_in_transit_enabled = false
                ssh_authorized_keys  = "instance-ssh-key"
                backup_policy          = "gold"
        },
    ##Add New Instances for phoenix here##
    }
```
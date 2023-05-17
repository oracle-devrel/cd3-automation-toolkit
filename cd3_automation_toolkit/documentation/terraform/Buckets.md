## auto.tfvars syntax for Storage Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## Storage
1. Buckets
- <b>Syntax</b>

  ````
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
    
   ````
- <b>Example</b>
  ````
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
   
    ````

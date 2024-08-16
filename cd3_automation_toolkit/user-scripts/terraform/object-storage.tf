# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Object Storage
# Create Object Storage Policies
############################

data "oci_objectstorage_namespace" "bucket_namespace" {
  #Optional
  compartment_id = var.tenancy_ocid
}

module "oss-policies" {
  source   = "./modules/identity/iam-policy"
  for_each = var.oss_policies != null ? var.oss_policies : {}

  tenancy_ocid          = var.tenancy_ocid
  policy_name           = each.value.name
  policy_compartment_id = each.value.compartment_id != "root" ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  policy_description    = each.value.policy_description
  policy_statements     = each.value.policy_statements

  #Optional
  defined_tags        = each.value.defined_tags != {} ? each.value.defined_tags : {}
  freeform_tags       = each.value.freeform_tags != {} ? each.value.freeform_tags : {}
  policy_version_date = each.value.policy_version_date != null ? each.value.policy_version_date : null
}

/*
output "oss_policies_id_map" {
  value = [ for k,v in merge(module.oss-policies.*...) : v.policies_id_map]
}
*/

#############################
# Module Block - Object Storage
# Create Object Storage
#############################

module "oss-buckets" {
  source   = "./modules/storage/object-storage"
  for_each = var.buckets != null ? var.buckets : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  name           = each.value.name
  namespace      = data.oci_objectstorage_namespace.bucket_namespace.namespace

  #Optional
  access_type   = each.value.access_type != "" ? each.value.access_type : null   # Defaults to 'NoPublicAccess' as per hashicorp terraform
  auto_tiering  = each.value.auto_tiering != "" ? each.value.auto_tiering : null # Defaults to 'Disabled' as per hashicorp terraform
  defined_tags  = each.value.defined_tags != {} ? each.value.defined_tags : {}
  freeform_tags = each.value.freeform_tags != {} ? each.value.freeform_tags : {}
  kms_key_id    = each.value.kms_key_id != "" ? each.value.kms_key_id : null
  #metadata             = each.value.metadata != {} ? each.value.metadata : {}
  object_events_enabled = each.value.object_events_enabled != "" ? each.value.object_events_enabled : null # Defaults to 'false' as per hashicorp terraform
  storage_tier          = each.value.storage_tier != "" ? each.value.storage_tier : null                   # Defaults to 'Standard' as per hashicorp terraform
  versioning            = each.value.versioning != "" ? each.value.versioning : null
  retention_rules       = each.value.retention_rules
  bucket                = each.value.name
  replication_policy    = coalesce(each.value.replication_policy, null)
  lifecycle_policy      = each.value.lifecycle_policy
  rules                 = each.value.lifecycle_policy.rules

}

#############################
# Module Block - OSS Logging
# Create Object Storage Log Groups and Logs
#############################

data "oci_objectstorage_bucket" "buckets" {
  depends_on = [module.oss-buckets]
  for_each   = var.oss_logs != null ? var.oss_logs : {}
  #Required
  name      = each.value.resource
  namespace = data.oci_objectstorage_namespace.bucket_namespace.namespace
}

module "oss-log-groups" {
  source   = "./modules/managementservices/log-group"
  for_each = var.oss_log_groups != null ? var.oss_log_groups : {}

  # Log Groups
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  display_name = each.value.display_name

  #Optional
  defined_tags  = each.value.defined_tags
  description   = each.value.description
  freeform_tags = each.value.freeform_tags
}

/*
output "oss_log_group_map" {
  value = [ for k,v in merge(module.oss-log-groups.*...) : v.log_group_tf_id ]
}
*/

module "oss-logs" {
  source   = "./modules/managementservices/log"
  for_each = var.oss_logs != null ? var.oss_logs : {}

  # Logs
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.display_name
  log_group_id   = length(regexall("ocid1.loggroup.oc*", each.value.log_group_id)) > 0 ? each.value.log_group_id : merge(module.oss-log-groups.*...)[each.value.log_group_id]["log_group_tf_id"]

  log_type = each.value.log_type
  #Required
  source_category        = each.value.category
  source_resource        = length(regexall("ocid1.*", each.value.resource)) > 0 ? each.value.resource : data.oci_objectstorage_bucket.buckets[each.key].name
  source_service         = each.value.service
  source_type            = each.value.source_type
  defined_tags           = each.value.defined_tags
  freeform_tags          = each.value.freeform_tags
  log_is_enabled         = (each.value.is_enabled == "" || each.value.is_enabled == null) ? true : each.value.is_enabled
  log_retention_duration = (each.value.retention_duration == "" || each.value.retention_duration == null) ? 30 : each.value.retention_duration

}

/*
output "oss_logs_id" {
  value = [ for k,v in merge(module.oss-logs.*...) : v.log_tf_id]
}
*/
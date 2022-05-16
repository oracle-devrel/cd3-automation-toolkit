############################
# Module Block - Object Storage
# Create Object Storage Policies
############################

module "oss-policies" {
  source   = "./modules/identity/iam-policy"
  for_each = var.oss_policies != null ? var.oss_policies : {}

  depends_on            = [module.iam-groups]
  tenancy_ocid          = var.tenancy_ocid
  policy_name           = each.value.name
  policy_compartment_id = each.value.compartment_id != "root" ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  policy_description    = each.value.policy_description
  policy_statements     = each.value.policy_statements

  #Optional
  defined_tags        = each.value.defined_tags
  freeform_tags       = each.value.freeform_tags
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

module "oss" {
  source   = "./modules/storage/bucket"
  for_each = (var.oss != null || var.oss != {}) ? var.oss : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  name = each.value.bucket_name

  #Optional
  access_type = each.value.access_type
  auto_tiering = each.value.auto_tiering
  defined_tags = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  kms_key_id = each.value.kms_key_id != "" ? merge(module.keys.*...)[each.value.kms_key_id]["key_tf_id"] : ""
  #kms_key_id = each.value.kms_key_id != "" ? try(merge(module.keys.*...)[each.value.kms_key_id]["key_tf_id"],data.) : ""
  metadata = each.value.metadata
  object_events_enabled = each.value.object_events_enabled
  storage_tier = var.bucket_storage_tier
  retention_rules {
    display_name = var.retention_rule_display_name
    duration {
        #Required
        time_amount = var.retention_rule_duration_time_amount
        time_unit = var.retention_rule_duration_time_unit
    }
    time_rule_locked = var.retention_rule_time_rule_locked
  }
  versioning = var.bucket_versioning
}

#############################
# Module Block - Management Services for Object Storage
# Create Object Storage Log Groups and Logs
#############################

data "oci_objectstorage_namespace" "objectstorage_namespace" {
  #Optional
  compartment_id = var.tenancy_ocid
}

data "oci_objectstorage_bucket" "buckets" {
  for_each = (var.oss_logs != null || var.oss_logs != {}) ? var.oss_logs : {}
  #Required
  name      = each.value.resource
  namespace = data.oci_objectstorage_namespace.objectstorage_namespace.namespace
}

module "oss-log-groups" {
  source   = "./modules/managementservices/log-group"
  for_each = (var.oss_log_groups != null || var.oss_log_groups != {}) ? var.oss_log_groups : {}

  # Log Groups
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  display_name = each.value.display_name != null ? each.value.display_name : null

  #Optional
  defined_tags  = each.value.defined_tags
  description   = each.value.description != null ? each.value.description : null
  freeform_tags = each.value.freeform_tags
}

/*
output "oss_log_group_map" {
  value = [ for k,v in merge(module.oss-log-groups.*...) : v.log_group_tf_id ]
}
*/

module "oss-logs" {
  source     = "./modules/managementservices/log"
  depends_on = [module.subnets, module.oss-log-groups]
  for_each   = (var.oss_logs != null || var.oss_logs != {}) ? var.oss_logs : {}

  # Logs
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.display_name != null ? each.value.display_name : null
  log_group_id   = length(regexall("ocid1.loggroup.oc1*", each.value.log_group_id)) > 0 ? each.value.log_group_id : merge(module.oss-log-groups.*...)[each.value.log_group_id]["log_group_tf_id"]

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
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
  compartment_id = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null

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
  compartment_id = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null
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
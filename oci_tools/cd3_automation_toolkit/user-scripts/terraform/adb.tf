// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Module Block - Autonomous database
## Create autonomous database
#############################


module "adb" {
  source   = "./modules/database/adb"
  for_each = var.adb != null ? var.adb : {}
  admin_password        = each.value.admin_password
  compartment_id        = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  cpu_core_count        = each.value.cpu_core_count
  db_version            = each.value.db_version
  db_workload           = each.value.db_workload
  db_name               = each.value.db_name
  defined_tags          = each.value.defined_tags
  display_name          = each.value.display_name
  freeform_tags         = each.value.freeform_tags
  data_storage_size_in_tbs = each.value.data_storage_size_in_tbs != null ? each.value.data_storage_size_in_tbs : null
}

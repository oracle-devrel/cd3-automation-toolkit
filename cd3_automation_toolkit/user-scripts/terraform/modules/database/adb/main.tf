# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Autonomous database
## Create autonomous database
################################

resource "oci_database_autonomous_database" "autonomous_database" {
  #Required
  compartment_id = var.compartment_id
  db_name        = var.db_name

  #Optional
  admin_password           = var.admin_password
  character_set            = var.character_set
  cpu_core_count           = var.cpu_core_count
  database_edition         = var.database_edition
  data_storage_size_in_tbs = var.data_storage_size_in_tbs
  db_version               = var.db_version
  db_workload              = var.db_workload
  defined_tags             = var.defined_tags
  display_name             = var.display_name
  license_model            = var.license_model
  ncharacter_set           = var.ncharacter_set
  dynamic "customer_contacts" {
    for_each = var.customer_contacts!=null ? (var.customer_contacts[0] != "" ? var.customer_contacts : []) : []
    content {
        email = customer_contacts.value
    }
   }
  nsg_ids                  = length(var.network_security_group_ids) != 0 ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : null
  freeform_tags            = var.freeform_tags
  subnet_id                = var.subnet_id
  whitelisted_ips          = var.whitelisted_ips
}
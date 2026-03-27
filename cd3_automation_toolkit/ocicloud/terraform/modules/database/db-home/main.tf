# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

############################
# Resource Block - DB Home
# Create Database DB Home
############################


resource "oci_database_db_home" "database_db_home" {
  db_version                 = var.db_version
  defined_tags               = var.defined_tags
  display_name               = var.display_name
  freeform_tags              = var.freeform_tags
  source                     = var.db_source
  vm_cluster_id              = var.vm_cluster_id


    lifecycle {
    ignore_changes = [source]
  }
  timeouts {}

}

/*
resource "time_sleep" "wait_2_minutes" {
  depends_on = [oci_database_db_home.database_db_home]
  create_duration = "120s"

}
*/

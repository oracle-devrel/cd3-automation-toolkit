// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Resource Block - Autonomous database
## Create autonomous database
################################

resource "oci_database_autonomous_database" "autonomous_database" {
    #Required
    compartment_id = var.compartment_id
    db_name = var.db_name

    #Optional
    admin_password = var.admin_password
    cpu_core_count = var.cpu_core_count
    data_storage_size_in_tbs = var.data_storage_size_in_tbs
    db_version = var.db_version
    db_workload = var.db_workload
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags
}
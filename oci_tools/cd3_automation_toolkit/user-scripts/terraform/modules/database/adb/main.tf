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
    admin_password        = var.admin_password
    character_set         = var.character_set
    cpu_core_count        = var.cpu_core_count
    database_edition      = var.database_edition
    data_storage_size_in_tbs = var.data_storage_size_in_tbs
    db_version            = var.db_version
    db_workload           = var.db_workload
    defined_tags          = var.defined_tags
    display_name          = var.display_name
    license_model         = var.license_model
    ncharacter_set        = var.ncharacter_set
    nsg_ids               = length(var.network_security_group_ids) != 0 ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : null
    freeform_tags         = var.freeform_tags
    subnet_id             = var.subnet_id != null ? (length(regexall("ocid1.subnet.oc1*", var.subnet_id)) > 0 ? var.subnet_id : data.oci_core_subnets.oci_subnets_adb[0].subnets[0].id) : null
    whitelisted_ips       = var.whitelisted_ips
}
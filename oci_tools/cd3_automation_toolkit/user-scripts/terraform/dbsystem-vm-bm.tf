module "dbsystem-vm-dm" {
  source = "./modules/database/dbsystem-vm-bm"

  for_each = var.dbsystem_vm_bm != null ? var.dbsystem_vm_bm : {}
    availability_domain = each.value.availability_domain
    compartment_id      = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[0][each.value.compartment_id]) : var.tenancy_ocid
    hostname            = each.value.hostname
    display_name        = each.value.display_name
    db_version          = each.value.db_version
    cluster_name        = each.value.hostname
    shape               = each.value.shape
    ssh_public_key      = length(regexall("ssh-rsa*",each.value.ssh_public_key)) > 0 ? each.value.ssh_public_key : var.ssh_public_keys[0][each.value.ssh_public_key]
    subnet_id           = merge(module.subnets.*...)[each.value.subnet_id]["subnet_tf_id"]
    backup_subnet_id    = each.value.backup_subnet_id != "" ? merge(module.subnets.*...)[each.value.backup_subnet_id]["subnet_tf_id"] : null
  #  backup_subnet_id = each.value.backup_subnet_id
    node_count          = each.value.node_count
    nsg_ids             = each.value.nsg_ids != null ?  [for nsg in each.value.nsg_ids : ( length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : try(merge(module.nsgs.*...)[nsg]["nsg_tf_id"][nsg],merge(module.nsgs.*...)[nsg]["nsg_tf_id"],merge(module.nsgs.*...)[nsg]["nsg_tf_id"]))] : null

    backup_network_nsg_id = each.value.backup_network_nsg_ids != null ? [for nsg in each.value.backup_network_nsg_ids : ( length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : try(merge(module.nsgs.*...)[nsg]["nsg_tf_id"][nsg],merge(module.nsgs.*...)[nsg]["nsg_tf_id"],merge(module.nsgs.*...)[nsg]["nsg_tf_id"]))] : null
    #backup_network_nsg_id = each.value.backup_network_nsg_ids

    time_zone          = each.value.time_zone
    cpu_core_count     = each.value.cpu_core_count
    database_edition = each.value.database_edition
    data_storage_size_in_gb = each.value.data_storage_size_in_gb
    data_storage_percentage = each.value.data_storage_percentage
    disk_redundancy = each.value.disk_redundancy
    license_model = each.value.license_model
    pdb_name = each.value.pdb_name
    admin_password = each.value.admin_password
    db_workload = each.value.db_workload
    auto_backup_enabled = each.value.auto_backup_enabled
    character_set = each.value.character_set
    ncharacter_set = each.value.ncharacter_set
    recovery_window_in_days = each.value.recovery_window_in_days
    defined_tags   = each.value.defined_tags
    freeform_tags  = each.value.freeform_tags

}
# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
# Module Block - DB Home
# Create Database DB Homes
#################################

data "oci_database_cloud_vm_clusters" "oci_cloud_vm_clusters" {
  for_each                        = var.db_homes != null ? var.db_homes : {}
  compartment_id                  = (length(regexall("ocid1.compartment.", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id])
  cloud_exadata_infrastructure_id = each.value.exadata_infrastructure_id != null ? (length(regexall("ocid1.cloudexadatainfrastructure.", each.value.exadata_infrastructure_id)) > 0 ? each.value.exadata_infrastructure_id : data.oci_database_cloud_exadata_infrastructures.oci_cloud_exadata_infrastructures[each.key].cloud_exadata_infrastructures[0].id) : null
  display_name                    = each.value.vm_cluster_id
  state                           = "AVAILABLE"
}


data "oci_database_cloud_exadata_infrastructures" "oci_cloud_exadata_infrastructures" {
  #runs only when exadata_infrastructure_id = name
  for_each = {
    for k, v in var.db_homes :
    k => v
  if v.exadata_infrastructure_id != null && length(regexall("ocid1.cloudexadatainfrastructure.", v.exadata_infrastructure_id)) == 0 }

  compartment_id = (length(regexall("ocid1.compartment.", each.value.exadata_infrastructure_comp_id)) > 0 ? each.value.exadata_infrastructure_comp_id : var.compartment_ocids[each.value.exadata_infrastructure_comp_id])
  display_name   = each.value.exadata_infrastructure_id
  state          = "AVAILABLE"
}



module "db-homes" {
  #depends_on = [module.exa-vmclusters]
  source                         = "../../modules/database/db-home"
  for_each                       = var.db_homes != null ? var.db_homes : {}
  compartment_id                 = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  db_version                     = each.value.db_version
  display_name                   = each.value.display_name
  db_source                      = each.value.db_source
  vm_cluster_id                  = each.value.vm_cluster_id != null ? (length(regexall("ocid1.cloudvmcluster.oc1*", each.value.vm_cluster_id)) > 0 ? each.value.vm_cluster_id : data.oci_database_cloud_vm_clusters.oci_cloud_vm_clusters[each.key].cloud_vm_clusters[0].id) : null
  defined_tags                   = each.value.defined_tags
  freeform_tags                  = each.value.freeform_tags
  exadata_infrastructure_id      = each.value.exadata_infrastructure_id
  exadata_infrastructure_comp_id = each.value.exadata_infrastructure_comp_id
}


#############################
# Module Block - Database CDB
# Create Databases
#############################

data "oci_database_db_homes" "oci_db_homes" {
  for_each       = var.cdb_databases != null ? var.cdb_databases : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.db_home_id
  state          = "Available"
  #vm_cluster_id  = var.vm_cluster_name != null ? data.oci_database_cloud_vm_clusters.existing_cloud_vm_clusters[0].cloud_vm_clusters[0].id : null
  vm_cluster_id = each.value.vm_cluster_id != null ? (length(regexall("ocid1.cloudvmcluster.oc1*", each.value.vm_cluster_id)) > 0 ? each.value.vm_cluster_id : data.oci_database_cloud_vm_clusters.oci_cloud_vm_clusters_dbh[each.key].cloud_vm_clusters[0].id) : null
}


data "oci_database_cloud_vm_clusters" "oci_cloud_vm_clusters_dbh" {
  for_each = {
    for k, v in var.cdb_databases :
    k => v
  if v.vm_cluster_id != null && length(regexall("ocid1.cloudvmcluster.oc1*", v.vm_cluster_id)) == 0 }
  compartment_id = (length(regexall("ocid1.compartment.", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id])
  display_name   = each.value.vm_cluster_id
  state          = "AVAILABLE"
}

module "databases" {
  source = "../../modules/database/cdb"
  #depends_on = [module.db-homes]

  for_each       = var.cdb_databases != null ? var.cdb_databases : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  database       = each.value.database != [] ? each.value.database : []
  db_home_id     = each.value.db_home_id != null ? (length(regexall("ocid1.dbhome.oc*", each.value.db_home_id)) > 0 ? each.value.db_home_id : try(merge(module.db-homes.*...)[each.value.db_home_id]["db_home_tf_id"], data.oci_database_db_homes.oci_db_homes[each.key].db_homes[0].db_home_id)) : null

  db_source                      = each.value.db_source
  exadata_infrastructure_comp_id = each.value.exadata_infrastructure_comp_id
  #db_version = each.value.db_version

}

##############################
# Module Block - Database PDB
# Create PDBs
##############################

data "oci_database_cloud_vm_clusters" "pdb_cloud_vm_clusters" {
  for_each = {
    for k, v in var.pdb_databases :
    k => v
    if v.vm_cluster_id != null && length(regexall("ocid1.cloudvmcluster.", v.vm_cluster_id)) == 0
  }
  compartment_id = (length(regexall("ocid1.compartment.", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id] )
  display_name = each.value.vm_cluster_id
  state        = "AVAILABLE"
}

data "oci_database_db_homes" "pdb_db_homes" {
  for_each       = var.pdb_databases != null ? var.pdb_databases : {}
  compartment_id = length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]
  display_name   = each.value.db_home_id
  state          = "AVAILABLE"
  vm_cluster_id = (each.value.vm_cluster_id == null ? null : (length(regexall("ocid1.cloudvmcluster.", each.value.vm_cluster_id)) > 0 ? each.value.vm_cluster_id : data.oci_database_cloud_vm_clusters.pdb_cloud_vm_clusters[each.key].cloud_vm_clusters[0].id))
}


data "oci_database_databases" "existing_cdb_dbs" {
  for_each       = var.pdb_databases != null ? var.pdb_databases : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  #db_home_id     = each.value.db_home_id != null ? (length(regexall("ocid1.dbhome.oc*", each.value.db_home_id)) > 0 ? each.value.db_home_id : try(merge(module.db-homes.*...)[each.value.db_home_id]["db_home_tf_id"], data.oci_database_db_homes.oci_db_homes[each.value.database_id].db_homes[0].db_home_id)) : null
  #db_home_id      = each.value.db_home_id != null ? (length(regexall("ocid1.dbhome.oc*", each.value.db_home_id)) > 0 ? each.value.db_home_id : data.oci_database_db_homes.oci_db_homes[each.value.db_home_id].db_homes[0].db_home_id) : null
  db_home_id = (length(regexall("ocid1.dbhome.oc*", each.value.db_home_id)) > 0 ? each.value.db_home_id : data.oci_database_db_homes.pdb_db_homes[each.key].db_homes[0].db_home_id)
  db_name = each.value.database_id
  state   = "Available"
}

/*
data "oci_secrets_secretbundle" "pdb_admin_password" {
  for_each  = var.pdb_databases != null ? var.pdb_databases : {}
  secret_id = each.value.pdb_admin_password_secret_id
}

data "oci_secrets_secretbundle" "tde_wallet_password" {
  for_each       = var.pdb_databases != null ? var.pdb_databases : {}
  secret_id      = each.value.tde_wallet_password_secret_id
}
*/


data "oci_secrets_secretbundle" "pdb_admin_password" {
  for_each = {
    for k, v in var.pdb_databases :
    k => v
    if v.pdb_admin_secret_id != null
  }

  secret_id = each.value.pdb_admin_secret_id
}

data "oci_secrets_secretbundle" "tde_wallet_password" {
  for_each = {
    for k, v in var.pdb_databases :
    k => v
    if v.tde_wallet_secret_id != null
  }

  secret_id = each.value.tde_wallet_secret_id
}

module "pdb-databases" {
  for_each = var.pdb_databases != null ? var.pdb_databases : {}
  source   = "../../modules/database/pdb"
  #container_database_id = each.value.cdb_name != null ? try(merge(module.databases.*...)[each.value.cdb_name]["cdb_name_tf_id"], data.oci_database_databases.existing_cdb_dbs[each.key].databases[0].id) : null
  container_database_id          = each.value.database_id != null ? (length(regexall("ocid1.database.oc*", each.value.database_id)) > 0 ? each.value.database_id : try(merge(module.databases.*...)[each.value.database_id]["cdb_name_tf_id"], data.oci_database_databases.existing_cdb_dbs[each.key].databases[0].id)) : null
  exadata_infrastructure_comp_id = each.value.exadata_infrastructure_comp_id
  pdb_admin_password             = (each.value.pdb_admin_secret_id != null ? base64decode(data.oci_secrets_secretbundle.pdb_admin_password[each.key].secret_bundle_content[0].content) : each.value.pdb_admin_password)
  pdb_name                       = each.value.pdb_name
  #TDE wallet password is not required when Database is configured to use customer-managed (Vault service) key
  tde_wallet_password = (each.value.tde_wallet_secret_id != null ? base64decode(data.oci_secrets_secretbundle.tde_wallet_password[each.key].secret_bundle_content[0].content) : each.value.tde_wallet_password)
  defined_tags        = each.value.defined_tags
  freeform_tags       = each.value.freeform_tags

}




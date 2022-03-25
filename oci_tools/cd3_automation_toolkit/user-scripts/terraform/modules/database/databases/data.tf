// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

########################
# Data Block - Database
# Create Databases
########################

data "oci_database_cloud_vm_clusters" "existing_cloud_vm_clusters" {
    count = var.vm_cluster_name != null ? 1 : 0
    #Required
    compartment_id = var.compartment_id
    display_name = var.vm_cluster_name
    state = "Available"
}

data "oci_database_db_homes" "existing_db_home" {
  compartment_id = var.compartment_id
  display_name   = var.db_home_name
  state          = "Available"
  vm_cluster_id  = var.vm_cluster_name != null ? data.oci_database_cloud_vm_clusters.existing_cloud_vm_clusters[0].cloud_vm_clusters[0].id : null
}

data "oci_database_database_software_images" "custom_database_software_images" {
  #Required
  compartment_id = var.compartment_id
  #Optional
  display_name = var.custom_database_image_name
  state        = "Available"
}
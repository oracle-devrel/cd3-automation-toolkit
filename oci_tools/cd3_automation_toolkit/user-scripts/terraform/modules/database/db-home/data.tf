// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#########################
# Data Block - Database
# Create Database Db Home
#########################

data "oci_database_cloud_vm_clusters" "existing_cloud_vm_cluster" {
  count = var.vm_cluster_id != null ? 1 : 0
  #Required
  compartment_id = var.compartment_id

  #Optional
  #cloud_exadata_infrastructure_id = "oci_database_cloud_exadata_infrastructure.${var.exadata_infra_name}.id"
  display_name = var.vm_cluster_id
 # state        = "AVAILABLE"
}

data "oci_database_database_software_images" "custom_database_software_images" {
  count = var.custom_database_image_name != null ? 1 : 0
  #Required
  compartment_id = var.compartment_id

  #Optional
 # display_name = var.custom_database_image_name      #Seems to be a provider bug and this filter is not working
  state        = "Available"
}
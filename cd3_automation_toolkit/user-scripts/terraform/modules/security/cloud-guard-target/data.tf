// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Data Block - Security
## Create Cloud Guard Target
################################

locals {
  recipes = {
    OCI_Responder_Recipe              = data.oci_cloud_guard_responder_recipes.root_responder_recipes.responder_recipe_collection[0].items[0].id
    OCI_Activity_Detector_Recipe      = data.oci_cloud_guard_detector_recipes.root_activity_detector_recipes.detector_recipe_collection[0].items[0].id
    OCI_Configuration_Detector_Recipe = data.oci_cloud_guard_detector_recipes.root_config_detector_recipes.detector_recipe_collection[0].items[0].id
    OCI_Threat_Detector_Recipe        = data.oci_cloud_guard_detector_recipes.root_threat_detector_recipes.detector_recipe_collection[0].items[0].id
  }
}

data "oci_cloud_guard_responder_recipes" "root_responder_recipes" {
  #Required
  compartment_id = var.tenancy_ocid
  display_name   = "OCI Responder Recipe"
}

data "oci_cloud_guard_detector_recipes" "root_activity_detector_recipes" {
  #Required
  compartment_id = var.tenancy_ocid
  display_name   = "OCI Activity Detector Recipe"
}

data "oci_cloud_guard_detector_recipes" "root_config_detector_recipes" {
  #Required
  compartment_id = var.tenancy_ocid
  display_name   = "OCI Configuration Detector Recipe"
}

data "oci_cloud_guard_detector_recipes" "root_threat_detector_recipes" {
  #Required
  compartment_id = var.tenancy_ocid
  display_name   = "OCI Threat Detector Recipe"
}

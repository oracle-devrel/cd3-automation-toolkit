# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Data Block - Security
## Create Cloud Guard Target
################################

locals {
  detector_recipes = {
    "OCI Activity Detector Recipe"          = data.oci_cloud_guard_detector_recipes.root_activity_detector_recipes.detector_recipe_collection[0].items[0].id
    "OCI Configuration Detector Recipe"     = data.oci_cloud_guard_detector_recipes.root_config_detector_recipes.detector_recipe_collection[0].items[0].id
    "OCI Threat Detector Recipe"            = data.oci_cloud_guard_detector_recipes.root_threat_detector_recipes.detector_recipe_collection[0].items[0].id
    "OCI Instance Security Detector Recipe" = data.oci_cloud_guard_detector_recipes.root_instance_security_detector_recipes.detector_recipe_collection[0].items[0].id
  }
  responder_recipes = {
    "OCI Responder Recipe" = data.oci_cloud_guard_responder_recipes.root_responder_recipes.responder_recipe_collection[0].items[0].id
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

data "oci_cloud_guard_detector_recipes" "root_instance_security_detector_recipes" {
  #Required
  compartment_id = var.tenancy_ocid
  display_name   = "OCI Instance Security Detector Recipe"
}



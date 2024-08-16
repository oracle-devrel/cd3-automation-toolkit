# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Security
## Create Cloud Guard Config
################################

resource "oci_cloud_guard_cloud_guard_configuration" "cloud_guard_configuration" {
  #Required
  compartment_id   = var.compartment_id
  reporting_region = var.reporting_region
  status           = var.status

  #Optional
  self_manage_resources = var.self_manage_resources
}

resource "time_sleep" "wait_60_seconds" {
  depends_on      = [oci_cloud_guard_cloud_guard_configuration.cloud_guard_configuration]
  create_duration = "60s"
}


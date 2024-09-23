# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_mysql_mysql_configurations" "mysql_configurations" {

  compartment_id = var.compartment_id
  display_name   = var.configuration_id


}

data "oci_core_shapes" "present_ad" {
  compartment_id      = var.compartment_id
  availability_domain = var.availability_domain == "" || var.availability_domain == null ? element(local.ADs, 0) : var.availability_domain
}

data "oci_core_vcns" "oci_vcns_instances" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}

locals {


  ADs = [
    for ad in data.oci_identity_availability_domains.ads.availability_domains : ad.name
  ]
}
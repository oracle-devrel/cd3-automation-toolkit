# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}
data "oci_mysql_shapes" "mysql_config_shapes" {
    #Required
    compartment_id = var.compartment_id



}
data "oci_core_shapes" "present_ad" {
  compartment_id      = var.compartment_id

}


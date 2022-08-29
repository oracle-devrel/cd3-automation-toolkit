// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Storage
# Create MTs
############################

resource "oci_file_storage_mount_target" "mount_target" {
    #Required
    availability_domain = var.availability_domain
    compartment_id = var.compartment_id
    subnet_id = var.subnet_id!= "" ? (length(regexall("ocid1.subnet.oc1*", var.subnet_id)) > 0 ? var.subnet_id : data.oci_core_subnets.oci_subnets_mts[var.subnet_id].subnets.*.id[0]) : null

    #Optional
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags
    hostname_label = var.hostname_label
    ip_address = var.ip_address
    nsg_ids = var.network_compartment_id != [] ? local.nsg_ids : null
    lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}
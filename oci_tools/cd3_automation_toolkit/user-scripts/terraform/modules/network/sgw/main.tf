// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Service Gateway
############################

data "oci_core_services" "oci_services" {
}

/*
output "services_id_map"{
    value = merge(zipmap(data.oci_core_services.oci_services.services.*.name,data.oci_core_services.oci_services.services.*.id))
}
*/

resource "oci_core_service_gateway" "service_gateway" {

  #Required
  compartment_id = var.compartment_id
  services {
    #Required
    service_id = contains(split("-", data.oci_core_services.oci_services.services.0.cidr_block), var.service) == true ? data.oci_core_services.oci_services.services.0.id : data.oci_core_services.oci_services.services.1.id
  }
  vcn_id = var.vcn_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags
  #route_table_id = (var.route_table_id != "" && var.route_table_id != null) ? var.route_table_id : null

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }

}
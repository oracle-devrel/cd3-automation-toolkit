// Copyright (c) 2021, 2022, Oracle and/or its affiliates.


#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer
#######################################

resource "oci_network_load_balancer_network_load_balancer" "network_load_balancer" {
  #Required
  compartment_id                 = var.compartment_id
  display_name                   = var.display_name
  subnet_id                      = var.subnet_id != null ? (length(regexall("ocid1.subnet.oc1*", var.subnet_id)) > 0 ? var.subnet_id : data.oci_core_subnets.oci_subnets_nlbs.subnets[0].id) : null
  is_preserve_source_destination = var.is_preserve_source_destination
  is_private                     = var.is_private
  network_security_group_ids     = var.network_security_group_ids != [] ? local.nsg_ids : null
  nlb_ip_version                 = var.nlb_ip_version
  defined_tags                   = var.defined_tags
  freeform_tags                  = var.freeform_tags

  dynamic "reserved_ips" {
    for_each = var.reserved_ips_id != [] ? var.reserved_ips_id : []
    content {
      #Optional
      id = reserved_ips.value
    }
  }
  lifecycle {
    ignore_changes = [reserved_ips, defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}

#terraform import "module.network-load-balancers[\"ash1-np-ade-nlb\"].oci_network_load_balancer_network_load_balancer.network_load_balancer" ocid1.networkloadbalancer.oc1.iad.amaaaaaambgqraaahshwlidpo4euy6b6tmkfg534ortljx3ncdsxahgwelma
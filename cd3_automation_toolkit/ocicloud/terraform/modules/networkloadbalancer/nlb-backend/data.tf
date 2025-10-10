# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Data Block - Network Load Balancer
# Create Network Load Balancer Backend
#######################################

data "oci_core_instances" "nlb_instances" {
  #state          = "RUNNING"
  filter {
    name   = "state"
    values = ["RUNNING","STOPPED"]
  }
  compartment_id = var.instance_compartment
}

data "oci_core_instance" "nlb_instance_ip" {
  # for_each = { for k, v in var.ip_address : k => v if regexall("IP:*", var.ip_address) }
  count       = length(regexall("IP:*", var.ip_address)) == 0 ? 1 : 0
  instance_id = merge(local.nlb_instance_ocid.ocid.*...)[split("NAME:", var.ip_address)[1]][0]
}

data "oci_core_vnic_attachments" "nlb_instance_vnic_attachments" {
  # for_each = { for k, v in var.ip_address : k => v if regexall("IP:*", var.ip_address) }
  count          = length(regexall("IP:*", var.ip_address)) == 0 ? 1 : 0
  compartment_id = var.instance_compartment
  instance_id    = merge(local.nlb_instance_ocid.ocid.*...)[split("NAME:", var.ip_address)[1]][0]
  #dynamic "filter" {
  #  for_each = var.vnic_vlan !=null ? [1] : []
  #  content {
  #    name   = "vlan_tag"
  #    values = [var.vnic_vlan]
  #  }
  #}
}

# Filter on VNIC OCID
data "oci_core_private_ips" "private_ips_by_ip_address" {
  count   = length(regexall("IP:*", var.ip_address)) == 0 ? 1 : 0
  vnic_id = merge(local.nlb_instance_vnic_ocid.vnic_ocids.*...)[merge(local.nlb_instance_ocid.ocid.*...)[split("NAME:", var.ip_address)[1]][0]][0]
}

locals {
  nlb_instance_ocid = {
    # for instances in data.oci_core_instances.nlb_instances :
    # "ocid" => { for instance in instances.instances : instance.display_name => instance.id... }...
    "ocid" = { for instance in data.oci_core_instances.nlb_instances.instances : instance.display_name => instance.id... }
  }
  nlb_instance_vnic_ocid = {
    for vnics in data.oci_core_vnic_attachments.nlb_instance_vnic_attachments :
    "vnic_ocids" => { for vnic in vnics.vnic_attachments : vnic.instance_id => vnic.vnic_id... }...
  }
  nlb_private_ip_ocid = {
    for private_ips in data.oci_core_private_ips.private_ips_by_ip_address :
    "private_ocids" => { for private_ip in private_ips.private_ips : private_ip.vnic_id => private_ip.id... }...
  }

}


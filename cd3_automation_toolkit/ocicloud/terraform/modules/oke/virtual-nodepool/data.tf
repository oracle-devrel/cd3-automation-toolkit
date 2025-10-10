# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Data Block - Nodepool
## Create Nodepool and nodes
#############################

locals {
  nodepool_nsg_ids = var.worker_nsg_ids != null ? flatten(tolist([for nsg in var.worker_nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups_workers[nsg].network_security_groups[*].id)])) : null
  pod_nsg_ids      = var.pod_nsg_ids != null ? flatten(tolist([for nsg in var.pod_nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups_pods[nsg].network_security_groups[*].id)])) : null
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}


data "oci_core_vcns" "oci_vcns_virtual_nodepools" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}

data "oci_core_network_security_groups" "network_security_groups_pods" {
  for_each       = var.pod_nsg_ids != null ? { for nsg in var.pod_nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_virtual_nodepools[var.vcn_names[0]].virtual_networks.*.id[0]
}

data "oci_core_network_security_groups" "network_security_groups_workers" {
  for_each       = var.worker_nsg_ids != null ? { for nsg in var.worker_nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_virtual_nodepools[var.vcn_names[0]].virtual_networks.*.id[0]
}

# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_containerengine_virtual_node_pool" "virtual_nodepool" {
    #Required
    cluster_id = var.cluster_name
    compartment_id = var.compartment_id
    display_name = var.display_name
    placement_configurations {
        availability_domain = data.oci_identity_availability_domains.ads.availability_domains[var.availability_domain].name
        subnet_id           = var.subnet_id
        fault_domain = var.fault_domains
    }

    #Optional
    defined_tags       = var.nodepool_defined_tags
    freeform_tags      = var.nodepool_freeform_tags

    dynamic "initial_virtual_node_labels" {
    for_each = var.initial_virtual_node_labels != null ? { for k, v in var.initial_virtual_node_labels : k => v } : {}
    content {
      key   = initial_virtual_node_labels.key
      value = initial_virtual_node_labels.value
     }
    }

    nsg_ids = var.worker_nsg_ids != null ? (local.nodepool_nsg_ids == [] ? ["INVALID WORKER NSG Name"] : local.nodepool_nsg_ids) : null
    #Required
    pod_configuration {
        #Required
        shape = var.node_shape #var.virtual_node_pool_pod_configuration_shape
        subnet_id = var.pod_subnet_id

        #Optional
        nsg_ids = var.pod_nsg_ids != null ? (local.pod_nsg_ids == [] ? ["INVALID POD NSG Name"] : local.pod_nsg_ids) : null
    }
    size = var.size

    #Optional
    dynamic "taints" {
    for_each = var.taints != null ? var.taints : []
    content {
      key    = taints.value.key
      value  = taints.value.value
      effect = taints.value.effect
     }
    }

    virtual_node_tags {
        defined_tags                        = var.node_defined_tags
        freeform_tags                       = var.node_freeform_tags
    }
     # do not destroy the node pool if the kubernetes version has changed as part of the upgrade
    lifecycle {
        ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}
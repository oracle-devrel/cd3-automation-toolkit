# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
resource "oci_containerengine_node_pool" "nodepool" {
  cluster_id         = var.cluster_name
  compartment_id     = var.compartment_id
  node_shape         = var.node_shape
  name               = var.display_name
  kubernetes_version = var.kubernetes_version
  ssh_public_key     = var.ssh_public_key
  defined_tags       = var.nodepool_defined_tags
  freeform_tags      = var.nodepool_freeform_tags

  dynamic "initial_node_labels" {
    for_each = var.initial_node_labels != null ? { for k, v in var.initial_node_labels : k => v } : {}
    content {
      key   = initial_node_labels.key
      value = initial_node_labels.value
    }
  }

  node_config_details {
    placement_configs {
      #Required
      availability_domain = data.oci_identity_availability_domains.ads.availability_domains[var.availability_domain].name
      subnet_id           = var.subnet_id
      fault_domains       = var.fault_domains
    }
    node_pool_pod_network_option_details {
      #Required
      cni_type = var.cni_type

      #Optional
      max_pods_per_node = var.max_pods_per_node
      pod_nsg_ids       = var.pod_nsg_ids != null ? (local.pod_nsg_ids == [] ? ["INVALID POD NSG Name"] : local.pod_nsg_ids) : null
      pod_subnet_ids   = var.pod_subnet_ids != null ? [var.pod_subnet_ids] : null
    }
    size                                = var.size
    nsg_ids                             = var.worker_nsg_ids != null ? (local.nodepool_nsg_ids == [] ? ["INVALID WORKER NSG Name"] : local.nodepool_nsg_ids) : null
    is_pv_encryption_in_transit_enabled = var.is_pv_encryption_in_transit_enabled
    kms_key_id                          = var.kms_key_id
    defined_tags                        = var.node_defined_tags
    freeform_tags                       = var.node_freeform_tags
  }

  node_source_details {
    boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
    image_id                = var.image_id
    source_type             = var.source_type
  }


  # node_metadata = {
  #   user_data = var.cloudinit_nodepool_common == "" && lookup(var.cloudinit_nodepool, each.key, null) == null ? data.cloudinit_config.worker.rendered : lookup(var.cloudinit_nodepool, each.key, null) != null ? filebase64(lookup(var.cloudinit_nodepool, each.key, null)) : filebase64(var.cloudinit_nodepool_common)
  # }

  node_shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_in_gbs
  }


  # do not destroy the node pool if the kubernetes version has changed as part of the upgrade
  lifecycle {
    ignore_changes = [node_config_details[0].placement_configs, kubernetes_version, defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], node_config_details[0].defined_tags["Oracle-Tags.CreatedOn"], node_config_details[0].defined_tags["Oracle-Tags.CreatedBy"]]
  }
}

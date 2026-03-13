# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Module Block - OKE
# Create OKE clusters and Nodepools
#######################################


data "oci_core_subnets" "oci_subnets_endpoint" {
  # depends_on = [module.subnets] # Uncomment to create Network and OKE together
  for_each       = var.clusters != null ? var.clusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.endpoint_subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_cluster[each.key].virtual_networks.*.id[0]
}

locals {

  nodepool_worker_subnets_map = distinct([for k, v in var.nodepools : {
    for kk, vv in v.placement_configs : "${vv.vcn_name}_${vv.subnet_id}" => {
      network_compartment_id  = vv.network_compartment_id
      vcn_name                = vv.vcn_name
      subnet_id               = vv.subnet_id
      capacity_reservation_id = vv.capacity_reservation_id
    }...
  }])
  nodepool_placement_configs = { for k, v in var.nodepools : k => {
    for kk, vv in v.placement_configs :
    kk => {
      subnet_id               = length(regexall("ocid1.subnet.oc*", vv.subnet_id)) > 0 ? vv.subnet_id : data.oci_core_subnets.oci_nodepool_subnets_worker["${vv.vcn_name}_${vv.subnet_id}"].subnets.*.id[0]
      availability_domain     = vv.availability_domain
      fault_domains           = vv.fault_domains
      capacity_reservation_id = vv.capacity_reservation_id
    }
    }
  }
  nodepool_snet_list = merge(flatten([
    for item in local.nodepool_worker_subnets_map :
    { for k, v in item : k => v[0] } if length(item) != 0
  ])...)
  nodepool_vcn_map = {
    for vcn_name, ids in {
      for v in local.nodepool_snet_list :
      v.vcn_name => v.network_compartment_id...
    } :
    vcn_name => ids[0]
  }

  virtual_nodepool_worker_subnets_map = distinct([for k, v in var.nodepools : {
    for kk, vv in v.placement_configs : "${vv.vcn_name}_${vv.subnet_id}" => {
      network_compartment_id = vv.network_compartment_id
      vcn_name               = vv.vcn_name
      subnet_id              = vv.subnet_id
    }...
  }])

  virtual_nodepool_placement_configs = { for k, v in var.virtual-nodepools : k => {
    for kk, vv in v.placement_configs :
    kk => {
      subnet_id           = length(regexall("ocid1.subnet.oc*", vv.subnet_id)) > 0 ? vv.subnet_id : data.oci_core_subnets.oci_virtual_nodepool_subnets_worker["${vv.vcn_name}_${vv.subnet_id}"].subnets.*.id[0]
      availability_domain = vv.availability_domain
      fault_domain        = vv.fault_domain
    }
    }
  }
  virtual_nodepool_snet_list = merge(flatten([
    for item in local.virtual_nodepool_worker_subnets_map :
    { for k, v in item : k => v[0] } if length(item) != 0
  ])...)

  virtual_nodepool_vcn_map = {
    for vcn_name, ids in {
      for v in local.virtual_nodepool_snet_list :
      v.vcn_name => v.network_compartment_id...
    } :
    vcn_name => ids[0]
  }
}

data "oci_core_subnets" "oci_nodepool_subnets_worker" {
  for_each       = { for k, v in local.nodepool_snet_list : k => v if length(regexall("ocid1.subnet.oc*", v.subnet_id)) == 0 }
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_nodepool[each.value.vcn_name].virtual_networks.*.id[0]

}

data "oci_core_subnets" "oci_subnets_pod" {
  # depends_on = [module.subnets] # Uncomment to create Network and OKE together
  for_each       = var.nodepools != null ? var.nodepools : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.pod_subnet_ids
  vcn_id         = data.oci_core_vcns.oci_vcns_nodepool[each.value.vcn_name].virtual_networks.*.id[0]
}


data "oci_core_subnets" "oci_virtual_nodepool_subnets_worker" {
  for_each       = { for k, v in local.virtual_nodepool_snet_list : k => v if length(regexall("ocid1.subnet.oc*", v.subnet_id)) == 0 }
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_virtual_nodepool[each.value.vcn_name].virtual_networks.*.id[0]

}

data "oci_core_subnets" "oci_subnets_virtual_pod" {
  # depends_on = [module.subnets] # Uncomment to create Network and OKE together
  for_each       = var.virtual-nodepools != null ? var.virtual-nodepools : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.pod_subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_virtual_nodepool[each.value.vcn_name].virtual_networks.*.id[0]
}


data "oci_core_vcns" "oci_vcns_cluster" {
  # depends_on = [module.vcns] # Uncomment to create Network and OKE together
  for_each       = var.clusters != null ? var.clusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

data "oci_core_vcns" "oci_vcns_nodepool" {
  # depends_on = [module.vcns] # Uncomment to create Network and OKE together
  for_each       = local.nodepool_vcn_map
  compartment_id = each.value != null ? (length(regexall("ocid1.compartment.oc*", each.value)) > 0 ? each.value : var.compartment_ocids[each.value]) : var.compartment_ocids[each.value]
  display_name   = each.key
}

data "oci_core_vcns" "oci_vcns_virtual_nodepool" {
  # depends_on = [module.vcns] # Uncomment to create Network and OKE together
  for_each       = local.virtual_nodepool_vcn_map
  compartment_id = each.value != null ? (length(regexall("ocid1.compartment.oc*", each.value)) > 0 ? each.value : var.compartment_ocids[each.value]) : var.compartment_ocids[each.value]
  display_name   = each.key
}


module "clusters" {
  source                          = "../../modules/oke/cluster"
  for_each                        = var.clusters
  display_name                    = each.value.display_name
  compartment_id                  = length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]
  network_compartment_id          = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.compartment_id]
  vcn_names                       = [each.value.vcn_name]
  type                            = each.value.cluster_type
  is_policy_enabled               = each.value.is_policy_enabled
  policy_kms_key_id               = each.value.policy_kms_key_id
  kubernetes_version              = each.value.kubernetes_version
  is_kubernetes_dashboard_enabled = each.value.is_kubernetes_dashboard_enabled
  is_tiller_enabled               = each.value.is_tiller_enabled
  cni_type                        = each.value.cni_type
  is_public_ip_enabled            = each.value.is_public_ip_enabled
  nsg_ids                         = each.value.nsg_ids
  endpoint_subnet_id              = length(regexall("ocid1.subnet.oc*", each.value.endpoint_subnet_id)) > 0 ? each.value.endpoint_subnet_id : data.oci_core_subnets.oci_subnets_endpoint[each.key].subnets.*.id[0]
  is_pod_security_policy_enabled  = each.value.is_pod_security_policy_enabled
  pods_cidr                       = each.value.pods_cidr
  services_cidr                   = each.value.services_cidr
  service_lb_subnet_ids           = each.value.service_lb_subnet_ids
  kms_key_id                      = each.value.cluster_kms_key_id
  defined_tags                    = each.value.defined_tags
  freeform_tags                   = each.value.freeform_tags
  volume_defined_tags             = each.value.volume_defined_tags
  volume_freeform_tags            = each.value.volume_freeform_tags
  lb_defined_tags                 = each.value.lb_defined_tags
  lb_freeform_tags                = each.value.lb_freeform_tags
}

module "nodepools" {
  source       = "../../modules/oke/nodepool"
  for_each     = var.nodepools
  tenancy_ocid = var.tenancy_ocid
  display_name = each.value.display_name
  #availability_domain                 = each.value.availability_domain
  #fault_domains                       = each.value.fault_domains
  cluster_name           = length(regexall("ocid1.cluster.oc*", each.value.cluster_name)) > 0 ? each.value.cluster_name : merge(module.clusters.*...)[each.value.cluster_name]["cluster_tf_id"]
  compartment_id         = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  vcn_names              = [each.value.vcn_name]
  node_shape             = each.value.node_shape
  initial_node_labels    = each.value.initial_node_labels
  kubernetes_version     = each.value.kubernetes_version
  placement_configs      = local.nodepool_placement_configs[each.key]

  #subnet_id                           = length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_worker[each.key].subnets.*.id[0]
  size                                = each.value.size
  is_pv_encryption_in_transit_enabled = each.value.is_pv_encryption_in_transit_enabled
  cni_type                            = each.value.cni_type
  init_script_path                    = each.value.init_script_path
  max_pods_per_node                   = each.value.max_pods_per_node
  pod_nsg_ids                         = each.value.pod_nsg_ids
  pod_subnet_ids                      = each.value.pod_subnet_ids != null ? (length(regexall("ocid1.subnet.oc*", each.value.pod_subnet_ids)) > 0 ? each.value.pod_subnet_ids : data.oci_core_subnets.oci_subnets_pod[each.key].subnets.*.id[0]) : null
  worker_nsg_ids                      = each.value.worker_nsg_ids
  memory_in_gbs                       = each.value.memory_in_gbs
  ocpus                               = each.value.ocpus
  image_id                            = length(regexall("ocid1.image.oc*", each.value.image_id)) > 0 ? each.value.image_id : var.oke_source_ocids[each.value.image_id]
  source_type                         = each.value.source_type
  boot_volume_size_in_gbs             = each.value.boot_volume_size_in_gbs
  ssh_public_key                      = each.value.ssh_public_key != null ? (length(regexall("ssh-rsa*", each.value.ssh_public_key)) > 0 ? each.value.ssh_public_key : lookup(var.oke_ssh_keys, each.value.ssh_public_key, null)) : null
  kms_key_id                          = each.value.nodepool_kms_key_id
  node_defined_tags                   = each.value.node_defined_tags
  node_freeform_tags                  = each.value.node_freeform_tags
  nodepool_defined_tags               = each.value.nodepool_defined_tags
  nodepool_freeform_tags              = each.value.nodepool_freeform_tags
}
module "virtual-nodepools" {
  source                      = "../../modules/oke/virtual-nodepool"
  for_each                    = var.virtual-nodepools
  tenancy_ocid                = var.tenancy_ocid
  display_name                = each.value.display_name
  cluster_name                = length(regexall("ocid1.cluster.oc*", each.value.cluster_name)) > 0 ? each.value.cluster_name : merge(module.clusters.*...)[each.value.cluster_name]["cluster_tf_id"]
  compartment_id              = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id      = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  vcn_names                   = [each.value.vcn_name]
  node_shape                  = each.value.node_shape
  placement_configs           = local.virtual_nodepool_placement_configs[each.key]
  initial_virtual_node_labels = each.value.initial_virtual_node_labels
  taints                      = each.value.taints
  #subnet_id                   = length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_virtual_worker[each.key].subnets.*.id[0]
  size                   = each.value.size
  pod_nsg_ids            = each.value.pod_nsg_ids
  pod_subnet_id          = (length(regexall("ocid1.subnet.oc*", each.value.pod_subnet_id)) > 0 ? each.value.pod_subnet_id : data.oci_core_subnets.oci_subnets_virtual_pod[each.key].subnets.*.id[0])
  worker_nsg_ids         = each.value.worker_nsg_ids
  node_defined_tags      = each.value.node_defined_tags
  node_freeform_tags     = each.value.node_freeform_tags
  nodepool_defined_tags  = each.value.nodepool_defined_tags
  nodepool_freeform_tags = each.value.nodepool_freeform_tags
}
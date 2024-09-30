# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Block SDDC
# Create SDDC
############################################

locals {
  vlan_ids = ["nsx_edge_uplink1vlan_id", "nsx_edge_uplink2vlan_id", "nsx_edge_vtep_vlan_id", "nsx_vtep_vlan_id", "vmotion_vlan_id", "vsan_vlan_id", "vsphere_vlan_id", "replication_vlan_id", "provisioning_vlan_id", "hcx_vlan_id"]
  vlan_config = flatten([for index in local.vlan_ids : [
    for key, val in var.sddcs : {
      #(index) = lookup(val, index, 0)
      compartment_id = val.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", val.network_compartment_id)) > 0 ? val.network_compartment_id : var.compartment_ocids[val.network_compartment_id]) : null
      display_name   = lookup(val, index, 0)
      vcn_id         = data.oci_core_vcns.oci_vcns_sddc[key].virtual_networks.*.id[0]
    }
  ]])

  ds_vols = flatten([for key, val in var.sddcs : [
    for item in concat(local.mgmt_vols[val.display_name], local.wkld_vols[val.display_name]) : {
      volume_display_name   = item.volume_display_name
      volume_compartment_id = item.volume_compartment_id
    }
  ]])

  mgmt_vols = { for key, val in var.sddcs :
    val.display_name => try([for item in val.management_datastore : {
      volume_compartment_id = try(split("@", item)[0], null)
      volume_display_name   = try(split("@", item)[1], null)
  }], []) }

  wkld_vols = { for key, val in var.sddcs :
    val.display_name => try([for item in val.workload_datastore :
      {
        volume_compartment_id = try(split("@", item)[0], null)
        volume_display_name   = try(split("@", item)[1], null)
  }], []) }

  management_datastores = { for key, val in var.sddcs : key => (val.management_datastore != null ? [for value in val.management_datastore : data.oci_core_volumes.ds_volumes[split("@", value)[1]].volumes.*.id[0]] : [])
  }

  workload_datastores = { for key, val in var.sddcs : key => (val.workload_datastore != null ? [for value in val.workload_datastore : data.oci_core_volumes.ds_volumes[split("@", value)[1]].volumes.*.id[0]] : [])
  }
}

data "oci_core_volumes" "ds_volumes" {
  for_each       = { for value in local.ds_vols : value.volume_display_name => value.volume_compartment_id if value.volume_display_name != null }
  compartment_id = each.value != null ? (length(regexall("ocid1.compartment.oc*", each.value)) > 0 ? each.value : var.compartment_ocids[each.value]) : var.compartment_ocids[each.value]
  display_name   = each.key
  state          = "AVAILABLE"

}

data "oci_core_vcns" "oci_vcns_sddc" {
  # depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each       = var.sddcs != null ? var.sddcs : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

data "oci_core_subnets" "oci_subnets_sddc" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.sddcs != null ? var.sddcs : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.provisioning_subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_sddc[each.key].virtual_networks.*.id[0]
}

data "oci_core_vlans" "sddc_vlan_id" {
  #Required
  for_each       = { for vlan in local.vlan_config : vlan.display_name => vlan if vlan.display_name != null }
  compartment_id = each.value.compartment_id
  display_name   = each.key
  vcn_id         = each.value.vcn_id
}

module "sddcs" {
  #depends_on = [module.vlans]
  source                      = "./modules/sddc/sddc"
  for_each                    = var.sddcs != null ? var.sddcs : {}
  compartment_id              = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id      = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  compute_availability_domain = each.value.availability_domain == "multi-AD" ? each.value.availability_domain : (each.value.availability_domain != "" && each.value.availability_domain != null) ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  esxi_hosts_count            = each.value.esxi_hosts_count != "" ? each.value.esxi_hosts_count : null
  nsx_edge_uplink1vlan_id     = each.value.nsx_edge_uplink1vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_edge_uplink1vlan_id)) > 0 ? each.value.nsx_edge_uplink1vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_uplink1vlan_id].vlans[0].id) : null
  nsx_edge_uplink2vlan_id     = each.value.nsx_edge_uplink2vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_edge_uplink2vlan_id)) > 0 ? each.value.nsx_edge_uplink2vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_uplink2vlan_id].vlans[0].id) : null
  nsx_edge_vtep_vlan_id       = each.value.nsx_edge_vtep_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_edge_vtep_vlan_id)) > 0 ? each.value.nsx_edge_vtep_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_vtep_vlan_id].vlans[0].id) : null
  nsx_vtep_vlan_id            = each.value.nsx_vtep_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_vtep_vlan_id)) > 0 ? each.value.nsx_vtep_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_vtep_vlan_id].vlans[0].id) : null
  provisioning_subnet_id      = each.value.provisioning_subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.provisioning_subnet_id)) > 0 ? each.value.provisioning_subnet_id : data.oci_core_subnets.oci_subnets_sddc[each.key].subnets.*.id[0]) : null
  ssh_authorized_keys         = each.value.ssh_authorized_keys != null ? (length(regexall("ssh-rsa*", each.value.ssh_authorized_keys)) > 0 ? each.value.ssh_authorized_keys : lookup(var.sddc_ssh_keys, each.value.ssh_authorized_keys, null)) : null
  vmotion_vlan_id             = each.value.vmotion_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.vmotion_vlan_id)) > 0 ? each.value.vmotion_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.vmotion_vlan_id].vlans[0].id) : null
  vmware_software_version     = each.value.vmware_software_version != "" ? each.value.vmware_software_version : null
  vsan_vlan_id                = each.value.vsan_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.vsan_vlan_id)) > 0 ? each.value.vsan_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.vsan_vlan_id].vlans[0].id) : null
  vsphere_vlan_id             = each.value.vsphere_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.vsphere_vlan_id)) > 0 ? each.value.vsphere_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.vsphere_vlan_id].vlans[0].id) : null
  #Optional
  initial_host_ocpu_count               = each.value.initial_host_ocpu_count != "" ? each.value.initial_host_ocpu_count : null
  initial_host_shape_name               = each.value.initial_host_shape_name != "" ? each.value.initial_host_shape_name : null
  capacity_reservation_id               = each.value.capacity_reservation_id != "" ? each.value.capacity_reservation_id : null
  initial_cluster_display_name          = each.value.initial_cluster_display_name != "" ? each.value.initial_cluster_display_name : null #new addition
  display_name                          = each.value.display_name != "" ? each.value.display_name : null                                 #edited
  defined_tags                          = each.value.defined_tags != {} ? each.value.defined_tags : {}
  freeform_tags                         = each.value.freeform_tags != {} ? each.value.freeform_tags : {}
  hcx_action                            = each.value.hcx_action != "" ? each.value.hcx_action : null
  hcx_vlan_id                           = each.value.hcx_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.hcx_vlan_id)) > 0 ? each.value.hcx_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.hcx_vlan_id].vlans[0].id) : null
  initial_commitment                    = each.value.initial_commitment != "" ? each.value.initial_commitment : null
  instance_display_name_prefix          = each.value.instance_display_name_prefix != "" ? each.value.instance_display_name_prefix : null
  is_hcx_enabled                        = each.value.is_hcx_enabled != "" ? each.value.is_hcx_enabled : null
  is_shielded_instance_enabled          = each.value.is_shielded_instance_enabled != "" ? each.value.is_shielded_instance_enabled : null
  is_single_host_sddc                   = each.value.is_single_host_sddc != "" ? each.value.is_single_host_sddc : null
  provisioning_vlan_id                  = each.value.provisioning_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.provisioning_vlan_id)) > 0 ? each.value.provisioning_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.provisioning_vlan_id].vlans[0].id) : null
  refresh_hcx_license_status            = each.value.refresh_hcx_license_status != "" ? each.value.refresh_hcx_license_status : null
  replication_vlan_id                   = each.value.replication_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.replication_vlan_id)) > 0 ? each.value.replication_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.replication_vlan_id].vlans[0].id) : null
  reserving_hcx_on_premise_license_keys = each.value.reserving_hcx_on_premise_license_keys != "" ? each.value.reserving_hcx_on_premise_license_keys : null
  workload_network_cidr                 = each.value.workload_network_cidr != "" ? each.value.workload_network_cidr : null
  management_datastore                  = local.management_datastores[each.key] != null ? local.management_datastores[each.key] : []
  workload_datastore                    = local.workload_datastores[each.key] != null ? local.workload_datastores[each.key] : []

}

############################################
# Module Block SDDC-Cluster
# Create additional SDDC-Cluster
############################################

locals {
  vlan_ids_sddc_cluster = ["nsx_edge_uplink1vlan_id", "nsx_edge_uplink2vlan_id", "nsx_edge_vtep_vlan_id", "nsx_vtep_vlan_id", "vmotion_vlan_id", "vsan_vlan_id", "vsphere_vlan_id", "replication_vlan_id", "provisioning_vlan_id", "hcx_vlan_id"]
  vlan_config_sddc_cluster = flatten([for index in local.vlan_ids_sddc_cluster : [
    for key, val in var.sddc-clusters : {
      #(index) = lookup(val, index, 0)
      compartment_id = val.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", val.network_compartment_id)) > 0 ? val.network_compartment_id : var.compartment_ocids[val.network_compartment_id]) : null
      display_name   = lookup(val, index, 0)
      vcn_id         = data.oci_core_vcns.oci_vcns_sddc_cluster[key].virtual_networks.*.id[0]
    }
  ]])

  ##grouping by display name
  group_display_name = {
    for item in local.vlan_config_sddc_cluster : item.display_name => item...
  }
  #removing duplicate entry
  deduplicated_vlan_config = {
    for key, value in local.group_display_name : key => value[0]
  }
  #converting map to a list
  deduplicated_vlan_list = values(local.deduplicated_vlan_config)


  ds_vols_sddc_cluster = flatten([for key, val in var.sddc-clusters : [
    #for item in concat(local.mgmt_vols_sddc_cluster[val.display_name],local.wkld_vols_sddc_cluster[val.display_name]): {
    for item in local.wkld_vols_sddc_cluster[val.display_name] : {
      volume_display_name   = item.volume_display_name
      volume_compartment_id = item.volume_compartment_id
    }
  ]])

  wkld_vols_sddc_cluster = { for key, val in var.sddc-clusters :
    val.display_name => try([for item in val.workload_datastore :
      {
        volume_compartment_id = try(split("@", item)[0], null)
        volume_display_name   = try(split("@", item)[1], null)
  }], []) }


  workload_datastores_sddc_cluster = { for key, val in var.sddc-clusters : key => (val.workload_datastore != null ? [for value in val.workload_datastore : data.oci_core_volumes.ds_volumes_sddc_cluster[split("@", value)[1]].volumes.*.id[0]] : [])
  }
}

data "oci_core_volumes" "ds_volumes_sddc_cluster" {
  for_each       = { for value in local.ds_vols_sddc_cluster : value.volume_display_name => value.volume_compartment_id if value.volume_display_name != null }
  compartment_id = each.value != null ? (length(regexall("ocid1.compartment.oc*", each.value)) > 0 ? each.value : var.compartment_ocids[each.value]) : var.compartment_ocids[each.value]
  display_name   = each.key
  state          = "AVAILABLE"

}

data "oci_core_vcns" "oci_vcns_sddc_cluster" {
  #depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each       = var.sddc-clusters != null ? var.sddc-clusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

data "oci_core_subnets" "oci_subnets_sddc_cluster" {
  #depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.sddc-clusters != null ? var.sddc-clusters : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.provisioning_subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_sddc_cluster[each.key].virtual_networks.*.id[0]
}

data "oci_core_vlans" "sddc_cluster_vlan_id" {
  #depends_on = [module.vlans]
  #Required
  for_each       = { for vlan in local.deduplicated_vlan_list : vlan.display_name => vlan if vlan.display_name != null }
  compartment_id = each.value.compartment_id
  display_name   = each.key
  vcn_id         = each.value.vcn_id
}

data "oci_ocvp_sddcs" "oci_sddcs" {
  depends_on     = [module.sddcs]
  for_each       = var.sddc-clusters != null ? var.sddc-clusters : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.sddc_id
  state          = "ACTIVE"
}

module "sddc-clusters" {
  #depends_on                   = [module.nsgs, module.vcns, module.route-tables, module.vlans, module.sddcs]
  depends_on                   = [module.sddcs]
  source                       = "./modules/sddc/sddc-cluster"
  for_each                     = var.sddc-clusters != null ? var.sddc-clusters : {}
  compartment_id               = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id       = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  compute_availability_domain  = each.value.availability_domain == "multi-AD" ? each.value.availability_domain : (each.value.availability_domain != "" && each.value.availability_domain != null) ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  display_name                 = each.value.display_name != "" ? each.value.display_name : null
  vmware_software_version      = each.value.vmware_software_version != "" ? each.value.vmware_software_version : null
  initial_commitment           = each.value.initial_commitment != "" ? each.value.initial_commitment : null
  initial_host_ocpu_count      = each.value.initial_host_ocpu_count != "" ? each.value.initial_host_ocpu_count : null
  initial_host_shape_name      = each.value.initial_host_shape_name != "" ? each.value.initial_host_shape_name : null
  esxi_hosts_count             = each.value.esxi_hosts_count != "" ? each.value.esxi_hosts_count : null
  instance_display_name_prefix = each.value.instance_display_name_prefix != "" ? each.value.instance_display_name_prefix : null
  is_shielded_instance_enabled = each.value.is_shielded_instance_enabled != "" ? each.value.is_shielded_instance_enabled : null
  nsx_edge_uplink1vlan_id      = each.value.nsx_edge_uplink1vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_edge_uplink1vlan_id)) > 0 ? each.value.nsx_edge_uplink1vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.nsx_edge_uplink1vlan_id].vlans[0].id) : null
  nsx_edge_uplink2vlan_id      = each.value.nsx_edge_uplink2vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_edge_uplink2vlan_id)) > 0 ? each.value.nsx_edge_uplink2vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_uplink2vlan_id].vlans[0].id) : null
  nsx_edge_vtep_vlan_id        = each.value.nsx_edge_vtep_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_edge_vtep_vlan_id)) > 0 ? each.value.nsx_edge_vtep_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.nsx_edge_vtep_vlan_id].vlans[0].id) : null
  nsx_vtep_vlan_id             = each.value.nsx_vtep_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.nsx_vtep_vlan_id)) > 0 ? each.value.nsx_vtep_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.nsx_vtep_vlan_id].vlans[0].id) : null
  provisioning_subnet_id       = each.value.provisioning_subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.provisioning_subnet_id)) > 0 ? each.value.provisioning_subnet_id : data.oci_core_subnets.oci_subnets_sddc_cluster[each.key].subnets.*.id[0]) : null
  vmotion_vlan_id              = each.value.vmotion_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.vmotion_vlan_id)) > 0 ? each.value.vmotion_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.vmotion_vlan_id].vlans[0].id) : null
  vsan_vlan_id                 = each.value.vsan_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.vsan_vlan_id)) > 0 ? each.value.vsan_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.vsan_vlan_id].vlans[0].id) : null
  vsphere_vlan_id              = each.value.vsphere_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.vsphere_vlan_id)) > 0 ? each.value.vsphere_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.vsphere_vlan_id].vlans[0].id) : null
  replication_vlan_id          = each.value.replication_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.replication_vlan_id)) > 0 ? each.value.replication_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.replication_vlan_id].vlans[0].id) : null
  hcx_vlan_id                  = each.value.hcx_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.hcx_vlan_id)) > 0 ? each.value.hcx_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.hcx_vlan_id].vlans[0].id) : null
  provisioning_vlan_id         = each.value.provisioning_vlan_id != null ? (length(regexall("ocid1.vlan.oc*", each.value.provisioning_vlan_id)) > 0 ? each.value.provisioning_vlan_id : data.oci_core_vlans.sddc_cluster_vlan_id[each.value.provisioning_vlan_id].vlans[0].id) : null
  workload_network_cidr        = each.value.workload_network_cidr != "" ? each.value.workload_network_cidr : null
  sddc_id                      = each.value.sddc_id != null ? (length(regexall("ocid1.vmwaresddc.oc*", each.value.sddc_id)) > 0 ? each.value.sddc_id : data.oci_ocvp_sddcs.oci_sddcs[each.key].sddc_collection[0].id) : null
  workload_datastore           = local.workload_datastores_sddc_cluster[each.key] != null ? local.workload_datastores_sddc_cluster[each.key] : []
  defined_tags                 = each.value.defined_tags != {} ? each.value.defined_tags : {}
  freeform_tags                = each.value.freeform_tags != {} ? each.value.freeform_tags : {}
  esxi_software_version        = each.value.esxi_software_version != "" ? each.value.esxi_software_version : null
  ssh_authorized_keys          = each.value.ssh_authorized_keys != null ? (length(regexall("ssh-rsa*", each.value.ssh_authorized_keys)) > 0 ? each.value.ssh_authorized_keys : lookup(var.sddc_ssh_keys, each.value.ssh_authorized_keys, null)) : null
}

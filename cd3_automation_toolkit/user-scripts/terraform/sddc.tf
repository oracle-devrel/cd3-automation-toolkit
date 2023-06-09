############################################
# Module Block SDDC
# Create SDDC
############################################

locals {
  vlan_ids = ["nsx_edge_uplink1vlan_id", "nsx_edge_uplink2vlan_id", "nsx_edge_vtep_vlan_id", "nsx_vtep_vlan_id", "vmotion_vlan_id", "vsan_vlan_id", "vsphere_vlan_id", "replication_vlan_id", "provisioning_vlan_id", "hcx_vlan_id"]
  vlan_config = flatten([for index in local.vlan_ids : [
    for key, val in var.sddcs : {
      #(index) = lookup(val, index, 0)
      compartment_id = val.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", val.network_compartment_id)) > 0 ? val.network_compartment_id : var.compartment_ocids[val.network_compartment_id]) : null
      display_name   = lookup(val, index, 0)
      vcn_id         = data.oci_core_vcns.oci_vcns_sddc[key].virtual_networks.*.id[0]
    }
  ]])
}


data "oci_core_vcns" "oci_vcns_sddc" {
  # depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each       = var.sddcs != null ? var.sddcs : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

data "oci_core_subnets" "oci_subnets_sddc" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.sddcs != null ? var.sddcs : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.provisioning_subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_sddc[each.key].virtual_networks.*.id[0]
}


data "oci_core_vlans" "sddc_vlan_id" {
  #Required
  for_each       = { for vlan in local.vlan_config : vlan.display_name => vlan }
  compartment_id = each.value.compartment_id
  display_name   = each.key
  vcn_id         = each.value.vcn_id
}

module "sddcs" {
  #depends_on = [module.vlans]
  source                      = "./modules/sddc"
  for_each                    = var.sddcs != null ? var.sddcs : {}
  compartment_id              = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id      = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  compute_availability_domain = each.value.availability_domain == "multi-AD" ? each.value.availability_domain : (each.value.availability_domain != "" && each.value.availability_domain != null) ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  esxi_hosts_count            = each.value.esxi_hosts_count != "" ? each.value.esxi_hosts_count : null
  nsx_edge_uplink1vlan_id     = each.value.nsx_edge_uplink1vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.nsx_edge_uplink1vlan_id)) > 0 ? each.value.nsx_edge_uplink1vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_uplink1vlan_id].vlans[0].id) : null
  nsx_edge_uplink2vlan_id     = each.value.nsx_edge_uplink2vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.nsx_edge_uplink2vlan_id)) > 0 ? each.value.nsx_edge_uplink2vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_uplink2vlan_id].vlans[0].id) : null
  nsx_edge_vtep_vlan_id       = each.value.nsx_edge_vtep_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.nsx_edge_vtep_vlan_id)) > 0 ? each.value.nsx_edge_vtep_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_edge_vtep_vlan_id].vlans[0].id) : null
  nsx_vtep_vlan_id            = each.value.nsx_vtep_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.nsx_vtep_vlan_id)) > 0 ? each.value.nsx_vtep_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.nsx_vtep_vlan_id].vlans[0].id) : null
  provisioning_subnet_id      = each.value.provisioning_subnet_id != "" ? (length(regexall("ocid1.subnet.oc1*", each.value.provisioning_subnet_id)) > 0 ? each.value.provisioning_subnet_id : data.oci_core_subnets.oci_subnets_sddc[each.key].subnets.*.id[0]) : null
  ssh_authorized_keys         = each.value.ssh_authorized_keys != null ? (length(regexall("ssh-rsa*", each.value.ssh_authorized_keys)) > 0 ? each.value.ssh_authorized_keys : lookup(var.sddc_ssh_keys, each.value.ssh_authorized_keys, null)) : null
  vmotion_vlan_id             = each.value.vmotion_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.vmotion_vlan_id)) > 0 ? each.value.vmotion_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.vmotion_vlan_id].vlans[0].id) : null
  vmware_software_version     = each.value.vmware_software_version != "" ? each.value.vmware_software_version : null
  vsan_vlan_id                = each.value.vsan_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.vsan_vlan_id)) > 0 ? each.value.vsan_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.vsan_vlan_id].vlans[0].id) : null
  vsphere_vlan_id             = each.value.vsphere_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.vsphere_vlan_id)) > 0 ? each.value.vsphere_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.vsphere_vlan_id].vlans[0].id) : null
  #Optional
  capacity_reservation_id               = each.value.capacity_reservation_id != "" ? each.value.capacity_reservation_id : null
  display_name                          = each.value.display_name != "" ? each.value.display_name : null
  defined_tags                          = each.value.defined_tags != {} ? each.value.defined_tags : {}
  freeform_tags                         = each.value.freeform_tags != {} ? each.value.freeform_tags : {}
  hcx_action                            = each.value.hcx_action != "" ? each.value.hcx_action : null
  hcx_vlan_id                           = each.value.hcx_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.hcx_vlan_id)) > 0 ? each.value.hcx_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.hcx_vlan_id].vlans[0].id) : null
  initial_host_ocpu_count               = each.value.initial_host_ocpu_count != "" ? each.value.initial_host_ocpu_count : null
  initial_host_shape_name               = each.value.initial_host_shape_name != "" ? each.value.initial_host_shape_name : null
  initial_sku                           = each.value.initial_sku != "" ? each.value.initial_sku : null
  instance_display_name_prefix          = each.value.instance_display_name_prefix != "" ? each.value.instance_display_name_prefix : null
  is_hcx_enabled                        = each.value.is_hcx_enabled != "" ? each.value.is_hcx_enabled : null
  is_shielded_instance_enabled          = each.value.is_shielded_instance_enabled != "" ? each.value.is_shielded_instance_enabled : null
  is_single_host_sddc                   = each.value.is_single_host_sddc != "" ? each.value.is_single_host_sddc : null
  provisioning_vlan_id                  = each.value.provisioning_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.provisioning_vlan_id)) > 0 ? each.value.provisioning_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.provisioning_vlan_id].vlans[0].id) : null
  refresh_hcx_license_status            = each.value.refresh_hcx_license_status != "" ? each.value.refresh_hcx_license_status : null
  replication_vlan_id                   = each.value.replication_vlan_id != null ? (length(regexall("ocid1.vlan.oc1*", each.value.replication_vlan_id)) > 0 ? each.value.replication_vlan_id : data.oci_core_vlans.sddc_vlan_id[each.value.replication_vlan_id].vlans[0].id) : null
  reserving_hcx_on_premise_license_keys = each.value.reserving_hcx_on_premise_license_keys != "" ? each.value.reserving_hcx_on_premise_license_keys : null
  workload_network_cidr                 = each.value.workload_network_cidr != "" ? each.value.workload_network_cidr : null
}
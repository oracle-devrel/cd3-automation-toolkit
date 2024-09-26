# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - SDDC
# Create SDDC
############################
resource "oci_ocvp_sddc" "sddc" {
  compartment_id              = var.compartment_id
  vmware_software_version     = var.vmware_software_version
  ssh_authorized_keys         = var.ssh_authorized_keys


  initial_configuration {
    initial_cluster_configurations {
        display_name                 = var.initial_cluster_display_name
        initial_commitment           = var.initial_commitment
        compute_availability_domain  = var.compute_availability_domain
        esxi_hosts_count             = var.esxi_hosts_count
        vsphere_type                 = "MANAGEMENT"
        initial_host_ocpu_count      = var.initial_host_ocpu_count
        initial_host_shape_name      = var.initial_host_shape_name
        instance_display_name_prefix = var.instance_display_name_prefix
        is_shielded_instance_enabled = var.is_shielded_instance_enabled
        capacity_reservation_id      = var.capacity_reservation_id
        workload_network_cidr        = var.workload_network_cidr

        network_configuration {
          nsx_edge_uplink1vlan_id     = var.nsx_edge_uplink1vlan_id
          nsx_edge_uplink2vlan_id     = var.nsx_edge_uplink2vlan_id
          nsx_edge_vtep_vlan_id       = var.nsx_edge_vtep_vlan_id
          nsx_vtep_vlan_id            = var.nsx_vtep_vlan_id
          provisioning_subnet_id      = var.provisioning_subnet_id
          vmotion_vlan_id             = var.vmotion_vlan_id
          vsan_vlan_id                = var.vsan_vlan_id
          vsphere_vlan_id             = var.vsphere_vlan_id
          provisioning_vlan_id         = var.provisioning_vlan_id
          replication_vlan_id          = var.replication_vlan_id
          hcx_vlan_id                  = var.hcx_vlan_id
         }


        dynamic "datastores" {
            for_each = length(var.management_datastore) != 0 ? [1] : []
             content {
             datastore_type = "MANAGEMENT"
             block_volume_ids = var.management_datastore
            }
        }
        dynamic "datastores" {
            for_each = length(var.workload_datastore) != 0 ? [1] : []
            content {
            datastore_type = "WORKLOAD"
            block_volume_ids = var.workload_datastore
            }
        }
      }
  }

  #Optional
  defined_tags                 = var.defined_tags
  display_name                 = var.display_name
  freeform_tags                = var.freeform_tags
  hcx_action                   = var.hcx_action
  is_hcx_enabled               = var.is_hcx_enabled
  is_single_host_sddc          = var.is_single_host_sddc
}


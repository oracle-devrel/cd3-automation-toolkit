# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - SDDC Cluster
# Create SDDC Cluster
############################

resource "oci_ocvp_cluster" "sddc_cluster" {
    #Required
    compute_availability_domain = var.compute_availability_domain
    esxi_hosts_count = var.esxi_hosts_count
    network_configuration {
        #Required
        nsx_edge_vtep_vlan_id = var.nsx_edge_vtep_vlan_id
        nsx_vtep_vlan_id = var.nsx_vtep_vlan_id
        provisioning_subnet_id = var.provisioning_subnet_id
        vmotion_vlan_id = var.vmotion_vlan_id
        vsan_vlan_id = var.vsan_vlan_id
        #Optional
        hcx_vlan_id = var.hcx_vlan_id
        nsx_edge_uplink1vlan_id = var.nsx_edge_uplink1vlan_id
        nsx_edge_uplink2vlan_id = var.nsx_edge_uplink2vlan_id
        provisioning_vlan_id = var.provisioning_vlan_id
        replication_vlan_id = var.replication_vlan_id
        vsphere_vlan_id = var.vsphere_vlan_id
    }
    sddc_id = var.sddc_id
    #Optional
    capacity_reservation_id = var.capacity_reservation_id

    dynamic "datastores" {
        for_each = length(var.workload_datastore) != 0 ? [1] : []
        content {
        datastore_type = "WORKLOAD"
        block_volume_ids = var.workload_datastore
        }
    }
    defined_tags = var.defined_tags
    display_name = var.display_name
    esxi_software_version = var.esxi_software_version
    freeform_tags = var.freeform_tags
    initial_commitment = var.initial_commitment
    initial_host_ocpu_count = var.initial_host_ocpu_count
    initial_host_shape_name = var.initial_host_shape_name
    instance_display_name_prefix = var.instance_display_name_prefix
    is_shielded_instance_enabled = var.is_shielded_instance_enabled
    vmware_software_version = var.vmware_software_version
    workload_network_cidr = var.workload_network_cidr
    timeouts { create = "45m" }
}


// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - SDDC
# Create SDDC
############################
resource "oci_ocvp_sddc" "sddc" {
    compartment_id = var.compartment_id
    compute_availability_domain = var.compute_availability_domain
    esxi_hosts_count = var.esxi_hosts_count
    nsx_edge_uplink1vlan_id = var.nsx_edge_uplink1vlan_id
    nsx_edge_uplink2vlan_id = var.nsx_edge_uplink2vlan_id
    nsx_edge_vtep_vlan_id = var.nsx_edge_vtep_vlan_id
    nsx_vtep_vlan_id = var.nsx_vtep_vlan_id
    provisioning_subnet_id = var.provisioning_subnet_id
    ssh_authorized_keys = var.ssh_authorized_keys
    vmotion_vlan_id = var.vmotion_vlan_id
    vmware_software_version = var.vmware_software_version
    vsan_vlan_id = var.vsan_vlan_id
    vsphere_vlan_id = var.vsphere_vlan_id

    #Optional
    capacity_reservation_id = var.capacity_reservation_id
    defined_tags = var.defined_tags
    display_name = var.display_name
    freeform_tags = var.freeform_tags
    hcx_action = var.hcx_action
    hcx_vlan_id = var.hcx_vlan_id
    initial_host_ocpu_count = var.initial_host_ocpu_count
    initial_host_shape_name = var.initial_host_shape_name
    initial_sku = var.initial_sku
    instance_display_name_prefix = var.instance_display_name_prefix
    is_hcx_enabled = var.is_hcx_enabled
    is_shielded_instance_enabled = var.is_shielded_instance_enabled
    is_single_host_sddc = var.is_single_host_sddc
    provisioning_vlan_id = var.provisioning_vlan_id
    replication_vlan_id = var.replication_vlan_id
    workload_network_cidr = var.workload_network_cidr
}


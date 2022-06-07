// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################################
# Module Block - Private IPs, Public IP Pools and Reserved IPs
# Create Private IPs, Public IP Pools and Reserved IPs
# Allowed Values:
# Lifetime Values can be one of EPHEMERAL or RESERVED
############################################

locals {
    vnic_id = [ for key,value in var.private_ips : zipmap(data.oci_core_vnic_attachments.vnic_attachments[key].vnic_attachments.*.display_name, data.oci_core_vnic_attachments.vnic_attachments[key].vnic_attachments.*.vnic_id)]
    private_ip_id = [ for key,value in data.oci_core_private_ips.ip_address : zipmap(data.oci_core_private_ips.ip_address[key].private_ips.*.ip_address, data.oci_core_private_ips.ip_address[key].private_ips.*.id)]
    instance_id = [ for key,value in data.oci_core_instances.instances_for_vnic : zipmap(data.oci_core_instances.instances_for_vnic[key].instances.*.display_name, data.oci_core_instances.instances_for_vnic[key].instances.*.id)]
}

data "oci_core_vnic_attachments" "vnic_attachments" {
    depends_on = [module.vnic-attachments]
    for_each = var.private_ips != null  && var.private_ips != {} ? var.private_ips : {}

    #Required
    compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
    instance_id = local.instance_id[0][each.value.instance_id]
    filter {
        name = "state"
        values = ["ATTACHED"]
    }
}

data "oci_core_subnets" "oci_subnets_vnics" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each = var.vnic_attachments != null && var.vnic_attachments != {} ? var.vnic_attachments : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_vnics[each.value.display_name].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_vnics" {
  # depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each = var.vnic_attachments != null  && var.vnic_attachments != {} ? var.vnic_attachments : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

data "oci_core_instances" "instances_for_vnic" {
  # depends_on = [module.instances]
  for_each       = var.vnic_attachments != null && var.vnic_attachments != {} ? var.vnic_attachments : {}
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   =  each.value.instance_id
  state = "RUNNING"
}

# Filter on VNIC ID
data "oci_core_private_ips" "ip_address" {
    depends_on = [module.private-ips, module.vnic-attachments]
    for_each = var.reserved_ips != null && var.reserved_ips != {} ? var.reserved_ips : {}

    #Optional
   # ip_address = each.value.private_ip_id
   # subnet_id = each.value.subnet_id
   # vlan_id = each.value.vlan_id
    vnic_id = each.value.vnic_id != "" ? (length(regexall("ocid1.vnic.oc1*",each.value.vnic_id)) > 0 ? each.value.vnic_id : local.vnic_id.0[each.value.vnic_id]) : local.vnic_id.0[""] #data.oci_core_vnic_attachments.vnic_attachments[each.key].vnic_attachments[0].vnic_id) : null
}

module "vnic-attachments" {
    source = "./modules/network/vnic-attachment"
    for_each = var.vnic_attachments != null && var.vnic_attachments != {}  ? var.vnic_attachments : {}

    #Optional
    subnet_id            = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc1*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_vnics[each.value.display_name].subnets.*.id[0]) : null
    vcn_names            = [each.value.vcn_name]
    defined_tags         = each.value.defined_tags
    display_name         = each.value.display_name
    freeform_tags        = each.value.freeform_tags
    private_ip           = each.value.private_ip
    skip_source_dest_check  = each.value.skip_source_dest_check
    vlan_id              = each.value.vlan_id
    nsg_ids              = each.value.nsg_ids
    instance_id          = each.value.instance_id != "" ? length(regexall("ocid1.instance.oc1*", each.value.instance_id)) > 0 ? each.value.attach_to_instance : try(merge(module.instances.*...)[each.value.instance_id]["instance_tf_id"], data.oci_core_instances.instances_for_vnic[each.key].instances.*.id[0]) : ""
#    nic_index            = each.value.nic_index
#    assign_private_dns_record = each.value.assign_private_dns_record
#    assign_public_ip     =  each.value.assign_public_ip
#    hostname_label       = each.value.hostname_label

    }

module "private-ips" {
    depends_on = [module.vnic-attachments]
    source = "./modules/ip/secondary-private-ip"
    for_each = var.private_ips != null && var.private_ips != {} ? var.private_ips : {}

    #Optional
    defined_tags         = each.value.defined_tags
    display_name         = each.value.display_name
    freeform_tags        = each.value.freeform_tags
    hostname_label       = each.value.hostname_label
    ip_address           = each.value.ip_address
    vlan_id              = each.value.vlan_id
    vnic_id              = each.value.vnic_id != "" ? (length(regexall("ocid1.vnic.oc1*",each.value.vnic_id)) > 0 ? each.value.vnic_id : local.vnic_id.0[each.value.vnic_id]) : local.vnic_id.0[""] #data.oci_core_vnic_attachments.vnic_attachments[each.key].vnic_attachments[0].vnic_id) : null
}

module "public-ip-pools" {
    source = "./modules/ip/public-ip-pool"
    for_each = var.public_ip_pools != null && var.public_ip_pools != {} ? var.public_ip_pools : {}

    #Required
    compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

    #Optional
    defined_tags         = each.value.defined_tags
    display_name         = each.value.display_name
    freeform_tags        = each.value.freeform_tags

}

module "reserved-ips" {
    source = "./modules/ip/reserved-public-ip"
    for_each = var.reserved_ips != null && var.reserved_ips != {}  ? var.reserved_ips : {}
    depends_on = [module.private-ips]

    #Required
    compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
    lifetime = each.value.lifetime

    #Optional
    defined_tags         = each.value.defined_tags
    display_name         = each.value.display_name
    freeform_tags        = each.value.freeform_tags
    private_ip_id        = each.value.private_ip_id != "" ? (length(regexall("ocid1.privateip.oc1*", each.value.private_ip_id)) > 0 ? each.value.private_ip_id : (length(regexall("\\.", each.value.private_ip_id)) == 3 ? local.private_ip_id[0][each.value.private_ip_id] : merge(module.private-ips.*...)[each.value.private_ip_id].private_ip_tf_id)) : null
    public_ip_pool_id    = each.value.public_ip_pool_id != "" ? (length(regexall("ocid1.publicippool.oc1*", each.value.public_ip_pool_id)) > 0 ? each.value.public_ip_pool_id : merge(module.public-ip-pools.*...)[each.value.public_ip_pool_id].public_ip_pool_tf_id) : null
}


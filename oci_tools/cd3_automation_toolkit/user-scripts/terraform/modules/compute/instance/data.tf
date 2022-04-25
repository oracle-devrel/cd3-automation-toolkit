// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
## Data Block - Instance
## Create Instance and Boot Volume Backup Policy
#############################

locals {
  nsg_ids = flatten(tolist([for nsg in var.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)]))
}


data "oci_core_vcns" "oci_vcns_instances" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}


data "oci_core_dedicated_vm_hosts" "existing_vm_host" {
  count          = var.dedicated_vm_host_name != null ? 1 : 0
  compartment_id = var.compartment_id
  display_name   = var.dedicated_vm_host_name
  state          = "ACTIVE"
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each = {for nsg in var.nsg_ids: nsg => nsg }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id = data.oci_core_vcns.oci_vcns_instances[var.vcn_names[0]].virtual_networks.*.id[0]
}

data "oci_core_boot_volumes" "all_boot_volumes" {
  depends_on = [oci_core_instance.core_instance]
  count     = var.boot_tf_policy != "" ? 1 : 0
  #Required
  compartment_id = var.compartment_id
  availability_domain =  var.availability_domain
  filter {
    name   = "display_name"
    values = [join(" ", [var.display_name, "(Boot Volume)"])]
  }
  filter {
    name = "state"
    values = ["AVAILABLE"]
  }
}

data "oci_core_volume_backup_policies" "boot_vol_backup_policy" {
  count     = var.boot_tf_policy != "" ? 1 : 0

  filter {
    name   = "display_name"
    values = [lower(var.boot_tf_policy)]
  }

}

data "oci_core_volume_backup_policies" "boot_vol_custom_policy" {
  count     = var.boot_tf_policy != "" ? 1 : 0
  compartment_id = local.policy_tf_compartment_id
  filter {
    name   = "display_name"
    values = [var.boot_tf_policy]
  }
}

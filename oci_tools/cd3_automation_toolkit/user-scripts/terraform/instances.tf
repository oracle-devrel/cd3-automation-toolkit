#// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
#
#############################
## Module Block - Instances
## Create Instance
#############################

module "instances" {
  source   = "./modules/instance/instance"
  for_each = var.instance_vms != null ? var.instance_vms : {}
  availability_domain   = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id        = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[0][each.value.compartment_id]) : var.tenancy_ocid
  dedicated_vm_host_name= each.value.dedicated_vm_host_id != null ? each.value.dedicated_vm_host_id : null
  shape                 = each.value.shape
  ocpu_count            = each.value.ocpus
  defined_tags          = each.value.defined_tags
  display_name          = each.value.display_name
  #extended_metadata    = each.value.extended_metadata
  fault_domain          = each.value.fault_domain
  freeform_tags         = each.value.freeform_tags
  source_type           = each.value.source_type
  source_image_id       = each.value.source_type == "image" ? try(each.value.source_id == "Linux" ? var.Linux : each.value.source_id == "Windows" ? var.Windows : length(regexall("ocid1.image.oc1.*", each.value.source_id )) > 0 ? each.value.source_id : each.value.source_id) : each.value.source_id
  subnet_id             = merge(module.subnets.*...)[each.value.subnet_id]["subnet_tf_id"]
  assign_public_ip      = each.value.assign_public_ip
  ssh_public_keys       = length(regexall("ssh-rsa*",each.value.ssh_authorized_keys)) > 0 ? each.value.ssh_authorized_keys : var.ssh_public_key
  hostname_label        = each.value.display_name
  nsg_ids               = each.value.nsg_ids != null ?  [for nsg in each.value.nsg_ids : ( length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : try(merge(module.nsgs.*...)[nsg]["nsg_tf_id"][nsg],merge(module.nsgs.*...)[nsg]["nsg_tf_id"],merge(module.nsgs.*...)[nsg]["nsg_tf_id"]))] : null
}


#module "instance" {
#  source = "./modules/instance/instance"
#  compartment_id = "ocid1.compartment.oc1..aaaaaaaapmksuq5cemyfej4ljckx5yt32aajhcvvpon2bhnxn26odngehd7a"
#  shape = "VM.Standard2.1"
#  availability_domain = "wdWU:PHX-AD-1"
#  subnet_id = "ocid1.subnet.oc1.phx.aaaaaaaagqdtgadgleshz7l4xp5miaizp2fe2izojze42m3xlwj3bmziyq7a"
#  source_image_id       = "ocid1.image.oc1.phx.aaaaaaaa3imx2f53jbfwtl6akamfxbl2kkke74jbrek2hk5xgjvcgrw6v6fa"
#}
resource "oci_core_instance" "instances" {
  display_name        = var.instance_name
  availability_domain = var.instance_ad
  fault_domain        = var.instance_fd
  compartment_id      = var.instance_compartment_ocid
  shape               = var.instance_shape

  shape_config {

    memory_in_gbs = var.instance_ram
    ocpus         = var.instance_ocpus
    #baseline_ocpu_utilization = var.baseline_ocpu_utilization
  }
  source_details {
    source_id   = var.instance_image_ocid
    source_type = "image"
    #boot_volume_size_in_gbs = var.boot_volume_size
  }
  create_vnic_details {
    #assign_public_ip = local.PulicIP == true ? "false" : "true"
    assign_public_ip = var.assign_public_ip
    subnet_id        = var.subnet_id
    nsg_ids          = var.nsg_id == null ? [] : [var.nsg_id]
  }
  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = fileexists("${path.root}/scripts/${var.cloud_init_script}") ? "${base64encode(file("${path.root}/scripts/${var.cloud_init_script}"))}" : null
  }

  lifecycle {
    ignore_changes = []
  }
}

data "oci_core_instance" "instance" {
    #Required
    instance_id = oci_core_instance.instances.id
}
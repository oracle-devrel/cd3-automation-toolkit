/*
data "oci_identity_availability_domain" "ad" {
  compartment_id = var.tenancy_ocid
  ad_number      = var.availability_domain_number
}
*/

data "oci_identity_tenancy" "tenancy" {
    #Required
    tenancy_id = var.tenancy_ocid
}

data "oci_core_subnet" "subnet" {
  #Required
  count     = var.vcn_strategy == "Use Existing VCN" ? 1 : 0
  subnet_id = var.existing_subnet_id
}

data "oci_identity_compartment" "compartment" {
    #Required
    id = local.instance_compartment_ocid
    depends_on = [module.instance]
}

data "oci_core_images" "oracle_linux" {
  compartment_id   = var.tenancy_ocid
  operating_system = "Oracle Linux"
  shape            = var.instance_shape
  #display_name     = var.instance_os_version
  sort_by          = "TIMECREATED"
  sort_order       = "DESC"
  state            = "AVAILABLE"

   #filter restricts to OL
  filter {
    name   = "operating_system_version"
    values = ["${local.os_version}"]
    regex  = false
  }
}

data "oci_identity_users" "users" {

  compartment_id = var.tenancy_ocid
}

output "users_details" {
  value = data.oci_identity_users.users
}


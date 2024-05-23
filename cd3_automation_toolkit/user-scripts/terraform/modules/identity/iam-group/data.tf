data "oci_identity_users" "users" {

  #for_each = {for member in var.members :member => member}
  compartment_id = var.tenancy_ocid
}


#output "users_data" {
  #value = [for member in var.members : data.oci_identity_users.users[member].users[*].id]
#}
output "users_details" {
  value = data.oci_identity_users.users
}


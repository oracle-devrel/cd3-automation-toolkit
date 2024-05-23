data "oci_identity_domains" "iam_domains" {
  # Required
  compartment_id = var.tenancy_ocid

  # Optional
  display_name = var.idcs_endpoint

}

############################
# Data Source Block - Identity
# Get User Information by Email
############################


data "oci_identity_domains_users" "users" {
  idcs_endpoint = data.oci_identity_domains.iam_domains.domains[0].url
}







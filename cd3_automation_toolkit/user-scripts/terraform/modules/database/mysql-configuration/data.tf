############################
# Data Block - Database
# Create MySQL Configurations
############################

data "oci_mysql_shapes" "mysql_config_shapes" {
    #Required
    compartment_id = var.compartment_id
}
data "oci_core_shapes" "present_ad" {
  compartment_id      = var.compartment_id

}


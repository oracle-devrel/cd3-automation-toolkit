# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Database
# Create MySQL Configurations
############################

output "db_system_configuration_id" {
  description = "The OCID of the MySQL DB configuration."
  value       = oci_mysql_mysql_configuration.mysql_configuration.id
}

output "db_system_configuration" {
  description = "The display name of the MySQL configuration."
  value       = oci_mysql_mysql_configuration.mysql_configuration.display_name
}

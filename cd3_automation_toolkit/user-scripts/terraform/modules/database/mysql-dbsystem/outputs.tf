# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Database
# Create MySQL DB Systems
############################

output "db_system_id" {
  description = "The OCID of the MySQL DB system."
  value       = oci_mysql_mysql_db_system.db_system.id
}

output "db_system_hostname" {
  description = "The hostname of the MySQL DB system."
  value       = oci_mysql_mysql_db_system.db_system.hostname_label
}

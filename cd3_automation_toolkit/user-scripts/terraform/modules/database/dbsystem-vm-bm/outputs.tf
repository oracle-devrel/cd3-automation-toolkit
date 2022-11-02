// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Database
# Create Database VM BM
############################

output "database_tf_id" {
  value = oci_database_db_system.database_db_system.id
}
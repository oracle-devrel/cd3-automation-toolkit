// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

##############################
# Outputs Block - Database CDB
# Create Databases
##############################

output "cdb_name_tf_id" {
  value = oci_database_database.new_database.id
}
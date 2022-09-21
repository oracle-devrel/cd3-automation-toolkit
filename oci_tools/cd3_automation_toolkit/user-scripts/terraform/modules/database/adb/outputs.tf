// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Autonomous database
## Create autonomous database
################################

output "adb_tf_id" {
  value = oci_database_autonomous_database.autonomous_database.id
}
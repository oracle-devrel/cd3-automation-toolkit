# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Outputs Block - Autonomous database
## Create autonomous database
################################

output "adb_tf_id" {
  value = oci_database_autonomous_database.autonomous_database.id
}
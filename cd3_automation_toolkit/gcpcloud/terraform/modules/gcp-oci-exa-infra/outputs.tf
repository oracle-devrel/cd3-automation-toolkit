# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##########################################
## Outputs Block - Oracle ExaInfra @GCP
## Create Oracle ExaInfra @GCP
##########################################

output "infrastructure_id" {
  description = "Exadata Infrastructure ID"
  value       = google_oracle_database_cloud_exadata_infrastructure.exadata_infrastructure.properties[0].ocid
}

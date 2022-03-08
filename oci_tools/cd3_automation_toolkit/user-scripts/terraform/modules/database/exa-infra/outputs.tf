// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Outputs Block - Database
# Create ExaInfra
############################


output "exainfra_tf_id" {
  value = oci_database_cloud_exadata_infrastructure.exa_infra.id
}
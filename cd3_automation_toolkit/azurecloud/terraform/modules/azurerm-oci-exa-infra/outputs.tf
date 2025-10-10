# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Outputs Block - Oracle ExaInfra @Azure
## Create Oracle ExaInfra @Azure
#####################################

output "resource_id" {
  description = "Resource ID of Exadata Infrastructure in Azure"
  value = azurerm_oracle_exadata_infrastructure.exadata_infrastructure.id
}

/*
output "resource" {
  description = "Resource Object of Exadata Infrastructure in Azure"
  value = azurerm_oracle_exadata_infrastructure.this
}
*/
output "oci_region" {
  description = "Region of the Exadata Infrastructure in OCI"
  value = regex("(?:region=)([^?&/]+)",data.azurerm_oracle_exadata_infrastructure.exadata_infrastructures.oci_url)[0]
}

output "oci_compartment_ocid" {
  description = "Compartment OCID of the Exadata Infrastructure in OCI"
  value = regex("(?:compartmentId=)([^?&/]+)",data.azurerm_oracle_exadata_infrastructure.exadata_infrastructures.oci_url)[0]
}
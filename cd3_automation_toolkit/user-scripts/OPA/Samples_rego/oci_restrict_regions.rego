##########################################
# OCI restrict/deny regions for terraform#
##########################################


package terraform

import future.keywords.in
import input as tfplan

# Allowed Terraform resources
deny_regions = [
  "us-ashburn-1",
  "us-phoenix-1"
]

deny_region[reason] {
    resource := tfplan.variables[_]
    region := resource.value

    array_contains(deny_regions, region)
    deny := true
    reason := "Not allowed to provision resources in this region for OCI tenancy."
}

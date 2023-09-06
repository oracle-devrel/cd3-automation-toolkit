######################################
#Deny Launch igw/ngw in given tenancy#
######################################


package terraform

import future.keywords.in
import input as tfplan


deny_oci_services = ["oci_core_internet_gateway",
		     "oci_core_nat_gateway"]


deny_igw_and_ngw_launch[msg] {

     resource := tfplan.resource_changes[_]
     array_contains(deny_oci_services, resource.type) 

     msg := sprintf("%-40s : IGW/NGW is not allowed in this OCI tenancy", [resource.address])
}



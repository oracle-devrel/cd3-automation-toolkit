
    resource "oci_identity_policy" "AdminPolicy" {
            compartment_id = "${var.tenancy_ocid}" 
            description = "Administartors"
            name = "AdminPolicy"
            statements = [ "Allow group ${oci_identity_group.OCI_Admins.name},${oci_identity_group.Network_Admins.name} to read all-resources in tenancy" , 
                    "Allow group ${oci_identity_group.Network_Admins.name} to manage all-resources in comaprtment ${oci_identity_compartment.Networking.name}"  ]
        }
    resource "oci_identity_policy" "InstancePolicy" {
            compartment_id = "${oci_identity_compartment.Ryder-Dev.id}" 
            description = "Instance Manage"
            name = "InstancePolicy"
            statements = [ "Allow group ${oci_identity_group.VM_Admins.name} to manage instance-family in comaprtment ${oci_identity_compartment.Ryder-Dev.name}" , 
                    "Allow group ${oci_identity_group.VM_Admins.name} to read all-resources in tenancy"  ]
        }
    
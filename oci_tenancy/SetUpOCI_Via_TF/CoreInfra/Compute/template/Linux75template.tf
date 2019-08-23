resource "oci_core_instance" "##Hostname##" {
        #Required
        #availability_domain = "##Availability Domain##"
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.##Availability Domain##.name}"
        compartment_id = "${var.##Compartment Name##}"
        fault_domain = "##Fault Domain##"
        ### windows image id - oci image ###
        source_details {
		        source_id  = "${var.linux75_ocid}"
                source_type = "image"
        }
        shape = "##Shape##"


        #Optional
        create_vnic_details {
                #Required
                subnet_id = "${oci_core_subnet.##subnet name##.id}"
                assign_public_ip = ##Pub Address##

                #Optional
                display_name = "##Hostname##"
                hostname_label = "##Hostname##"
                private_ip = "##IP Address##"
                skip_source_dest_check = false
                ## NSG Info ##
        }
        display_name = "##Hostname##"
        hostname_label = "##Hostname##"
        metadata = {

				ssh_authorized_keys = "##SSH-key-var-name##"
        }

        subnet_id = "${oci_core_subnet.##subnet name##.id}"
        ## Defined Tag Info ##
}

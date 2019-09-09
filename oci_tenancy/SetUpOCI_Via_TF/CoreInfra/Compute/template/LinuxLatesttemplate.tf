resource "oci_core_instance" "##Hostname##" {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.##Availability Domain##.name}"
        compartment_id = "${var.##Compartment Name##}"
        shape = "##Shape##"

        #Optional
        fault_domain = "##Fault Domain##"
        source_details {
		        source_id  = "${var.linux_latest_ocid}"
                source_type = "image"
        }
        create_vnic_details {
                #Required
                subnet_id = "${oci_core_subnet.##subnet name##.id}"

                #Optional
                assign_public_ip = ##Pub Address##
                display_name = "##Hostname##"
                hostname_label = "##Hostname##"
                private_ip = "##IP Address##"
                skip_source_dest_check = false

                ##NSGs##
        }

        ##DedicatedVMHost##

        display_name = "##Hostname##"
        hostname_label = "##Hostname##"
        metadata = {

				ssh_authorized_keys = "${var.##SSH-key-var-name##}"
        }
        subnet_id = "${oci_core_subnet.##subnet name##.id}"

        ## Defined Tag Info ##
}

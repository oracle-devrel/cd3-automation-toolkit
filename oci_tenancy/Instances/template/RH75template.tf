resource "oci_core_instance" "##Hostname##" {
        #Required
        #availability_domain = "##Availability Domain##"
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.##Availability Domain##.name}"
        compartment_id = "${var.compartment_ocid}"
### windows image id - oci image ###
        source_details {
		        source_id  = "${var.rh75_gen1_ocid}"
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
        }
        display_name = "##Hostname##"
        hostname_label = "##Hostname##"
        metadata {
                #ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArnZV6lMb+QcUXdJVaupCDtlxCgkbJuUwnfYpKGSZI0Xev9CBUqlXujWM6l7kIb7C4EeNgR4sw+2fTxlcVFPbbryahrOgW9IG8AUwzOqBbQNwyCui1hyOksF3Z1hNBqRL8qsZOj6FnKr3hv+4ESBi7YHhcGK4qTBpzkYpUPMOXqDb1ODo/Mjp4+p7ih0xF5UP6icw7UK45oXhTmkefQLUdpLGiosDGjoiDZZT5vQ4m2gfoLWJnEbp3HbjNJbz/zJDyJWhhN6P4k/wQDQKp4Vvphu11BTSwHLWQqAFK2X8HxZbmD/sKdzxEeWn3qXD8++DOqxAVpxVtCqKROxPXwYa0Q=="
				ssh_authorized_keys = "##SSH-key##"
        }

        subnet_id = "${oci_core_subnet.##subnet name##.id}"
}

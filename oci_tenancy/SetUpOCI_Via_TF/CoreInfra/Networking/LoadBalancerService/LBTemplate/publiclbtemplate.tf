resource "oci_load_balancer" "##LBName##" {
  shape          = "##LBSize##Mbps"
  compartment_id = "${var.ntk_compartment_ocid}"
  subnet_ids     = [
    "${oci_core_subnet.##LBSubnet1##.id}",
    "${oci_core_subnet.##LBSubnet2##.id}"
  ]
  display_name   = "##LBName##"
}

resource "oci_load_balancer_backend_set" "##LB_BES_Name##" {
  name             = "##LB_BES_Name##"
  load_balancer_id = "${oci_load_balancer.##LBName##.id}"
  policy           = "ROUND_ROBIN"

  health_checker {
    port     = "80"
    protocol = "HTTP"
    response_body_regex = ".*"
    url_path = "/"
  }
}

resource "oci_load_balancer_hostname" "##LBHostName##" {
    #Required
    hostname = "##LBURL##"
    load_balancer_id = "${oci_load_balancer.##LBName##.id}"
    name = "##LBHostName##"
}

resource "oci_load_balancer_listener" "##LBListener##" {
  load_balancer_id         = "${oci_load_balancer.##LBName##.id}"
  name                     = "http"
  default_backend_set_name = "${oci_load_balancer_backend_set.##LB_BES_Name##.id}"
  hostname_names           = ["${oci_load_balancer_hostname.##LBHostName##.name}"]
  port                     = 80
  protocol                 = "HTTP"
  connection_configuration {
    idle_timeout_in_seconds = "2"
  }
}

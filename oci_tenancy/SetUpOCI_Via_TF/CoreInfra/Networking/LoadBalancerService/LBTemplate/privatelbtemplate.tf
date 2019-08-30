resource "oci_load_balancer_load_balancer" "##LBName##" {
  shape          = "##LBSize##Mbps"
  compartment_id = "${var.ntk_compartment_ocid}"
  subnet_ids     = [
    "${oci_core_subnet.##LBSubnet1##.id}"
  ]
  display_name   = "##LBName##"
  is_private = true
  ## NSG Info ##
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

resource "oci_load_balancer_backend" "##LB_BES_Name##_##serverName##" {
  load_balancer_id = "${oci_load_balancer.##LBName##.id}"
  backendset_name  = "${oci_load_balancer_backend_set.##LB_BES_Name##.id}"
  ip_address       = "${oci_core_instance.##serverName##.private_ip}"
  port             = 80
  backup           = false
  drain            = false
  offline          = false
  weight           = 1
}

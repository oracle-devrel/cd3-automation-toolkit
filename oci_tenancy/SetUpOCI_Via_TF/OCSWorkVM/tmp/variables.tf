variable "ssh_public_key" {
        type = "string"
        default = "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA3HrADHAKh07+1Ux0GiVZ5RWG7lU3CsKl4USwHN6sFdM8HPepv+Wpsr+OVeU5po5u/u24QgHGzST10TqHGyMq1/krGTThhg3O1yh5KKhhKWM8LngtkBBhQrTStBvWMfTd48TWnG07hmT23dywge7IFXKH3SOiWc8MaqxVsOCtaqv21Osvmfpu52BlNLHi8CymvGs9ocw9YsSlkwraqW7oxZGTW9AyGC8RcxeoWKd/mia8jJ91XcEbVUzBV1eJBdtW+L8doATLmkFvfDwCQ3E3rMF1WqN60ktCCmSDezapV6uh91VG7DsaANkFM0JlLOxNJ6AjhEYPoOFfpGWPOS3t6w== rsa-key-20180322"
}
variable "tenancy_ocid" {
        type = "string"
        default = "ocid1.tenancy.oc1..aaaaaaaa25y2onbrqku7vqiz4rw3rpf44rszvarpq3zrzvrbzgeekrh5silq"
}
variable "user_ocid" {
        type = "string"
        default = "ocid1.user.oc1..aaaaaaaacthustctj5qpzptv2pioxqqz4mzn4wmzffg4oeb75fzzxuoqtarq"
}
variable "compartment_ocid" {
        type = "string"
        default = ""
}
variable "ntk_compartment_ocid" {
        type = "string"
        default = "ocid1.compartment.oc1..aaaaaaaadlsew3uzgskgdwtbqnuu3algyweoo2j42iqdhldc4oqbsrb373nq"
}
#Added below variable because tf file generated through Koala uses this variable for network components
variable "compartment_id" {
        type = "string"
        default = "ocid1.compartment.oc1..aaaaaaaadlsew3uzgskgdwtbqnuu3algyweoo2j42iqdhldc4oqbsrb373nq"
}
variable "fingerprint" {
        type = "string"
        default = "a2:9d:39:04:e4:0a:9a:7f:51:0e:00:d6:d6:d4:d2:7d"
}
variable "private_key_path" {
        type = "string"
        default = "/root/ocswork/keys/oci_api_key.pem"
}
variable "region" {
        type = "string"
        default = "us-phoenix-1"
}

variable "windows_latest_ocid" {
        type = "string"
        default = "ocid1.image.oc1.phx.aaaaaaaawrgasvwdmyiy2ebeikudvbvtxlqmvixu7vwmmmhfhwmsn6f3g33a"
}
variable "linux_latest_ocid"{
        type = "string"
        default = "ocid1.image.oc1.phx.aaaaaaaa2wadtmv6j6zboncfobau7fracahvweue6dqipmcd5yj6s54f3wpq"
}
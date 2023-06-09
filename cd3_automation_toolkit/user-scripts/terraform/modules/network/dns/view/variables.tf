#############################
# Variable Block - DNS View #
#############################
variable "view_compartment_id" {
  type    = string
  default = null
}

variable "view_scope" {
  type    = string
  default = "PRIVATE"
}

variable "view_display_name" {
  type    = string
  default = null
}

variable "view_defined_tags" {
  type    = map(string)
  default = {}
}

variable "view_freeform_tags" {
  type    = map(string)
  default = {}
}